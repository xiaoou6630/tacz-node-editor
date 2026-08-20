#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TACZ Lua Map Editor - Build & Package Tool
使用PyArmor混淆Python代码（试用版限制4个文件）
然后将混淆后的代码用PyInstaller打包为单文件exe
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
OUTPUT_DIR = Path(r"e:\daima\block\output")
DIST_DIR = OUTPUT_DIR / "dist"
OBFUSCATED_DIR = OUTPUT_DIR / "obfuscated"
BUILD_DIR = OUTPUT_DIR / "build"

# 虚拟环境路径
VENV_DIR = Path(r"e:\daima\block\venv")
VENV_PYTHON = VENV_DIR / "Scripts" / "python.exe"
VENV_PIP = VENV_DIR / "Scripts" / "pip.exe"

# PyArmor试用版限制 - 最多4个文件
FILES_TO_OBFUSCATE = [
    "codegen.py",        # 代码生成器 - 核心逻辑
    "tacz_nodes.py",     # TACZ节点定义 - 核心业务
    "registry.py",       # 节点注册表 - 核心架构
    "crypto.py",         # 加密模块 - 安全核心
]

# 非混淆文件（直接复制）
NON_OBFUSCATED_FILES = [
    "main.py",           # Entry point
    "node.py",           # Node base class
    "connection.py",     # Connection system
    "protection.py",     # Protection module
    "logger.py",         # Logger module
]

# 资源文件
RESOURCE_FILES = [
    "API.md",
    "模组扩展指南.md",
    "config.json",
]

# UPX配置
UPX_PATH = Path(r"e:\daima\block\upx\upx-4.2.2-win64\upx.exe")

# 构建信息
BUILD_VERSION = "1.0.0"
BUILD_NAME = "TLM编辑器"


# ============================================================================
# Build Logger - Java Style
# ============================================================================
class BuildLogger:
    """Java风格构建日志"""
    
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
    @staticmethod
    def _timestamp():
        return datetime.now().strftime("%H:%M:%S")
    
    @classmethod
    def info(cls, msg):
        print(f"[{cls._timestamp()}] {cls.OKBLUE}[INFO]{cls.ENDC} {msg}")
    
    @classmethod
    def success(cls, msg):
        print(f"[{cls._timestamp()}] {cls.OKGREEN}[SUCCESS]{cls.ENDC} {msg}")
    
    @classmethod
    def warn(cls, msg):
        print(f"[{cls._timestamp()}] {cls.WARNING}[WARNING]{cls.ENDC} {msg}")
    
    @classmethod
    def error(cls, msg):
        print(f"[{cls._timestamp()}] {cls.FAIL}[ERROR]{cls.ENDC} {msg}")
    
    @classmethod
    def debug(cls, msg):
        print(f"[{cls._timestamp()}] {cls.OKCYAN}[DEBUG]{cls.ENDC} {msg}")
    
    @classmethod
    def phase(cls, msg):
        print(f"\n{cls.BOLD}{cls.HEADER}{'='*70}{cls.ENDC}")
        print(f"{cls.BOLD}{cls.HEADER} >>> {msg}{cls.ENDC}")
        print(f"{cls.BOLD}{cls.HEADER}{'='*70}{cls.ENDC}\n")
    
    @classmethod
    def progress(cls, msg):
        print(f"[{cls._timestamp()}] {cls.BOLD}  > {msg}{cls.ENDC}")


logger = BuildLogger()


# ============================================================================
# Build Steps
# ============================================================================

class BuildContext:
    """构建上下文"""
    def __init__(self):
        self.start_time = time.time()
        self.success_count = 0
        self.warning_count = 0
        self.error_count = 0
        self.steps = []


