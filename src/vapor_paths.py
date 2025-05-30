"""
VAPOR Cross-Platform Path Management
Handles directory structure across Windows, macOS, Linux, and Steam Deck
"""

import os
import sys
from pathlib import Path
import platform

class VaporPaths:
    """Cross-platform path management for VAPOR"""
    
    def __init__(self):
        self.platform = platform.system().lower()
        self.is_frozen = getattr(sys, 'frozen', False)  # PyInstaller detection
        
        # Determine base application directory
        if self.is_frozen:
            # Running as executable
            self.app_dir = Path(sys.executable).parent
        else:
            # Running as script
            self.app_dir = Path(__file__).parent
        
        # Set up cross-platform data directories
        self._setup_data_directories()
        
        # Initialize all paths
        self._initialize_paths()
    
    def _setup_data_directories(self):
        """Set up cross-platform data directories"""
        if self.platform == "windows":
            self.base_data_dir = Path.home() / "AppData" / "Local" / "VAPOR"
        elif self.platform == "darwin":  # macOS
            self.base_data_dir = Path.home() / "Library" / "Application Support" / "VAPOR"
        else:  # Linux, Steam Deck
            # Follow XDG Base Directory specification
            xdg_data_home = os.environ.get('XDG_DATA_HOME', Path.home() / '.local' / 'share')
            self.base_data_dir = Path(xdg_data_home) / "VAPOR"
    
    def _initialize_paths(self):
        """Initialize all VAPOR directory paths"""
        # Core data directories
        self.profiles_dir = self.base_data_dir / "profiles"
        self.cache_dir = self.base_data_dir / "cache"
        self.logs_dir = self.base_data_dir / "logs"
        self.artwork_cache_dir = self.base_data_dir / "artwork_cache"
        
        # Specific cache directories
        self.game_cache_dir = self.cache_dir / "games"
        self.api_cache_dir = self.cache_dir / "api"
        
        # Configuration files
        self.active_profile_file = self.base_data_dir / "active_profile.txt"
        self.settings_file = self.base_data_dir / "settings.json"
        
        # Asset paths (bundled with application)
        self.assets_dir = self.app_dir / "assets"
        self.logo_file = self._find_logo_file()
    
    def _find_logo_file(self):
        """Find the logo file in various possible locations"""
        possible_paths = [
            self.app_dir / "Vapor_Logo.png",
            self.app_dir / "assets" / "Vapor_Logo.png",
            Path("Vapor_Logo.png"),  # Current directory
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
        
        return None  # Logo not found
    
    def _find_icon_file(self):
        """Find the icon file for executable builds"""
        possible_paths = [
            self.app_dir / "Vapor_Icon.png",
            self.app_dir / "assets" / "Vapor_Icon.png", 
            Path("Vapor_Icon.png"),  # Current directory
            # Fallback to logo if icon not found
            self.app_dir / "Vapor_Logo.png",
            Path("Vapor_Logo.png"),
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
        
        return None  # No icon found
    
    def print_paths(self):
        """Print all paths for debugging"""
        print(f"🗂️ VAPOR Directory Structure:")
        print(f"  Platform: {self.platform}")
        print(f"  Frozen: {self.is_frozen}")
        print(f"  App Dir: {self.app_dir}")
        print(f"  Data Dir: {self.base_data_dir}")
        print(f"  Profiles: {self.profiles_dir}")
        print(f"  Cache: {self.cache_dir}")
        print(f"  Logs: {self.logs_dir}")
        print(f"  Artwork Cache: {self.artwork_cache_dir}")
        print(f"  Logo: {self.logo_file}")

# Global instance
vapor_paths = VaporPaths()

def ensure_vapor_directories():
    """Ensure all VAPOR directories exist"""
    directories = [
        vapor_paths.base_data_dir,
        vapor_paths.profiles_dir,
        vapor_paths.cache_dir,
        vapor_paths.logs_dir,
        vapor_paths.artwork_cache_dir,
        vapor_paths.game_cache_dir,
        vapor_paths.api_cache_dir,
    ]
    
    for directory in directories:
        try:
            directory.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"⚠️ Warning: Could not create directory {directory}: {e}")
    
    print(f"✅ VAPOR directories initialized at: {vapor_paths.base_data_dir}")

def get_steam_paths():
    """Get potential Steam installation paths for current platform"""
    steam_paths = []
    
    if vapor_paths.platform == "windows":
        steam_paths = [
            Path("C:/Program Files (x86)/Steam"),
            Path("C:/Program Files/Steam"),
            Path.home() / "AppData" / "Local" / "Steam",
            Path("D:/Steam"),
            Path("E:/Steam"),
            Path("F:/Steam"),
        ]
    elif vapor_paths.platform == "darwin":  # macOS
        steam_paths = [
            Path.home() / "Library" / "Application Support" / "Steam",
            Path("/Applications/Steam.app/Contents/MacOS"),
        ]
    else:  # Linux, Steam Deck
        steam_paths = [
            Path.home() / ".steam" / "steam",
            Path.home() / ".local" / "share" / "Steam",
            Path("/usr/share/steam"),
            Path("/opt/steam"),
            # Steam Deck specific paths
            Path.home() / ".var" / "app" / "com.valvesoftware.Steam" / ".local" / "share" / "Steam",
            Path("/home/deck/.local/share/Steam"),  # Steam Deck user
        ]
    
    # Return only existing paths
    return [path for path in steam_paths if path.exists()]

def get_platform_info():
    """Get detailed platform information"""
    return {
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'frozen': getattr(sys, 'frozen', False),
        'python_version': sys.version,
    }
