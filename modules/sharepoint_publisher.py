# modules/sharepoint_publisher.py
"""
SharePoint Publisher - Publish templates to SharePoint via Power Automate.

This module handles template publication by sending files to a Power Automate
HTTP trigger, which in turn saves them to SharePoint. No direct SharePoint
API access or App Registration is required.

Environment Variables:
  - POWER_AUTOMATE_TEMPLATE_PUBLISH_URL: The HTTP trigger URL for the PA flow (required)
  - SHAREPOINT_TARGET_ROOT: Base folder in SharePoint (default: /Templates/Released/)
"""
import base64
import json
import os
import logging
from dataclasses import dataclass
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


# ============================================================================
# Configuration
# ============================================================================

POWER_AUTOMATE_URL = os.environ.get("POWER_AUTOMATE_TEMPLATE_PUBLISH_URL", "")
SHAREPOINT_TARGET_ROOT = os.environ.get("SHAREPOINT_TARGET_ROOT", "/Templates/Released/")

# Timeout for Power Automate calls (seconds)
PA_TIMEOUT = int(os.environ.get("PA_PUBLISH_TIMEOUT", "120"))


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class PublishRequest:
    """Request payload for Power Automate template publish."""
    plugin_id: str
    template_name: str
    version: str
    target_folder: str
    files: list[dict]  # [{"filename": ..., "content_base64": ..., "content_type": ...}]

    def to_dict(self) -> dict:
        return {
            "plugin_id": self.plugin_id,
            "template_name": self.template_name,
            "version": self.version,
            "target_folder": self.target_folder,
            "files": self.files,
        }


@dataclass
class PublishResponse:
    """Response from Power Automate after publishing."""
    ok: bool
    sharepoint_folder: Optional[str] = None
    template_file_url: Optional[str] = None
    metadata_file_url: Optional[str] = None
    validation_file_url: Optional[str] = None
    item_ids: Optional[dict] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    error_details: Optional[str] = None

    def to_dict(self) -> dict:
        if self.ok:
            return {
                "ok": True,
                "sharepoint": {
                    "folder": self.sharepoint_folder,
                    "template_file_url": self.template_file_url,
                    "metadata_file_url": self.metadata_file_url,
                    "validation_file_url": self.validation_file_url,
                    "item_ids": self.item_ids or {},
                },
            }
        return {
            "ok": False,
            "error": {
                "code": self.error_code or "UNKNOWN",
                "message": self.error_message or "Unknown error",
                "details": self.error_details or "",
            },
        }


# ============================================================================
# Publisher Functions
# ============================================================================

def _encode_file(content: bytes, filename: str, content_type: str) -> dict:
    """Encode a file for the Power Automate request."""
    return {
        "filename": filename,
        "content_base64": base64.b64encode(content).decode("utf-8"),
        "content_type": content_type,
    }


