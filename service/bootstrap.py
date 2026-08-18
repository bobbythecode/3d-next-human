"""Load MakeHuman Human + modifiers without starting a Qt window."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np

_MH_ROOT = Path(__file__).resolve().parents[1] / "makehuman"
_READY = False
_NUMPY_UNIQUE = np.unique


def _install_sys_path() -> None:
    cwd = str(_MH_ROOT)
    extra = [
        cwd,
        str(_MH_ROOT / "lib"),
        str(_MH_ROOT / "apps"),
        str(_MH_ROOT / "shared"),
        str(_MH_ROOT / "core"),
        str(_MH_ROOT / "apps" / "gui"),
    ]
    sys.path[:0] = [p for p in extra if p not in sys.path]
    os.chdir(cwd)


class _HeadlessApp:
    splash = None
    statusBar = None
    log_window = None
    selectedHuman = None
    loadHandlers = {}
    modelCamera = None

    def progress(self, *args, **kwargs):
        return None

    def addLogMessage(self, *args, **kwargs):
        return None


def ensure_runtime() -> None:
    global _READY
    if _READY:
        return
    for name in ("PyQt5", "PyQt6", "OpenGL"):
        if name in sys.modules:
            raise RuntimeError(f"{name} must not be imported in headless human-api")
    _install_sys_path()
    from core import G

    G.app = _HeadlessApp()
    G.cameras = [None, None]
    G.args = {"noshaders": True}

    import log

    log.init()
    np.unique = _NUMPY_UNIQUE

    _READY = True


def qt_imported() -> bool:
    return any(name in sys.modules for name in ("PyQt5", "PyQt6", "PySide2", "PySide6"))
