"""
Tests for rule engine and DSL evaluation.
"""
import pytest
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from modules.dsl_allowlist import (
    is_operator_allowed,
    evaluate_condition,
    validate_rule_depth,
    ALLOWED_OPERATORS,
    MAX_NESTING_DEPTH,
)
from modules.rule_engine import RuleEngine
from modules.plugin_loader import load_plugin


class TestDSLAllowlist:
    """Tests for DSL allowlist functionality."""

    def test_allowed_operators(self):
        """Test that expected operators are allowed."""
        allowed = ["and", "or", "not", "equals", "not_equals", "gt", "gte", "lt", "lte",
                   "in", "not_in", "exists", "not_exists", "is_empty", "not_empty",
                   "contains", "not_contains", "starts_with", "ends_with"]

        for op in allowed:
            assert is_operator_allowed(op), f"Operator '{op}' should be allowed"

    def test_disallowed_operators(self):
        """Test that dangerous operators are not allowed."""
        disallowed = ["eval", "exec", "regex", "match", "lambda", "import"]

        for op in disallowed:
            assert not is_operator_allowed(op), f"Operator '{op}' should not be allowed"

    def test_evaluate_equals(self):
        """Test equals operator."""
        condition = {"operator": "equals", "field": "status", "value": "active"}
        data = {"status": "active"}

        assert evaluate_condition(condition, data) is True

        data = {"status": "inactive"}
        assert evaluate_condition(condition, data) is False

    def test_evaluate_not_equals(self):
        """Test not_equals operator."""
        condition = {"operator": "not_equals", "field": "status", "value": "active"}
        data = {"status": "inactive"}

        assert evaluate_condition(condition, data) is True

    def test_evaluate_gt_gte_lt_lte(self):
        """Test comparison operators."""
        data = {"value": 50}

        assert evaluate_condition({"operator": "gt", "field": "value", "value": 40}, data) is True
        assert evaluate_condition({"operator": "gt", "field": "value", "value": 50}, data) is False
        assert evaluate_condition({"operator": "gte", "field": "value", "value": 50}, data) is True
        assert evaluate_condition({"operator": "lt", "field": "value", "value": 60}, data) is True
        assert evaluate_condition({"operator": "lte", "field": "value", "value": 50}, data) is True

    def test_evaluate_in_not_in(self):
        """Test membership operators."""
        condition_in = {"operator": "in", "field": "status", "values": ["a", "b", "c"]}
        condition_not_in = {"operator": "not_in", "field": "status", "values": ["x", "y", "z"]}

        data = {"status": "b"}
        assert evaluate_condition(condition_in, data) is True
        assert evaluate_condition(condition_not_in, data) is True

    def test_evaluate_exists_not_exists(self):
        """Test existence operators."""
        condition_exists = {"operator": "exists", "field": "name"}
        condition_not_exists = {"operator": "not_exists", "field": "age"}

        data = {"name": "John"}
        assert evaluate_condition(condition_exists, data) is True
        assert evaluate_condition(condition_not_exists, data) is True

    def test_evaluate_is_empty_not_empty(self):
        """Test emptiness operators."""
        data_empty = {"list": [], "text": ""}
        data_filled = {"list": [1, 2], "text": "hello"}

        assert evaluate_condition({"operator": "is_empty", "field": "list"}, data_empty) is True
        assert evaluate_condition({"operator": "is_empty", "field": "text"}, data_empty) is True
        assert evaluate_condition({"operator": "not_empty", "field": "list"}, data_filled) is True
        assert evaluate_condition({"operator": "not_empty", "field": "text"}, data_filled) is True

    def test_evaluate_string_operators(self):
        """Test string operators."""
        data = {"text": "hello world"}

        assert evaluate_condition({"operator": "contains", "field": "text", "value": "world"}, data) is True
        assert evaluate_condition({"operator": "not_contains", "field": "text", "value": "foo"}, data) is True
        assert evaluate_condition({"operator": "starts_with", "field": "text", "value": "hello"}, data) is True
        assert evaluate_condition({"operator": "ends_with", "field": "text", "value": "world"}, data) is True

    def test_evaluate_and_operator(self):
        """Test AND operator."""
        condition = {
            "operator": "and",
            "conditions": [
                {"operator": "equals", "field": "a", "value": 1},
                {"operator": "equals", "field": "b", "value": 2},
            ]
        }

        assert evaluate_condition(condition, {"a": 1, "b": 2}) is True
        assert evaluate_condition(condition, {"a": 1, "b": 3}) is False

    def test_evaluate_or_operator(self):
        """Test OR operator."""
        condition = {
            "operator": "or",
            "conditions": [
                {"operator": "equals", "field": "a", "value": 1},
                {"operator": "equals", "field": "b", "value": 2},
            ]
        }

        assert evaluate_condition(condition, {"a": 1, "b": 3}) is True
        assert evaluate_condition(condition, {"a": 0, "b": 2}) is True
        assert evaluate_condition(condition, {"a": 0, "b": 0}) is False

    def test_evaluate_not_operator(self):
        """Test NOT operator."""
        condition = {
            "operator": "not",
            "condition": {"operator": "equals", "field": "a", "value": 1}
        }

        assert evaluate_condition(condition, {"a": 2}) is True
        assert evaluate_condition(condition, {"a": 1}) is False

    def test_nested_field_access(self):
        """Test nested field access with dot notation."""
        from modules.dsl_allowlist import get_value

        data = {"user": {"profile": {"name": "John"}}}

        assert get_value(data, "user.profile.name") == "John"
        assert get_value(data, "user.profile.age") is None

    def test_max_nesting_depth(self):
        """Test max nesting depth validation."""
        # Create deeply nested condition
        deep_condition = {
            "operator": "and",
            "conditions": [{
                "operator": "and",
                "conditions": [{
                    "operator": "and",
                    "conditions": [{
                        "operator": "and",
                        "conditions": [{
                            "operator": "equals",
                            "field": "x",
                            "value": 1
                        }]
                    }]
                }]
            }]
        }

        depth = validate_rule_depth(deep_condition)
        assert depth > MAX_NESTING_DEPTH

    def test_disallowed_operator_raises(self):
        """Test that disallowed operators raise ValueError."""
        condition = {"operator": "eval", "field": "x", "value": "code"}

        with pytest.raises(ValueError):
            evaluate_condition(condition, {"x": 1})


