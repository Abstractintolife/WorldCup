"""应用内视频播放器（直播 / 点播）—— 支持 M3U8(HLS) / FLV / MP4 等源。

设计
-----
* 基于 Qt6 ``QtMultimedia`` 的 ``QMediaPlayer`` + ``QVideoWidget`` + ``QAudioOutput``。
* 顶部「源地址」输入条：可粘贴 / 导入任意 **M3U8** 直播源或 FLV/MP4 链接，
  点「播放」即载入；记忆最近一次的地址。
* 底部控制条：播放/暂停、停止、音量、全屏、状态指示（缓冲/错误等）。
* **健壮性**：``QtMultimedia`` 在个别精简环境（缺音频后端）下可能导入失败 ——
  这里采用**惰性导入 + 优雅降级**：导入失败时弹出友好提示，并提供
  「用系统播放器打开」兜底，绝不让主程序崩溃。

关于 M3U8/HLS 解码
-------------------
Qt6 的多媒体后端（Windows: Media Foundation / 通用: FFmpeg）原生支持 HLS。
若所在平台缺少对应解码器，会在状态栏给出提示并可改用系统播放器。
"""
from __future__ import annotations

import logging

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

log = logging.getLogger(__name__)

_PRIMARY = "#00BFFF"
_LIVE = "#FF3057"
_TEXT = "#FFFFFF"
_DIM = "#B0BEC5"


def multimedia_available() -> bool:
    """检测当前环境是否可用 QtMultimedia（用于优雅降级）。"""
    try:
        from PyQt6.QtMultimedia import QMediaPlayer  # noqa: F401
        from PyQt6.QtMultimediaWidgets import QVideoWidget  # noqa: F401
        return True
    except Exception as exc:  # pragma: no cover - 环境相关
        log.warning("QtMultimedia 不可用：%s", exc)
        return False


