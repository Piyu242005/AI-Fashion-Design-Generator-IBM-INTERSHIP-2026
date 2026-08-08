"""
DEPRECATED legacy entrypoint.

Moved to `examples/legacy/image_gen.py`. Use the registry-driven CLI instead:
`piyu generate ...` or `piyu edit ...`.
"""

from __future__ import annotations

import pathlib
import runpy
import sys

_ROOT = pathlib.Path(__file__).resolve().parent
_TARGET = _ROOT / "examples" / "legacy" / "image_gen.py"

print(
    "[piyu] WARNING: `image_gen.py` is a legacy wrapper; use `piyu generate|edit ...` instead.",
    file=sys.stderr,
)

runpy.run_path(str(_TARGET), run_name="__main__")

