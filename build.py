"""Cross-platform build script using PyInstaller."""

import os
import platform
import subprocess
import sys

APP_NAME = "TelegramPet"
ICON_WIN = "assets/icon.ico"
ICON_MAC = "assets/icon.icns"


def build():
    system = platform.system()
    sep = ";" if system == "Windows" else ":"

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name", APP_NAME,
        "--add-data", f"config.example.toml{sep}.",
        "--hidden-import", "telethon",
        "--hidden-import", "PySide6.QtWidgets",
        "--hidden-import", "PySide6.QtCore",
        "--hidden-import", "PySide6.QtGui",
        "--collect-submodules", "telethon",
    ]

    if system == "Windows" and os.path.exists(ICON_WIN):
        cmd += ["--icon", ICON_WIN]
    elif system == "Darwin":
        if os.path.exists(ICON_MAC):
            cmd += ["--icon", ICON_MAC]
        cmd += ["--osx-bundle-identifier", "com.telegrampet.app"]

    cmd.append("main.py")

    print(f"Building for {system}...")
    print(f"Command: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    print(f"\nBuild complete! Output in dist/{APP_NAME}")


if __name__ == "__main__":
    build()
