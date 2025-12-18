import datetime as dt
import json
import pathlib
import os
from pathlib import PosixPath
from typing import Dict, Any, Optional, Iterator, cast, List
import logging
import threading
from contextlib import contextmanager

from .config import Config
from .models import PkgEvent

toml: Any

try:
    import toml as _toml_module  # type: ignore[import-untyped]
except ImportError:  # pragma: no cover
    _toml_module = None  # type: ignore[assignment]

toml = cast(Optional[Any], _toml_module)  # type: ignore[assignment]

logger = logging.getLogger(__name__)
_TOML_WARNING_EMITTED = False

if os.name == "posix":
    import fcntl  # type: ignore

    @contextmanager
    def _file_lock(path: pathlib.Path) -> Iterator[None]:
        """Context manager acquiring an exclusive advisory lock on *path*."""
        with path.open("a") as lock_fp:
            try:
                fcntl.flock(lock_fp, fcntl.LOCK_EX)
                yield
            finally:
                fcntl.flock(lock_fp, fcntl.LOCK_UN)

else:
    try:  # pragma: no cover - exercised via patched os.name in tests
        import msvcrt  # type: ignore

        @contextmanager
        def _file_lock(path: pathlib.Path) -> Iterator[None]:
            with path.open("a") as lock_fp:
                try:
                    msvcrt.locking(lock_fp.fileno(), msvcrt.LK_LOCK, 1)  # type: ignore[attr-defined]
                    yield
                finally:
                    lock_fp.seek(0)
                    msvcrt.locking(lock_fp.fileno(), msvcrt.LK_UNLCK, 1)  # type: ignore[attr-defined]

    except ImportError:
        # Non-Windows environment with os.name patched to 'nt' (tests); use a no-op lock.
        @contextmanager
        def _file_lock(path: pathlib.Path) -> Iterator[None]:  # pragma: no cover
            with path.open("a"):
                yield


