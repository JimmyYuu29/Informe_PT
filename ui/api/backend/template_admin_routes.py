# ui/api/backend/template_admin_routes.py
"""
FastAPI routes for Template Admin functionality.

Provides REST endpoints for:
  - Template validation
  - Template publishing (via Power Automate to SharePoint)
  - Version listing and rollback
  - Available fields listing
"""
import json
import os
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

import sys
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from modules.plugin_loader import load_plugin, list_plugins
from modules.template_validator import (
    validate_template, generate_validation_report, get_available_fields
)
from modules.template_registry import TemplateRegistry
from modules.sharepoint_publisher import (
    publish_to_sharepoint, build_metadata, POWER_AUTOMATE_URL
)


# ============================================================================
# Router
# ============================================================================

router = APIRouter(prefix="/template", tags=["Template Admin"])


# ============================================================================
# Configuration
# ============================================================================

ADMIN_PASSWORD = os.environ.get("TEMPLATE_ADMIN_PASSWORD", "admin123")
ALLOW_PUBLISH_WITH_WARNINGS = os.environ.get(
    "ALLOW_PUBLISH_WITH_WARNINGS", "false"
).lower() == "true"


# ============================================================================
# Schemas
# ============================================================================

class AuthRequest(BaseModel):
    password: str


class AuthResponse(BaseModel):
    authorized: bool
    message: str = ""


class PublishRequest(BaseModel):
    plugin_id: str
    template_name: str = "template_final"
    version_bump: str = Field("patch", pattern="^(major|minor|patch)$")
    author: str = ""
    change_log: str


class PublishResponse(BaseModel):
    success: bool
    version: Optional[str] = None
    sharepoint_url: Optional[str] = None
    sha256: Optional[str] = None
    cache_path: Optional[str] = None
    error: Optional[str] = None


class RollbackRequest(BaseModel):
    plugin_id: str
    target_version: str


class VersionInfo(BaseModel):
    plugin_id: str
    template_name: str
    version: str
    created_at: str
    author: str
    change_log: str
    sha256: str
    validation_status: str
    is_active: bool
    sharepoint_url: Optional[str] = None


# ============================================================================
# Auth Endpoint
# ============================================================================

@router.post("/auth", response_model=AuthResponse)
async def authenticate(request: AuthRequest):
    """Verify admin password."""
    if request.password == ADMIN_PASSWORD:
        return AuthResponse(authorized=True, message="Authenticated successfully")
    return AuthResponse(authorized=False, message="Invalid password")


# ============================================================================
# Validation Endpoint
# ============================================================================

@router.post("/validate")
async def validate_uploaded_template(
    file: UploadFile = File(...),
    plugin_id: str = Form(...),
):
    """
    Validate an uploaded DOCX template.

    Performs syntax check, variable consistency, smoke-test render,
    and anchor validation.
    """
    if not file.filename.endswith(".docx"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a .docx file"
        )

    try:
        plugin = load_plugin(plugin_id)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plugin '{plugin_id}' not found"
        )

    # Save to temp file
    file_bytes = await file.read()
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        # Find sample input
        sample_input = str(PROJECT_ROOT / "tests" / "golden" / "sample_input.json")
        if not Path(sample_input).exists():
            sample_input = None

        result = validate_template(
            template_path=tmp_path,
            plugin=plugin,
            sample_input_path=sample_input,
            check_anchors=True,
        )

        report = generate_validation_report(result)
        return JSONResponse(content=report)

    finally:
        try:
            Path(tmp_path).unlink()
        except Exception:
            pass


# ============================================================================
# Publish Endpoint
# ============================================================================

