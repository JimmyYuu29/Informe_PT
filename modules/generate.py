# modules/generate.py
"""
Generate - Unified entry point for document generation.
"""
import time
from datetime import date
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass, field

from .plugin_loader import PluginPack, load_plugin
from .contract_validator import validate_input, ValidationResult
from .context_builder import ContextBuilder
from .renderer_docx import DocxRenderer
from .rule_engine import EvaluationTrace
from .audit_logger import AuditLogger, GenerationTrace


@dataclass
class GenerationOptions:
    """Options for document generation."""
    validate: bool = True
    strict_validation: bool = True
    apply_cell_colors: bool = True
    output_path: Optional[Path] = None
    save_trace: bool = True


@dataclass
class GenerationResult:
    """Result of a document generation."""
    success: bool
    output_path: Optional[Path] = None
    trace_id: Optional[str] = None
    trace_file: Optional[Path] = None
    validation_result: Optional[ValidationResult] = None
    evaluation_traces: list[EvaluationTrace] = field(default_factory=list)
    error: Optional[str] = None
    duration_ms: int = 0

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "output_path": str(self.output_path) if self.output_path else None,
            "trace_id": self.trace_id,
            "trace_file": str(self.trace_file) if self.trace_file else None,
            "validation": self.validation_result.to_dict() if self.validation_result else None,
            "error": self.error,
            "duration_ms": self.duration_ms,
        }


def preprocess_input(data: dict) -> dict:
    """Preprocess input data before validation and generation."""
    processed = dict(data)

    # Convert date strings to date objects
    if "fecha_fin_fiscal" in processed:
        fecha = processed["fecha_fin_fiscal"]
        if isinstance(fecha, str):
            try:
                parts = fecha.split("-")
                processed["fecha_fin_fiscal"] = date(
                    int(parts[0]), int(parts[1]), int(parts[2])
                )
            except Exception:
                pass

    # Convert numeric strings to numbers
    numeric_fields = [
        "master_file",
        "cifra_1", "cifra_0",
        "ebit_1", "ebit_0",
        "resultado_fin_1", "resultado_fin_0",
        "ebt_1", "ebt_0",
        "resultado_net_1", "resultado_net_0",
    ]

    for field_name in numeric_fields:
        if field_name in processed:
            value = processed[field_name]
            if isinstance(value, str):
                try:
                    if "." in value or "," in value:
                        processed[field_name] = float(value.replace(",", "."))
                    else:
                        processed[field_name] = int(value)
                except ValueError:
                    pass

    return processed


def generate(
    plugin_id: str,
    input_data: dict,
    options: Optional[GenerationOptions] = None
) -> GenerationResult:
    """
    Generate a document from a plugin and input data.

    This is the main unified entry point for document generation.

    Args:
        plugin_id: The ID of the plugin to use.
        input_data: Input data dictionary.
        options: Optional generation options.

    Returns:
        GenerationResult with output path, traces, and status.
    """
    if options is None:
        options = GenerationOptions()

    start_time = time.time()
    result = GenerationResult(success=False)

    try:
        # Load plugin
        plugin = load_plugin(plugin_id)

        # Initialize audit logger
        audit_logger = AuditLogger(
            plugin_id=plugin_id,
            sensitive_fields=plugin.get_sensitive_fields()
        )

        # Generate trace ID
        from .audit_logger import generate_trace_id
        result.trace_id = generate_trace_id()

        # Log generation start
        audit_logger.log_generation_start(result.trace_id, input_data)

        # Preprocess input
        processed_data = preprocess_input(input_data)

        # Validate if requested
        if options.validate:
            validation_result = validate_input(plugin, processed_data)
            result.validation_result = validation_result

            audit_logger.log_validation_result(
                result.trace_id,
                validation_result.is_valid,
                validation_result.errors,
                validation_result.warnings
            )

            if not validation_result.is_valid and options.strict_validation:
                result.error = "; ".join(validation_result.errors[:5])
                result.duration_ms = int((time.time() - start_time) * 1000)
                return result

        # Render document
        renderer = DocxRenderer(plugin)
        output_path, traces = renderer.render(
            processed_data,
            output_path=options.output_path,
            apply_cell_colors=options.apply_cell_colors
        )

        result.output_path = output_path
        result.evaluation_traces = traces
        result.success = True

        # Log rule evaluation
        audit_logger.log_rule_evaluation(result.trace_id, traces)

        # Calculate duration
        result.duration_ms = int((time.time() - start_time) * 1000)

        # Log completion
        audit_logger.log_generation_complete(
            result.trace_id,
            output_path,
            result.duration_ms
        )

        # Save trace if requested
        if options.save_trace:
            trace = audit_logger.create_trace(
                input_data=processed_data,
                output_path=output_path,
                evaluation_traces=traces,
                validation_errors=(
                    result.validation_result.errors
                    if result.validation_result else []
                ),
                duration_ms=result.duration_ms
            )
            result.trace_file = audit_logger.save_trace(trace)

    except FileNotFoundError as e:
        result.error = f"Plugin or template not found: {e}"
        result.duration_ms = int((time.time() - start_time) * 1000)
    except Exception as e:
        result.error = f"Generation failed: {e}"
        result.duration_ms = int((time.time() - start_time) * 1000)

        # Log error if we have audit logger
        try:
            if 'audit_logger' in locals():
                audit_logger.log_generation_error(result.trace_id, e)
        except Exception:
            pass

    return result


def generate_with_validation(
    plugin_id: str,
    input_data: dict
) -> tuple[GenerationResult, ValidationResult]:
    """
    Generate a document with explicit validation result return.

    Convenience wrapper that returns both generation and validation results.
    """
    options = GenerationOptions(validate=True, strict_validation=False)
    result = generate(plugin_id, input_data, options)
    return result, result.validation_result
