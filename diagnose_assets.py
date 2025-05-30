#!/usr/bin/env python3
"""
Quick diagnostic to check where VAPOR is looking for assets
"""

import sys
from pathlib import Path

print("🔍 VAPOR Asset Diagnostic")
print("=" * 40)

# Check current working directory
print(f"Current working directory: {Path.cwd()}")

# Check script location
if hasattr(sys, '_MEIPASS'):
    print(f"Running from PyInstaller bundle: {sys._MEIPASS}")
    bundle_dir = Path(sys._MEIPASS)
else:
    print(f"Running from script: {Path(__file__).parent}")
    bundle_dir = Path(__file__).parent

print(f"Executable location: {Path(sys.executable).parent}")

# Test all the paths we're checking
icon_paths = [
    Path("assets/Vapor_Icon.png"),  # New assets directory
    Path("assets/Vapor_Logo.png"),  # Fallback to logo in assets
    Path("Vapor_Icon.png"),  # Legacy location (current directory)
    Path("Vapor_Logo.png"),  # Legacy logo location
    Path(sys.executable).parent / "assets" / "Vapor_Icon.png",  # Next to .exe in assets
    Path(sys.executable).parent / "Vapor_Icon.png",  # Next to .exe (legacy)
    bundle_dir / "assets" / "Vapor_Icon.png",  # In bundle assets
    bundle_dir / "Vapor_Icon.png",  # In bundle root
]

print("\n🖼️ Checking icon paths:")
found_icons = []
for i, path in enumerate(icon_paths, 1):
    exists = path.exists()
    status = "✅" if exists else "❌"
    print(f"{i}. {status} {path}")
    if exists:
        found_icons.append(path)

if found_icons:
    print(f"\n🎉 Found {len(found_icons)} icon(s):")
    for icon in found_icons:
        print(f"  • {icon}")
else:
    print("\n😢 No icons found!")

# Check if we're in the right directory
vapor_files = list(Path.cwd().glob("*VAPOR*"))
print(f"\nVAPOR-related files in current directory: {len(vapor_files)}")
for file in vapor_files[:5]:  # Show first 5
    print(f"  • {file.name}")

print("\n🔧 Suggested fixes:")
if not found_icons:
    print("1. Copy Vapor_Icon.png to same folder as executable")
    print("2. Or copy entire assets/ folder to executable location")
