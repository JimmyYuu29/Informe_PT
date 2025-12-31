# modules/rule_engine.py
"""
Rule Engine - Evaluate logic rules and determine document content.
"""
from typing import Any, Optional
from dataclasses import dataclass, field
from .plugin_loader import PluginPack
from .dsl_allowlist import evaluate_condition


@dataclass
class RuleHit:
    """Represents a rule that was evaluated and its result."""
    rule_id: str
    rule_name: str
    condition_met: bool
    action_type: str
    affected_elements: list[str] = field(default_factory=list)
    source_block_ids: list[str] = field(default_factory=list)


@dataclass
class EvaluationTrace:
    """Trace of rule evaluation for audit/debugging."""
    decision_id: str
    decision_name: str
    rule_hits: list[RuleHit] = field(default_factory=list)
    outcome: str = ""


class RuleEngine:
    """Engine for evaluating conditional logic rules."""

    def __init__(self, plugin: PluginPack):
        self.plugin = plugin
        self.rules = plugin.get_rules()
        self.decisions = plugin.decision_map.get("decisions", {})
        self.texts = plugin.get_text_blocks()
        self.tables = plugin.get_table_definitions()

    def evaluate_all_rules(self, data: dict) -> tuple[dict, list[EvaluationTrace]]:
        """
        Evaluate all rules against the input data.

        Returns:
            tuple: (visibility_map, traces)
                - visibility_map: dict mapping element keys to visibility (bool)
                - traces: list of EvaluationTrace for audit
        """
        visibility = {}
        traces = []

        # Process each decision
        for decision_id, decision in self.decisions.items():
            trace = EvaluationTrace(
                decision_id=decision_id,
                decision_name=decision.get("name", decision_id)
            )

            rule_ids = decision.get("rules", [])
            for rule_id in rule_ids:
                rule = self.rules.get(rule_id, {})
                if not rule:
                    continue

                hit = self._evaluate_rule(rule, data)
                trace.rule_hits.append(hit)

                # Update visibility based on rule action
                if hit.condition_met:
                    action = rule.get("action", {})
                    action_type = action.get("type", "")

                    if action_type == "include_text":
                        text_key = action.get("text_key", "")
                        visibility[f"text:{text_key}"] = True

                    elif action_type == "include_table":
                        table_key = action.get("table_key", "")
                        visibility[f"table:{table_key}"] = True

                    elif action_type == "include_block":
                        includes = action.get("includes", [])
                        for elem in includes:
                            visibility[f"element:{elem}"] = True

            traces.append(trace)

        # Determine visibility for conditional elements
        self._update_conditional_visibility(visibility, data)

        return visibility, traces

    def _evaluate_rule(self, rule: dict, data: dict) -> RuleHit:
        """Evaluate a single rule."""
        rule_id = rule.get("rule_id", "unknown")
        rule_name = rule.get("name", rule_id)
        condition = rule.get("condition", {})
        action = rule.get("action", {})
        source_block_ids = rule.get("source_block_ids", [])

        # Handle for_each rules
        for_each = rule.get("for_each")
        if for_each:
            # For list iteration rules, check if any item matches
            items = data.get(for_each, [])
            condition_met = False
            for item in items:
                item_data = {**data, "servicio": item, "item": item}
                try:
                    if evaluate_condition(condition, item_data):
                        condition_met = True
                        break
                except Exception:
                    continue
        else:
            try:
                condition_met = evaluate_condition(condition, data)
            except Exception:
                condition_met = False

        return RuleHit(
            rule_id=rule_id,
            rule_name=rule_name,
            condition_met=condition_met,
            action_type=action.get("type", ""),
            affected_elements=action.get("includes", []),
            source_block_ids=source_block_ids
        )

    def _update_conditional_visibility(self, visibility: dict, data: dict) -> None:
        """Update visibility for elements with conditions."""
        # Check text blocks with conditions
        for text_key, text_def in self.texts.items():
            condition_str = text_def.get("condition")
            if condition_str:
                visible = self._evaluate_simple_condition(condition_str, data)
                visibility[f"text:{text_key}"] = visible

        # Check tables with conditions
        for table_key, table_def in self.tables.items():
            condition_str = table_def.get("condition")
            if condition_str:
                visible = self._evaluate_simple_condition(condition_str, data)
                visibility[f"table:{table_key}"] = visible

    def _evaluate_simple_condition(self, condition_str: str, data: dict) -> bool:
        """Evaluate a simple string condition like 'master_file == 1'."""
        try:
            if "==" in condition_str:
                parts = condition_str.split("==")
                field = parts[0].strip()
                expected = parts[1].strip()

                # Handle nested field (e.g., "servicio.enabled")
                actual = data
                for part in field.split("."):
                    if isinstance(actual, dict):
                        actual = actual.get(part)
                    else:
                        actual = None
                        break

                # Try numeric comparison first
                try:
                    expected_val = int(expected)
                    return actual == expected_val
                except ValueError:
                    # Boolean comparison
                    if expected.lower() == "true":
                        return actual is True
                    elif expected.lower() == "false":
                        return actual is False
                    # String comparison
                    return str(actual) == expected

        except Exception:
            pass

        return True  # Default to visible if parsing fails

    def get_visible_texts(self, visibility: dict) -> list[str]:
        """Get list of visible text block keys."""
        return [
            key.replace("text:", "")
            for key, visible in visibility.items()
            if key.startswith("text:") and visible
        ]

    def get_visible_tables(self, visibility: dict) -> list[str]:
        """Get list of visible table keys."""
        return [
            key.replace("table:", "")
            for key, visible in visibility.items()
            if key.startswith("table:") and visible
        ]

    def get_enabled_services(self, data: dict) -> list[dict]:
        """Get list of enabled service blocks."""
        servicios = data.get("servicios_oovv", [])
        return [s for s in servicios if s.get("enabled", False)]
