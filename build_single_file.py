#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TLM Editor - Build & Package Tool (MIT Open Source)
直接使用 PyInstaller 打包为单文件 exe

体积优化策略（参考业界最佳实践）：
1. 通过 .spec 文件精确控制构建，过滤不需要的 DLL
2. -OO 优化：去除 docstring / assert
3. DLL 白名单：删掉 opengl32sw.dll (~15MB)，不用的 Qt 组件
4. QM 翻译文件过滤
5. 移除 PyArmor / cryptography（开源无需保护）
"""

import os
import sys
import shutil
import subprocess
import time
from pathlib import Path
from datetime import datetime


# ============================================================================
# Configuration
# ============================================================================
PROJECT_DIR = Path(r"e:\daima\block\pyqt6_editor")
PROJECT_ROOT = PROJECT_DIR.parent
OUTPUT_DIR = Path(r"e:\daima\block\output")
DIST_DIR = OUTPUT_DIR / "dist"
BUILD_DIR = OUTPUT_DIR / "build"

VENV_DIR = Path(r"e:\daima\block\venv")
UPX_PATH = Path(r"e:\daima\block\upx\upx-4.2.2-win64\upx.exe")

BUILD_VERSION = "2.0.0"
BUILD_NAME = "TLM编辑器"


# ============================================================================
# Logger
# ============================================================================
class L:
    H = '\033[95m'; B = '\033[94m'; C = '\033[96m'; G = '\033[92m'
    Y = '\033[93m'; R = '\033[91m'; X = '\033[0m'; BD = '\033[1m'

    @staticmethod
    def _ts(): return datetime.now().strftime("%H:%M:%S")
    @classmethod
    def info(cls, m): print(f"[{cls._ts()}] {cls.B}[INFO]{cls.X} {m}")
    @classmethod
    def ok(cls, m): print(f"[{cls._ts()}] {cls.G}[OK]{cls.X} {m}")
    @classmethod
    def warn(cls, m): print(f"[{cls._ts()}] {cls.Y}[WARN]{cls.X} {m}")
    @classmethod
    def err(cls, m): print(f"[{cls._ts()}] {cls.R}[ERR]{cls.X} {m}")
    @classmethod
    def step(cls, m): print(f"\n{cls.BD}{cls.H}{'='*60}{cls.X}")
    @classmethod
    def phase(cls, m): print(f"\n{cls.BD}{cls.C}>>> {m}{cls.X}")


# ============================================================================
# Build
# ============================================================================

def clean():
    L.step("STEP 1: Clean")
    for d in [DIST_DIR, BUILD_DIR]:
        if d.exists():
            L.phase(f"Removing {d.name}...")
            try:
                shutil.rmtree(d)
            except PermissionError:
                L.warn("File locked, retrying after rename...")
                import tempfile
                time.sleep(1)
                try:
                    shutil.rmtree(d)
                except PermissionError:
                    # 改名再删
                    tmp = Path(tempfile.gettempdir()) / f"old_{d.name}_{int(time.time())}"
                    L.warn(f"Moving to: {tmp}")
                    shutil.move(str(d), str(tmp))
                    try:
                        shutil.rmtree(tmp, ignore_errors=True)
                    except Exception:
                        pass
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    L.ok("Cleaned")


def build():
    L.step("STEP 2: PyInstaller Build (Spec + DLL Filter)")

    entry = PROJECT_DIR / "main.py"
    if not entry.exists():
        L.err(f"Entry not found: {entry}")
        sys.exit(1)

    # ============================================================
    # 排除的 Python 模块
    # ============================================================
    excludes = [
        # 标准库
        "tkinter", "unittest", "pydoc",
        "distutils", "test", "tests", "lib2to3",
        "asyncio", "multiprocessing", "concurrent",
        "urllib", "html", "csv", "bz2", "lzma",
        "plistlib", "secrets",
        "email", "http", "xml",
        "importlib_metadata",
        # 加密/保护（开源版不需要）
        "cryptography", "pyarmor", "pyarmor.cli",
        "pyinstxtractor_ng", "spark_parser", "uncompyle6", "xdis",
        # 环境中无关包
        "numpy", "matplotlib", "PIL", "pillow", "openpyxl",
        "flask", "Flask", "flask_cors", "flask_sock",
        "fastapi", "starlette", "uvicorn", "mcp",
        "sqlalchemy", "psycopg2", "sqlite3",
        "ryven", "ryvencore", "ryvencore_qt",
        "pyparsing", "fonttools", "contourpy",
        "certifi", "httpx", "aiohttp", "aiosignal", "aiofiles",
        "jsonschema", "referencing", "rpds_py",
        "websocket_client", "websockets", "wsproto",
        "pygments", "textdistance", "pypinyin",
        "waitress", "watchfiles", "blinker",
        "phone_mcp", "waiting",
        "cython", "pefile", "altgraph",
        "setuptools", "pkg_resources", "wheel",
        "pytest", "pluggy", "iniconfig",
        "pydantic", "pydantic_core", "pydantic_settings",
        "annotated_types", "typing_inspection",
        "markupsafe", "jinja2", "click", "greenlet",
        "pystray", "pywin32", "win32",
        "sse_starlette", "python_multipart",
        "cffi", "pycparser", "simple_websocket",
        "yarl", "multidict", "propcache", "frozenlist",
        # Qt 无关组件
        "PySide6", "PySide6_Addons", "PySide6_Essentials",
        "shiboken6", "QtPy",
        "PyQt6.QtMultimedia", "PyQt6.QtMultimediaWidgets",
        "PyQt6.QtNetwork", "PyQt6.QtPrintSupport",
        "PyQt6.QtOpenGL", "PyQt6.QtSql", "PyQt6.QtTest",
        "PyQt6.QtWebChannel", "PyQt6.QtWebSockets",
        "PyQt6.QtWebEngine", "PyQt6.QtWebEngineWidgets",
        "PyQt6.QtWebEngineCore",
        "PyQt6.QtDesigner", "PyQt6.QtHelp",
        "PyQt6.QtXml", "PyQt6.QtXmlPatterns",
        "PyQt6.QtBluetooth", "PyQt6.QtNfc",
        "PyQt6.QtSensors", "PyQt6.QtSerialPort",
        "PyQt6.QtPositioning",
        "PyQt6.QtQuick", "PyQt6.QtQuickWidgets",
        "PyQt6.QtQml",
    ]

    # ============================================================
    # DLL 黑名单（打包后删除，不减白不减）
    # ============================================================
    unwanted_dlls = [
        # 软件渲染器 (~15MB，PyQt6 自带但根本不用)
        'opengl32sw.dll',
        # D3D 编译器 (~3MB)
        'd3dcompiler_47.dll',
        # 图形加速（GUI 不需要）
        'libEGL.dll', 'libGLESv2.dll',
        # 加密库（已移除 cryptography）
        'libcrypto-1_1.dll',
        # Qt 不需要的组件
        'Qt6Quick', 'Qt6Qml', 'Qt6Svg', 'Qt6Network', 'Qt6DBus',
        'Qt6Designer', 'Qt6Help', 'Qt6Xml',
        'Qt6Bluetooth', 'Qt6Nfc', 'Qt6Sensors', 'Qt6SerialPort',
        'Qt6Positioning',
        # Qt 最小化平台插件
        'qminimal.dll', 'qoffscreen.dll', 'qwebgl.dll', 'qdirect2d.dll',
        # 图标引擎
        'iconengines\\\\',
        # 打印支持
        'Qt6PrintSupport',
        # Web Engine（~60MB，不要）
        'qtwebengine_', 'QtWebEngine', 'Qt6Web',
        # QML 模型
        'Qt6QmlModels', 'Qt6QuickControls2', 'Qt6QuickTemplates2',
        'Qt6QuickTest',
        # 不需要的图片格式
        'qgif', 'qicns', 'qico', 'qtga', 'qwbmp',
        'qsvg', 'qjpeg', 'qtiff', 'qwebp',
        # MSVC 运行库（系统自带）
        'MSVCP140', 'VCRUNTIME140',
        'api-ms-win-crt-',
        # 音频编解码（GUI 编辑器不用）
        'avcodec-', 'avformat-', 'avutil-', 'swscale-',
        'concrt140.dll',
    ]

    # ============================================================
    # 生成 .spec 文件
    # ============================================================
    exclude_str = ',\n        '.join(repr(m) for m in excludes)
    src_repr = repr(str(entry))

    spec = f'''# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    [{src_repr}],
    pathex=[{repr(str(PROJECT_ROOT))}],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[{repr(str(PROJECT_DIR))}],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        {exclude_str},
    ],
    noarchive=False,
    optimize=2,
)
pyz = PYZ(a.pure)

# DLL 过滤：删掉不需要的 DLL 和 imageformats
UNWANTED_DLLS = {repr(unwanted_dlls)}
a.binaries = [
    b for b in a.binaries
    if not any(pat in b[0] for pat in UNWANTED_DLLS)
]

# 删掉 Qt 翻译文件 (.qm)
a.datas = [
    d for d in a.datas
    if not d[0].endswith('.qm')
]

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='{BUILD_NAME}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx={str(UPX_PATH.exists())},
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    upx_dir={repr(str(UPX_PATH.parent)) if UPX_PATH.exists() else 'None'},
)
'''

    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    spec_path = BUILD_DIR / f"{BUILD_NAME}.spec"
    spec_path.write_text(spec, encoding='utf-8')
    L.ok(f"Spec written: {spec_path}")
    L.ok(f"DLL filter: {len(unwanted_dlls)} patterns")

    # ============================================================
    # 执行 PyInstaller
    # ============================================================
    venv_python = VENV_DIR / "Scripts" / "python.exe"
    python_exe = venv_python if venv_python.exists() else sys.executable

    cmd = [
        str(python_exe), "-OO", "-m", "PyInstaller",
        "--noconfirm", "--clean",
        "--distpath", str(DIST_DIR),
        "--workpath", str(BUILD_DIR),
        str(spec_path),
    ]

    L.phase(f"Building with {python_exe.name} -OO...")
    L.info(f"Source: {entry}")
    L.info(f"Output: {DIST_DIR}/{BUILD_NAME}.exe")
    L.info(f"Excluded: {len(excludes)} Python modules + {len(unwanted_dlls)} DLL patterns")
    print()

    start = time.time()
    try:
        result = subprocess.run(cmd, cwd=str(PROJECT_DIR), timeout=600)
        if result.returncode != 0:
            L.err("PyInstaller failed")
            sys.exit(1)
    except subprocess.TimeoutExpired:
        L.err("Build timeout (10 min)")
        sys.exit(1)

    elapsed = time.time() - start
    exe_path = DIST_DIR / f"{BUILD_NAME}.exe"

    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        L.ok(f"Build OK: {BUILD_NAME}.exe ({size_mb:.2f} MB, {elapsed:.0f}s)")
        return exe_path
    else:
        L.err(f"Exe not found: {exe_path}")
        sys.exit(1)


def compress(exe_path):
    L.step("STEP 3: UPX Compression")

    if not UPX_PATH.exists():
        L.warn(f"UPX not found: {UPX_PATH}")
        return

    before = exe_path.stat().st_size / (1024 * 1024)
    L.phase(f"Before: {before:.2f} MB")

    try:
        r = subprocess.run(
            [str(UPX_PATH), "--ultra-brute", "--force", str(exe_path)],
            capture_output=True, text=True, timeout=300,
        )
        if r.returncode == 0:
            after = exe_path.stat().st_size / (1024 * 1024)
            saved = (1 - after / before) * 100
            L.ok(f"After: {after:.2f} MB (saved {saved:.1f}%)")
        else:
            L.warn(f"UPX failed: {r.stderr.strip()[:200]}")
    except subprocess.TimeoutExpired:
        L.warn("UPX timeout")
    except Exception as e:
        L.warn(f"UPX error: {e}")


def summary(exe_path):
    L.step("BUILD COMPLETE")
    size_mb = exe_path.stat().st_size / (1024 * 1024)
    old_size = 39.0  # 旧版大小
    print(f"  Output : {exe_path}")
    print(f"  Size   : {size_mb:.2f} MB")
    if size_mb < old_size:
        print(f"  vs 旧版: 节省 {(1 - size_mb / old_size) * 100:.1f}%")
    print()
    print("\033[1;32m  ✓ 打包完成！\033[0m")
    print()


# ============================================================================
# Main
# ============================================================================
def main():
    print(f"\n{L.BD}{L.C}")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║     TLM Editor - Build Tool (MIT)                       ║")
    print("║     PyInstaller + Spec + DLL Filter + UPX               ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"{L.X}")

    clean()
    exe_path = build()
    compress(exe_path)
    summary(exe_path)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n中断退出")
        sys.exit(1)
    except Exception as e:
        print(f"\n\033[91m错误: {e}\033[0m")
        import traceback
        traceback.print_exc()
        sys.exit(1)
