#!/usr/bin/env python3
"""
VAPOR Build Fix Script
Cleans up problematic spec files and rebuilds with proper configuration
"""

import os
import shutil
import time
import subprocess
from pathlib import Path

def force_kill_processes():
    """Force kill any hanging PyInstaller processes"""
    print("🔄 Stopping any running PyInstaller processes...")
    try:
        # Kill PyInstaller processes on Windows
        subprocess.run(["taskkill", "/F", "/IM", "python.exe"], 
                      capture_output=True, check=False)
        subprocess.run(["taskkill", "/F", "/IM", "pyinstaller.exe"], 
                      capture_output=True, check=False)
        time.sleep(2)  # Give processes time to die
        print("✅ Processes stopped")
    except Exception as e:
        print(f"⚠️ Could not kill processes: {e}")

def cleanup_build_artifacts():
    """Clean up previous build artifacts that might cause issues"""
    print("🧹 Cleaning up previous build artifacts...")
    
    project_root = Path(__file__).parent
    
    # Files and directories to clean
    cleanup_items = [
        "vapor_windows.spec",
        "vapor_linux.spec", 
        "vapor_macos.spec",
        "build",
        "dist",
    ]
    
    for item in cleanup_items:
        item_path = project_root / item
        
        if item_path.exists():
            try:
                if item_path.is_file():
                    item_path.unlink()
                    print(f"✅ Removed file: {item}")
                elif item_path.is_dir():
                    # Use more aggressive removal for locked directories
                    for retry in range(3):
                        try:
                            shutil.rmtree(item_path, ignore_errors=True)
                            if not item_path.exists():
                                print(f"✅ Removed directory: {item}")
                                break
                            time.sleep(1)
                        except Exception as e:
                            if retry == 2:  # Last attempt
                                print(f"⚠️ Could not fully remove {item}: {e}")
                                # Try to remove what we can
                                try:
                                    shutil.rmtree(item_path, onerror=lambda func, path, exc: None)
                                except:
                                    pass
                            else:
                                time.sleep(2)  # Wait and retry
            except Exception as e:
                print(f"⚠️ Could not remove {item}: {e}")
    
    # Clean PyInstaller cache
    try:
        cache_dir = Path.home() / "AppData" / "Local" / "pyinstaller"
        if cache_dir.exists():
            shutil.rmtree(cache_dir, ignore_errors=True)
            print("✅ Cleared PyInstaller cache")
    except Exception as e:
        print(f"⚠️ Could not clear cache: {e}")

def main():
    """Main cleanup and fix process"""
    print("🔧 VAPOR Build Fix Script")
    print("=" * 40)
    
    force_kill_processes()
    cleanup_build_artifacts()
    
    print("\n🎯 Ready to rebuild!")
    print("Now run: BUILD_ALL_PLATFORMS.bat")
    print("Or: python build_multiplatform.py all")

if __name__ == "__main__":
    main()
