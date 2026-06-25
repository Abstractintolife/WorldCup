@echo off
REM ============================================================================
REM  世界杯赛事终端 —— Windows 单文件打包（Nuitka）
REM
REM  产物：build_nuitka\WorldCupConsole.exe —— 单个 exe，编译成原生机器码，
REM        没有可被反编译的 .py/.pyc 源码（防盗用）。分发时只需这一个文件。
REM
REM  前置要求（只需装一次）：
REM    1) Python 3.12 或 3.13（qasync 暂不支持 3.14）
REM    2) 项目依赖：       python -m pip install -r requirements.txt
REM    3) Nuitka：         python -m pip install nuitka
REM    4) C 编译器：首次运行 Nuitka 会自动下载 MinGW64（已加 --assume-yes-for-downloads
REM       自动同意）；也可改用已安装的 MSVC（Visual Studio Build Tools）。
REM
REM  用法：在仓库根目录双击本脚本，或在命令行执行  scripts\build_windows_nuitka.bat
REM ============================================================================
setlocal
cd /d "%~dp0\.."

python -m nuitka ^
  --standalone ^
  --onefile ^
  --enable-plugin=pyqt6 ^
  --assume-yes-for-downloads ^
  --windows-console-mode=disable ^
  --windows-icon-from-ico=assets\icon\app.ico ^
  --include-data-dir=assets=assets ^
  --include-data-files=背景图.png=背景图.png ^
  --include-data-files=光标.png=光标.png ^
  --include-data-files=点击光标.png=点击光标.png ^
  --include-data-files=app\services\land_mask.b64=app\services\land_mask.b64 ^
  --include-package=pypinyin ^
  --include-package=h2 ^
  --include-package=hpack ^
  --include-package=hyperframe ^
  --include-package-data=certifi ^
  --output-dir=build_nuitka ^
  --output-filename=WorldCupConsole.exe ^
  --company-name="kiro" ^
  --product-name="FIFA World Cup Console 2026" ^
  --file-version=1.0.0 ^
  --product-version=1.0.0 ^
  main.py

echo.
echo ============================================================================
echo  打包完成。单文件 exe 位于： build_nuitka\WorldCupConsole.exe
echo  分发时只需这一个文件。首次启动稍慢（onefile 需先解压到临时目录）。
echo ============================================================================
endlocal
