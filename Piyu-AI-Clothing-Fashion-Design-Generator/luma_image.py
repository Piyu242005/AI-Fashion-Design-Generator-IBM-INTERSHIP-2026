"""
DEPRECATED legacy entrypoint.

Moved to `examples/legacy/luma_image.py`. Prefer:
  - `piyu generate --model luma-image ...`
"""

from __future__ import annotations

import pathlib
import runpy
import sys

_ROOT = pathlib.Path(__file__).resolve().parent
_TARGET = _ROOT / "examples" / "legacy" / "luma_image.py"

print(
    "[piyu] WARNING: `luma_image.py` is legacy; use `piyu generate --model luma-image ...` instead.",
    file=sys.stderr,
)

runpy.run_path(str(_TARGET), run_name="__main__")

