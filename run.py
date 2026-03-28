#!/usr/bin/env python3
"""
Invisibility Cloak Application
Entry point for running the real-time invisibility cloak effect.

Usage:
    python run.py                    # Default (red cloak, gaussian blending)
    python run.py --color blue       # Blue cloak
    python run.py --color green      # Green cloak
    python run.py --blend simple     # Simple blending
    python run.py --color red --blend alpha  # Red cloak with alpha blending
"""

import sys
import argparse
from src.main import InvisibilityCloakProcessor
from config.settings import COLOR_PRESETS


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Invisibility Cloak - Real-time video effect'
    )

    parser.add_argument(
        '--color',
        type=str,
        default='red',
        choices=list(COLOR_PRESETS.keys()),
        help='Color of the cloak (default: red)'
    )

    parser.add_argument(
        '--blend',
        type=str,
        default='gaussian',
        choices=['simple', 'gaussian', 'alpha', 'pyramid'],
        help='Blending method (default: gaussian)'
    )

    parser.add_argument(
        '--camera',
        type=int,
        default=0,
        help='Camera device index (default: 0)'
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode'
    )

    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_arguments()

    print("=" * 70)
    print("Invisibility Cloak - Real-time Video Effect")
    print("=" * 70)
    print()
    print(f"Configuration:")
    print(f"  Cloak Color: {args.color}")
    print(f"  Blend Method: {args.blend}")
    print(f"  Camera Index: {args.camera}")
    print()
    print("Controls:")
    print("  SPACE  - Capture background")
    print("  R      - Reset background")
    print("  Q      - Quit application")
    print()
    print("=" * 70)
    print()

    # Create processor
    processor = InvisibilityCloakProcessor(
        cloak_color=args.color,
        blend_method=args.blend
    )

    # Run
    try:
        processor.run()
    except Exception as e:
        print(f"[Error] {e}")
        import traceback
        traceback.print_exc()
    finally:
        processor.cleanup()


if __name__ == '__main__':
    main()