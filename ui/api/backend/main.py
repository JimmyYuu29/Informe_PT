#!/usr/bin/env python3
# ui/api/backend/main.py
"""
FastAPI Backend for Document Generation Platform.

Run with: uvicorn ui.api.backend.main:app --reload
"""
import sys
from pathlib import Path
from typing import Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from modules.plugin_loader import load_plugin, list_plugins
from modules.generate import generate, GenerationOptions
from modules.contract_validator import validate_input
from modules.validate_plugin import validate_plugin as validate_plugin_integrity

from .schemas import (
    PluginInfo,
    PluginListResponse,
    PluginSchemaResponse,
    FieldDefinition,
    ValidationRequest,
    ValidationResponse,
    GenerateRequest,
    GenerateResponse,
    DecisionTrace,
    TraceHit,
    ErrorResponse,
)
from .deps import get_plugin, get_settings, Settings


# Create FastAPI app
app = FastAPI(
    title="Document Generation API",
    description="API for generating documents from YAML-configured plugins",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Health Check
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}


# ============================================================================
# Plugin Endpoints
# ============================================================================

@app.get("/plugins", response_model=PluginListResponse)
async def get_plugins():
    """
    List all available plugins.

    Returns a list of plugin IDs and basic information.
    """
    plugin_ids = list_plugins()
    plugins = []

    for plugin_id in plugin_ids:
        try:
            plugin = load_plugin(plugin_id)
            manifest = plugin.manifest

            plugins.append(PluginInfo(
                plugin_id=plugin_id,
                name=manifest.get("name", plugin_id),
                description=manifest.get("description"),
                version=manifest.get("version", "1.0.0"),
                language=manifest.get("language", "es"),
            ))
        except Exception:
            # Include plugin even if loading fails
            plugins.append(PluginInfo(
                plugin_id=plugin_id,
                name=plugin_id,
            ))

    return PluginListResponse(
        plugins=plugins,
        count=len(plugins),
    )


@app.get("/plugins/{plugin_id}/schema", response_model=PluginSchemaResponse)
async def get_plugin_schema(plugin_id: str):
    """
    Get the input schema for a plugin.

    Returns field definitions and UI configuration.
    """
    try:
        plugin = load_plugin(plugin_id)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plugin '{plugin_id}' not found",
        )

    fields_def = plugin.get_field_definitions()
    ui_sections = plugin.get_ui_sections()

    # Convert to response format
    fields = []
    for field_name, field_def in fields_def.items():
        fields.append(FieldDefinition(
            name=field_name,
            type=field_def.get("type", "text"),
            label=field_def.get("label", field_name),
            required=field_def.get("required", False),
            description=field_def.get("description"),
            multiline=field_def.get("multiline", False),
            condition=field_def.get("condition"),
            values=field_def.get("values"),
            validation=field_def.get("validation"),
            item_schema=field_def.get("item_schema"),
        ))

    return PluginSchemaResponse(
        plugin_id=plugin_id,
        fields=fields,
        ui_sections=ui_sections,
    )


# ============================================================================
# Validation Endpoint
# ============================================================================

@app.post("/plugins/{plugin_id}/validate", response_model=ValidationResponse)
async def validate_data(plugin_id: str, request: ValidationRequest):
    """
    Validate input data against a plugin's schema.

    Returns validation errors and warnings.
    """
    try:
        plugin = load_plugin(plugin_id)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plugin '{plugin_id}' not found",
        )

    result = validate_input(plugin, request.data)

    return ValidationResponse(
        is_valid=result.is_valid,
        errors=result.errors,
        warnings=result.warnings,
    )


# ============================================================================
# Generation Endpoint
# ============================================================================

@app.post("/plugins/{plugin_id}/generate", response_model=GenerateResponse)
async def generate_document(plugin_id: str, request: GenerateRequest):
    """
    Generate a document from input data.

    Returns the path to the generated document and trace information.
    """
    try:
        plugin = load_plugin(plugin_id)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plugin '{plugin_id}' not found",
        )

    # Create generation options
    options = GenerationOptions(
        validate=request.validate,
        strict_validation=request.strict_validation,
        apply_cell_colors=request.apply_cell_colors,
        save_trace=True,
    )

    # Generate document
    result = generate(plugin_id, request.data, options)

    # Build response
    validation_response = None
    if result.validation_result:
        validation_response = ValidationResponse(
            is_valid=result.validation_result.is_valid,
            errors=result.validation_result.errors,
            warnings=result.validation_result.warnings,
        )

    decision_traces = []
    for trace in result.evaluation_traces:
        hits = [
            TraceHit(
                rule_id=h.rule_id,
                rule_name=h.rule_name,
                condition_met=h.condition_met,
                action_type=h.action_type,
                source_block_ids=h.source_block_ids,
            )
            for h in trace.rule_hits
        ]
        decision_traces.append(DecisionTrace(
            decision_id=trace.decision_id,
            decision_name=trace.decision_name,
            rule_hits=hits,
        ))

    return GenerateResponse(
        success=result.success,
        output_path=str(result.output_path) if result.output_path else None,
        trace_id=result.trace_id,
        trace_file=str(result.trace_file) if result.trace_file else None,
        validation=validation_response,
        decision_traces=decision_traces,
        error=result.error,
        duration_ms=result.duration_ms,
    )


# ============================================================================
# Download Endpoint
# ============================================================================

@app.get("/download/{filename}")
async def download_document(filename: str):
    """
    Download a generated document by filename.
    """
    output_dir = PROJECT_ROOT / "output"
    file_path = output_dir / filename

    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File '{filename}' not found",
        )

    # Security check - ensure file is within output directory
    try:
        file_path.resolve().relative_to(output_dir.resolve())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


# ============================================================================
# Plugin Validation Endpoint (for CI)
# ============================================================================

@app.get("/plugins/{plugin_id}/validate-integrity")
async def validate_plugin_pack(plugin_id: str):
    """
    Validate a plugin pack's integrity (for CI/deployment).

    Checks required files, references, operators, etc.
    """
    result = validate_plugin_integrity(plugin_id)

    return {
        "plugin_id": plugin_id,
        "is_valid": result.is_valid,
        "errors": result.errors,
        "warnings": result.warnings,
        "info": result.info,
    }


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "code": "HTTP_ERROR"},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": str(exc), "code": "INTERNAL_ERROR"},
    )


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
