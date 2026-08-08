"""
DEPRECATED legacy entrypoint.

Moved to `examples/legacy/sora_video.py`. Prefer:
  piyu video-generate --model sora ...
"""

from __future__ import annotations

import pathlib
import runpy
import sys

_ROOT = pathlib.Path(__file__).resolve().parent
_TARGET = _ROOT / "examples" / "legacy" / "sora_video.py"

print(
    "[piyu] WARNING: `sora_video.py` is legacy; use `piyu video-generate --model sora` instead.",
    file=sys.stderr,
)

runpy.run_path(str(_TARGET), run_name="__main__")

