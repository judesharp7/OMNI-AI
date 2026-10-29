#!/usr/bin/env python3
"""
build.py — Portable build script for the OMNI Kernel.

Usage:
    python build.py          # auto-detects compiler, builds shared lib
    python build.py --test   # builds and runs self-test
    python build.py --clean  # removes build artefacts
"""
import os
import sys
import platform
import subprocess
import shutil
import argparse
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC  = HERE / "omni_kernel.cpp"


def find_compiler():
    """Auto-detect the best available C++ compiler."""
    for cc in ("g++", "clang++", "cl"):
        if shutil.which(cc):
            return cc
    return None


def build_shared(compiler: str):
    """Compile omni_kernel as a shared library."""
    system = platform.system()
    if compiler == "cl":
        out = HERE / "omni_kernel.dll"
        cmd = [
            compiler, "/std:c++17", "/O2", "/EHsc", "/LD",
            str(SRC), f"/Fe:{out}"
        ]
    else:
        ext = ".dll" if system == "Windows" else ".so" if system == "Linux" else ".dylib"
        out = HERE / f"omni_kernel{ext}"
        cmd = [
            compiler, "-std=c++17", "-O3", "-shared", "-fPIC",
            "-Wall", "-Wextra",
            str(SRC), "-o", str(out),
        ]
        if system != "Windows":
            cmd.append("-lpthread")

    print(f"[BUILD] {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(HERE))
    if result.returncode != 0:
        print("[BUILD] ❌ Compilation failed")
        sys.exit(1)
    print(f"[BUILD] ✅ Built: {out}")
    return out


def build_test(compiler: str):
    """Compile and run the self-test."""
    system = platform.system()
    ext = ".exe" if system == "Windows" else ""
    out = HERE / f"omni_kernel_test{ext}"

    if compiler == "cl":
        cmd = [
            compiler, "/std:c++17", "/O2", "/EHsc",
            "/DOMNI_KERNEL_TEST",
            str(SRC), f"/Fe:{out}"
        ]
    else:
        cmd = [
            compiler, "-std=c++17", "-O2",
            "-DOMNI_KERNEL_TEST",
            str(SRC), "-o", str(out),
        ]
        if system != "Windows":
            cmd.append("-lpthread")

    print(f"[TEST-BUILD] {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(HERE))
    if result.returncode != 0:
        print("[TEST-BUILD] ❌ Compilation failed")
        sys.exit(1)

    print(f"[TEST-RUN] {out}")
    result = subprocess.run([str(out)], cwd=str(HERE))
    if result.returncode != 0:
        print("[TEST-RUN] ❌ Self-test FAILED")
        sys.exit(1)
    print("[TEST-RUN] ✅ All tests passed")


def clean():
    """Remove build artefacts."""
    exts = {".dll", ".so", ".dylib", ".exe", ".obj", ".o", ".exp", ".lib"}
    for f in HERE.iterdir():
        if f.suffix in exts:
            f.unlink()
            print(f"[CLEAN] Removed {f.name}")
    build_dir = HERE / "build"
    if build_dir.exists():
        shutil.rmtree(build_dir)
        print("[CLEAN] Removed build/")


def main():
    parser = argparse.ArgumentParser(description="OMNI Kernel build script")
    parser.add_argument("--test", action="store_true", help="Build + run self-test")
    parser.add_argument("--clean", action="store_true", help="Remove build artefacts")
    parser.add_argument("--compiler", type=str, default=None, help="Override compiler")
    args = parser.parse_args()

    if args.clean:
        clean()
        return

    compiler = args.compiler or find_compiler()
    if not compiler:
        print("[BUILD] ❌ No C++ compiler found. Install g++, clang++, or MSVC.")
        sys.exit(1)

    print(f"[BUILD] Using compiler: {compiler}")
    print(f"[BUILD] Platform: {platform.system()} {platform.machine()}")

    if args.test:
        build_test(compiler)
    else:
        build_shared(compiler)


if __name__ == "__main__":
    main()
