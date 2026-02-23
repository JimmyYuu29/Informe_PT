# modules/__init__.py
"""
Enterprise Document Generation Platform - Core Modules
"""
from .generate import generate
from .validate_plugin import validate_plugin
from .template_validator import validate_template
from .template_registry import TemplateRegistry

__all__ = ["generate", "validate_plugin", "validate_template", "TemplateRegistry"]
