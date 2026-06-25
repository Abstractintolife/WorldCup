# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller 打包配置 —— 世界杯赛事终端。

用法：
    pip install pyinstaller
    pyinstaller WorldCupConsole.spec            # 产物在 dist/WorldCupConsole/
    pyinstaller --clean WorldCupConsole.spec    # 清理后重新打包

说明：
* 必须在「目标操作系统」上打包（PyInstaller 不能跨平台交叉编译）：
  Windows 上打 .exe、macOS 上打 .app、Linux 上打可执行文件。
* 请使用 Python 3.13 或 3.12（qasync 暂不支持 3.14）。
* 默认 onedir 模式（启动快、易排错）。需要单文件改用 onefile（见底部注释）。
"""
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# httpx[http2] 的 HTTP/2 依赖是按需导入的，静态分析可能漏掉，显式补上；
# certifi 提供 TLS 根证书（修复打包后 SSL 证书校验失败）；
# pypinyin 的词典以子模块形式存放，整体收集更稳妥。
hiddenimports = ["h2", "hpack", "hyperframe", "certifi"] + collect_submodules("pypinyin")

# 随程序打包的数据文件（源路径, 包内目标目录）。
# 运行时 app/config.py 用 __file__ 反推 ROOT_DIR，因此目标目录需与源结构一致。
datas = [
    ("assets", "assets"),                            # 国旗位图 assets/flags/*.png（及字体 assets/fonts/*.ttf 若有）
    ("app/services/land_mask.b64", "app/services"),  # 3D 地球仪陆地掩膜
    # 仓库根目录的资源：config.py 用 ROOT_DIR/__file__ 反推后从「包根」读取，
    # 因此目标目录填 "."（即解包根 _MEIPASS / onedir 的 _internal 根）。
    ("背景图.png", "."),                              # 主页/全局背景图（缺则回退程序化渐变）
    ("光标.png", "."),                               # 默认箭头光标兜底（主图为 assets/cursor.png）
    ("点击光标.png", "."),                            # 点击手型光标兜底（主图为 assets/click_cursor.png）
]
# certifi 的 cacert.pem —— 确保 httpx/ssl 在打包后能找到 CA 根证书。
datas += collect_data_files("certifi")

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter"],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="WorldCupConsole",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,            # GUI 应用：不弹出命令行黑窗
    disable_windowed_traceback=False,
    argv_emulation=False,     # macOS 拖拽打开文件需要时设 True
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="assets/icon/app.ico",   # Windows exe 图标（macOS 用 app.icns）
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="WorldCupConsole",
)

# ── macOS 可选：生成 .app 程序包（取消注释）────────────────────────────
# app = BUNDLE(
#     coll,
#     name="WorldCupConsole.app",
#     icon=None,              # app.icns
#     bundle_identifier="com.kiro.worldcupconsole",
# )

# ── 单文件模式（onefile）：把上面的 EXE(...) 改为包含全部二进制并删除 COLLECT ──
# exe = EXE(pyz, a.scripts, a.binaries, a.datas, [],
#           name="WorldCupConsole", console=False, upx=True)
# （单文件启动稍慢，因为每次运行会先解压到临时目录）