def publish_to_sharepoint(
    plugin_id: str,
    template_name: str,
    version: str,
    template_bytes: bytes,
    metadata_json: dict,
    validation_report_json: dict,
    pa_url: Optional[str] = None,
    target_root: Optional[str] = None,
) -> PublishResponse:
    """
    Publish a template to SharePoint via Power Automate.

    Args:
        plugin_id: Plugin ID.
        template_name: Template filename (without version suffix).
        version: Version string (e.g., "1.2.0").
        template_bytes: Raw DOCX file bytes.
        metadata_json: Metadata dictionary.
        validation_report_json: Validation report dictionary.
        pa_url: Override Power Automate URL (default: env var).
        target_root: Override SharePoint target root (default: env var).

    Returns:
        PublishResponse with SharePoint URLs or error details.

    Raises:
        ValueError: If Power Automate URL is not configured.
    """
    url = pa_url or POWER_AUTOMATE_URL
    root = target_root or SHAREPOINT_TARGET_ROOT

    if not url:
        raise ValueError(
            "Power Automate URL not configured. "
            "Set POWER_AUTOMATE_TEMPLATE_PUBLISH_URL environment variable."
        )

    # Build target folder
    target_folder = f"{root.rstrip('/')}/{plugin_id}/"

    # Build file list
    files = [
        _encode_file(
            template_bytes,
            f"{template_name}__{version}.docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ),
        _encode_file(
            json.dumps(metadata_json, indent=2, ensure_ascii=False).encode("utf-8"),
            f"metadata__{version}.json",
            "application/json",
        ),
        _encode_file(
            json.dumps(validation_report_json, indent=2, ensure_ascii=False).encode("utf-8"),
            f"validation_report__{version}.json",
            "application/json",
        ),
    ]

    # Build request
    request = PublishRequest(
        plugin_id=plugin_id,
        template_name=template_name,
        version=version,
        target_folder=target_folder,
        files=files,
    )

    # Send to Power Automate
    try:
        logger.info(
            f"Publishing template to SharePoint via Power Automate: "
            f"plugin={plugin_id}, version={version}, target={target_folder}"
        )

        response = httpx.post(
            url,
            json=request.to_dict(),
            timeout=PA_TIMEOUT,
            headers={"Content-Type": "application/json"},
        )

        # Check HTTP status
        if response.status_code not in (200, 202):
            logger.error(
                f"Power Automate returned HTTP {response.status_code}: {response.text}"
            )
            return PublishResponse(
                ok=False,
                error_code=f"HTTP_{response.status_code}",
                error_message=f"Power Automate returned HTTP {response.status_code}",
                error_details=response.text[:500],
            )

        # Parse response
        resp_data = response.json()

        if resp_data.get("ok"):
            sp = resp_data.get("sharepoint", {})
            logger.info(f"Template published successfully: {sp}")
            return PublishResponse(
                ok=True,
                sharepoint_folder=sp.get("folder"),
                template_file_url=sp.get("template_file_url"),
                metadata_file_url=sp.get("metadata_file_url"),
                validation_file_url=sp.get("validation_file_url"),
                item_ids=sp.get("item_ids"),
            )
        else:
            error = resp_data.get("error", {})
            logger.error(f"Power Automate returned error: {error}")
            return PublishResponse(
                ok=False,
                error_code=error.get("code", "PA_ERROR"),
                error_message=error.get("message", "Power Automate returned an error"),
                error_details=error.get("details", ""),
            )

    except httpx.TimeoutException:
        logger.error(f"Power Automate request timed out after {PA_TIMEOUT}s")
        return PublishResponse(
            ok=False,
            error_code="TIMEOUT",
            error_message=f"Power Automate request timed out after {PA_TIMEOUT} seconds",
            error_details="The Power Automate flow may still be processing. Check SharePoint manually.",
        )

    except httpx.ConnectError as e:
        logger.error(f"Cannot connect to Power Automate: {e}")
        return PublishResponse(
            ok=False,
            error_code="CONNECTION_ERROR",
            error_message="Cannot connect to Power Automate endpoint",
            error_details=str(e),
        )

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON response from Power Automate: {e}")
        return PublishResponse(
            ok=False,
            error_code="INVALID_RESPONSE",
            error_message="Power Automate returned invalid JSON",
            error_details=str(e),
        )

    except Exception as e:
        logger.error(f"Unexpected error publishing to SharePoint: {e}")
        return PublishResponse(
            ok=False,
            error_code="INTERNAL_ERROR",
            error_message=f"Unexpected error: {type(e).__name__}",
            error_details=str(e),
        )


def build_metadata(
    plugin_id: str,
    template_name: str,
    version: str,
    author: str,
    change_log: str,
    sha256: str,
    variables: list[str],
    validation_status: str,
    validation_errors: list[str],
    validation_warnings: list[str],
    previous_version: Optional[str] = None,
) -> dict:
    """
    Build metadata dictionary for a template version.

    This is the metadata stored alongside the template in SharePoint
    and in the local registry.
    """
    from datetime import datetime

    return {
        "plugin_id": plugin_id,
        "template_name": template_name,
        "version": version,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "author": author,
        "change_log": change_log,
        "sha256": sha256,
        "variables": variables,
        "validation": {
            "status": validation_status,
            "errors": validation_errors,
            "warnings": validation_warnings,
        },
        "previous_version": previous_version,
    }
