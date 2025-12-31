# modules/validate_plugin.py
"""
Plugin Validator - Validates plugin pack integrity for CI/deployment.
"""
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

from .plugin_loader import PluginPack, load_plugin, get_plugin_path
from .dsl_allowlist import ALLOWED_OPERATORS, validate_rule_depth, MAX_NESTING_DEPTH


@dataclass
class PluginValidationResult:
    """Result of plugin validation."""
    plugin_id: str
    is_valid: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    info: list[str] = field(default_factory=list)

    def add_error(self, message: str) -> None:
        self.errors.append(message)
        self.is_valid = False

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)

    def add_info(self, message: str) -> None:
        self.info.append(message)

    def to_dict(self) -> dict:
        return {
            "plugin_id": self.plugin_id,
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "info": self.info,
        }


def validate_required_files(plugin_id: str) -> PluginValidationResult:
    """Validate that all required files exist."""
    result = PluginValidationResult(plugin_id=plugin_id)
    plugin_path = get_plugin_path(plugin_id)

    required_files = [
        "manifest.yaml",
        "config.yaml",
        "fields.yaml",
        "texts.yaml",
        "tables.yaml",
        "logic.yaml",
        "decision_map.yaml",
        "refs.yaml",
        "derived.yaml",
        "formatting.yaml",
    ]

    for filename in required_files:
        file_path = plugin_path / filename
        if not file_path.exists():
            result.add_error(f"Required file missing: {filename}")
        else:
            result.add_info(f"Found: {filename}")

    return result


def validate_field_references(plugin: PluginPack) -> PluginValidationResult:
    """Validate that all field references in tables/texts resolve."""
    result = PluginValidationResult(plugin_id=plugin.plugin_id)
    fields_def = plugin.get_field_definitions()
    derived_def = plugin.get_derived_fields()
    all_fields = set(fields_def.keys()) | set(derived_def.keys())

    # Check table field references
    tables = plugin.get_table_definitions()
    for table_id, table_def in tables.items():
        # Check rows
        for row in table_def.get("rows", []):
            fields_list = row.get("fields", [])
            for field_name in fields_list:
                if field_name and field_name not in all_fields:
                    result.add_warning(
                        f"Table '{table_id}' references unknown field: {field_name}"
                    )

        # Check columns
        for col in table_def.get("columns", []):
            field_name = col.get("field")
            if field_name and field_name not in all_fields:
                result.add_warning(
                    f"Table '{table_id}' column references unknown field: {field_name}"
                )

    # Check derived field dependencies
    for derived_id, derived_def_item in derived_def.items():
        deps = derived_def_item.get("dependencies", [])
        for dep in deps:
            if dep not in all_fields:
                result.add_warning(
                    f"Derived field '{derived_id}' depends on unknown field: {dep}"
                )

    return result


def validate_rule_operators(plugin: PluginPack) -> PluginValidationResult:
    """Validate that all rule operators are allowlisted."""
    result = PluginValidationResult(plugin_id=plugin.plugin_id)
    rules = plugin.get_rules()

    def check_condition_operators(condition: dict, rule_id: str, depth: int = 0) -> None:
        if depth > MAX_NESTING_DEPTH:
            result.add_error(
                f"Rule '{rule_id}' exceeds max nesting depth ({MAX_NESTING_DEPTH})"
            )
            return

        operator = condition.get("operator", "")
        if operator and operator.lower() not in ALLOWED_OPERATORS:
            result.add_error(
                f"Rule '{rule_id}' uses disallowed operator: {operator}"
            )

        # Check nested conditions
        for nested in condition.get("conditions", []):
            check_condition_operators(nested, rule_id, depth + 1)

        inner = condition.get("condition")
        if inner:
            check_condition_operators(inner, rule_id, depth + 1)

    for rule_id, rule in rules.items():
        condition = rule.get("condition", {})
        if condition:
            check_condition_operators(condition, rule_id)
            # Also validate depth
            depth = validate_rule_depth(condition)
            if depth > MAX_NESTING_DEPTH:
                result.add_error(
                    f"Rule '{rule_id}' has nesting depth {depth} (max {MAX_NESTING_DEPTH})"
                )

    if not result.errors:
        result.add_info(f"All {len(rules)} rules use only allowlisted operators")

    return result


