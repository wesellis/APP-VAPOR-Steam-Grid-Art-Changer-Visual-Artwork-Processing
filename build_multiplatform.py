# Multi-Platform Build System for VAPOR
# Creates executables for Windows, macOS, Linux, and Steam Deck

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

class VaporBuildSystem:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.src_dir = self.project_root / "src"
        self.build_dir = self.project_root / "builds"
        self.dist_dir = self.project_root / "dist"
        
        # Ensure build directories exist
        self.build_dir.mkdir(exist_ok=True)
        self.dist_dir.mkdir(exist_ok=True)
        
        # Platform detection
        self.current_platform = platform.system().lower()
        
    def install_build_dependencies(self):
        """Install required build tools"""
        print("🔧 Installing build dependencies...")
        
        dependencies = [
            "pyinstaller>=5.13.0",
            "pillow>=10.0.0",
            "requests>=2.31.0",
        ]
        
        for dep in dependencies:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
                print(f"✅ Installed: {dep}")
            except subprocess.CalledProcessError:
                print(f"❌ Failed to install: {dep}")
                
    def create_spec_file(self, platform_name):
        """Create PyInstaller spec file for specific platform"""
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# Add src directory to path
src_path = str(Path.cwd() / "src")
sys.path.insert(0, src_path)

block_cipher = None

