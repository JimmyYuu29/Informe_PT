# modules/audit_logger.py
"""
Audit Logger - Logging and traceability for document generation.
"""
import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass, field, asdict

from .rule_engine import EvaluationTrace, RuleHit


# Configure logging
LOG_DIR = Path(__file__).parent.parent / "logs"


def ensure_log_dir() -> Path:
    """Ensure the log directory exists."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    return LOG_DIR


@dataclass
class GenerationTrace:
    """Complete trace of a document generation."""
    trace_id: str
    plugin_id: str
    timestamp: str
    input_hash: str
    output_path: Optional[str]
    decision_traces: list[dict] = field(default_factory=list)
    validation_errors: list[str] = field(default_factory=list)
    masked_fields: list[str] = field(default_factory=list)
    duration_ms: Optional[int] = None


class AuditLogger:
    """Logger for document generation with traceability."""

    def __init__(self, plugin_id: str, sensitive_fields: Optional[list[str]] = None):
        self.plugin_id = plugin_id
        self.sensitive_fields = sensitive_fields or []
        self.logger = logging.getLogger(f"docgen.{plugin_id}")

        # Configure handler if not already configured
        if not self.logger.handlers:
            ensure_log_dir()
            handler = logging.FileHandler(LOG_DIR / f"{plugin_id}.log")
            handler.setFormatter(
                logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            )
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def mask_sensitive_data(self, data: dict) -> dict:
        """Mask sensitive fields in data for logging."""
        masked = dict(data)
        for field_name in self.sensitive_fields:
            if field_name in masked and masked[field_name]:
                # Mask all but first 2 chars
                original = str(masked[field_name])
                if len(original) > 2:
                    masked[field_name] = original[:2] + "*" * (len(original) - 2)
                else:
                    masked[field_name] = "**"
        return masked

    def log_generation_start(self, trace_id: str, input_data: dict) -> None:
        """Log the start of a generation."""
        masked_data = self.mask_sensitive_data(input_data)
        self.logger.info(
            f"Generation started - trace_id={trace_id} "
            f"input_fields={list(masked_data.keys())}"
        )

    def log_validation_result(
        self,
        trace_id: str,
        is_valid: bool,
        errors: list[str],
        warnings: list[str]
    ) -> None:
        """Log validation results."""
        if is_valid:
            self.logger.info(
                f"Validation passed - trace_id={trace_id} warnings={len(warnings)}"
            )
        else:
            self.logger.warning(
                f"Validation failed - trace_id={trace_id} errors={errors}"
            )

    def log_rule_evaluation(
        self,
        trace_id: str,
        traces: list[EvaluationTrace]
    ) -> None:
        """Log rule evaluation results."""
        for trace in traces:
            hits = [h.rule_id for h in trace.rule_hits if h.condition_met]
            self.logger.debug(
                f"Decision '{trace.decision_id}' evaluated - trace_id={trace_id} "
                f"rules_hit={hits}"
            )

    def log_generation_complete(
        self,
        trace_id: str,
        output_path: Path,
        duration_ms: int
    ) -> None:
        """Log successful generation completion."""
        self.logger.info(
            f"Generation complete - trace_id={trace_id} "
            f"output={output_path.name} duration_ms={duration_ms}"
        )

    def log_generation_error(
        self,
        trace_id: str,
        error: Exception
    ) -> None:
        """Log a generation error."""
        self.logger.error(
            f"Generation failed - trace_id={trace_id} error={str(error)}"
        )

    def create_trace(
        self,
        input_data: dict,
        output_path: Optional[Path] = None,
        evaluation_traces: Optional[list[EvaluationTrace]] = None,
        validation_errors: Optional[list[str]] = None,
        duration_ms: Optional[int] = None
    ) -> GenerationTrace:
        """Create a complete generation trace."""
        trace_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()

        # Create input hash (simple hash of sorted keys)
        input_hash = str(hash(tuple(sorted(input_data.keys()))))

        # Convert evaluation traces to dicts
        decision_traces = []
        if evaluation_traces:
            for et in evaluation_traces:
                decision_traces.append({
                    "decision_id": et.decision_id,
                    "decision_name": et.decision_name,
                    "rule_hits": [
                        {
                            "rule_id": h.rule_id,
                            "rule_name": h.rule_name,
                            "condition_met": h.condition_met,
                            "action_type": h.action_type,
                            "source_block_ids": h.source_block_ids,
                        }
                        for h in et.rule_hits
                    ],
                })

        return GenerationTrace(
            trace_id=trace_id,
            plugin_id=self.plugin_id,
            timestamp=timestamp,
            input_hash=input_hash,
            output_path=str(output_path) if output_path else None,
            decision_traces=decision_traces,
            validation_errors=validation_errors or [],
            masked_fields=self.sensitive_fields,
            duration_ms=duration_ms,
        )

    def save_trace(self, trace: GenerationTrace) -> Path:
        """Save a trace to a JSON file."""
        ensure_log_dir()
        trace_file = LOG_DIR / f"trace_{trace.trace_id}.json"
        with open(trace_file, "w", encoding="utf-8") as f:
            json.dump(asdict(trace), f, indent=2, ensure_ascii=False)
        return trace_file


def generate_trace_id() -> str:
    """Generate a unique trace ID."""
    return str(uuid.uuid4())
