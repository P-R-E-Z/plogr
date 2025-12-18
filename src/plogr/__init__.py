"""Main package for plogr"""

from __future__ import annotations

import importlib.metadata
from typing import Any

from .backends.base import PackageBackend

_BACKENDS: dict[str, type[PackageBackend]] = {}


def register_backend(name: str, backend_class: type[PackageBackend]) -> None:
    """Register a new package manager backend

    Args:
        name: Name of the package manager (e.g., 'dnf', apt, etc.)
        backend_class: Backend class to register
    """
    _BACKENDS[name] = backend_class


def get_backend(name: str | None = None) -> PackageBackend | None:
    """Get a package manager backend by name

    Args:
        name: Name of the package manager (e.g., 'dnf', apt, etc.)

    Returns:
        PackageBackend instance or None if not found/available
    """
    if name and (backend_class := _BACKENDS.get(name.lower())):
        return backend_class()
    return None


def detect_available_backends(
    config: Any | None = None,
    logger: Any | None = None,
) -> dict[str, PackageBackend]:
    """Detect and return all available package manager backends

    Args:
        config: Optional configuration to pass to backends
        logger: Optional PackageLogger to attach to each backend (if supported)

    Returns:
        Dictionary mapping backend names to initialized backend instances
    """
    available = {}
    for name, backend_class in _BACKENDS.items():
        if backend_class.is_available():
            backend_instance = backend_class(config)
            # If the backend expects a logger attribute, wire it here centrally.
            if logger is not None and hasattr(backend_instance, "logger"):
                backend_instance.logger = logger  # type: ignore[attr-defined]
            available[name] = backend_instance
    return available


try:
    __version__ = importlib.metadata.version("plogr")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0"

from . import backends  # noqa: F401, E402

for backend_name, backend_class in backends.discovered_backends.items():
    register_backend(backend_name, backend_class)
