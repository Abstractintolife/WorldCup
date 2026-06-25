# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller 打包配置（单文件 onefile 版）—— 世界杯赛事终端。

产物：dist/WorldCupConsole.exe —— 单个 exe，分发时只需这一个文件，用户看不到
任何 .py 文件。注意：onefile 内部仍是 .pyc 字节码，理论上可被反编译；若要「无
可反编译源码」的强防护，请改用 Nuitka（见 scripts/build_windows_nuitka.bat）。

用法：
    pip install pyinstaller
    pyinstaller WorldCupConsole-onefile.spec
    pyinstaller --clean WorldCupConsole-onefile.spec   # 清理后重新打包

说明：
* 必须在 Windows 上打包（PyInstaller 不能跨平台交叉编译）。
* 请使用 Python 3.13 或 3.12（qasync 暂不支持 3.14）。
* 单文件启动稍慢：每次运行会先把内容解压到系统临时目录。
"""
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# httpx[http2] 的 HTTP/2 依赖是按需导入的，静态分析可能漏掉，显式补上；
# certifi 提供 TLS 根证书（修复打包后 SSL 证书校验失败）；
# pypinyin 的词典以子模块形式存放，整体收集更稳妥。
hiddenimports = ["h2", "hpack", "hyperframe", "certifi"] + collect_submodules("pypinyin")

# 随程序打包的数据文件（源路径, 包内目标目录）。onefile 运行时全部解压到
# sys._MEIPASS 临时目录，app/config.py 已据此解析 ROOT_DIR。
datas = [
    ("assets", "assets"),
    ("app/services/land_mask.b64", "app/services"),
    ("背景图.png", "."),
    ("光标.png", "."),
    ("点击光标.png", "."),
]
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

# 单文件：把全部二进制 / 数据都塞进 EXE，且不使用 COLLECT。
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="WorldCupConsole",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,            # GUI 应用：不弹出命令行黑窗
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="assets/icon/app.ico",
)