class TestRuleEngine:
    """Tests for rule engine functionality."""

    def test_load_pt_review_rules(self):
        """Test loading rules from pt_review plugin."""
        plugin = load_plugin("pt_review")
        engine = RuleEngine(plugin)

        assert len(engine.rules) > 0

    def test_evaluate_master_file_decision(self):
        """Test master_file decision evaluation."""
        plugin = load_plugin("pt_review")
        engine = RuleEngine(plugin)

        # Test with master_file = 0 (no access)
        data_no_access = {"master_file": 0}
        visibility, traces = engine.evaluate_all_rules(data_no_access)

        # Should show the no-access warning text
        assert "text:s1_master_file_no_access" in visibility

        # Test with master_file = 1 (has access)
        data_has_access = {"master_file": 1}
        visibility, traces = engine.evaluate_all_rules(data_has_access)

        # Should NOT show the no-access warning
        # (visibility might not have it or it's False)

    def test_get_enabled_services(self):
        """Test getting enabled services."""
        plugin = load_plugin("pt_review")
        engine = RuleEngine(plugin)

        data = {
            "servicios_oovv": [
                {"enabled": True, "titulo_servicio_oovv": "Service 1"},
                {"enabled": False, "titulo_servicio_oovv": "Service 2"},
                {"enabled": True, "titulo_servicio_oovv": "Service 3"},
            ]
        }

        enabled = engine.get_enabled_services(data)
        assert len(enabled) == 2
        assert enabled[0]["titulo_servicio_oovv"] == "Service 1"
        assert enabled[1]["titulo_servicio_oovv"] == "Service 3"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
