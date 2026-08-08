"""Unified command-line interface for Piyu: `piyu <service> --model <model> ...`."""


def main(argv=None):
    """CLI entry (lazy import so ``python -m tryon.cli.main`` avoids double-load)."""
    from tryon.cli.main import main as _main

    return _main(argv)


__all__ = ["main"]