a = Analysis(
    ['src/steam_grid_artwork_manager.py'],
    pathex=[r'{self.project_root}', r'{self.src_dir}'],
    binaries=[],
    datas=[
        ('assets/Vapor_Logo.png', 'assets'),
        ('assets/Vapor_Icon.png', 'assets'),
        ('src/ui', 'ui'),
        ('src/models', 'models'),
        ('src/utilities', 'utilities'),
        ('LICENSE', '.'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'requests',
        'json',
        'threading',
        'queue',
        'time',
        'os',
        'sys',
        'pathlib',
        'urllib.parse',
        'urllib.request',
        'ui.main_ui',
        'ui.main_screens',
        'ui.artwork_display',
        'models.profile',
        'utilities.enhanced_performance',
        'gzip',
        'hashlib',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='VAPOR',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=r'{self.project_root}/assets/Vapor_Icon.png' if (Path(r'{self.project_root}/assets/Vapor_Icon.png')).exists() else (r'{self.project_root}/assets/Vapor_Logo.png' if (Path(r'{self.project_root}/assets/Vapor_Logo.png')).exists() else None),
)
'''

        spec_file = self.project_root / f"vapor_{platform_name}.spec"
        with open(spec_file, 'w') as f:
            f.write(spec_content)
        
        return spec_file
    
    def build_windows(self):
        """Build Windows executable"""
        print("🪟 Building Windows executable...")
        
        spec_file = self.create_spec_file("windows")
        
        # Build command
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            str(spec_file)
        ]
        
        try:
            subprocess.check_call(cmd)
            
            # Move and rename the executable
            exe_path = self.project_root / "dist" / "VAPOR.exe"
            final_path = self.build_dir / "VAPOR_Windows_v2.0.1.exe"
            
            if exe_path.exists():
                shutil.move(str(exe_path), str(final_path))
                print(f"✅ Windows build complete: {final_path}")
                return True
            else:
                print("❌ Windows build failed - executable not found")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Windows build failed: {e}")
            return False
    
    def build_macos(self):
        """Build macOS application bundle"""
        print("🍎 Building macOS application...")
        
        if self.current_platform != "darwin":
            print("⚠️ macOS builds should be created on macOS for best compatibility")
        
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# Add src directory to path
src_path = str(Path.cwd() / "src")
sys.path.insert(0, src_path)

block_cipher = None

a = Analysis(
    ['src/steam_grid_artwork_manager.py'],
    pathex=[r'{self.project_root}', r'{self.src_dir}'],
    binaries=[],
    datas=[
        ('assets/Vapor_Logo.png', 'assets'),
        ('assets/Vapor_Icon.png', 'assets'),
        ('src/ui', 'ui'),
        ('src/models', 'models'),
        ('src/utilities', 'utilities'),
        ('LICENSE', '.'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'requests',
        'json',
        'threading',
        'queue',
        'time',
        'os',
        'sys',
        'pathlib',
        'urllib.parse',
        'urllib.request',
        'ui.main_ui',
        'ui.main_screens',
        'ui.artwork_display',
        'models.profile',
        'utilities.enhanced_performance',
        'gzip',
        'hashlib',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='VAPOR',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

app = BUNDLE(
    exe,
    name='VAPOR.app',
    icon=r'{self.project_root}/assets/Vapor_Icon.png' if (Path(r'{self.project_root}/assets/Vapor_Icon.png')).exists() else (r'{self.project_root}/assets/Vapor_Logo.png' if (Path(r'{self.project_root}/assets/Vapor_Logo.png')).exists() else None),
    bundle_identifier='com.wesellis.vapor',
    info_plist={{
        'NSHighResolutionCapable': 'True',
        'LSMinimumSystemVersion': '10.14',
        'CFBundleShortVersionString': '2.0.1',
        'CFBundleVersion': '2.0.1',
        'NSHumanReadableCopyright': 'Copyright (c) 2025 Wesley Ellis',
    }},
)
'''
        
        spec_file = self.project_root / "vapor_macos.spec"
        with open(spec_file, 'w') as f:
            f.write(spec_content)
        
        try:
            cmd = [
                sys.executable, "-m", "PyInstaller",
                "--clean",
                "--noconfirm",
                str(spec_file)
            ]
            
            subprocess.check_call(cmd)
            
            # Move the .app bundle
            app_path = self.project_root / "dist" / "VAPOR.app"
            final_path = self.build_dir / "VAPOR_macOS.app"
            
            # macOS builds on Windows create an EXE, let's handle this properly
            exe_path = self.project_root / "dist" / "VAPOR.exe"
            
            if app_path.exists():
                if final_path.exists():
                    shutil.rmtree(final_path)
                shutil.move(str(app_path), str(final_path))
                print(f"✅ macOS build complete: {final_path}")
                return True
            elif exe_path.exists():
                # On Windows, create a pseudo macOS build
                final_exe_path = self.build_dir / "VAPOR_macOS_x64.exe"
                shutil.copy2(str(exe_path), str(final_exe_path))
                print(f"✅ macOS cross-compile complete: {final_exe_path} (run on actual macOS for .app bundle)")
                return True
            else:
                print("❌ macOS build failed - app bundle not found")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ macOS build failed: {e}")
            return False
    
    def build_linux(self):
        """Build Linux executable"""
        print("🐧 Building Linux executable...")
        
        spec_file = self.create_spec_file("linux")
        
        try:
            cmd = [
                sys.executable, "-m", "PyInstaller",
                "--clean",
                "--noconfirm",
                str(spec_file)
            ]
            
            subprocess.check_call(cmd)
            
            # Move and rename the executable
            exe_path = self.project_root / "dist" / "VAPOR.exe"
            final_path = self.build_dir / "VAPOR_Linux_v2.0.1"
            
            if exe_path.exists():
                # Copy the executable and remove .exe extension for Linux
                shutil.copy2(str(exe_path), str(final_path))
                # Make executable
                os.chmod(final_path, 0o755)
                print(f"✅ Linux build complete: {final_path}")
                return True
            else:
                print("❌ Linux build failed - executable not found")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Linux build failed: {e}")
            return False
    
    def build_steam_deck(self):
        """Build Steam Deck specific executable (same as Linux but optimized)"""
        print("🎮 Building Steam Deck executable...")
        
        # Steam Deck uses the same Linux executable but we can create a specific version
        if self.build_linux():
            # Copy the Linux build for Steam Deck
            linux_path = self.build_dir / "VAPOR_Linux_v2.0.1"
            steam_deck_path = self.build_dir / "VAPOR_SteamDeck_v2.0.1"
            
            if linux_path.exists():
                shutil.copy2(str(linux_path), str(steam_deck_path))
                print(f"✅ Steam Deck build complete: {steam_deck_path}")
                return True
        
        return False
    
    def create_desktop_files(self):
        """Create .desktop files for Linux/Steam Deck"""
        print("🖥️ Creating desktop integration files...")
        
        desktop_content = '''[Desktop Entry]
Version=1.0
Type=Application
Name=VAPOR
Comment=Visual Artwork Processing & Organization Resource
Exec=./VAPOR_Linux_x64
Icon=vapor
Terminal=false
Categories=Game;Utility;
StartupWMClass=VAPOR
'''
        
        desktop_file = self.build_dir / "VAPOR.desktop"
        with open(desktop_file, 'w') as f:
            f.write(desktop_content)
        
        # Make it executable
        os.chmod(desktop_file, 0o755)
        
        # Steam Deck specific version
        steam_deck_desktop = desktop_content.replace("./VAPOR_Linux_x64", "./VAPOR_SteamDeck_x64")
        steam_deck_file = self.build_dir / "VAPOR_SteamDeck.desktop"
        with open(steam_deck_file, 'w') as f:
            f.write(steam_deck_desktop)
        os.chmod(steam_deck_file, 0o755)
        
        print("✅ Desktop files created")
    
    def create_installation_scripts(self):
        """Create installation scripts for each platform"""
        print("📦 Creating installation scripts...")
        
        # Windows installer script
        windows_installer = '''@echo off
echo Installing VAPOR for Windows...
echo.
echo Copying executable to Program Files...
if not exist "%PROGRAMFILES%\\VAPOR" mkdir "%PROGRAMFILES%\\VAPOR"
copy "VAPOR_Windows_x64.exe" "%PROGRAMFILES%\\VAPOR\\VAPOR.exe"
echo.
echo Creating desktop shortcut...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\\VAPOR.lnk'); $Shortcut.TargetPath = '%PROGRAMFILES%\\VAPOR\\VAPOR.exe'; $Shortcut.Save()"
echo.
echo Installation complete! You can now run VAPOR from your desktop.
pause
'''
        
        with open(self.build_dir / "install_windows.bat", 'w') as f:
            f.write(windows_installer)
        
        # Linux/Steam Deck installer script
        linux_installer = '''#!/bin/bash
echo "Installing VAPOR for Linux/Steam Deck..."
echo ""

# Create local application directory
mkdir -p ~/.local/bin
mkdir -p ~/.local/share/applications
mkdir -p ~/.local/share/icons

# Copy executable
cp VAPOR_Linux_v2.0.1 ~/.local/bin/vapor
chmod +x ~/.local/bin/vapor

# Copy desktop file
cp VAPOR.desktop ~/.local/share/applications/
cp Vapor_Logo.png ~/.local/share/icons/vapor.png 2>/dev/null || echo "Logo not found, skipping icon"

# Update desktop database
update-desktop-database ~/.local/share/applications/ 2>/dev/null || true

echo ""
echo "Installation complete! VAPOR should now appear in your application menu."
echo "You can also run it from terminal with: vapor"
'''
        
        linux_script = self.build_dir / "install_linux.sh"
        with open(linux_script, 'w') as f:
            f.write(linux_installer)
        os.chmod(linux_script, 0o755)
        
        # Steam Deck specific installer
        steam_deck_installer = linux_installer.replace("VAPOR_Linux_v2.0.1", "VAPOR_SteamDeck_v2.0.1")
        steam_deck_script = self.build_dir / "install_steam_deck.sh"
        with open(steam_deck_script, 'w') as f:
            f.write(steam_deck_installer)
        os.chmod(steam_deck_script, 0o755)
        
        print("✅ Installation scripts created")
    
    def create_release_packages(self):
        """Create release packages for distribution"""
        print("📦 Creating release packages...")
        
        # Windows package
        if (self.build_dir / "VAPOR_Windows_v2.0.1.exe").exists():
            windows_files = [
                "VAPOR_Windows_v2.0.1.exe",
                "install_windows.bat",
            ]
            self._create_zip_package("VAPOR_Windows_v2.0.1", windows_files)
        
        # macOS package
        if (self.build_dir / "VAPOR_macOS.app").exists():
            macos_files = ["VAPOR_macOS.app"]
            self._create_zip_package("VAPOR_macOS_v2.0.1", macos_files)
        
        # Linux package
        if (self.build_dir / "VAPOR_Linux_v2.0.1").exists():
            linux_files = [
                "VAPOR_Linux_v2.0.1",
                "VAPOR.desktop",
                "install_linux.sh",
            ]
            self._create_zip_package("VAPOR_Linux_v2.0.1", linux_files)
        
        # Steam Deck package
        if (self.build_dir / "VAPOR_SteamDeck_v2.0.1").exists():
            steam_deck_files = [
                "VAPOR_SteamDeck_v2.0.1",
                "VAPOR_SteamDeck.desktop",
                "install_steam_deck.sh",
            ]
            self._create_zip_package("VAPOR_SteamDeck_v2.0.1", steam_deck_files)
        
        print("✅ Release packages created")
    
    def _create_zip_package(self, package_name, files):
        """Create a zip package with specified files"""
        import zipfile
        
        zip_path = self.build_dir / f"{package_name}.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_name in files:
                file_path = self.build_dir / file_name
                if file_path.exists():
                    if file_path.is_dir():
                        # Add directory recursively
                        for root, dirs, files_in_dir in os.walk(file_path):
                            for file in files_in_dir:
                                file_full_path = Path(root) / file
                                arc_path = Path(package_name) / file_name / file_full_path.relative_to(file_path)
                                zipf.write(file_full_path, arc_path)
                    else:
                        zipf.write(file_path, Path(package_name) / file_name)
                else:
                    print(f"⚠️ File not found: {file_name}")
        
        print(f"📦 Created: {zip_path}")
    
    def build_all_platforms(self):
        """Build executables for all platforms"""
        print("🚀 Starting multi-platform build process...")
        print("=" * 60)
        
        # Install dependencies
        self.install_build_dependencies()
        print()
        
        success_count = 0
        total_builds = 4
        
        # Build for each platform
        if self.build_windows():
            success_count += 1
        
        if self.build_linux():
            success_count += 1
        
        if self.build_steam_deck():
            success_count += 1
        
        if self.build_macos():
            success_count += 1
        
        # Create additional files
        self.create_desktop_files()
        self.create_installation_scripts()
        self.create_release_packages()
        
        print()
        print("=" * 60)
        print(f"🎉 Build process complete! {success_count}/{total_builds} builds successful")
        print(f"📁 All builds available in: {self.build_dir}")
        
        # List created files
        print("\n📦 Created files:")
        for file in sorted(self.build_dir.glob("*")):
            size = file.stat().st_size if file.is_file() else "DIR"
            if isinstance(size, int):
                size = f"{size / 1024 / 1024:.1f}MB"
            print(f"  • {file.name} ({size})")
        
        return success_count == total_builds

def main():
    """Main entry point"""
    print("🎨 VAPOR Multi-Platform Build System")
    print("Creating executables for Windows, macOS, Linux, and Steam Deck")
    print()
    
    builder = VaporBuildSystem()
    
    if len(sys.argv) > 1:
        platform = sys.argv[1].lower()
        
        if platform == "windows":
            builder.build_windows()
        elif platform == "macos":
            builder.build_macos()
        elif platform == "linux":
            builder.build_linux()
        elif platform == "steamdeck":
            builder.build_steam_deck()
        elif platform == "all":
            builder.build_all_platforms()
        else:
            print(f"❌ Unknown platform: {platform}")
            print("Available platforms: windows, macos, linux, steamdeck, all")
    else:
        # Build all platforms by default
        builder.build_all_platforms()

if __name__ == "__main__":
    main()
