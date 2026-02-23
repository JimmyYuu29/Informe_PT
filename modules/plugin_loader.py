# modules/plugin_loader.py
"""
Plugin Loader - Load and cache YAML plugin packs.
"""
import os
from pathlib import Path
from typing import Any, Optional
import yaml
from functools import lru_cache


# Base paths
CONFIG_BASE = Path(__file__).parent.parent / "config"
YAMLS_BASE = CONFIG_BASE / "yamls"
TEMPLATES_BASE = CONFIG_BASE / "templates"


def get_plugin_path(plugin_id: str) -> Path:
    """Get the path to a plugin's YAML directory."""
    return YAMLS_BASE / plugin_id


def get_template_path(plugin_id: str) -> Path:
    """Get the path to a plugin's template.

    Resolution order:
    1. Template registry active version (local cache)
    2. Plugin-specific templates directory (config/templates/<plugin_id>/)
    3. Legacy fallback (config/template_final.docx)
    """
    # Check template registry for active version
    try:
        from .template_registry import TemplateRegistry
        registry = TemplateRegistry()
        active_path = registry.get_active_template_path(plugin_id)
        if active_path and active_path.exists():
            return active_path
    except Exception:
        pass  # Registry not available or error - fallback to defaults

    # Check plugin-specific templates dir
    plugin_template_dir = TEMPLATES_BASE / plugin_id
    if plugin_template_dir.exists():
        template_file = plugin_template_dir / "template_final.docx"
        if template_file.exists():
            return template_file

    # Fallback to config root (legacy path for pt_review)
    legacy_path = CONFIG_BASE / "template_final.docx"
    if legacy_path.exists():
        return legacy_path

    raise FileNotFoundError(f"Template not found for plugin '{plugin_id}'")


def list_plugins() -> list[str]:
    """List all available plugin IDs."""
    if not YAMLS_BASE.exists():
        return []
    return [d.name for d in YAMLS_BASE.iterdir() if d.is_dir() and (d / "manifest.yaml").exists()]


@lru_cache(maxsize=16)
def load_yaml_file(file_path: str) -> dict:
    """Load and cache a YAML file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_plugin_file(plugin_id: str, filename: str) -> dict:
    """Load a specific YAML file from a plugin."""
    plugin_path = get_plugin_path(plugin_id)
    file_path = plugin_path / filename

    if not file_path.exists():
        raise FileNotFoundError(f"File '{filename}' not found for plugin '{plugin_id}'")

    return load_yaml_file(str(file_path))


class PluginPack:
    """Represents a loaded plugin pack with all YAML configurations."""

    def __init__(self, plugin_id: str):
        self.plugin_id = plugin_id
        self.path = get_plugin_path(plugin_id)

        if not self.path.exists():
            raise FileNotFoundError(f"Plugin '{plugin_id}' not found at {self.path}")

        # Load all YAML files
        self._manifest: Optional[dict] = None
        self._config: Optional[dict] = None
        self._fields: Optional[dict] = None
        self._texts: Optional[dict] = None
        self._tables: Optional[dict] = None
        self._logic: Optional[dict] = None
        self._decision_map: Optional[dict] = None
        self._refs: Optional[dict] = None
        self._derived: Optional[dict] = None
        self._formatting: Optional[dict] = None
        self._comentarios_valorativos: Optional[dict] = None

    def _load_if_exists(self, filename: str) -> dict:
        """Load a YAML file if it exists, return empty dict otherwise."""
        file_path = self.path / filename
        if file_path.exists():
            return load_yaml_file(str(file_path))
        return {}

    @property
    def manifest(self) -> dict:
        if self._manifest is None:
            self._manifest = self._load_if_exists("manifest.yaml")
        return self._manifest

    @property
    def config(self) -> dict:
        if self._config is None:
            self._config = self._load_if_exists("config.yaml")
        return self._config

    @property
    def fields(self) -> dict:
        if self._fields is None:
            self._fields = self._load_if_exists("fields.yaml")
        return self._fields

    @property
    def texts(self) -> dict:
        if self._texts is None:
            self._texts = self._load_if_exists("texts.yaml")
        return self._texts

    @property
    def tables(self) -> dict:
        if self._tables is None:
            self._tables = self._load_if_exists("tables.yaml")
        return self._tables

    @property
    def logic(self) -> dict:
        if self._logic is None:
            self._logic = self._load_if_exists("logic.yaml")
        return self._logic

    @property
    def decision_map(self) -> dict:
        if self._decision_map is None:
            self._decision_map = self._load_if_exists("decision_map.yaml")
        return self._decision_map

    @property
    def refs(self) -> dict:
        if self._refs is None:
            self._refs = self._load_if_exists("refs.yaml")
        return self._refs

    @property
    def derived(self) -> dict:
        if self._derived is None:
            self._derived = self._load_if_exists("derived.yaml")
        return self._derived

    @property
    def formatting(self) -> dict:
        if self._formatting is None:
            self._formatting = self._load_if_exists("formatting.yaml")
        return self._formatting

    @property
    def comentarios_valorativos(self) -> dict:
        if self._comentarios_valorativos is None:
            self._comentarios_valorativos = self._load_if_exists("comentarios_valorativos.yaml")
        return self._comentarios_valorativos

    def get_field_definitions(self) -> dict:
        """Get all field definitions."""
        return self.fields.get("fields", {})

    def get_text_blocks(self) -> dict:
        """Get all text blocks."""
        return self.texts.get("texts", {})

    def get_table_definitions(self) -> dict:
        """Get all table definitions."""
        return self.tables.get("tables", {})

    def get_rules(self) -> dict:
        """Get all logic rules."""
        return self.logic.get("rules", {})

    def get_derived_fields(self) -> dict:
        """Get all derived field definitions."""
        return self.derived.get("derived_fields", {})

    def get_comentarios_valorativos(self) -> dict:
        """Get all comentarios valorativos definitions."""
        return self.comentarios_valorativos.get("comentarios_valorativos", {})

    def get_template_path(self) -> Path:
        """Get the path to this plugin's template."""
        return get_template_path(self.plugin_id)

    def get_ui_sections(self) -> list:
        """Get UI section configuration."""
        return self.config.get("ui", {}).get("sections", [])

    def get_sensitive_fields(self) -> list:
        """Get list of sensitive field names."""
        return self.manifest.get("sensitive_fields", [])


def load_plugin(plugin_id: str) -> PluginPack:
    """Load a complete plugin pack."""
    return PluginPack(plugin_id)