class PackageLogger:
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self._thread_lock = threading.RLock()

        if toml is None:
            self._warn_toml_missing()

        self._setup_paths()
        self._ensure_directories()

    def _setup_paths(self):
        """Setup paths based on scope"""
        if self.config.is_system_scope:
            self.data_dir = PosixPath("/var/log/plogr")
            self.json_file = self.data_dir / "packages.json"
            self.toml_file = self.data_dir / "packages.toml"
        else:
            self.data_dir = PosixPath.home() / ".local/share/plogr"
            self.json_file = self.data_dir / "packages.json"
            self.toml_file = self.data_dir / "packages.toml"

    def _ensure_directories(self):
        """Create directories if they don't exist"""
        self.data_dir.mkdir(parents=True, exist_ok=True)

        if self.config.is_system_scope:
            self.data_dir.chmod(0o755)
        else:
            self.data_dir.chmod(0o700)

        if not self.json_file.exists():
            self.json_file.write_text("[]")
        if not self.toml_file.exists():
            self.toml_file.write_text("")

        if self.config.is_system_scope:
            self.json_file.chmod(0o644)
            self.toml_file.chmod(0o644)
        else:
            self.json_file.chmod(0o600)
            self.toml_file.chmod(0o600)

    def log_package(
        self,
        name: str,
        manager: str,
        action: str,
        version: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> None:
        """Log a package action"""
        if not name or not name.strip():
            logger.warning(f"Warning: Invalid package name: {name}")
            return

        event = PkgEvent(
            name=name.strip(),
            manager=manager,
            action=action,
            scope=self.config.scope,
            removed=action == "remove",
            version=version,
            metadata=metadata,
        )

        self._upsert_json_and_toml(event.to_dict())

    def _upsert_json_and_toml(self, entry: Dict[str, Any]) -> None:
        """Upsert the JSON log, updating prior install on removal; then rewrite TOML from JSON."""
        try:
            with self._thread_lock:
                with _file_lock(self.json_file):
                    if self.json_file.exists() and self.json_file.stat().st_size > 0:
                        data: List[Dict[str, Any]] = json.loads(self.json_file.read_text())
                    else:
                        data = []

                    if entry.get("removed"):
                        # Find last matching install record to mark as removed
                        idx_to_update: Optional[int] = None
                        for i in range(len(data) - 1, -1, -1):
                            rec = data[i]
                            if (
                                rec.get("name") == entry.get("name")
                                and rec.get("manager") == entry.get("manager")
                                and not rec.get("removed", False)
                            ):
                                idx_to_update = i
                                break
                        if idx_to_update is not None:
                            data[idx_to_update]["removed"] = True
                            data[idx_to_update]["action"] = "remove"
                            data[idx_to_update]["date_removed"] = entry.get("date")
                        else:
                            data.append(entry)
                    else:
                        data.append(entry)

                    # Write JSON back
                    if len(data) > 1000:
                        self._write_json_streaming(data)
                    else:
                        self._atomic_write(self.json_file, json.dumps(data, indent=2))

                # Rewrite TOML based on the current JSON content to reflect updated flags
                self._rewrite_toml_from_json_data(data)
        except Exception as e:
            logger.error(f"Error updating log files: {e}")

    def _rewrite_toml_from_json_data(self, data: List[Dict[str, Any]]) -> None:
        """Rewrite TOML file completely to match JSON state."""
        if toml is None:
            return
        try:
            with self._thread_lock:
                with _file_lock(self.toml_file):
                    lines: List[str] = []
                    for rec in data:
                        if rec.get("removed"):
                            lines.append("# --REMOVED--\n")
                        lines.append(toml.dumps(rec))
                        lines.append("\n")
                    content = "".join(lines)
                    self._atomic_write(self.toml_file, content)
        except Exception as e:
            logger.error(f"Error writing to TOML log file: {e}")

    def _append_json(self, entry: Dict[str, Any]):
        """Append entry to JSON log file"""
        try:
            with self._thread_lock:
                with _file_lock(self.json_file):
                    if self.json_file.exists() and self.json_file.stat().st_size > 0:
                        data = json.loads(self.json_file.read_text())
                    else:
                        data = []

                    data.append(entry)

                    if len(data) > 1000:
                        self._write_json_streaming(data)
                    else:
                        self._atomic_write(self.json_file, json.dumps(data, indent=2))
        except Exception as e:
            logger.error(f"Error writing to JSON log file: {e}")

    def _atomic_write(self, path: pathlib.Path, content: str) -> None:
        """Write *content* to *path* atomically using a temporary file."""
        tmp_path = path.with_suffix(path.suffix + ".tmp")
        tmp_path.write_text(content)
        tmp_path.replace(path)

    def _write_json_streaming(self, data: list):
        """Write JSON data using streaming to avoid memory issues atomically."""
        tmp_path = self.json_file.with_suffix(".json.tmp")
        with tmp_path.open("w") as f:
            f.write("[\n")
            for i, item in enumerate(data):
                json.dump(item, f, indent=2)
                if i < len(data) - 1:
                    f.write(",\n")
            f.write("\n]")
        tmp_path.replace(self.json_file)

    def query(
        self,
        name: Optional[str] = None,
        manager: Optional[str] = None,
        since: Optional[dt.date] = None,
    ) -> list:
        """Query the package log"""
        try:
            data = json.loads(self.json_file.read_text())
            results = data

            if name:
                results = [e for e in results if name.lower() in e.get("name", "").lower()]

            if manager:
                results = [e for e in results if e.get("manager") == manager]

            if since:
                results = [
                    e for e in results if dt.datetime.fromisoformat(e.get("date")).date() >= since
                ]

            return results
        except Exception as e:
            logger.error(f"Error querying log file: {e}")
            return []

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics from log files"""
        try:
            data = json.loads(self.json_file.read_text())

            total = len(data)
            installed = sum(1 for e in data if not e.get("removed", False))
            removed = sum(1 for e in data if e.get("removed", False))
            downloads = sum(1 for e in data if e.get("manager") == "download")

            stats = {
                "total": total,
                "installed": installed,
                "removed": removed,
                "downloads": downloads,
                "scope": self.config.scope,
            }
            return stats
        except Exception:
            return {
                "total": 0,
                "installed": 0,
                "removed": 0,
                "downloads": 0,
                "scope": self.config.scope,
            }

    def _warn_toml_missing(self) -> None:
        """Emit a one-time warning when TOML support is unavailable."""
        global _TOML_WARNING_EMITTED
        if _TOML_WARNING_EMITTED:
            return

        logger.warning("TOML output disabled: optional dependency 'toml' not installed.")
        _TOML_WARNING_EMITTED = True
