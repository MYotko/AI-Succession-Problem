#!/usr/bin/env python3
"""Bootstrap Gate Validator — command-line interface."""

import argparse
import json
import sys
import os

# Allow running as `python cli.py` from within the package directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bootstrap_gate_validator.validator import BootstrapGateValidator
from bootstrap_gate_validator.schema import validate_config, SchemaError
from bootstrap_gate_validator.report import format_text_report, format_json_report


def main():
    parser = argparse.ArgumentParser(
        description='Bootstrap Gate Validator for The Lineage Imperative v1.x.1',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            'Examples:\n'
            '  python cli.py sample_input.json\n'
            '  python cli.py sample_input.json --output json\n'
            '  python cli.py sample_input.json --outfile report.txt\n'
        ),
    )
    parser.add_argument('config', help='Path to JSON configuration file')
    parser.add_argument(
        '--output',
        choices=['json', 'text'],
        default='text',
        help='Output format (default: text)',
    )
    parser.add_argument(
        '--outfile',
        help='Write output to file instead of stdout',
    )
    args = parser.parse_args()

    try:
        with open(args.config) as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f'Error: configuration file not found: {args.config}', file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f'Error: invalid JSON in {args.config}: {e}', file=sys.stderr)
        sys.exit(1)

    try:
        validate_config(config)
    except SchemaError as e:
        print(f'Schema error: {e}', file=sys.stderr)
        sys.exit(1)

    validator = BootstrapGateValidator()
    results = validator.validate(config)

    if args.output == 'json':
        output = format_json_report(results)
    else:
        output = format_text_report(results)

    if args.outfile:
        with open(args.outfile, 'w') as f:
            f.write(output)
        print(f'Report written to {args.outfile}', file=sys.stderr)
    else:
        print(output)


if __name__ == '__main__':
    main()
