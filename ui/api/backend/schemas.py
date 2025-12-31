# ui/api/backend/schemas.py
"""
Pydantic schemas for API request/response models.
"""
from datetime import date
from typing import Any, Optional
from pydantic import BaseModel, Field


# ============================================================================
# Plugin Schemas
# ============================================================================

class PluginInfo(BaseModel):
    """Basic plugin information."""
    plugin_id: str
    name: str
    description: Optional[str] = None
    version: str = "1.0.0"
    language: str = "es"


class PluginListResponse(BaseModel):
    """Response for listing plugins."""
    plugins: list[PluginInfo]
    count: int


# ============================================================================
# Field Schemas
# ============================================================================

class FieldDefinition(BaseModel):
    """Field definition for schema endpoint."""
    name: str
    type: str
    label: str
    required: bool = False
    description: Optional[str] = None
    multiline: bool = False
    condition: Optional[str] = None
    values: Optional[list] = None  # For enum fields
    validation: Optional[dict] = None
    item_schema: Optional[dict] = None  # For list fields


class PluginSchemaResponse(BaseModel):
    """Response for plugin schema endpoint."""
    plugin_id: str
    fields: list[FieldDefinition]
    ui_sections: list[dict]


# ============================================================================
# Validation Schemas
# ============================================================================

class ValidationRequest(BaseModel):
    """Request to validate input data."""
    data: dict = Field(..., description="Input data to validate")


class ValidationResponse(BaseModel):
    """Response from validation endpoint."""
    is_valid: bool
    errors: list[str] = []
    warnings: list[str] = []


# ============================================================================
# Generation Schemas
# ============================================================================

class GenerateRequest(BaseModel):
    """Request to generate a document."""
    data: dict = Field(..., description="Input data for document generation")
    validate: bool = Field(True, description="Whether to validate before generating")
    strict_validation: bool = Field(False, description="Fail on validation errors")
    apply_cell_colors: bool = Field(True, description="Apply cell background colors")


class TraceHit(BaseModel):
    """A single rule evaluation result."""
    rule_id: str
    rule_name: str
    condition_met: bool
    action_type: str
    source_block_ids: list[str] = []


class DecisionTrace(BaseModel):
    """Trace of a decision evaluation."""
    decision_id: str
    decision_name: str
    rule_hits: list[TraceHit] = []


class GenerateResponse(BaseModel):
    """Response from generation endpoint."""
    success: bool
    output_path: Optional[str] = None
    trace_id: Optional[str] = None
    trace_file: Optional[str] = None
    validation: Optional[ValidationResponse] = None
    decision_traces: list[DecisionTrace] = []
    error: Optional[str] = None
    duration_ms: int = 0


# ============================================================================
# Error Schemas
# ============================================================================

class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    detail: Optional[str] = None
    code: str = "ERROR"


class PluginNotFoundError(BaseModel):
    """Plugin not found error."""
    error: str = "Plugin not found"
    plugin_id: str
    code: str = "PLUGIN_NOT_FOUND"