def validate_text_source_blocks(plugin: PluginPack) -> PluginValidationResult:
    """Validate that text blocks have source_block_ids."""
    result = PluginValidationResult(plugin_id=plugin.plugin_id)
    texts = plugin.get_text_blocks()

    for text_key, text_def in texts.items():
        source_ids = text_def.get("source_block_ids", [])
        if not source_ids:
            result.add_warning(
                f"Text block '{text_key}' has no source_block_ids (traceability gap)"
            )

    return result


def validate_decision_map_coverage(plugin: PluginPack) -> PluginValidationResult:
    """Validate that all rules are covered by decisions."""
    result = PluginValidationResult(plugin_id=plugin.plugin_id)
    rules = plugin.get_rules()
    decisions = plugin.decision_map.get("decisions", {})

    # Collect all rules referenced by decisions
    covered_rules = set()
    for decision_id, decision in decisions.items():
        for rule_id in decision.get("rules", []):
            covered_rules.add(rule_id)

    # Check for uncovered rules
    for rule_id in rules.keys():
        if rule_id not in covered_rules:
            result.add_warning(
                f"Rule '{rule_id}' is not referenced by any decision"
            )

    if not result.warnings:
        result.add_info(f"All {len(rules)} rules are covered by decisions")

    return result


def validate_template_exists(plugin: PluginPack) -> PluginValidationResult:
    """Validate that the template file exists."""
    result = PluginValidationResult(plugin_id=plugin.plugin_id)

    try:
        template_path = plugin.get_template_path()
        if template_path.exists():
            result.add_info(f"Template found: {template_path.name}")
        else:
            result.add_error(f"Template not found: {template_path}")
    except FileNotFoundError as e:
        result.add_error(str(e))

    return result


def validate_plugin(plugin_id: str) -> PluginValidationResult:
    """
    Complete validation of a plugin pack.

    This is the main entry point for CI/deployment validation.

    Args:
        plugin_id: The ID of the plugin to validate.

    Returns:
        PluginValidationResult with all validation results.
    """
    result = PluginValidationResult(plugin_id=plugin_id)

    # Step 1: Check required files
    files_result = validate_required_files(plugin_id)
    result.errors.extend(files_result.errors)
    result.warnings.extend(files_result.warnings)
    result.info.extend(files_result.info)

    if files_result.errors:
        result.is_valid = False
        return result

    # Load plugin for further validation
    try:
        plugin = load_plugin(plugin_id)
    except Exception as e:
        result.add_error(f"Failed to load plugin: {e}")
        return result

    # Step 2: Validate template exists
    template_result = validate_template_exists(plugin)
    result.errors.extend(template_result.errors)
    result.warnings.extend(template_result.warnings)
    result.info.extend(template_result.info)

    # Step 3: Validate field references
    refs_result = validate_field_references(plugin)
    result.errors.extend(refs_result.errors)
    result.warnings.extend(refs_result.warnings)

    # Step 4: Validate rule operators
    ops_result = validate_rule_operators(plugin)
    result.errors.extend(ops_result.errors)
    result.warnings.extend(ops_result.warnings)
    result.info.extend(ops_result.info)

    # Step 5: Validate text source blocks
    texts_result = validate_text_source_blocks(plugin)
    result.warnings.extend(texts_result.warnings)

    # Step 6: Validate decision map coverage
    decisions_result = validate_decision_map_coverage(plugin)
    result.warnings.extend(decisions_result.warnings)
    result.info.extend(decisions_result.info)

    # Final status
    result.is_valid = len(result.errors) == 0

    return result


def validate_all_plugins() -> dict[str, PluginValidationResult]:
    """Validate all available plugins."""
    from .plugin_loader import list_plugins

    results = {}
    for plugin_id in list_plugins():
        results[plugin_id] = validate_plugin(plugin_id)

    return results
