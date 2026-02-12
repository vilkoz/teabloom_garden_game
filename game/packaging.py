import os
import sys
from pathlib import Path


def resource_path(relative_path: str) -> str:
    """Resolve a path that works both during development and when bundled by PyInstaller.

    Args:
        relative_path: Path relative to project root (e.g., 'assets/images/foo.png')

    Returns:
        Absolute string path to the resource.
    """
    # When bundled by PyInstaller, files are extracted to sys._MEIPASS
    if hasattr(sys, '_MEIPASS'):
        base = Path(sys._MEIPASS)
    else:
        # Assume project root is two levels up from this file (game/packaging.py)
        base = Path(__file__).resolve().parents[1]

    return str(base / relative_path)
