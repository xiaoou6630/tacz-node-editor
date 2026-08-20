import os
import sys
import shutil
import subprocess
import time
import urllib.request
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SOURCE_FILE = PROJECT_ROOT / "源代码（使用前请三联哦😮）" / "使用时请改为.py格式.py"
VENV_DIR = PROJECT_ROOT / "build_venv"
BUILD_DIR = PROJECT_ROOT / "build"
DIST_DIR = PROJECT_ROOT / "dist"
PY38_DIR = PROJECT_ROOT / "build_python38"
EXE_NAME = "ksp_localization_tool_v3.0"
UPX_EXE = PROJECT_ROOT / "upx" / "upx-4.2.2-win64" / "upx.exe"

PY38_EMBED_URL = "https://www.python.org/ftp/python/3.8.10/python-3.8.10-embed-amd64.zip"
GET_PIP_URL = "https://bootstrap.pypa.io/pip/get-pip.py"

PYTHON38_PATHS = [
    r"C:\Python38\python.exe",
    r"C:\Program Files\Python38\python.exe",
    r"C:\Users\{}\AppData\Local\Programs\Python\Python38\python.exe",
]


def banner():
    print()
    print("\033[1;36m" + "=" * 60 + "\033[0m")
    print("\033[1;36m   KSP Localization Tool v3.0 - Build Script\033[0m")
    print("\033[1;36m" + "=" * 60 + "\033[0m")
    print()


def step(msg):
    print(f"\n\033[1;33m>>> {msg}\033[0m")


def ok(msg):
    print(f"  \033[92m✓\033[0m {msg}")


def warn(msg):
    print(f"  \033[93m⚠\033[0m {msg}")


def fail(msg):
    print(f"  \033[91m✗\033[0m {msg}")


def run(cmd, **kwargs):
    return subprocess.run(cmd, check=True, **kwargs)


