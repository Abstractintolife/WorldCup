"""收藏按钮（星形切换）。"""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QPushButton

from app.services.favorites import EntityKind, Favorites
from app.ui.design.app_cursor import pointing_hand_cursor


class FavoriteButton(QPushButton):
    """绑定 Favorites 服务的星标切换按钮。"""

    toggled_changed = pyqtSignal(bool)

    def __init__(
        self,
        favorites: Favorites,
        kind: EntityKind,
        entity_id: str,
        label_text: str = "",
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._favorites = favorites
        self._kind = kind
        self._entity_id = entity_id
        self._label_text = label_text
        self.setProperty("ghost", True)
        self.setCursor(pointing_hand_cursor())
        self.clicked.connect(self._on_click)
        self._sync()

    def set_entity(self, kind: EntityKind, entity_id: str) -> None:
        self._kind = kind
        self._entity_id = entity_id
        self._sync()

    def _on_click(self) -> None:
        added = self._favorites.toggle(self._kind, self._entity_id)
        self.toggled_changed.emit(added)
        self._sync()

    def _sync(self) -> None:
        is_fav = self._favorites.is_favorite(self._kind, self._entity_id)
        prefix = "★" if is_fav else "☆"
        suffix = "已收藏" if is_fav else "收藏"
        text = f"{prefix}  {suffix}"
        if self._label_text:
            text = f"{prefix}  {self._label_text}"
        self.setText(text)
        self.setStyleSheet(
            "color: #FFD700; font-weight: 700;" if is_fav else "color: #B0BEC5;"
        )
