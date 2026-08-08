"""
DEPRECATED legacy entrypoint.

Moved to `examples/legacy/gpt_image.py`. Prefer:
  - `piyu generate --model gpt-image ...`
  - `piyu edit --model gpt-image ...`
"""

from __future__ import annotations

import pathlib
import runpy
import sys

_ROOT = pathlib.Path(__file__).resolve().parent
_TARGET = _ROOT / "examples" / "legacy" / "gpt_image.py"

print(
    "[piyu] WARNING: `gpt_image.py` is legacy; use `piyu generate|edit --model gpt-image` instead.",
    file=sys.stderr,
)

runpy.run_path(str(_TARGET), run_name="__main__")