class VideoPlayerDialog(QDialog):
    """直播 / 视频播放窗口。支持导入 M3U8 等源地址。"""

    # 跨实例记忆最近播放过的源地址，省得每次重输
    _last_url: str = ""

    def __init__(self, url: str = "", title: str = "直播间",
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(900, 560)
        self.setStyleSheet(
            "QDialog{background:#0B1020;}"
            f"QLabel{{color:{_TEXT};}}"
            "QLineEdit{background: rgba(255,255,255,0.06); color:#fff;"
            " border:1px solid rgba(255,255,255,0.16); border-radius:9px;"
            " padding:8px 12px; font-size:13px;}"
            f"QLineEdit:focus{{border:1px solid {_PRIMARY};}}"
            "QPushButton{background: rgba(255,255,255,0.08); color:#fff;"
            " border:1px solid rgba(255,255,255,0.16); border-radius:9px;"
            " padding:8px 14px; font-size:13px; font-weight:700;}"
            "QPushButton:hover{background: rgba(255,255,255,0.16);}"
            f"QPushButton#Primary{{background:{_PRIMARY}; border:none;}}"
            "QPushButton#Primary:hover{background:#46D2FF;}"
        )

        self._player = None
        self._audio = None
        self._video = None
        self._available = multimedia_available()

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 14)
        root.setSpacing(12)

        # ── 源地址输入条 ──
        src = QHBoxLayout()
        src.setSpacing(8)
        tag = QLabel("源地址")
        tag.setStyleSheet(f"color:{_DIM}; font-size:12px; font-weight:800;")
        src.addWidget(tag)
        self._url_edit = QLineEdit()
        self._url_edit.setPlaceholderText(
            "粘贴 M3U8 / FLV / MP4 直播源地址，例如 https://.../live.m3u8")
        self._url_edit.returnPressed.connect(self._play_from_input)
        src.addWidget(self._url_edit, 1)
        paste_btn = QPushButton("粘贴")
        paste_btn.clicked.connect(self._paste)
        src.addWidget(paste_btn)
        self._play_btn = QPushButton("▶  播放")
        self._play_btn.setObjectName("Primary")
        self._play_btn.clicked.connect(self._play_from_input)
        src.addWidget(self._play_btn)
        root.addLayout(src)

        # ── 视频显示区 ──
        if self._available:
            self._build_player(root)
        else:
            self._build_fallback(root)

        # ── 控制条 ──
        ctl = QHBoxLayout()
        ctl.setSpacing(10)
        self._toggle_btn = QPushButton("⏸  暂停")
        self._toggle_btn.clicked.connect(self._toggle)
        self._toggle_btn.setEnabled(False)
        ctl.addWidget(self._toggle_btn)
        self._stop_btn = QPushButton("⏹  停止")
        self._stop_btn.clicked.connect(self._stop)
        self._stop_btn.setEnabled(False)
        ctl.addWidget(self._stop_btn)

        vol_tag = QLabel("🔊")
        ctl.addWidget(vol_tag)
        self._vol = QSlider(Qt.Orientation.Horizontal)
        self._vol.setFixedWidth(120)
        self._vol.setRange(0, 100)
        self._vol.setValue(80)
        self._vol.valueChanged.connect(self._set_volume)
        ctl.addWidget(self._vol)

        ctl.addStretch(1)
        self._status = QLabel("就绪")
        self._status.setStyleSheet(f"color:{_DIM}; font-size:12px;")
        ctl.addWidget(self._status)
        ctl.addStretch(1)

        self._sys_btn = QPushButton("用系统播放器打开")
        self._sys_btn.clicked.connect(self._open_external)
        ctl.addWidget(self._sys_btn)
        self._full_btn = QPushButton("⛶  全屏")
        self._full_btn.clicked.connect(self._toggle_fullscreen)
        self._full_btn.setEnabled(self._available)
        ctl.addWidget(self._full_btn)
        root.addLayout(ctl)

        # 预填地址（本次传入 > 上次记忆）
        initial = url or VideoPlayerDialog._last_url
        if initial:
            self._url_edit.setText(initial)
            if url:
                # 显式传入地址时自动开播
                self._play(url)

    # ── 构建播放控件 ───────────────────────
    def _build_player(self, root: QVBoxLayout) -> None:
        from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer
        from PyQt6.QtMultimediaWidgets import QVideoWidget

        self._video = QVideoWidget()
        self._video.setStyleSheet("background:#000; border-radius:12px;")
        self._video.setMinimumHeight(380)
        root.addWidget(self._video, 1)

        self._player = QMediaPlayer(self)
        self._audio = QAudioOutput(self)
        self._audio.setVolume(0.8)
        self._player.setAudioOutput(self._audio)
        self._player.setVideoOutput(self._video)
        self._player.playbackStateChanged.connect(self._on_state)
        self._player.mediaStatusChanged.connect(self._on_media_status)
        self._player.errorOccurred.connect(self._on_error)

    def _build_fallback(self, root: QVBoxLayout) -> None:
        box = QLabel(
            "⚠️  当前运行环境缺少多媒体解码后端，无法内嵌播放。\n\n"
            "请点击右下角「用系统播放器打开」，用本机播放器观看该直播源，\n"
            "或在安装了 Qt 多媒体后端（FFmpeg）的环境中运行本程序。")
        box.setWordWrap(True)
        box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        box.setMinimumHeight(380)
        box.setStyleSheet(
            "background: rgba(255,255,255,0.04); border:1px dashed rgba(255,255,255,0.2);"
            f" border-radius:12px; color:{_DIM}; font-size:14px; padding:24px;")
        root.addWidget(box, 1)

    # ── 交互 ───────────────────────────────
    def _paste(self) -> None:
        from PyQt6.QtWidgets import QApplication
        text = QApplication.clipboard().text().strip()
        if text:
            self._url_edit.setText(text)

    def _play_from_input(self) -> None:
        url = self._url_edit.text().strip()
        if not url:
            self._status.setText("请输入有效的源地址")
            return
        self._play(url)

    def _play(self, url: str) -> None:
        VideoPlayerDialog._last_url = url
        self._url_edit.setText(url)
        if not self._available or self._player is None:
            self._status.setText("环境不支持内嵌播放，请用系统播放器打开")
            return
        kind = "直播" if url.lower().split("?")[0].endswith((".m3u8", ".flv")) else "视频"
        self._status.setText(f"正在加载{kind}流…")
        self._player.setSource(QUrl(url))
        self._player.play()
        self._toggle_btn.setEnabled(True)
        self._stop_btn.setEnabled(True)

    def _toggle(self) -> None:
        if self._player is None:
            return
        from PyQt6.QtMultimedia import QMediaPlayer
        if self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self._player.pause()
        else:
            self._player.play()

    def _stop(self) -> None:
        if self._player is not None:
            self._player.stop()
        self._status.setText("已停止")

    def _set_volume(self, v: int) -> None:
        if self._audio is not None:
            self._audio.setVolume(v / 100.0)

    def _open_external(self) -> None:
        url = self._url_edit.text().strip()
        if not url:
            QMessageBox.information(self, "提示", "请先输入直播源地址。")
            return
        QDesktopServices.openUrl(QUrl(url))

    def _toggle_fullscreen(self) -> None:
        if self.isFullScreen():
            self.showNormal()
            self._full_btn.setText("⛶  全屏")
        else:
            self.showFullScreen()
            self._full_btn.setText("⛶  退出全屏")

    # ── QMediaPlayer 回调 ───────────────────
    def _on_state(self, state) -> None:
        from PyQt6.QtMultimedia import QMediaPlayer
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self._toggle_btn.setText("⏸  暂停")
        else:
            self._toggle_btn.setText("▶  播放")

    def _on_media_status(self, status) -> None:
        from PyQt6.QtMultimedia import QMediaPlayer
        S = QMediaPlayer.MediaStatus
        mapping = {
            S.LoadingMedia: "加载中…",
            S.BufferingMedia: "缓冲中…",
            S.BufferedMedia: "播放中 ●",
            S.StalledMedia: "网络缓冲…",
            S.EndOfMedia: "播放结束",
            S.InvalidMedia: "无效的媒体源",
            S.NoMedia: "就绪",
        }
        if status in mapping:
            self._status.setText(mapping[status])

    def _on_error(self, error, error_string: str = "") -> None:
        from PyQt6.QtMultimedia import QMediaPlayer
        if error == QMediaPlayer.Error.NoError:
            return
        msg = error_string or "播放出错"
        self._status.setText(f"⚠️ {msg}")
        log.warning("视频播放错误：%s", msg)

    # ── 资源释放 ───────────────────────────
    def closeEvent(self, ev) -> None:
        try:
            if self._player is not None:
                self._player.stop()
        except Exception:
            pass
        super().closeEvent(ev)