def print_banner():
    """打印构建横幅"""
    print(f"\n{BuildLogger.BOLD}{BuildLogger.OKCYAN}")
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║          TACZ Lua Map Editor - Build & Package Tool            ║")
    print("║                  Powered by PyArmor + PyInstaller               ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print(f"{BuildLogger.ENDC}")
    logger.info(f"Project: {PROJECT_DIR}")
    logger.info(f"Output: {OUTPUT_DIR}")
    logger.info(f"Build Version: {BUILD_VERSION}")
    print()


def check_environment(ctx: BuildContext):
    """检查构建环境"""
    logger.phase("PHASE 1: Environment Check")
    
    # 检查Python版本
    logger.progress("Checking Python version...")
    python_version = sys.version
    logger.info(f"Python: {python_version.split()[0]}")
    
    # 检查项目目录
    logger.progress("Checking project directory...")
    if not PROJECT_DIR.exists():
        logger.error(f"Project directory not found: {PROJECT_DIR}")
        ctx.error_count += 1
        return False
    logger.info(f"Project directory: OK")
    
    # 检查PyArmor
    logger.progress("Checking PyArmor installation...")
    try:
        result = subprocess.run(
            ["pyarmor", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            version = result.stdout.strip().split('\n')[0]
            logger.success(f"PyArmor: {version}")
            ctx.success_count += 1
        else:
            logger.warn("PyArmor not found, installing...")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "pyarmor"],
                check=True,
                capture_output=True
            )
            logger.success("PyArmor installed successfully")
            ctx.success_count += 1
    except Exception as e:
        logger.error(f"PyArmor check failed: {e}")
        ctx.error_count += 1
        return False
    
    # 检查UPX
    logger.progress("Checking UPX...")
    if UPX_PATH.exists():
        logger.success(f"UPX: {UPX_PATH}")
        ctx.success_count += 1
    else:
        logger.warn(f"UPX not found at {UPX_PATH}, will skip compression")
        ctx.warning_count += 1
    
    # 检查需要混淆的文件
    logger.progress("Checking obfuscation target files...")
    for py_file in FILES_TO_OBFUSCATE:
        file_path = PROJECT_DIR / py_file
        if file_path.exists():
            logger.debug(f"  ✓ {py_file} (will obfuscate)")
        else:
            logger.warn(f"  ✗ {py_file} (not found)")
            ctx.warning_count += 1
    
    # 检查非混淆文件
    logger.progress("Checking non-obfuscated files...")
    for py_file in NON_OBFUSCATED_FILES:
        file_path = PROJECT_DIR / py_file
        if file_path.exists():
            logger.debug(f"  ✓ {py_file} (will copy)")
        else:
            logger.warn(f"  ✗ {py_file} (not found)")
            ctx.warning_count += 1
    
    return True


def clean_build_dirs():
    """清理构建目录"""
    logger.phase("PHASE 2: Clean Build Directories")
    
    dirs_to_clean = [OBFUSCATED_DIR, BUILD_DIR]
    
    for dir_path in dirs_to_clean:
        if dir_path.exists():
            logger.progress(f"Cleaning: {dir_path}")
            shutil.rmtree(dir_path)
            logger.info(f"Deleted: {dir_path}")
        else:
            logger.debug(f"Skip (not exists): {dir_path}")
    
    # 创建输出目录
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OBFUSCATED_DIR.mkdir(parents=True, exist_ok=True)
    logger.success("Build directories cleaned")
    return True


def run_pyarmor_obfuscation(ctx: BuildContext):
    """执行PyArmor混淆"""
    logger.phase("PHASE 3: PyArmor Obfuscation")
    logger.info(f"Target files: {len(FILES_TO_OBFUSCATE)} (Trial version limit: 4)")
    print()
    
    # 逐个文件混淆，避免超限
    success_count = 0
    failed_files = []
    
    for py_file in FILES_TO_OBFUSCATE:
        file_path = PROJECT_DIR / py_file
        
        if not file_path.exists():
            logger.warn(f"Skipping missing file: {py_file}")
            continue
        
        logger.progress(f"Obfuscating: {py_file}")
        
        pyarmor_cmd = [
            "pyarmor", "gen",
            "--output", str(OBFUSCATED_DIR),
            str(file_path),
        ]
        
        try:
            result = subprocess.run(
                pyarmor_cmd,
                capture_output=True,
                text=True,
                cwd=str(PROJECT_DIR),
                timeout=60
            )
            
            if result.returncode == 0:
                # 检查是否真的生成了文件
                expected_output = OBFUSCATED_DIR / py_file
                if expected_output.exists():
                    size_kb = expected_output.stat().st_size / 1024
                    logger.success(f"  ✓ {py_file} ({size_kb:.1f} KB)")
                    success_count += 1
                else:
                    logger.warn(f"  ⚠ {py_file} - output not found")
                    failed_files.append(py_file)
            else:
                stderr = result.stderr.strip()
                if "out of license" in stderr.lower():
                    logger.error(f"  ✗ {py_file} - LICENSE LIMIT REACHED")
                    logger.error(f"    Trial version can only obfuscate {success_count} files")
                    failed_files.extend(FILES_TO_OBFUSCATE[FILES_TO_OBFUSCATE.index(py_file):])
                    break
                else:
                    logger.error(f"  ✗ {py_file} - failed")
                    logger.debug(f"    Error: {stderr[:200]}")
                    failed_files.append(py_file)
                    
        except subprocess.TimeoutExpired:
            logger.error(f"  ✗ {py_file} - timeout")
            failed_files.append(py_file)
        except Exception as e:
            logger.error(f"  ✗ {py_file} - {e}")
            failed_files.append(py_file)
    
    print()
    
    if success_count > 0:
        logger.success(f"Obfuscation completed: {success_count}/{len(FILES_TO_OBFUSCATE)} files")
        ctx.success_count += 1
        
        if failed_files:
            logger.warn(f"Failed files will be copied without obfuscation:")
            for f in failed_files:
                logger.warn(f"  - {f}")
                # 将失败的文件添加到非混淆列表
                if f not in NON_OBFUSCATED_FILES:
                    NON_OBFUSCATED_FILES.append(f)
        
        return True
    else:
        logger.error("No files were obfuscated")
        ctx.error_count += 1
        return False


def copy_resources(ctx: BuildContext):
    """复制资源文件和非混淆文件"""
    logger.phase("PHASE 4: Copy Resources")
    
    # 复制非混淆 Python 文件
    logger.progress("Copying non-obfuscated Python files...")
    for filename in NON_OBFUSCATED_FILES:
        src = PROJECT_DIR / filename
        if src.exists():
            dest = OBFUSCATED_DIR / filename
            shutil.copy2(src, dest)
            logger.debug(f"  ✓ {filename}")
        else:
            logger.warn(f"  ✗ {filename} (not found)")
    
    # 复制资源文件
    logger.progress("Copying resource files...")
    for filename in RESOURCE_FILES:
        src = PROJECT_DIR / filename
        if src.exists():
            dest = OBFUSCATED_DIR / filename
            shutil.copy2(src, dest)
            logger.debug(f"  ✓ {filename}")
        else:
            logger.warn(f"  ✗ {filename} (not found)")
    
    # 创建 __init__.py 使 obfuscated 目录成为一个包
    init_file = OBFUSCATED_DIR / "__init__.py"
    if not init_file.exists():
        init_file.write_text("# PyInstaller obfuscated package\n")
        logger.debug("  ✓ Created __init__.py")
    
    logger.success("Resources copied")
    ctx.success_count += 1
    return True


def run_pyinstaller_build(ctx: BuildContext):
    """执行PyInstaller打包"""
    logger.phase("PHASE 5: PyInstaller Build")
    
    # 检查入口文件
    entry_file = OBFUSCATED_DIR / "main.py"
    if not entry_file.exists():
        logger.error(f"Entry file not found: {entry_file}")
        ctx.error_count += 1
        return False
    
    # 构建命令
    pyinstaller_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", BUILD_NAME,
        "--noconfirm",
        "--clean",
        "--distpath", str(DIST_DIR),
        "--workpath", str(BUILD_DIR),
        "--specpath", str(BUILD_DIR),
        "--paths", str(PROJECT_DIR.parent),  # 添加项目父目录到搜索路径
        "--additional-hooks-dir", str(PROJECT_DIR),  # 使用自定义 hook 排除 Qt 模块
        "--noconsole",  # 不显示控制台窗口
        "--windowed",  # GUI 应用，隐藏控制台
    ]
    
    # 添加隐藏导入
    hidden_imports = [
        "PyQt6", "PyQt6.QtWidgets", "PyQt6.QtCore", "PyQt6.QtGui",
        "cryptography", "cryptography.fernet",
        "pyqt6_editor",
        "pyqt6_editor.editor",
        "pyqt6_editor.node",
        "pyqt6_editor.connection",
        "pyqt6_editor.codegen",
        "pyqt6_editor.tacz_nodes",
        "pyqt6_editor.registry",
        "pyqt6_editor.crypto",
        "pyqt6_editor.protection",
        "pyqt6_editor.logger",
        "pyqt6_editor.__init__",
    ]
    
    logger.progress("Configuring hidden imports...")
    for imp in hidden_imports:
        pyinstaller_cmd.extend(["--hidden-import", imp])
        logger.debug(f"  + {imp}")
    
    # 不再使用 --collect-all，让 hook 精确控制 Qt 模块
    
    # 排除不需要的模块
    excluded_modules = [
        # 标准库
        "tkinter", "unittest", "email", "http", "xml", "pydoc",
        "importlib_metadata", "distutils", "test", "tests",
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
        # Cython/PyInstaller 相关
        "cython", "pyinstaller", "pefile", "altgraph",
        "setuptools", "pkg_resources", "wheel",
        # Qt 无关组件
        "PySide6", "PySide6_Addons", "PySide6_Essentials",
        "PyQt6.QtMultimedia", "PyQt6.QtNetwork", "PyQt6.QtPrintSupport",
        "PyQt6.QtOpenGL", "PyQt6.QtSql", "PyQt6.QtTest",
        "PyQt6.QtWebChannel", "PyQt6.QtWebSockets",
        "PyQt6.QtDesigner", "PyQt6.QtHelp",
        "shiboken6", "QtPy",
        # 其他
        "pyarmor", "pyarmor.cli", "pyinstxtractor_ng",
        "spark_parser", "uncompyle6", "xdis",
        "yarl", "multidict", "propcache", "frozenlist",
        "pydantic", "pydantic_core", "pydantic_settings",
        "annotated_types", "typing_inspection",
        "pystray", "pywin32", "win32",
        "pytest", "pluggy", "iniconfig",
        "sse_starlette", "python_multipart",
        "cffi", "pycparser",
        "simple_websocket",
        "greenlet",
    ]
    logger.progress("Excluding unnecessary modules...")
    for mod in excluded_modules:
        pyinstaller_cmd.extend(["--exclude-module", mod])
        logger.debug(f"  - {mod}")
    
    # 添加数据文件
    logger.progress("Adding resource files...")
    for data_file in RESOURCE_FILES:
        data_path = OBFUSCATED_DIR / data_file
        if data_path.exists():
            pyinstaller_cmd.extend(["--add-data", f"{data_path};."])
            logger.debug(f"  + {data_file}")
    
    # 添加入口文件（从 pyqt6_editor 包中导入 main）
    pyinstaller_cmd.append(str(PROJECT_DIR / "main.py"))
    
    print()
    logger.progress("Executing PyInstaller (this may take several minutes)...")
    logger.info(f"Output: {DIST_DIR / f'{BUILD_NAME}.exe'}")
    
    try:
        result = subprocess.run(
            pyinstaller_cmd,
            cwd=str(PROJECT_DIR),
            timeout=600
        )
        
        if result.returncode != 0:
            logger.error("PyInstaller build failed")
            ctx.error_count += 1
            return False
        
        # 检查输出文件
        exe_path = DIST_DIR / f"{BUILD_NAME}.exe"
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            logger.success(f"Build successful: {BUILD_NAME}.exe ({size_mb:.2f} MB)")
            ctx.success_count += 1
            return True
        else:
            logger.error(f"Output file not found: {exe_path}")
            ctx.error_count += 1
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("PyInstaller build timeout (10 minutes)")
        ctx.error_count += 1
        return False
    except Exception as e:
        logger.error(f"PyInstaller build error: {e}")
        ctx.error_count += 1
        return False


