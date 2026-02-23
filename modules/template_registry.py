# modules/template_registry.py
"""
Template Registry - Version management for DOCX templates.

Manages:
  - Version numbering (SemVer) per plugin_id
  - Local registry (JSON file) of all published template versions
  - Active version tracking for each plugin
  - Local template cache management
"""
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field, asdict


# ============================================================================
# Configuration defaults (overridable via environment variables)
# ============================================================================

import os

PROJECT_ROOT = Path(__file__).parent.parent

REGISTRY_PATH = Path(os.environ.get(
    "TEMPLATE_REGISTRY_PATH",
    str(PROJECT_ROOT / "data" / "template_registry.json")
))

CACHE_DIR = Path(os.environ.get(
    "TEMPLATE_CACHE_DIR",
    str(PROJECT_ROOT / "data" / "templates_cache")
))


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class TemplateVersion:
    """A single published template version."""
    plugin_id: str
    template_name: str
    version: str
    created_at: str
    author: str
    change_log: str
    sha256: str
    variables: list[str] = field(default_factory=list)
    validation_status: str = "PASS"
    validation_errors: list[str] = field(default_factory=list)
    validation_warnings: list[str] = field(default_factory=list)
    previous_version: Optional[str] = None
    sharepoint_url: Optional[str] = None
    sharepoint_metadata_url: Optional[str] = None
    sharepoint_validation_url: Optional[str] = None
    cache_path: Optional[str] = None
    is_active: bool = False

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "TemplateVersion":
        # Filter to only known fields
        known_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in known_fields}
        return cls(**filtered)


# ============================================================================
# Registry Class
# ============================================================================

