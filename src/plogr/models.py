from __future__ import annotations
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Any, Literal, TypedDict

Scope = Literal["user", "system"]


class PkgEventDict(TypedDict):
    name: str
    manager: str
    action: str
    scope: Scope
    date: str
    removed: bool
    version: str | None
    metadata: dict[str, Any] | None
    date_removed: str | None


@dataclass
class PkgEvent:
    name: str
    manager: str
    action: str
    scope: Scope
    date: datetime = field(default_factory=lambda: datetime.now().replace(microsecond=0))
    removed: bool = False
    version: str | None = None
    metadata: dict[str, Any] | None = None
    date_removed: datetime | None = None

    def to_dict(self) -> PkgEventDict:
        d: PkgEventDict = {
            "name": self.name,
            "manager": self.manager,
            "action": self.action,
            "scope": self.scope,
            "date": self.date.isoformat(timespec="seconds"),
            "removed": self.removed,
        }

        if self.version:
            d["version"] = self.version
        if self.metadata:
            d["metadata"] = self.metadata
        if self.date_removed:
            d["date_removed"] = self.date_removed.isoformat(timespec="seconds")

        return d
