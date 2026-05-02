#!/usr/bin/env python3
"""Set up a local Python virtual environment for running tests."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run(command: list[str]) -> None:
    """Run a command and stream output to the terminal."""
    print("+", " ".join(command))
    subprocess.run(command, check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create .venv and install test dependencies."
    )
    parser.add_argument(
        "--venv-dir",
        default=".venv",
        help="Directory to create the virtual environment in (default: .venv).",
    )
    parser.add_argument(
        "--recreate",
        action="store_true",
        help="Remove and recreate the virtual environment directory if it exists.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parent
    venv_dir = (repo_root / args.venv_dir).resolve()

    if args.recreate and venv_dir.exists():
        import shutil

        print(f"Removing existing environment: {venv_dir}")
        shutil.rmtree(venv_dir)

    if not venv_dir.exists():
        print(f"Creating virtual environment in: {venv_dir}")
        run([sys.executable, "-m", "venv", str(venv_dir)])
    else:
        print(f"Using existing virtual environment: {venv_dir}")

    python_bin = venv_dir / "bin" / "python"
    if not python_bin.exists():
        print("Error: could not find venv interpreter at", python_bin)
        return 1

    run([str(python_bin), "-m", "pip", "install", "--upgrade", "pip"])
    run([str(python_bin), "-m", "pip", "install", "pytest"])

    print("\nSetup complete.")
    print("Run tests with:")
    print(f"  {python_bin} -m pytest test_install.py -v")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
