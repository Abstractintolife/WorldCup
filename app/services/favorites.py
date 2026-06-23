"""收藏夹与设置（持久化到本地 JSON）。"""
from __future__ import annotations

import json
from typing import Literal

from app.config import FAVORITES_FILE, SETTINGS_FILE

EntityKind = Literal["team", "player", "match"]


class Favorites:
    """简易收藏夹，按实体种类分桶。"""

    def __init__(self) -> None:
        self._data: dict[str, list[str]] = {"team": [], "player": [], "match": []}
        self._load()

    def _load(self) -> None:
        if FAVORITES_FILE.exists():
            try:
                self._data.update(
                    json.loads(FAVORITES_FILE.read_text(encoding="utf-8"))
                )
            except Exception:
                pass

    def _save(self) -> None:
        FAVORITES_FILE.write_text(
            json.dumps(self._data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def is_favorite(self, kind: EntityKind, entity_id: str) -> bool:
        return entity_id in self._data.get(kind, [])

    def toggle(self, kind: EntityKind, entity_id: str) -> bool:
        bucket = self._data.setdefault(kind, [])
        if entity_id in bucket:
            bucket.remove(entity_id)
            self._save()
            return False
        bucket.append(entity_id)
        self._save()
        return True

    def list(self, kind: EntityKind) -> list[str]:
        return list(self._data.get(kind, []))


class Settings:
    """轻量级 JSON 设置文件。"""

    def __init__(self) -> None:
        self._data: dict[str, object] = {"theme": "dark"}
        if SETTINGS_FILE.exists():
            try:
                self._data.update(
                    json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
                )
            except Exception:
                pass

    def get(self, key: str, default: object = None) -> object:
        return self._data.get(key, default)

    def set(self, key: str, value: object) -> None:
        self._data[key] = value
        SETTINGS_FILE.write_text(
            json.dumps(self._data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
