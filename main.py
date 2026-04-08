#!/usr/bin/env python3
"""NASA UFO — Universal Flight Operations CLI entry point.

Usage:
    python main.py                                   # interactive mode
    python main.py --mission "Today's astronomy picture"
    python main.py --mission "Asteroids near Earth this week"
    python main.py --mission "Mars Curiosity rover photos sol 1000"
    python main.py --list-tools
"""

from __future__ import annotations

import argparse
import json
import sys

from nasa_ufo.agent import HostAgent


BANNER = r"""
  _   _    _    ____    _    _   _ _____ ___
 | \ | |  / \  / ___|  / \  | | | |  ___/ _ \
 |  \| | / _ \ \___ \ / _ \ | | | | |_ | | | |
 | |\  |/ ___ \ ___) / ___ \| |_| |  _|| |_| |
 |_| \_/_/   \_\____/_/   \_\\___/|_|   \___/

 🚀 Universal Flight Operations — NASA Edition
 Inspired by Microsoft UFO  |  https://api.nasa.gov
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nasa-ufo",
        description="NASA UFO agent — explore NASA data via natural language missions.",
    )
    parser.add_argument(
        "--mission", "-m",
        metavar="TEXT",
        help="Natural-language mission description to execute.",
    )
    parser.add_argument(
        "--list-tools", "-l",
        action="store_true",
        help="List available NASA tools and exit.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON.",
    )
    parser.add_argument(
        "--api-key",
        metavar="KEY",
        help="NASA API key (overrides NASA_API_KEY env var).",
    )
    return parser


def interactive_loop(agent: HostAgent) -> None:
    """Run an interactive REPL for entering missions."""
    print(BANNER)
    print("Type a mission (or 'quit' / 'tools' / 'history'):\n")
    while True:
        try:
            mission = input("🛸 Mission> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Safe travels, astronaut!")
            sys.exit(0)

        if not mission:
            continue
        if mission.lower() in ("quit", "exit", "q"):
            print("👋 Safe travels, astronaut!")
            sys.exit(0)
        if mission.lower() == "tools":
            _print_tools(agent)
            continue
        if mission.lower() == "history":
            _print_history(agent)
            continue

        result = agent.run(mission)
        print("\n" + str(result) + "\n")


def _print_tools(agent: HostAgent) -> None:
    print("\n📡 Available NASA Tools:")
    for name, desc in agent.list_tools().items():
        print(f"  • {name:18s} — {desc}")
    print()


def _print_history(agent: HostAgent) -> None:
    history = agent.history()
    if not history:
        print("  (no missions flown yet)")
        return
    print(f"\n📋 Mission history ({len(history)} mission(s)):")
    for i, r in enumerate(history, 1):
        status = "✅" if r.success else "❌"
        print(f"  {i}. {status} [{r.tool_used}] {r.mission[:60]}")
    print()


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    # Build the agent, injecting API key if provided
    import os
    if args.api_key:
        os.environ["NASA_API_KEY"] = args.api_key

    agent = HostAgent()

    if args.list_tools:
        _print_tools(agent)
        return

    if args.mission:
        result = agent.run(args.mission)
        if args.json:
            print(json.dumps(result.to_dict(), indent=2, default=str))
        else:
            print(str(result))
        sys.exit(0 if result.success else 1)

    # No flags — enter interactive mode
    interactive_loop(agent)


if __name__ == "__main__":
    main()
