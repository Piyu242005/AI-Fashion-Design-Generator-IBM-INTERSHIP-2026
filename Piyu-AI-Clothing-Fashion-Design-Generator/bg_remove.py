"""
DEPRECATED legacy entrypoint.

Moved to `examples/legacy/bg_remove.py`. Prefer:
  piyu bg-remove --model ben2 --image ... [--refine]
"""

from __future__ import annotations

import pathlib
import runpy
import sys

_ROOT = pathlib.Path(__file__).resolve().parent
_TARGET = _ROOT / "examples" / "legacy" / "bg_remove.py"

print(
    "[piyu] WARNING: `bg_remove.py` is legacy; use `piyu bg-remove --model ben2 ...` instead.",
    file=sys.stderr,
)

runpy.run_path(str(_TARGET), run_name="__main__")

