#!/usr/bin/env python3
"""
CLI script to generate a document.

Usage:
    python scripts/run_generate.py pt_review --input data.json
    python scripts/run_generate.py pt_review --input data.json --output report.docx
"""
import argparse
import json
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from modules.generate import generate, GenerationOptions
from modules.plugin_loader import list_plugins


def main():
    parser = argparse.ArgumentParser(
        description="Generate a document from a plugin and input data"
    )
    parser.add_argument(
        "plugin_id",
        help="Plugin ID to use for generation"
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Path to JSON input file"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file path (optional)"
    )
    parser.add_argument(
        "--no-validate",
        action="store_true",
        help="Skip validation"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on validation errors"
    )
    parser.add_argument(
        "--no-colors",
        action="store_true",
        help="Don't apply cell colors"
    )
    parser.add_argument(
        "--no-trace",
        action="store_true",
        help="Don't save trace file"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available plugins"
    )

    args = parser.parse_args()

    # List plugins
    if args.list:
        plugins = list_plugins()
        print("Available plugins:")
        for p in plugins:
            print(f"  - {p}")
        return 0

    # Load input data
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        return 1

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            input_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in input file: {e}")
        return 1

    # Create options
    output_path = Path(args.output) if args.output else None
    options = GenerationOptions(
        validate=not args.no_validate,
        strict_validation=args.strict,
        apply_cell_colors=not args.no_colors,
        output_path=output_path,
        save_trace=not args.no_trace,
    )

    # Generate
    print(f"Generating document with plugin '{args.plugin_id}'...")
    result = generate(args.plugin_id, input_data, options)

    # Output
    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        if result.success:
            print(f"\n\033[92mSuccess!\033[0m")
            print(f"  Output: {result.output_path}")
            print(f"  Trace ID: {result.trace_id}")
            print(f"  Duration: {result.duration_ms}ms")

            if result.validation_result:
                if result.validation_result.errors:
                    print(f"\n  Validation Errors:")
                    for e in result.validation_result.errors:
                        print(f"    - {e}")
                if result.validation_result.warnings:
                    print(f"\n  Validation Warnings:")
                    for w in result.validation_result.warnings:
                        print(f"    - {w}")
        else:
            print(f"\n\033[91mFailed!\033[0m")
            print(f"  Error: {result.error}")

            if result.validation_result and result.validation_result.errors:
                print(f"\n  Validation Errors:")
                for e in result.validation_result.errors:
                    print(f"    - {e}")

    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main())
