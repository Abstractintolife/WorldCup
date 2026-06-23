"""球队 Logo（队徽）显示控件 —— 即圆形国旗。"""
from __future__ import annotations

from PyQt6.QtWidgets import QWidget

from app.ui.widgets.image_loader import RemoteImage


class TeamLogo(RemoteImage):
    """显示国家队/俱乐部队徽。默认圆形裁剪。"""

    def __init__(
        self,
        url: str | None = None,
        parent: QWidget | None = None,
        *,
        size: int = 44,
        shape: str = "circle",
    ) -> None:
        super().__init__(parent, size=size, shape=shape)
        self.set_url(url)
