#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

# This script is intended to be invoked via Poe the Poet (`poe`). Python projects
# should include it in their `pyproject.toml` as a task, so that one can run
# `uv run check` or `uv run fix` from the project root.


def run(cmd: list[str]) -> None:
    print(f"Running: `{' '.join(cmd)}`")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        sys.exit(result.returncode)


def run_uv(args: list[str]) -> None:
    cmd = ["uv", "run", "--active"] + args
    run(cmd)


def main() -> None:
    args = sys.argv[1:]
    if len(args) == 1 and args[0] == "--test":
        cov_config_path = (Path(__file__).parent.parent / ".coveragerc").resolve()
        run_uv([
            "pytest",
            "tests/",
            "-v",
            "--cov=youtrack_sdk/",
            "--cov-branch",
            "--cov-report=term-missing:skip-covered",
            "--cov-report=html:coverage_html",
            f"--cov-config={cov_config_path}",
        ])
        return

    if len(args) > 1 or (args and args[0] != "--fix"):
        print(f"Usage: {args[0]} [--fix]", file=sys.stderr)
        print(args, file=sys.stderr)
        sys.exit(2)

    if "--fix" in args:
        run_uv(["ruff", "format"])
        run_uv(["ruff", "check", "--fix"])
        run_uv(["pyright"])
    else:
        run_uv(["ruff", "format", "--check"])
        run_uv(["ruff", "check"])
        run_uv(["pyright"])


if __name__ == "__main__":
    main()
