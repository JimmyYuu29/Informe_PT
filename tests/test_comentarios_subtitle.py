#!/usr/bin/env python3
"""
Test that the "Comentarios valorativos" subtitle is hidden when no comentarios are selected.
"""

import json
import sys
import zipfile
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from modules.generate import generate, GenerationOptions


def test_subtitle_hidden_when_no_comentarios():
    """
    Test that the "Comentarios valorativos" subtitle is NOT present
    when no comentario_valorativo is set to "si".
    """
    # Use sample input that has no comentario_valorativo fields (all default to "no")
    sample_input_path = PROJECT_ROOT / "tests" / "golden" / "sample_input.json"

    with open(sample_input_path, "r", encoding="utf-8") as f:
        input_data = json.load(f)

    # Ensure no comentarios are selected
    for i in range(1, 17):
        input_data[f"comentario_valorativo_{i}"] = "no"

    # Generate document
    options = GenerationOptions(
        validate=False,  # Skip validation for faster testing
        apply_cell_colors=False,
        save_trace=False,
    )

    result = generate("pt_review", input_data, options)

    assert result.success, f"Generation failed: {result.error}"

    # Read the generated document and check if subtitle is present
    with zipfile.ZipFile(result.output_path, 'r') as zf:
        doc_xml = zf.read("word/document.xml").decode("utf-8")

    # The subtitle should NOT be present when no comentarios are selected
    assert "Comentarios valorativos" not in doc_xml, \
        "ERROR: 'Comentarios valorativos' subtitle should be hidden when no comentarios are selected!"

    print("✓ PASS: Subtitle is correctly hidden when no comentarios are selected")
    return True


def test_subtitle_shown_when_comentario_selected():
    """
    Test that the "Comentarios valorativos" subtitle IS present
    when at least one comentario_valorativo is set to "si".
    """
    # Use sample input
    sample_input_path = PROJECT_ROOT / "tests" / "golden" / "sample_input.json"

    with open(sample_input_path, "r", encoding="utf-8") as f:
        input_data = json.load(f)

    # Set one comentario to "si"
    for i in range(1, 17):
        input_data[f"comentario_valorativo_{i}"] = "no"
    input_data["comentario_valorativo_1"] = "si"

    # Generate document
    options = GenerationOptions(
        validate=False,
        apply_cell_colors=False,
        save_trace=False,
    )

    result = generate("pt_review", input_data, options)

    assert result.success, f"Generation failed: {result.error}"

    # Read the generated document and check if subtitle is present
    with zipfile.ZipFile(result.output_path, 'r') as zf:
        doc_xml = zf.read("word/document.xml").decode("utf-8")

    # The subtitle SHOULD be present when at least one comentario is selected
    assert "Comentarios valorativos" in doc_xml, \
        "ERROR: 'Comentarios valorativos' subtitle should be shown when comentarios are selected!"

    print("✓ PASS: Subtitle is correctly shown when comentarios are selected")
    return True


if __name__ == "__main__":
    print("Testing Comentarios valorativos subtitle conditional display...")
    print()

    try:
        test_subtitle_hidden_when_no_comentarios()
    except AssertionError as e:
        print(f"✗ FAIL: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ ERROR: {e}")
        sys.exit(1)

    print()

    try:
        test_subtitle_shown_when_comentario_selected()
    except AssertionError as e:
        print(f"✗ FAIL: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ ERROR: {e}")
        sys.exit(1)

    print()
    print("All tests passed!")
    sys.exit(0)
