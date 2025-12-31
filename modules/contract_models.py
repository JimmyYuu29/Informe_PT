# modules/contract_models.py
"""
Contract Models - Dynamic Pydantic model generation from fields.yaml
"""
from datetime import date
from decimal import Decimal
from typing import Any, Optional, Type
from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator
import re


def create_field_type(field_def: dict) -> tuple[type, Any]:
    """
    Convert a YAML field definition to a Python type annotation and default.

    Returns:
        tuple: (type_annotation, default_value)
    """
    field_type = field_def.get("type", "text")
    required = field_def.get("required", False)
    default = field_def.get("default")

    # Base type mapping
    type_mapping = {
        "text": str,
        "date": date,
        "int": int,
        "decimal": Decimal,
        "currency": Decimal,
        "percentage": Decimal,
        "bool": bool,
    }

    # Handle enum type
    if field_type == "enum":
        # Enums are stored as strings
        base_type = str
    # Handle list type
    elif field_type == "list":
        item_type = field_def.get("item_type", "text")
        if item_type == "text":
            base_type = list[str]
        else:
            # Complex list with item_schema
            base_type = list[dict]
    else:
        base_type = type_mapping.get(field_type, str)

    # Make optional if not required
    if not required:
        if default is not None:
            return (Optional[base_type], default)
        return (Optional[base_type], None)

    return (base_type, ...)


def build_pydantic_model(
    model_name: str,
    fields_def: dict,
    include_derived: bool = False,
    derived_def: Optional[dict] = None
) -> Type[BaseModel]:
    """
    Dynamically build a Pydantic model from field definitions.

    Args:
        model_name: Name for the generated model class.
        fields_def: Dictionary of field definitions from fields.yaml.
        include_derived: Whether to include derived fields in the model.
        derived_def: Dictionary of derived field definitions.

    Returns:
        A dynamically generated Pydantic model class.
    """
    field_annotations: dict[str, Any] = {}
    field_defaults: dict[str, Any] = {}

    for field_name, field_def in fields_def.items():
        type_hint, default = create_field_type(field_def)
        field_annotations[field_name] = type_hint
        if default is not ...:
            field_defaults[field_name] = default

    # Add derived fields if requested
    if include_derived and derived_def:
        for derived_name, derived_info in derived_def.items():
            derived_type = derived_info.get("type", "decimal")
            if derived_type in ("int", "integer"):
                type_hint = int
            elif derived_type in ("decimal", "currency", "percentage"):
                type_hint = Decimal
            else:
                type_hint = str
            # Derived fields are always optional (computed)
            field_annotations[derived_name] = Optional[type_hint]
            field_defaults[derived_name] = None

    # Create the model class dynamically
    namespace = {"__annotations__": field_annotations}
    namespace.update(field_defaults)

    model = type(model_name, (BaseModel,), namespace)
    return model


class BasePluginInput(BaseModel):
    """Base class for plugin input models with common validation."""

    model_config = {"extra": "allow", "str_strip_whitespace": True}

    @model_validator(mode="before")
    @classmethod
    def coerce_empty_strings(cls, values: dict) -> dict:
        """Convert empty strings to None for optional fields."""
        if not isinstance(values, dict):
            return values
        return {
            k: (None if v == "" else v)
            for k, v in values.items()
        }


def validate_field_value(field_name: str, value: Any, field_def: dict) -> list[str]:
    """
    Validate a single field value against its definition.

    Returns:
        List of validation error messages (empty if valid).
    """
    errors = []
    field_type = field_def.get("type", "text")
    required = field_def.get("required", False)
    validation = field_def.get("validation", {})
    label = field_def.get("label", field_name)

    # Check required
    if required and (value is None or value == ""):
        errors.append(f"Field '{label}' is required")
        return errors

    if value is None:
        return errors

    # Type-specific validation
    if field_type == "text":
        if not isinstance(value, str):
            errors.append(f"Field '{label}' must be a string")
        else:
            # Strip whitespace for length validation
            stripped_value = value.strip()
            min_len = validation.get("min_length", 0)
            max_len = validation.get("max_length")
            if len(stripped_value) < min_len:
                errors.append(f"Field '{label}' must be at least {min_len} characters (current: {len(stripped_value)})")
            if max_len and len(stripped_value) > max_len:
                errors.append(f"Field '{label}' must be at most {max_len} characters (current: {len(stripped_value)})")

    elif field_type == "date":
        if not isinstance(value, (date, str)):
            errors.append(f"Field '{label}' must be a date")

    elif field_type == "enum":
        allowed_values = field_def.get("values", [])
        # Handle both simple list and list of dicts
        if allowed_values and isinstance(allowed_values[0], dict):
            allowed = [v.get("value") for v in allowed_values]
        else:
            allowed = allowed_values
        if value not in allowed:
            errors.append(f"Field '{label}' must be one of: {allowed}")

    elif field_type in ("currency", "decimal", "int"):
        try:
            float(value)
        except (TypeError, ValueError):
            errors.append(f"Field '{label}' must be a number")

    elif field_type == "list":
        if not isinstance(value, list):
            errors.append(f"Field '{label}' must be a list")
        else:
            min_items = field_def.get("min_items", 0)
            if len(value) < min_items:
                errors.append(f"Field '{label}' must have at least {min_items} items")

    # Format validation
    fmt = field_def.get("format")
    if fmt == "email" and value:
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, str(value)):
            errors.append(f"Field '{label}' must be a valid email address")

    return errors


def validate_input_data(data: dict, fields_def: dict, context: Optional[dict] = None) -> list[str]:
    """
    Validate input data against field definitions.

    Args:
        data: Input data dictionary.
        fields_def: Field definitions from fields.yaml.
        context: Optional context for conditional validation.

    Returns:
        List of validation error messages.
    """
    all_errors = []

    for field_name, field_def in fields_def.items():
        # Check field condition
        condition = field_def.get("condition")
        if condition and context:
            # Simple condition evaluation (e.g., "master_file == 1")
            try:
                if "==" in condition:
                    parts = condition.split("==")
                    cond_field = parts[0].strip()
                    cond_value = parts[1].strip()
                    actual_value = str(context.get(cond_field, ""))
                    if actual_value != cond_value:
                        continue  # Skip validation if condition not met
            except Exception:
                pass

        value = data.get(field_name)
        errors = validate_field_value(field_name, value, field_def)
        all_errors.extend(errors)

    return all_errors