def find_python38():
    for p in PYTHON38_PATHS:
        path = Path(p.format(os.environ.get("USERNAME", "")))
        if path.exists():
            return path
    try:
        result = subprocess.run(
            ["py", "-3.8", "-c", "import sys; print(sys.executable)"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return Path(result.stdout.strip())
    except Exception:
        pass
    return None


def download_file(url, dest, desc):
    ok(f"Downloading {desc}...")
    try:
        urllib.request.urlretrieve(url, str(dest))
        ok(f"Downloaded: {dest.name}")
        return True
    except Exception as e:
        fail(f"Download failed: {e}")
        return False


def bootstrap_python38():
    py38 = find_python38()
    if py38:
        ok(f"Found Python 3.8: {py38}")
        return py38

    warn("Python 3.8 not installed, downloading embeddable version...")
    py38_exe = PY38_DIR / "python.exe"

    if py38_exe.exists():
        ok(f"Using cached Python 3.8: {py38_exe}")
        return py38_exe

    PY38_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = PY38_DIR / "python-3.8.10-embed-amd64.zip"

    if not zip_path.exists():
        if not download_file(PY38_EMBED_URL, zip_path, "Python 3.8.10 embeddable"):
            sys.exit(1)

    ok("Extracting Python 3.8...")
    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(PY38_DIR)

    pth_file = PY38_DIR / "python38._pth"
    content = pth_file.read_text()
    if "import site" not in content:
        content += "\nimport site\n"
    if "# Lib\\site-packages" in content:
        content = content.replace("# Lib\\site-packages", "Lib\\site-packages")
    elif "Lib\\site-packages" not in content:
        content = content.rstrip() + "\nLib\\site-packages\n"
    pth_file.write_text(content)

    ok("Installing pip...")
    get_pip_path = PY38_DIR / "get-pip.py"
    if not download_file(GET_PIP_URL, get_pip_path, "get-pip.py"):
        sys.exit(1)
    subprocess.run([str(py38_exe), str(get_pip_path)],
                   capture_output=True, timeout=120, check=True)
    ok(f"Python 3.8 ready: {py38_exe}")
    return py38_exe


def setup_environment():
    step("STEP 1: Setup Python 3.8 Environment")

    py38 = bootstrap_python38()

    if VENV_DIR.exists():
        venv_py = VENV_DIR / "Scripts" / "python.exe"
        try:
            r = subprocess.run([str(venv_py), "-c", "import sys; print(sys.version_info[:2])"],
                               capture_output=True, text=True, timeout=10)
            if r.returncode == 0 and r.stdout.strip() == "(3, 8)":
                ok(f"Virtual environment OK: {VENV_DIR}")
            else:
                warn("venv Python version mismatch, recreating...")
                shutil.rmtree(VENV_DIR)
        except Exception:
            warn("venv corrupted, recreating...")
            shutil.rmtree(VENV_DIR)

    if not VENV_DIR.exists():
        ok(f"Creating virtual environment: {VENV_DIR}")
        run([str(py38), "-m", "venv", str(VENV_DIR), "--clear"])

    venv_python = VENV_DIR / "Scripts" / "python.exe"
    venv_pip = VENV_DIR / "Scripts" / "pip.exe"

    ok("Upgrading pip...")
    run([str(venv_python), "-m", "pip", "install", "--upgrade", "pip"],
        capture_output=True)

    ok("Installing PyQt5...")
    run([str(venv_pip), "install", "PyQt5"], capture_output=True)

    ok("Installing PyInstaller...")
    run([str(venv_pip), "install", "pyinstaller"], capture_output=True)

    ok("Environment setup complete")
    return venv_python


def build_exe(venv_python, upx_path=None):
    step("STEP 2: PyInstaller Build")

    if not SOURCE_FILE.exists():
        fail(f"Source file not found: {SOURCE_FILE}")
        sys.exit(1)

    for d in [BUILD_DIR, DIST_DIR]:
        if d.exists():
            shutil.rmtree(d)

    exclude_modules = [
        "tkinter", "unittest", "email", "http", "xml", "pydoc",
        "distutils", "test", "tests", "lib2to3",
        "asyncio", "multiprocessing", "concurrent",
        "urllib", "html", "csv", "bz2", "lzma",
        "json", "plistlib", "uuid", "secrets",
        "numpy", "matplotlib", "PIL", "pillow", "openpyxl",
        "flask", "Flask", "flask_cors", "flask_sock",
        "fastapi", "starlette", "uvicorn",
        "sqlalchemy", "psycopg2", "sqlite3",
        "certifi", "httpx", "aiohttp", "aiosignal", "aiofiles",
        "jsonschema", "referencing", "rpds_py",
        "websocket_client", "websockets", "wsproto",
        "pygments", "textdistance", "pypinyin",
        "pydantic", "pydantic_core", "pydantic_settings",
        "yarl", "multidict", "propcache", "frozenlist",
        "annotated_types", "typing_inspection",
        "greenlet", "markupsafe", "jinja2", "click",
        "pytest", "pluggy", "iniconfig",
        "cffi", "pycparser",
        "hashlib",
        "setuptools", "pkg_resources", "wheel",
        "PySide6", "PySide6_Addons", "PySide6_Essentials",
        "PyQt6", "PyQt6_Addons", "PyQt6_Essentials",
        "shiboken6",
        "PyQt5.QtMultimedia", "PyQt5.QtMultimediaWidgets",
        "PyQt5.QtNetwork", "PyQt5.QtPrintSupport",
        "PyQt5.QtOpenGL", "PyQt5.QtSql", "PyQt5.QtTest",
        "PyQt5.QtWebChannel", "PyQt5.QtWebSockets",
        "PyQt5.QtWebEngine", "PyQt5.QtWebEngineWidgets",
        "PyQt5.QtWebEngineCore",
        "PyQt5.QtDesigner", "PyQt5.QtHelp",
        "PyQt5.QtXml", "PyQt5.QtXmlPatterns",
        "PyQt5.QtBluetooth", "PyQt5.QtNfc",
        "PyQt5.QtSensors", "PyQt5.QtSerialPort",
        "PyQt5.QtPositioning", "PyQt5.QtLocation",
        "PyQt5.QtQuick", "PyQt5.QtQuickWidgets",
        "PyQt5.QtQml", "PyQt5.QtSvg",
    ]

    spec_path = BUILD_DIR / f"{EXE_NAME}.spec"

    exclude_mods_str = ',\n        '.join(repr(m) for m in exclude_modules)
    source_repr = repr(str(SOURCE_FILE))

    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    [{source_repr}],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        {exclude_mods_str},
    ],
    noarchive=False,
    optimize=2,
)
pyz = PYZ(a.pure)

