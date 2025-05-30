#!/usr/bin/env python3
"""
VAPOR Build Verification with Enhanced Checks for v2.0.1
Ensures all dependencies and files are ready for multi-platform builds
"""

import sys
import os
from pathlib import Path
import importlib.util
import subprocess

class BuildVerifier:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.src_dir = self.project_root / "src"
        self.errors = []
        self.warnings = []
        self.performance_features = []
        
    def check_file_exists(self, filepath, description="", critical=True):
        """Check if a file exists"""
        path = Path(filepath)
        if not path.exists():
            message = f"Missing {description}: {path}"
            if critical:
                self.errors.append(message)
                print(f"❌ {message}")
            else:
                self.warnings.append(message)
                print(f"⚠️  {message}")
            return False
        else:
            print(f"✅ Found {description}: {path}")
            return True
    
    def check_python_module(self, module_name, filepath=None):
        """Check if a Python module can be imported"""
        try:
            if filepath:
                spec = importlib.util.spec_from_file_location(module_name, filepath)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            else:
                __import__(module_name)
            print(f"✅ Python module '{module_name}' imports successfully")
            return True
        except Exception as e:
            message = f"Python module '{module_name}' failed to import: {e}"
            self.errors.append(message)
            print(f"❌ {message}")
            return False
    
    def check_enhanced_features(self):
        """Check for v2.0.1 enhanced performance features"""
        print("\n🚀 Checking v2.0.1 Enhanced Features...")
        
        # Check for enhanced performance utilities
        enhanced_perf_file = self.src_dir / "utilities" / "enhanced_performance.py"
        if enhanced_perf_file.exists():
            print("✅ Enhanced performance utilities available")
            self.performance_features.append("Enhanced retry mechanism")
            self.performance_features.append("Intelligent caching system")
        else:
            print("⚠️  Enhanced performance utilities not found (optional)")
        
        # Check version file for v2.0.1 features
        version_file = self.src_dir / "version.py"
        if version_file.exists():
            try:
                with open(version_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                if "check_for_updates" in content:
                    print("✅ Auto-update system available")
                    self.performance_features.append("Auto-update notifications")
                
                if "__changelog__" in content:
                    print("✅ Changelog tracking enabled")
                    self.performance_features.append("Performance tracking")
                    
                if "2.0.1" in content:
                    print("✅ Version updated to v2.0.1")
                else:
                    self.warnings.append("Version file may not be updated to v2.0.1")
                    
            except Exception as e:
                print(f"⚠️  Could not check version file: {e}")
    
    def check_dependencies(self):
        """Check if all required Python packages are installed"""
        print("\n🔍 Checking Python Dependencies...")
        
        required_packages = [
            'tkinter',
            'PIL',
            'requests',
            'psutil',
            'pathlib',
            'json',
            'threading',
            'logging',
            'gzip',  # New for v2.0.1 compression
            'hashlib',  # New for v2.0.1 caching
        ]
        
        optional_packages = [
            'packaging',  # For version comparison in updates
        ]
        
        for package in required_packages:
            try:
                __import__(package)
                print(f"✅ Package '{package}' is available")
            except ImportError as e:
                message = f"Missing required package: {package}"
                self.errors.append(message)
                print(f"❌ {message}")
        
        for package in optional_packages:
            try:
                __import__(package)
                print(f"✅ Optional package '{package}' is available")
                self.performance_features.append(f"Enhanced features ({package})")
            except ImportError:
                print(f"⚠️  Optional package '{package}' not available (auto-updates may not work)")
    
    def check_source_files(self):
        """Check all critical source files"""
        print("\n🔍 Checking Source Files...")
        
        # Core application files
        core_files = [
            (self.src_dir / "steam_grid_artwork_manager.py", "Main application", True),
            (self.src_dir / "version.py", "Version module", True),
            (self.src_dir / "vapor_paths.py", "Path management", True),
            (self.src_dir / "vapor_logging.py", "Logging system", True),
            (self.src_dir / "steamgrid_lib.py", "SteamGrid library", True),
            (self.src_dir / "steam_game_cache.py", "Game cache", True),
            (self.src_dir / "steam_library_analyzer.py", "Library analyzer", True),
        ]
        
        # v2.0.1 enhanced files
        enhanced_files = [
            (self.src_dir / "utilities" / "enhanced_performance.py", "Enhanced performance utilities", False),
        ]
        
        for filepath, description, critical in core_files + enhanced_files:
            self.check_file_exists(filepath, description, critical)
    
    def check_ui_modules(self):
        """Check UI module files"""
        print("\n🔍 Checking UI Modules...")
        
        ui_files = [
            (self.src_dir / "ui" / "main_ui.py", "Main UI module", True),
            (self.src_dir / "ui" / "main_screens.py", "Screen management", True),
            (self.src_dir / "ui" / "artwork_display.py", "Artwork display", True),
        ]
        
        for filepath, description, critical in ui_files:
            self.check_file_exists(filepath, description, critical)
    
    def check_model_files(self):
        """Check model files"""
        print("\n🔍 Checking Model Files...")
        
        model_files = [
            (self.src_dir / "models" / "profile.py", "Profile management", True),
        ]
        
        for filepath, description, critical in model_files:
            self.check_file_exists(filepath, description, critical)
    
    def check_assets(self):
        """Check asset files"""
        print("\n🔍 Checking Assets...")
        
        assets = [
            (self.project_root / "Vapor_Icon.png", "Application icon (preferred)", False),
            (self.project_root / "Vapor_Logo.png", "Application logo (fallback)", False),
            (self.project_root / "LICENSE", "License file", False),
            (self.project_root / "README.md", "Documentation", False),
            (self.project_root / "RELEASE_NOTES_v2.0.1.md", "v2.0.1 Release notes", False),
        ]
        
        for filepath, description, critical in assets:
            self.check_file_exists(filepath, description, critical)
        
        # Check if at least one icon exists
        icon_file = self.project_root / "Vapor_Icon.png"
        logo_file = self.project_root / "Vapor_Logo.png"
        
        if icon_file.exists():
            print("✅ Using dedicated icon file for executables")
        elif logo_file.exists():
            print("✅ Using logo file as executable icon (fallback)")
        else:
            self.warnings.append("No icon or logo file found - executables will use default system icon")
            print("⚠️ No icon files found - executables will use default system icon")
    
    def check_build_tools(self):
        """Check if build tools are available"""
        print("\n🔍 Checking Build Tools...")
        
        try:
            result = subprocess.run([sys.executable, "-m", "pip", "list"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                installed_packages = result.stdout.lower()
                
                build_packages = ['pyinstaller', 'pillow', 'requests', 'psutil']
                for package in build_packages:
                    if package in installed_packages:
                        print(f"✅ Build tool '{package}' is installed")
                    else:
                        message = f"Missing build tool: {package}"
                        self.warnings.append(message)
                        print(f"⚠️  {message}")
            else:
                print("⚠️  Could not check installed packages")
        except Exception as e:
            print(f"⚠️  Could not check build tools: {e}")
    
    def test_imports(self):
        """Test importing key modules"""
        print("\n🔍 Testing Module Imports...")
        
        # Add src to path for testing
        sys.path.insert(0, str(self.src_dir))
        
        modules_to_test = [
            'version',
            'vapor_paths',
            'vapor_logging',
            'steamgrid_lib',
            'steam_game_cache',
        ]
        
        for module_name in modules_to_test:
            self.check_python_module(module_name)
        
        # Test optional enhanced modules
        try:
            from utilities.enhanced_performance import EnhancedRetryMechanism, IntelligentCache
            print("✅ Enhanced performance utilities import successfully")
            self.performance_features.append("Advanced caching and retry mechanisms")
        except ImportError:
            print("⚠️  Enhanced performance utilities not available (will use fallbacks)")
    
    def check_cross_platform_compatibility(self):
        """Check for cross-platform compatibility issues"""
        print("\n🔍 Checking Cross-Platform Compatibility...")
        
        # Check for Windows-specific paths in code
        problematic_patterns = [
            ("C:\\\\", "Hardcoded Windows paths"),
            ("\\\\.exe", "Windows executable references"),
        ]
        
        python_files = list(self.src_dir.glob("**/*.py"))
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for pattern, description in problematic_patterns:
                    if pattern in content and "# Cross-platform" not in content:
                        self.warnings.append(f"Potential cross-platform issue in {py_file.name}: {description}")
                        
            except Exception as e:
                print(f"⚠️  Could not check {py_file}: {e}")
        
        print(f"✅ Checked {len(python_files)} Python files for compatibility")
    
    def run_verification(self):
        """Run complete verification process"""
        print("🚀 VAPOR v2.0.1 Build Verification")
        print("=" * 60)
        
        # Run all checks
        self.check_enhanced_features()
        self.check_dependencies()
        self.check_source_files()
        self.check_ui_modules()
        self.check_model_files()
        self.check_assets()
        self.check_build_tools()
        self.test_imports()
        self.check_cross_platform_compatibility()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 VERIFICATION SUMMARY")
        print("=" * 60)
        
        if not self.errors:
            print("🎉 ✅ BUILD READY FOR v2.0.1!")
            print("All critical requirements met. Ready for enhanced multi-platform builds.")
            
            if self.performance_features:
                print(f"\n🚀 Enhanced Features Available ({len(self.performance_features)}):")
                for feature in self.performance_features:
                    print(f"  • {feature}")
            
            if self.warnings:
                print(f"\n⚠️  {len(self.warnings)} warnings (non-critical):")
                for warning in self.warnings:
                    print(f"  • {warning}")
            
            return True
        else:
            print("❌ BUILD NOT READY!")
            print(f"Found {len(self.errors)} critical errors:")
            for error in self.errors:
                print(f"  • {error}")
            
            if self.warnings:
                print(f"\nAlso found {len(self.warnings)} warnings:")
                for warning in self.warnings:
                    print(f"  • {warning}")
            
            print("\n🔧 Next Steps:")
            print("1. Fix all critical errors listed above")
            print("2. Run this verification script again")
            print("3. Once all checks pass, run the build script")
            
            return False

def main():
    verifier = BuildVerifier()
    success = verifier.run_verification()
    
    if success:
        print("\n🚀 Ready to build v2.0.1! Run:")
        print("  Windows: BUILD_ALL_PLATFORMS.bat")
        print("  Linux/Mac: ./build_all_platforms.sh")
        print("  Manual: python build_multiplatform.py all")
        print("\n🌟 v2.0.1 includes enhanced performance and stability!")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
