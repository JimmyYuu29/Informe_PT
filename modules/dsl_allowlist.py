# modules/dsl_allowlist.py
"""
DSL Allowlist - Controlled DSL operators for rule evaluation.
No eval/exec - only allowlisted operators are permitted.
"""
from typing import Any, Callable
import re

# Allowlisted operators from enterprise_docgen_platform.superprompt.en.md
ALLOWED_OPERATORS = frozenset([
    # Logical
    "and", "or", "not",
    # Comparison
    "equals", "not_equals", "gt", "gte", "lt", "lte",
    # Membership
    "in", "not_in",
    # Existence
    "exists", "not_exists", "is_empty", "not_empty",
    # String
    "contains", "not_contains", "starts_with", "ends_with",
])

MAX_NESTING_DEPTH = 3


def is_operator_allowed(operator: str) -> bool:
    """Check if an operator is in the allowlist."""
    return operator in ALLOWED_OPERATORS


def get_value(data: dict, field: str) -> Any:
    """
    Get a value from nested data using dot notation.
    E.g., 'servicio.enabled' -> data['servicio']['enabled']
    """
    if not field:
        return None

    parts = field.split(".")
    current = data
    for part in parts:
        if isinstance(current, dict):
            current = current.get(part)
        elif isinstance(current, list) and part.isdigit():
            idx = int(part)
            current = current[idx] if 0 <= idx < len(current) else None
        else:
            return None
        if current is None:
            return None
    return current


def evaluate_condition(condition: dict, data: dict, depth: int = 0) -> bool:
    """
    Evaluate a condition against data using the controlled DSL.

    Args:
        condition: The condition dict with 'operator', 'field', 'value', etc.
        data: The input data to evaluate against.
        depth: Current nesting depth (for enforcing max depth).

    Returns:
        bool: Result of the condition evaluation.

    Raises:
        ValueError: If operator is not allowed or max depth exceeded.
    """
    if depth > MAX_NESTING_DEPTH:
        raise ValueError(f"Max nesting depth ({MAX_NESTING_DEPTH}) exceeded")

    operator = condition.get("operator", "").lower()

    if not is_operator_allowed(operator):
        raise ValueError(f"Operator '{operator}' is not in the allowlist")

    # Logical operators (compound conditions)
    if operator == "and":
        conditions = condition.get("conditions", [])
        return all(evaluate_condition(c, data, depth + 1) for c in conditions)

    if operator == "or":
        conditions = condition.get("conditions", [])
        return any(evaluate_condition(c, data, depth + 1) for c in conditions)

    if operator == "not":
        inner = condition.get("condition", {})
        return not evaluate_condition(inner, data, depth + 1)

    # Get field value for comparison operators
    field = condition.get("field", "")
    field_value = get_value(data, field)
    expected_value = condition.get("value")

    # Comparison operators
    if operator == "equals":
        return field_value == expected_value

    if operator == "not_equals":
        return field_value != expected_value

    if operator == "gt":
        return field_value is not None and field_value > expected_value

    if operator == "gte":
        return field_value is not None and field_value >= expected_value

    if operator == "lt":
        return field_value is not None and field_value < expected_value

    if operator == "lte":
        return field_value is not None and field_value <= expected_value

    # Membership operators
    if operator == "in":
        values = condition.get("values", [])
        return field_value in values

    if operator == "not_in":
        values = condition.get("values", [])
        return field_value not in values

    # Existence operators
    if operator == "exists":
        return field_value is not None

    if operator == "not_exists":
        return field_value is None

    if operator == "is_empty":
        if field_value is None:
            return True
        if isinstance(field_value, (str, list, dict)):
            return len(field_value) == 0
        return False

    if operator == "not_empty":
        if field_value is None:
            return False
        if isinstance(field_value, (str, list, dict)):
            return len(field_value) > 0
        return True

    # String operators
    if operator == "contains":
        if not isinstance(field_value, str):
            return False
        return str(expected_value) in field_value

    if operator == "not_contains":
        if not isinstance(field_value, str):
            return True
        return str(expected_value) not in field_value

    if operator == "starts_with":
        if not isinstance(field_value, str):
            return False
        return field_value.startswith(str(expected_value))

    if operator == "ends_with":
        if not isinstance(field_value, str):
            return False
        return field_value.endswith(str(expected_value))

    raise ValueError(f"Unknown operator: {operator}")


def validate_rule_depth(condition: dict, depth: int = 0) -> int:
    """
    Calculate the maximum depth of a condition tree.

    Returns:
        int: Maximum depth found in the condition tree.
    """
    if depth > MAX_NESTING_DEPTH:
        return depth

    operator = condition.get("operator", "").lower()

    if operator in ("and", "or"):
        conditions = condition.get("conditions", [])
        if not conditions:
            return depth
        return max(validate_rule_depth(c, depth + 1) for c in conditions)

    if operator == "not":
        inner = condition.get("condition", {})
        if not inner:
            return depth
        return validate_rule_depth(inner, depth + 1)

    return depth