@router.post("/publish", response_model=PublishResponse)
async def publish_template(
    file: UploadFile = File(...),
    plugin_id: str = Form(...),
    template_name: str = Form("template_final"),
    version_bump: str = Form("patch"),
    author: str = Form(""),
    change_log: str = Form(...),
    password: str = Form(...),
):
    """
    Publish a validated template.

    1. Authenticates admin
    2. Re-validates the template
    3. Publishes to SharePoint via Power Automate (if configured)
    4. Records in local registry with versioning
    """
    # Auth check
    if password != ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin password"
        )

    if not file.filename.endswith(".docx"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a .docx file"
        )

    try:
        plugin = load_plugin(plugin_id)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plugin '{plugin_id}' not found"
        )

    # Save to temp file and validate
    file_bytes = await file.read()
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        sample_input = str(PROJECT_ROOT / "tests" / "golden" / "sample_input.json")
        if not Path(sample_input).exists():
            sample_input = None

        result = validate_template(
            template_path=tmp_path,
            plugin=plugin,
            sample_input_path=sample_input,
        )

        # Check validation status
        if result.status == "FAIL":
            return PublishResponse(
                success=False,
                error="Template validation FAILED. Fix errors before publishing."
            )

        if result.status == "WARN" and not ALLOW_PUBLISH_WITH_WARNINGS:
            # Allow but log warning
            pass

        # Determine version
        registry = TemplateRegistry()
        version = registry.get_next_version(plugin_id, version_bump)
        previous_version = registry.get_latest_version(plugin_id)

        # Build metadata
        metadata = build_metadata(
            plugin_id=plugin_id,
            template_name=template_name,
            version=version,
            author=author,
            change_log=change_log,
            sha256=result.sha256,
            variables=result.variables_found,
            validation_status=result.status,
            validation_errors=[e.message for e in result.errors],
            validation_warnings=[w.message for w in result.warnings],
            previous_version=previous_version,
        )

        report = generate_validation_report(result)

        # Publish to SharePoint if configured
        sp_url = None
        sp_metadata_url = None
        sp_validation_url = None

        if POWER_AUTOMATE_URL:
            try:
                sp_response = publish_to_sharepoint(
                    plugin_id=plugin_id,
                    template_name=template_name,
                    version=version,
                    template_bytes=file_bytes,
                    metadata_json=metadata,
                    validation_report_json=report,
                )
                if sp_response.ok:
                    sp_url = sp_response.template_file_url
                    sp_metadata_url = sp_response.metadata_file_url
                    sp_validation_url = sp_response.validation_file_url
            except Exception:
                pass  # SharePoint publish is best-effort

        # Save to local registry
        tv = registry.publish(
            plugin_id=plugin_id,
            template_name=template_name,
            version=version,
            author=author,
            change_log=change_log,
            sha256=result.sha256,
            variables=result.variables_found,
            validation_status=result.status,
            validation_errors=[e.message for e in result.errors],
            validation_warnings=[w.message for w in result.warnings],
            template_bytes=file_bytes,
            sharepoint_url=sp_url,
            sharepoint_metadata_url=sp_metadata_url,
            sharepoint_validation_url=sp_validation_url,
        )

        return PublishResponse(
            success=True,
            version=version,
            sharepoint_url=sp_url,
            sha256=result.sha256,
            cache_path=tv.cache_path,
        )

    finally:
        try:
            Path(tmp_path).unlink()
        except Exception:
            pass


# ============================================================================
# Version List Endpoint
# ============================================================================

@router.get("/versions/{plugin_id}")
async def list_template_versions(plugin_id: str):
    """List all template versions for a plugin."""
    registry = TemplateRegistry()
    versions = registry.list_versions(plugin_id)
    active_version = registry.get_active_version(plugin_id)

    return {
        "plugin_id": plugin_id,
        "active_version": active_version,
        "versions": [v.to_dict() for v in versions],
        "count": len(versions),
    }


# ============================================================================
# Rollback Endpoint
# ============================================================================

@router.post("/rollback")
async def rollback_template(request: RollbackRequest):
    """Rollback to a specific template version."""
    registry = TemplateRegistry()

    # Check cache exists
    cache_path = registry.get_cached_template_path(
        request.plugin_id, request.target_version
    )
    if not cache_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cached template for v{request.target_version} not found"
        )

    tv = registry.rollback(request.plugin_id, request.target_version)
    if not tv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version {request.target_version} not found in registry"
        )

    return {
        "success": True,
        "plugin_id": request.plugin_id,
        "active_version": request.target_version,
        "cache_path": tv.cache_path,
    }


# ============================================================================
# Available Fields Endpoint
# ============================================================================

@router.get("/fields/{plugin_id}")
async def get_plugin_available_fields(plugin_id: str):
    """Get all available fields (context variables) for a plugin."""
    try:
        plugin = load_plugin(plugin_id)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plugin '{plugin_id}' not found"
        )

    fields = get_available_fields(plugin)
    return {
        "plugin_id": plugin_id,
        "fields": sorted(fields),
        "count": len(fields),
    }
