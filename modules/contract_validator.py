# modules/contract_validator.py
"""
Contract Validator - Validates input data against plugin contracts.
"""
from typing import Any, Optional
from .plugin_loader import PluginPack
from .contract_models import validate_input_data, validate_field_value
from .dsl_allowlist import evaluate_condition


class ValidationResult:
    """Result of a validation operation."""

    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.info: list[str] = []

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def add_error(self, message: str) -> None:
        self.errors.append(message)

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)

    def add_info(self, message: str) -> None:
        self.info.append(message)

    def merge(self, other: "ValidationResult") -> None:
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        self.info.extend(other.info)

    def to_dict(self) -> dict:
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "info": self.info,
        }


def validate_required_fields(
    data: dict,
    fields_def: dict,
    context: Optional[dict] = None
) -> ValidationResult:
    """Validate that all required fields are present and valid."""
    result = ValidationResult()

    for field_name, field_def in fields_def.items():
        # Check conditional requirement
        condition_str = field_def.get("condition")
        if condition_str and context:
            # Simple condition parsing
            if not _evaluate_simple_condition(condition_str, context):
                continue

        value = data.get(field_name)
        errors = validate_field_value(field_name, value, field_def)
        for error in errors:
            result.add_error(error)

    return result


def _evaluate_simple_condition(condition_str: str, context: dict) -> bool:
    """Evaluate a simple condition string like 'master_file == 1'."""
    try:
        if "==" in condition_str:
            parts = condition_str.split("==")
            field = parts[0].strip()
            expected = parts[1].strip()
            actual = context.get(field)
            # Handle numeric comparison
            try:
                expected_val = int(expected)
                return actual == expected_val
            except ValueError:
                return str(actual) == expected
    except Exception:
        pass
    return True  # Default to true if parsing fails


def validate_conditional_rules(
    data: dict,
    rules: dict,
    fields_def: dict
) -> ValidationResult:
    """Validate conditional rules from logic.yaml."""
    result = ValidationResult()

    for rule_id, rule in rules.items():
        condition = rule.get("condition")
        if not condition:
            continue

        action = rule.get("action", {})
        action_type = action.get("type")

        # Handle require_field and require_fields actions
        if action_type in ("require_field", "require_fields"):
            try:
                condition_met = evaluate_condition(condition, data)
            except Exception as e:
                result.add_warning(f"Rule {rule_id}: Could not evaluate condition - {e}")
                continue

            if condition_met:
                # Check if required fields are present
                if action_type == "require_field":
                    field_to_check = action.get("field", "")
                    validation_rule = action.get("validation", "not_empty")
                    value = data.get(field_to_check)
                    if validation_rule == "not_empty" and (value is None or value == ""):
                        field_def = fields_def.get(field_to_check, {})
                        label = field_def.get("label", field_to_check)
                        result.add_error(f"Field '{label}' is required by rule {rule_id}")

                elif action_type == "require_fields":
                    fields_to_check = action.get("fields", [])
                    for field_name in fields_to_check:
                        value = data.get(field_name)
                        if value is None or value == "":
                            field_def = fields_def.get(field_name, {})
                            label = field_def.get("label", field_name)
                            result.add_error(f"Field '{label}' is required by rule {rule_id}")

    return result


def validate_compliance_comments(
    data: dict,
    fields_def: dict
) -> ValidationResult:
    """
    Validate that compliance fields with 'no' or 'parcial' have comments.
    This implements the COND_005 rule from the YAML pack.
    """
    result = ValidationResult()

    # Local File compliance (14 rows)
    for i in range(1, 15):
        cumplido_field = f"cumplido_local_{i}"
        texto_field = f"texto_cumplido_local_{i}"

        cumplido_value = data.get(cumplido_field)
        texto_value = data.get(texto_field)

        if cumplido_value in ("no", "parcial"):
            if not texto_value:
                field_def = fields_def.get(cumplido_field, {})
                label = field_def.get("label", cumplido_field)
                result.add_error(
                    f"Comment required for '{label}' when compliance is '{cumplido_value}'"
                )

    # Master File compliance (17 rows) - only if master_file == 1
    if data.get("master_file") == 1:
        for i in range(1, 18):
            cumplido_field = f"cumplido_mast_{i}"
            texto_field = f"texto_cumplido_mast_{i}"

            cumplido_value = data.get(cumplido_field)
            texto_value = data.get(texto_field)

            if cumplido_value in ("no", "parcial"):
                if not texto_value:
                    field_def = fields_def.get(cumplido_field, {})
                    label = field_def.get("label", cumplido_field)
                    result.add_error(
                        f"Comment required for '{label}' when compliance is '{cumplido_value}'"
                    )

    return result


def validate_input(plugin: PluginPack, data: dict) -> ValidationResult:
    """
    Full validation of input data against a plugin's contract.

    Args:
        plugin: The loaded plugin pack.
        data: Input data dictionary.

    Returns:
        ValidationResult with all errors, warnings, and info.
    """
    result = ValidationResult()
    fields_def = plugin.get_field_definitions()
    rules = plugin.get_rules()

    # Step 1: Validate required fields
    required_result = validate_required_fields(data, fields_def, context=data)
    result.merge(required_result)

    # Step 2: Validate conditional rules
    rules_result = validate_conditional_rules(data, rules, fields_def)
    result.merge(rules_result)

    # Step 3: Validate compliance comments
    compliance_result = validate_compliance_comments(data, fields_def)
    result.merge(compliance_result)

    return result
