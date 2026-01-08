# ui/api/backend/deps.py
"""
FastAPI dependencies for the document generation API.
"""
from typing import Generator
from functools import lru_cache
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import Depends, HTTPException, status

from modules.plugin_loader import PluginPack, load_plugin, list_plugins


class PluginNotFoundError(Exception):
    """Raised when a plugin is not found."""
    def __init__(self, plugin_id: str):
        self.plugin_id = plugin_id
        super().__init__(f"Plugin '{plugin_id}' not found")


@lru_cache(maxsize=16)
def get_cached_plugin(plugin_id: str) -> PluginPack:
    """Get a cached plugin pack."""
    return load_plugin(plugin_id)


def get_plugin(plugin_id: str) -> PluginPack:
    """
    Dependency to get a plugin by ID.

    Raises HTTPException if plugin not found.
    """
    try:
        return get_cached_plugin(plugin_id)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plugin '{plugin_id}' not found",
        )


def get_available_plugins() -> list[str]:
    """Get list of available plugin IDs."""
    return list_plugins()


def validate_plugin_exists(plugin_id: str) -> bool:
    """Check if a plugin exists."""
    return plugin_id in list_plugins()


# Settings/config dependency
class Settings:
    """Application settings."""
    APP_NAME: str = "Document Generation API"
    VERSION: str = "1.1.0"
    DEBUG: bool = False
    CORS_ORIGINS: list[str] = ["*"]
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10 MB


@lru_cache
def get_settings() -> Settings:
    """Get application settings."""
    return Settings()
