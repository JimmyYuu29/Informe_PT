#!/usr/bin/env python3
"""
CLI script to validate a plugin pack.

Usage:
    python scripts/run_validate.py pt_review
    python scripts/run_validate.py --all
"""
import argparse
import json
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from modules.validate_plugin import validate_plugin, validate_all_plugins
from modules.plugin_loader import list_plugins


def print_result(result, verbose: bool = False):
    """Print validation result with colors."""
    status = "PASS" if result.is_valid else "FAIL"
    color = "\033[92m" if result.is_valid else "\033[91m"
    reset = "\033[0m"

    print(f"\n{color}[{status}]{reset} Plugin: {result.plugin_id}")

    if result.errors:
        print(f"\n  Errors ({len(result.errors)}):")
        for error in result.errors:
            print(f"    - {error}")

    if result.warnings:
        print(f"\n  Warnings ({len(result.warnings)}):")
        for warning in result.warnings:
            print(f"    - {warning}")

    if verbose and result.info:
        print(f"\n  Info ({len(result.info)}):")
        for info in result.info:
            print(f"    - {info}")


def main():
    parser = argparse.ArgumentParser(
        description="Validate plugin pack integrity"
    )
    parser.add_argument(
        "plugin_id",
        nargs="?",
        help="Plugin ID to validate"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Validate all plugins"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed info"
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

    # Validate all
    if args.all:
        results = validate_all_plugins()

        if args.json:
            output = {pid: r.to_dict() for pid, r in results.items()}
            print(json.dumps(output, indent=2))
        else:
            all_valid = True
            for result in results.values():
                print_result(result, args.verbose)
                if not result.is_valid:
                    all_valid = False

            print(f"\n{'='*50}")
            if all_valid:
                print("\033[92mAll plugins valid!\033[0m")
            else:
                print("\033[91mSome plugins have errors.\033[0m")

        return 0 if all(r.is_valid for r in results.values()) else 1

    # Validate single plugin
    if not args.plugin_id:
        parser.print_help()
        return 1

    result = validate_plugin(args.plugin_id)

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print_result(result, args.verbose)

    return 0 if result.is_valid else 1


if __name__ == "__main__":
    sys.exit(main())
