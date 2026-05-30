#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TACZ Lua Map Editor - Nuitka Build & Package Tool
使用 Nuitka 将 Python 代码编译为原生 C++ 再编译为 exe
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
DIST_DIR = OUTPUT_DIR / "nuitka_dist"
BUILD_DIR = OUTPUT_DIR / "nuitka_build"

BUILD_VERSION = "1.0.0"
BUILD_NAME = "TLM编辑器"

# MSVC 编译器路径
MSVC_BIN = Path(r"e:\c\VC\Tools\MSVC\14.50.35717\bin\Hostx64\x64")
MSVC_INCLUDE = Path(r"e:\c\VC\Tools\MSVC\14.50.35717\include")
MSVC_LIB = Path(r"e:\c\VC\Tools\MSVC\14.50.35717\lib\x64")

# Windows SDK
WIN_SDK_ROOT = Path(r"C:\Program Files (x86)\Windows Kits\10")
WIN_SDK_INCLUDES = [
    WIN_SDK_ROOT / "Include" / "10.0.26100.0" / "um",
    WIN_SDK_ROOT / "Include" / "10.0.26100.0" / "shared",
    WIN_SDK_ROOT / "Include" / "10.0.26100.0" / "ucrt",
]
WIN_SDK_LIBS = [
    WIN_SDK_ROOT / "Lib" / "10.0.26100.0" / "um" / "x64",
    WIN_SDK_ROOT / "Lib" / "10.0.26100.0" / "ucrt" / "x64",
]

# 资源文件
RESOURCE_FILES = [
    "API.md",
    "模组扩展指南.md",
    "config.json",
]

# UPX 配置
UPX_PATH = Path(r"e:\daima\block\upx\upx-4.2.2-win64\upx.exe")


# ============================================================================
# Build Logger
# ============================================================================
class BuildLogger:
    """Java 风格构建日志"""
    
    def __init__(self):
        self.start_time = time.time()
        # 确保 UTF-8 输出
        if sys.stdout.encoding != 'utf-8':
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if sys.stderr.encoding != 'utf-8':
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    
    def phase(self, msg):
        print(f"\n{'='*70}")
        print(f" >>> {msg}")
        print(f"{'='*70}\n")
    
    def progress(self, msg):
        print(f"  > {msg}")
    
    def debug(self, msg):
        print(f"    [DEBUG] {msg}")
    
    def success(self, msg):
        print(f"  [SUCCESS] {msg}")
    
    def warn(self, msg):
        print(f"  [WARNING] {msg}")
    
    def error(self, msg):
        print(f"  [ERROR] {msg}")
    
    def info(self, msg):
        print(f"    [INFO] {msg}")
    
    def elapsed(self):
        return time.time() - self.start_time


logger = BuildLogger()


# ============================================================================
# Build Steps
# ============================================================================

def clean_directories():
    """清理构建目录"""
    logger.phase("PHASE 1: Clean Build Directories")
    
    for d in [DIST_DIR, BUILD_DIR]:
        if d.exists():
            logger.progress(f"Cleaning: {d}")
            shutil.rmtree(d)
            logger.info(f"Deleted: {d}")
        else:
            d.mkdir(parents=True, exist_ok=True)
    
    logger.success("Build directories cleaned")
    return True


def copy_resources():
    """复制资源文件到构建目录"""
    logger.phase("PHASE 2: Copy Resources")
    
    for filename in RESOURCE_FILES:
        src = PROJECT_DIR / filename
        dest = PROJECT_DIR / filename
        if src.exists():
            logger.debug(f"  ✓ {filename}")
    
    logger.success("Resources ready")
    return True