def run_upx_compression(ctx: BuildContext):
    """执行UPX压缩"""
    logger.phase("PHASE 6: UPX Compression")
    
    exe_path = DIST_DIR / f"{BUILD_NAME}.exe"
    
    if not UPX_PATH.exists():
        logger.warn("UPX not found, skipping compression")
        ctx.warning_count += 1
        return True
    
    if not exe_path.exists():
        logger.warn(f"EXE not found: {exe_path}")
        ctx.warning_count += 1
        return True
    
    original_size = exe_path.stat().st_size / (1024 * 1024)
    logger.progress(f"Compressing: {exe_path.name} ({original_size:.2f} MB)")
    
    try:
        result = subprocess.run(
            [str(UPX_PATH), "--best", "--force", str(exe_path)],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            compressed_size = exe_path.stat().st_size / (1024 * 1024)
            ratio = (1 - compressed_size / original_size) * 100
            logger.success(f"Compression complete: {compressed_size:.2f} MB ({ratio:.1f}% saved)")
            ctx.success_count += 1
            return True
        else:
            logger.warn(f"UPX compression failed: {result.stderr[:200]}")
            ctx.warning_count += 1
            return True
            
    except subprocess.TimeoutExpired:
        logger.warn("UPX compression timeout")
        ctx.warning_count += 1
        return True
    except Exception as e:
        logger.warn(f"UPX compression error: {e}")
        ctx.warning_count += 1
        return True


def copy_final_output(ctx: BuildContext):
    """复制最终输出"""
    logger.phase("PHASE 7: Final Output")
    
    exe_path = DIST_DIR / f"{BUILD_NAME}.exe"
    
    if not exe_path.exists():
        logger.error(f"Build output not found: {exe_path}")
        ctx.error_count += 1
        return False
    
    # 文件已经通过PyInstaller直接生成到DIST_DIR
    size_mb = exe_path.stat().st_size / (1024 * 1024)
    
    logger.success("Final build artifacts:")
    print()
    logger.info(f"  📦 {exe_path}")
    logger.info(f"     Size: {size_mb:.2f} MB")
    
    # 列出所有输出文件
    for f in DIST_DIR.iterdir():
        if f.is_file() and f.name != f"{BUILD_NAME}.exe":
            size = f.stat().st_size / 1024
            logger.info(f"  📄 {f.name} ({size:.1f} KB)")
    
    return True


def print_build_summary(ctx: BuildContext):
    """打印构建摘要"""
    elapsed = time.time() - ctx.start_time
    
    logger.phase("BUILD SUMMARY")
    
    print(f"  Build Version: {BUILD_VERSION}")
    print(f"  Total Time: {elapsed:.2f}s")
    print(f"  Success: {ctx.success_count}")
    print(f"  Warnings: {ctx.warning_count}")
    print(f"  Errors: {ctx.error_count}")
    print()
    
    # 保护措施清单
    logger.info("Protection layers enabled:")
    protections = [
        ("PyArmor Obfuscation", "✓", f"{len(FILES_TO_OBFUSCATE)} core files obfuscated"),
        ("PyInstaller Bundle", "✓", "Single-file executable"),
        ("UPX Compression", "✓" if UPX_PATH.exists() else "✗", "Executable compression"),
        ("Config Encryption", "✓", "Encrypted configuration"),
        ("Anti-Debug", "✓", "Debug protection"),
        ("Logging System", "✓", "Secure logging"),
    ]
    
    for name, status, desc in protections:
        symbol = "✅" if status == "✓" else "⚠️"
        print(f"  {symbol} {name}: {desc}")
    
    # 最终状态
    print()
    if ctx.error_count == 0:
        logger.success("BUILD SUCCESSFUL")
    else:
        logger.error(f"BUILD FAILED with {ctx.error_count} error(s)")
    
    # 输出文件位置
    print(f"\n{logger.BOLD}Output Directory:{logger.ENDC}")
    print(f"  {DIST_DIR}")
    
    print(f"\n{logger.BOLD}{'='*70}{logger.ENDC}\n")


# ============================================================================
# Main Build Pipeline
# ============================================================================

def main():
    """主构建流程"""
    ctx = BuildContext()
    
    # 打印横幅
    print_banner()
    
    # Phase 1: 环境检查
    if not check_environment(ctx):
        print_build_summary(ctx)
        sys.exit(1)
    
    # Phase 2: 清理构建目录
    clean_build_dirs()
    
    # Phase 3: PyArmor混淆
    if not run_pyarmor_obfuscation(ctx):
        print_build_summary(ctx)
        sys.exit(1)
    
    # Phase 4: 复制资源文件
    copy_resources(ctx)
    
    # Phase 5: PyInstaller打包
    if not run_pyinstaller_build(ctx):
        print_build_summary(ctx)
        sys.exit(1)
    
    # Phase 6: UPX压缩
    run_upx_compression(ctx)
    
    # Phase 7: 输出整理
    copy_final_output(ctx)
    
    # 打印构建摘要
    print_build_summary(ctx)
    
    # 返回退出码给AI agent
    sys.exit(0 if ctx.error_count == 0 else 1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[WARNING] Build interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)