class TemplateRegistry:
    """
    Manages template version registry.

    Registry is stored as a JSON file with the structure:
    {
        "plugins": {
            "<plugin_id>": {
                "active_version": "1.0.0",
                "versions": [<TemplateVersion>, ...]
            }
        },
        "updated_at": "2026-01-01T00:00:00Z"
    }
    """

    def __init__(self, registry_path: Optional[Path] = None, cache_dir: Optional[Path] = None):
        self.registry_path = registry_path or REGISTRY_PATH
        self.cache_dir = cache_dir or CACHE_DIR
        self._data: Optional[dict] = None

    def _ensure_dirs(self) -> None:
        """Ensure registry directory and cache directory exist."""
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _load(self) -> dict:
        """Load registry from disk."""
        if self._data is not None:
            return self._data

        if self.registry_path.exists():
            with open(self.registry_path, "r", encoding="utf-8") as f:
                self._data = json.load(f)
        else:
            self._data = {"plugins": {}, "updated_at": ""}

        return self._data

    def _save(self) -> None:
        """Save registry to disk."""
        self._ensure_dirs()
        data = self._load()
        data["updated_at"] = datetime.utcnow().isoformat() + "Z"

        with open(self.registry_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _get_plugin_data(self, plugin_id: str) -> dict:
        """Get or create plugin entry in registry."""
        data = self._load()
        if plugin_id not in data["plugins"]:
            data["plugins"][plugin_id] = {
                "active_version": None,
                "versions": [],
            }
        return data["plugins"][plugin_id]

    # ========================================================================
    # Version Management
    # ========================================================================

    def get_next_version(self, plugin_id: str, bump: str = "patch") -> str:
        """
        Get the next version number for a plugin.

        Args:
            plugin_id: Plugin ID.
            bump: Version bump type: "major", "minor", or "patch".

        Returns:
            Next version string (e.g., "1.0.1").
        """
        plugin_data = self._get_plugin_data(plugin_id)
        versions = plugin_data.get("versions", [])

        if not versions:
            return "1.0.0"

        # Get the latest version
        latest = versions[-1]
        latest_version = latest.get("version", "0.0.0")

        try:
            parts = latest_version.split(".")
            major = int(parts[0]) if len(parts) > 0 else 0
            minor = int(parts[1]) if len(parts) > 1 else 0
            patch = int(parts[2]) if len(parts) > 2 else 0
        except (ValueError, IndexError):
            return "1.0.0"

        if bump == "major":
            major += 1
            minor = 0
            patch = 0
        elif bump == "minor":
            minor += 1
            patch = 0
        else:  # patch
            patch += 1

        return f"{major}.{minor}.{patch}"

    def get_latest_version(self, plugin_id: str) -> Optional[str]:
        """Get the latest version string for a plugin."""
        plugin_data = self._get_plugin_data(plugin_id)
        versions = plugin_data.get("versions", [])
        if not versions:
            return None
        return versions[-1].get("version")

    def get_active_version(self, plugin_id: str) -> Optional[str]:
        """Get the active version for a plugin."""
        plugin_data = self._get_plugin_data(plugin_id)
        return plugin_data.get("active_version")

    # ========================================================================
    # Template Cache
    # ========================================================================

    def cache_template(self, plugin_id: str, version: str, template_bytes: bytes) -> Path:
        """
        Save template to local cache.

        Args:
            plugin_id: Plugin ID.
            version: Version string.
            template_bytes: Raw DOCX file bytes.

        Returns:
            Path to the cached template file.
        """
        self._ensure_dirs()
        plugin_cache_dir = self.cache_dir / plugin_id
        plugin_cache_dir.mkdir(parents=True, exist_ok=True)

        cache_file = plugin_cache_dir / f"{version}.docx"
        with open(cache_file, "wb") as f:
            f.write(template_bytes)

        return cache_file

    def get_cached_template_path(self, plugin_id: str, version: str) -> Optional[Path]:
        """Get path to a cached template, if it exists."""
        cache_file = self.cache_dir / plugin_id / f"{version}.docx"
        if cache_file.exists():
            return cache_file
        return None

    # ========================================================================
    # Publish & Record
    # ========================================================================

    def publish(
        self,
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
        template_bytes: bytes,
        sharepoint_url: Optional[str] = None,
        sharepoint_metadata_url: Optional[str] = None,
        sharepoint_validation_url: Optional[str] = None,
    ) -> TemplateVersion:
        """
        Publish a new template version.

        Saves template to cache, records in registry, and sets as active.

        Returns:
            The created TemplateVersion.
        """
        plugin_data = self._get_plugin_data(plugin_id)
        previous_version = plugin_data.get("active_version")

        # Cache the template
        cache_path = self.cache_template(plugin_id, version, template_bytes)

        # Create version record
        tv = TemplateVersion(
            plugin_id=plugin_id,
            template_name=template_name,
            version=version,
            created_at=datetime.utcnow().isoformat() + "Z",
            author=author,
            change_log=change_log,
            sha256=sha256,
            variables=variables,
            validation_status=validation_status,
            validation_errors=validation_errors,
            validation_warnings=validation_warnings,
            previous_version=previous_version,
            sharepoint_url=sharepoint_url,
            sharepoint_metadata_url=sharepoint_metadata_url,
            sharepoint_validation_url=sharepoint_validation_url,
            cache_path=str(cache_path),
            is_active=True,
        )

        # Mark previous active version as inactive
        for v in plugin_data.get("versions", []):
            v["is_active"] = False

        # Add new version
        plugin_data["versions"].append(tv.to_dict())
        plugin_data["active_version"] = version

        self._save()
        return tv

    # ========================================================================
    # Version List & Retrieval
    # ========================================================================

    def list_versions(self, plugin_id: str) -> list[TemplateVersion]:
        """List all versions for a plugin (newest first)."""
        plugin_data = self._get_plugin_data(plugin_id)
        versions = plugin_data.get("versions", [])
        result = []
        for v in reversed(versions):
            result.append(TemplateVersion.from_dict(v))
        return result

    def get_version(self, plugin_id: str, version: str) -> Optional[TemplateVersion]:
        """Get a specific version record."""
        plugin_data = self._get_plugin_data(plugin_id)
        for v in plugin_data.get("versions", []):
            if v.get("version") == version:
                return TemplateVersion.from_dict(v)
        return None

    # ========================================================================
    # Rollback
    # ========================================================================

    def rollback(self, plugin_id: str, target_version: str) -> Optional[TemplateVersion]:
        """
        Rollback to a specific version.

        Sets the target version as active in the registry.

        Args:
            plugin_id: Plugin ID.
            target_version: Version string to rollback to.

        Returns:
            The activated TemplateVersion, or None if version not found.
        """
        plugin_data = self._get_plugin_data(plugin_id)
        versions = plugin_data.get("versions", [])

        found = False
        for v in versions:
            if v.get("version") == target_version:
                v["is_active"] = True
                found = True
            else:
                v["is_active"] = False

        if not found:
            return None

        plugin_data["active_version"] = target_version
        self._save()

        return self.get_version(plugin_id, target_version)

    # ========================================================================
    # Active Template Resolution
    # ========================================================================

    def get_active_template_path(self, plugin_id: str) -> Optional[Path]:
        """
        Get the path to the active template for a plugin.

        Returns the cached template path for the active version,
        or None if no active version exists.
        """
        active_version = self.get_active_version(plugin_id)
        if not active_version:
            return None

        return self.get_cached_template_path(plugin_id, active_version)