def run_nuitka_build():
    """执行 Nuitka 编译"""
    logger.phase("PHASE 3: Nuitka Build")
    
    entry = PROJECT_DIR / "main.py"
    if not entry.exists():
        logger.error(f"Entry file not found: {entry}")
        return False
    
    # 构建 Nuitka 命令（standalone + onefile）
    cmd = [
        sys.executable, "-m", "nuitka",
        "--standalone",
        "--onefile",
        "--windows-console-mode=disable",
        f"--output-dir={DIST_DIR}",
        f"--output-filename={BUILD_NAME}.exe",
        "--assume-yes-for-downloads",
        "--msvc=latest",
        "--include-package=pyqt6_editor",
        f"--include-data-dir={PROJECT_DIR}=pyqt6_editor",
        # 包含 cryptography 和 PyQt6
        "--include-package=cryptography",
        "--include-package=PyQt6",
        # 排除不需要的模块
        "--nofollow-import-to=tkinter",
        "--nofollow-import-to=unittest",
        "--nofollow-import-to=test",
        "--nofollow-import-to=pytest",
        "--nofollow-import-to=numpy",
        "--nofollow-import-to=matplotlib",
        "--nofollow-import-to=PIL",
        "--nofollow-import-to=flask",
        "--nofollow-import-to=fastapi",
        "--nofollow-import-to=sqlalchemy",
        "--nofollow-import-to=pygments",
        # 编译优化
        "--lto=yes",
        "--remove-output",
        str(entry),
    ]
    
    logger.progress("Executing Nuitka build (this may take 10-30 minutes)...")
    logger.info(f"Output: {DIST_DIR / f'{BUILD_NAME}.exe'}")
    logger.info(f"Entry: {entry}")
    
    try:
        result = subprocess.run(
            cmd,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=3600,
            env=os.environ.copy(),
            # 从项目父目录运行，这样 Nuitka 能找到 pyqt6_editor 包
            cwd=str(PROJECT_DIR.parent),
            # 实时输出到控制台
            stdout=None,
            stderr=None,
        )
        
        if result.returncode == 0:
            exe_path = DIST_DIR / f"{BUILD_NAME}.exe"
            if not exe_path.exists():
                # Nuitka onefile 输出可能在子目录
                for p in DIST_DIR.rglob("*.exe"):
                    if BUILD_NAME in p.name:
                        exe_path = p
                        break
            
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                logger.success(f"Build successful: {BUILD_NAME}.exe ({size_mb:.2f} MB)")
                return True
            else:
                logger.error(f"EXE not found after build")
                logger.debug(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
                return False
        else:
            logger.error(f"Nuitka build failed (exit code {result.returncode})")
            if result.stderr:
                logger.debug(result.stderr[-1000:])
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("Nuitka build timeout (30 minutes)")
        return False
    except Exception as e:
        logger.error(f"Nuitka build error: {e}")
        return False


def run_upx_compression():
    """执行 UPX 压缩"""
    logger.phase("PHASE 4: UPX Compression")
    
    exe_path = DIST_DIR / f"{BUILD_NAME}.exe"
    
    if not UPX_PATH.exists():
        logger.warn("UPX not found, skipping compression")
        return True
    
    if not exe_path.exists():
        logger.warn(f"EXE not found: {exe_path}")
        return True
    
    original_size = exe_path.stat().st_size / (1024 * 1024)
    logger.progress(f"Compressing: {exe_path.name} ({original_size:.2f} MB)")
    
    try:
        result = subprocess.run(
            [str(UPX_PATH), "--best", "--force", str(exe_path)],
            capture_output=True,
            text=True,
            timeout=180
        )
        
        if result.returncode == 0:
            compressed_size = exe_path.stat().st_size / (1024 * 1024)
            ratio = (1 - compressed_size / original_size) * 100
            logger.success(f"Compression complete: {compressed_size:.2f} MB ({ratio:.1f}% saved)")
            return True
        else:
            logger.warn(f"UPX compression failed: {result.stderr[:200]}")
            return True
            
    except subprocess.TimeoutExpired:
        logger.warn("UPX compression timeout")
        return True
    except Exception as e:
        logger.warn(f"UPX compression error: {e}")
        return True


def print_summary():
    """打印构建摘要"""
    logger.phase("BUILD SUMMARY")
    
    exe_path = DIST_DIR / f"{BUILD_NAME}.exe"
    
    print(f"  Build Version: {BUILD_VERSION}")
    print(f"  Total Time: {logger.elapsed():.2f}s")
    print()
    
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        logger.success(f"Output: {exe_path}")
        logger.info(f"Size: {size_mb:.2f} MB")
    else:
        logger.error("Build failed - no output file")


# ============================================================================
# Main
# ============================================================================
def main():
    print()
    print("╔" + "═"*68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "     TACZ Lua Map Editor - Nuitka Build Tool".center(68) + "║")
    print("║" + "     Compile Python to Native C++".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═"*68 + "╝")
    print()
    
    logger.info(f"Project: {PROJECT_DIR}")
    logger.info(f"Output: {DIST_DIR}")
    logger.info(f"Build Version: {BUILD_VERSION}")
    logger.info(f"MSVC: {MSVC_BIN / 'cl.exe' if (MSVC_BIN / 'cl.exe').exists() else 'Not found'}")
    
    # 执行构建步骤
    steps = [
        clean_directories,
        copy_resources,
        run_nuitka_build,
        run_upx_compression,
    ]
    
    for step in steps:
        if not step():
            logger.error(f"Build failed at: {step.__name__}")
            print_summary()
            sys.exit(1)
    
    print_summary()
    print()
    logger.success("BUILD SUCCESSFUL")
    print()
    print("="*70)
    print()


if __name__ == "__main__":
    main()
