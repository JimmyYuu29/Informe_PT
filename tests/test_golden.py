"""
Golden regression tests for document generation.

These tests verify that the system produces consistent, expected results
for a known set of inputs.
"""
import json
import pytest
import sys
from pathlib import Path
from datetime import date
from decimal import Decimal

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from modules.plugin_loader import load_plugin
from modules.generate import generate, GenerationOptions
from modules.contract_validator import validate_input
from modules.context_builder import calculate_derived_fields


# Path to golden test files
GOLDEN_DIR = Path(__file__).parent / "golden"


def load_golden_input() -> dict:
    """Load the golden test input."""
    input_file = GOLDEN_DIR / "sample_input.json"
    with open(input_file, "r", encoding="utf-8") as f:
        return json.load(f)


def load_golden_expected() -> dict:
    """Load the expected output metadata."""
    expected_file = GOLDEN_DIR / "expected_output.json"
    with open(expected_file, "r", encoding="utf-8") as f:
        return json.load(f)


class TestGoldenGeneration:
    """Golden tests for document generation."""

    @pytest.fixture
    def plugin(self):
        """Load the pt_review plugin."""
        return load_plugin("pt_review")

    @pytest.fixture
    def golden_input(self):
        """Load golden test input."""
        return load_golden_input()

    @pytest.fixture
    def golden_expected(self):
        """Load golden expected output."""
        return load_golden_expected()

    def test_golden_input_validates(self, plugin, golden_input, golden_expected):
        """Test that golden input passes validation."""
        result = validate_input(plugin, golden_input)

        expected_valid = golden_expected["expected_validation"]["is_valid"]
        max_errors = golden_expected["expected_validation"]["max_errors"]

        if expected_valid:
            assert result.is_valid or len(result.errors) <= max_errors, \
                f"Validation failed with errors: {result.errors}"
        else:
            assert not result.is_valid

    def test_golden_derived_fields(self, plugin, golden_input, golden_expected):
        """Test that derived fields calculate correctly."""
        derived_defs = plugin.get_derived_fields()
        derived = calculate_derived_fields(golden_input, derived_defs)

        expected_derived = golden_expected.get("expected_derived_values", {})

        for field_name, expected_value in expected_derived.items():
            if field_name in derived:
                actual = derived[field_name]
                # Handle Decimal conversion
                if isinstance(actual, Decimal):
                    actual = float(actual)
                assert actual == expected_value, \
                    f"Derived field '{field_name}' mismatch: {actual} != {expected_value}"

    def test_golden_generation_succeeds(self, golden_input, golden_expected):
        """Test that generation succeeds with golden input."""
        plugin_id = golden_expected["plugin_id"]

        options = GenerationOptions(
            validate=True,
            strict_validation=False,
            apply_cell_colors=True,
            save_trace=True,
        )

        result = generate(plugin_id, golden_input, options)

        expected_success = golden_expected["expected_generation"]["success"]
        assert result.success == expected_success, \
            f"Generation failed: {result.error}"

        if result.success:
            # Check output file exists
            assert result.output_path is not None
            assert result.output_path.exists()

            # Check file extension
            expected_ext = golden_expected["expected_generation"]["output_extension"]
            assert result.output_path.suffix == expected_ext

            # Check trace was created
            assert result.trace_id is not None

    def test_golden_master_file_decision(self, plugin, golden_input):
        """Test master file decision is evaluated correctly."""
        from modules.rule_engine import RuleEngine

        engine = RuleEngine(plugin)
        visibility, traces = engine.evaluate_all_rules(golden_input)

        # With master_file == 0, should show no-access warning
        master_file_value = golden_input.get("master_file")

        if master_file_value == 0:
            # Should include the no-access text
            assert visibility.get("text:s1_master_file_no_access", False), \
                "Expected no-access warning to be visible when master_file == 0"
        else:
            # Should not include the no-access text
            assert not visibility.get("text:s1_master_file_no_access", False), \
                "Expected no-access warning to be hidden when master_file == 1"

    def test_golden_input_schema_compliance(self, plugin, golden_input):
        """Test that golden input matches the plugin schema."""
        fields_def = plugin.get_field_definitions()

        # Check that required fields are present
        for field_name, field_def in fields_def.items():
            if field_def.get("required", False):
                # Check condition
                condition = field_def.get("condition")
                if condition:
                    # Skip conditional fields (they may not be required based on condition)
                    continue

                assert field_name in golden_input or field_name.startswith("cumplido_mast_"), \
                    f"Required field '{field_name}' missing from golden input"


class TestGoldenInputIntegrity:
    """Tests to verify golden input file integrity."""

    def test_golden_input_is_valid_json(self):
        """Test that golden input is valid JSON."""
        input_file = GOLDEN_DIR / "sample_input.json"
        assert input_file.exists(), "Golden input file not found"

        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert isinstance(data, dict)

    def test_golden_expected_is_valid_json(self):
        """Test that expected output is valid JSON."""
        expected_file = GOLDEN_DIR / "expected_output.json"
        assert expected_file.exists(), "Golden expected file not found"

        with open(expected_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert isinstance(data, dict)
        assert "plugin_id" in data
        assert "expected_validation" in data
        assert "expected_generation" in data

    def test_golden_input_has_expected_fields(self):
        """Test that golden input has expected structure."""
        data = load_golden_input()

        # Core fields
        assert "fecha_fin_fiscal" in data
        assert "entidad_cliente" in data
        assert "master_file" in data

        # Financial fields
        assert "cifra_1" in data
        assert "ebit_1" in data

        # Contact fields
        assert "contacto1" in data
        assert "correo_contacto1" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
