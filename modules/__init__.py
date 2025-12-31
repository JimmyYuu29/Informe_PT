# modules/__init__.py
"""
Enterprise Document Generation Platform - Core Modules
"""
from .generate import generate
from .validate_plugin import validate_plugin

__all__ = ["generate", "validate_plugin"]