UNWANTED_DLLS = [
    'opengl32sw.dll', 'd3dcompiler_47.dll', 'libEGL.dll', 'libGLESv2.dll',
    'libcrypto-1_1.dll',
    'Qt5Quick', 'Qt5Qml', 'Qt5Svg', 'Qt5Network', 'Qt5DBus',
    'Qt5Designer', 'Qt5Help', 'Qt5Xml', 'Qt5XmlPatterns',
    'Qt5Bluetooth', 'Qt5Nfc', 'Qt5Sensors', 'Qt5SerialPort',
    'Qt5Positioning', 'Qt5Location',
    'qminimal.dll', 'qoffscreen.dll', 'qwebgl.dll', 'qdirect2d.dll',
    'imageformats\\\\', 'iconengines\\\\', 'Qt5PrintSupport',
    'qtwebengine_', 'QtWebEngine', 'Qt5Web',
    'Qt5QmlModels', 'Qt5QuickControls2', 'Qt5QuickTemplates2',
    'Qt5QuickTest',
    'qgif', 'qicns', 'qico', 'qtga', 'qwbmp',
    'qsvg', 'qjpeg', 'qtiff', 'qwebp',
    'Qt5\\\\bin\\\\MSVCP140', 'Qt5\\\\bin\\\\VCRUNTIME140',
    'api-ms-win-crt-',
]
a.binaries = [
    b for b in a.binaries
    if not any(pat in b[0] for pat in UNWANTED_DLLS)
]

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
    name='{EXE_NAME}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx={str(upx_path is not None)},
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
'''
    if upx_path:
        spec_content += f"    upx_dir={repr(str(upx_path.parent))},\n"
    spec_content += ")\n"

    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    spec_path.write_text(spec_content, encoding='utf-8')
    ok(f"Spec file written: {spec_path}")
    ok("DLL filter injected into spec")

    ok(f"Source: {SOURCE_FILE}")
    ok(f"Output: {DIST_DIR / (EXE_NAME + '.exe')}")
    ok(f"Excluding {len(exclude_modules)} Python modules + DLL filter")
    print()

    build_cmd = [
        str(venv_python), "-OO", "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--distpath", str(DIST_DIR),
        "--workpath", str(BUILD_DIR),
        str(spec_path),
    ]

    start = time.time()
    try:
        run(build_cmd, timeout=600)
    except subprocess.TimeoutExpired:
        fail("Build timed out (10 minutes)")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        fail(f"Build failed with code {e.returncode}")
        sys.exit(1)

    elapsed = time.time() - start
    exe_path = DIST_DIR / f"{EXE_NAME}.exe"
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        ok(f"Build success: {EXE_NAME}.exe ({size_mb:.2f} MB, {elapsed:.0f}s)")
        return exe_path
    else:
        fail(f"Exe not found at {exe_path}")
        sys.exit(1)


def compress_exe(exe_path):
    step("STEP 3: UPX Compression")

    if not UPX_EXE.exists():
        warn(f"UPX not found at: {UPX_EXE}")
        warn("Skipping compression. Download from https://upx.github.io/")
        warn(f"  and extract to: {UPX_EXE.parent}")
        return exe_path

    before = exe_path.stat().st_size / (1024 * 1024)
    ok(f"Before: {before:.2f} MB")

    try:
        result = subprocess.run(
            [str(UPX_EXE), "--best", "--force", str(exe_path)],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode == 0:
            after = exe_path.stat().st_size / (1024 * 1024)
            saved = (1 - after / before) * 100
            ok(f"After: {after:.2f} MB (saved {saved:.1f}%)")
        else:
            warn(f"UPX failed: {result.stderr.strip()[:200]}")
    except subprocess.TimeoutExpired:
        warn("UPX timeout, skipping")
    except Exception as e:
        warn(f"UPX error: {e}")

    return exe_path


def summary(exe_path):
    step("BUILD COMPLETE")

    size_mb = exe_path.stat().st_size / (1024 * 1024)
    original = 34.2

    print(f"  Output : {exe_path}")
    print(f"  Size   : {size_mb:.2f} MB")
    if size_mb < original:
        saved = (1 - size_mb / original) * 100
        print(f"  vs 原版: 节省 {saved:.1f}%")
    print()
    print("\033[1;32m  ✓ 打包完成！\033[0m")
    print()


def find_upx():
    if UPX_EXE.exists():
        return UPX_EXE
    for upx_exe in (PROJECT_ROOT / "upx").rglob("upx.exe"):
        return upx_exe
    return None


def main():
    banner()

    upx_path = find_upx()
    venv_python = setup_environment()
    exe_path = build_exe(venv_python, upx_path)
    exe_path = compress_exe(exe_path)
    summary(exe_path)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n中断退出")
        sys.exit(1)
    except Exception as e:
        print(f"\n\033[91m错误: {e}\033[0m")
        import traceback
        traceback.print_exc()
        sys.exit(1)
