"""
DEPRECATED legacy entrypoint.

This script was moved to `examples/legacy/vton.py` as Piyu adopted the
registry-driven `piyu` CLI and MCP server.

Preferred:
  piyu vton --model <model> --person-image ... --garment-image ...
"""

from __future__ import annotations

import pathlib
import runpy
import sys

_ROOT = pathlib.Path(__file__).resolve().parent
_TARGET = _ROOT / "examples" / "legacy" / "vton.py"

print(
    "[piyu] WARNING: `vton.py` is a legacy wrapper; use `piyu vton --model ...` instead.",
    file=sys.stderr,
)

runpy.run_path(str(_TARGET), run_name="__main__")

