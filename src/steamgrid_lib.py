"""
Steam Grid Artwork Manager - Core Library
Author: Wesley Ellis - wes@wesellis.com

Professional toolkit for managing Steam library artwork using SteamGridDB.
"""

import os
import requests
import json
import time
import shutil
import webbrowser
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
import logging

class SteamGridAPI:
    """Interface for SteamGridDB API operations with enhanced performance and monitoring"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.steamgriddb.com/api/v2"
        self.headers = {"Authorization": f"Bearer {api_key}"}
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Simple in-memory cache for game lookups (session-based)
        self._game_cache = {}  # appid -> game_data
        self._artwork_cache = {}  # (game_id, art_type) -> artwork_list
        
        # Performance monitoring
        self._performance_stats = {
            'api_calls_total': 0,
            'api_calls_cached': 0,
            'total_response_time': 0.0,
            'fastest_response': float('inf'),
            'slowest_response': 0.0,
            'errors_total': 0,
            'timeouts_total': 0
        }
        
        # Enhanced connection pooling and reliability configuration
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=20,  # Increased connection pool for reuse
            pool_maxsize=50,     # Larger max connections in pool
            max_retries=requests.urllib3.util.Retry(
                total=0,  # We handle retries at app level
                backoff_factor=1,
                status_forcelist=[500, 502, 503, 504]
            )
        )
        self.session.mount('https://', adapter)
        self.session.mount('http://', adapter)
        
        # Enhanced keep-alive and connection reuse settings
        self.session.headers.update({
            'Connection': 'keep-alive',
            'User-Agent': 'VAPOR-ArtworkManager/2.0',
            'Accept-Encoding': 'gzip, deflate',
            'Accept': 'application/json'
        })
    
    def search_game(self, appid: int) -> Optional[Dict]:
        """Search for game by Steam App ID with enhanced error handling, caching, and performance monitoring"""
        # Performance monitoring - start timer
        start_time = time.time()
        self._performance_stats['api_calls_total'] += 1
        
        # Check cache first
        if appid in self._game_cache:
            self._performance_stats['api_calls_cached'] += 1
            print(f"Cache hit for AppID {appid} (saves {self._performance_stats['api_calls_cached']}/{self._performance_stats['api_calls_total']} = {100*self._performance_stats['api_calls_cached']/self._performance_stats['api_calls_total']:.1f}% cached)")
            return self._game_cache[appid]
        
        try:
            url = f"{self.base_url}/games/steam/{appid}"
            response = self.session.get(url, timeout=15)  # Increased timeout
            
            if response.status_code == 200:
                data = response.json()
                game_data = data.get("data")
                # Cache the result
                self._game_cache[appid] = game_data
                
                # Performance monitoring - record success
                response_time = time.time() - start_time
                self._update_performance_stats(response_time)
                print(f"API call successful for AppID {appid} ({response_time:.2f}s)")
                
                return game_data
            elif response.status_code == 404:
                # Cache negative results too (prevents repeated 404 lookups)
                self._game_cache[appid] = None
                return None
            elif response.status_code == 429:
                print(f"Rate limited by SteamGridDB API - will retry")
                raise requests.RequestException(f"Rate limited (429) - temporary issue")
            elif response.status_code in [500, 502, 503, 504]:
                print(f"SteamGridDB server error {response.status_code} - will retry")
                raise requests.RequestException(f"Server error ({response.status_code}) - temporary issue")
            else:
                print(f"API Error {response.status_code}: {response.text}")
                raise requests.RequestException(f"API Error {response.status_code}: {response.text}")
                
        except requests.Timeout as e:
            self._performance_stats['timeouts_total'] += 1
            self._performance_stats['errors_total'] += 1
            print(f"Timeout searching for AppID {appid}: {e} (timeout #{self._performance_stats['timeouts_total']})")
            raise requests.RequestException(f"Request timeout - network issue")
        except requests.ConnectionError as e:
            self._performance_stats['errors_total'] += 1
            print(f"Connection error searching for AppID {appid}: {e} (error #{self._performance_stats['errors_total']})")
            raise requests.RequestException(f"Connection failed - network issue")
        except requests.RequestException as e:
            self._performance_stats['errors_total'] += 1
            print(f"Network error searching for AppID {appid}: {e} (error #{self._performance_stats['errors_total']})")
            raise
    
    def get_artwork(self, game_id: int, artwork_type: str, 
                   styles: List[str] = None, types: List[str] = None,
                   dimensions: List[str] = None, limit: int = 50) -> List[Dict]:
        """Get artwork for a specific game with enhanced error handling, caching, and performance monitoring"""
        
        # Performance monitoring - start timer
        start_time = time.time()
        self._performance_stats['api_calls_total'] += 1
        
        # Create cache key for this specific request
        cache_key = (game_id, artwork_type, 
                    ','.join(styles) if styles else None,
                    ','.join(types) if types else None,
                    ','.join(dimensions) if dimensions else None,
                    limit)
        
        # Check cache first
        if cache_key in self._artwork_cache:
            self._performance_stats['api_calls_cached'] += 1
            print(f"Cache hit for {artwork_type} artwork (game {game_id}) - {self._performance_stats['api_calls_cached']}/{self._performance_stats['api_calls_total']} cached")
            return self._artwork_cache[cache_key]
        
        endpoint_map = {
            "grid": "grids",
            "hero": "heroes", 
            "logo": "logos",
            "icon": "icons"
        }
        
        if artwork_type not in endpoint_map:
            raise ValueError(f"Invalid artwork type: {artwork_type}")
        
        try:
            url = f"{self.base_url}/{endpoint_map[artwork_type]}/game/{game_id}"
            params = {}
            
            if styles:
                params["styles"] = ",".join(styles)
            if types:
                params["types"] = ",".join(types)
            if dimensions:
                params["dimensions"] = ",".join(dimensions)
            
            response = self.session.get(url, params=params, timeout=15)  # Increased timeout
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("data", [])
                artwork_list = results[:limit]
                # Cache the results
                self._artwork_cache[cache_key] = artwork_list
                
                # Performance monitoring - record success
                response_time = time.time() - start_time
                self._update_performance_stats(response_time)
                print(f"Retrieved {len(artwork_list)} {artwork_type} images for game {game_id} ({response_time:.2f}s)")
                
                return artwork_list
            elif response.status_code == 429:
                print(f"Rate limited getting {artwork_type} - will retry")
                raise requests.RequestException(f"Rate limited (429) - temporary issue")
            elif response.status_code in [500, 502, 503, 504]:
                print(f"Server error {response.status_code} getting {artwork_type} - will retry")
                raise requests.RequestException(f"Server error ({response.status_code}) - temporary issue")
            else:
                print(f"API Error {response.status_code} for {artwork_type}: {response.text}")
                # Cache empty results for non-critical errors to avoid repeated calls
                self._artwork_cache[cache_key] = []
                return []
                
        except requests.Timeout as e:
            self._performance_stats['timeouts_total'] += 1
            self._performance_stats['errors_total'] += 1
            print(f"Timeout getting {artwork_type} for game {game_id}: {e} (timeout #{self._performance_stats['timeouts_total']})")
            raise requests.RequestException(f"Request timeout - network issue")
        except requests.ConnectionError as e:
            self._performance_stats['errors_total'] += 1
            print(f"Connection error getting {artwork_type} for game {game_id}: {e} (error #{self._performance_stats['errors_total']})")
            raise requests.RequestException(f"Connection failed - network issue")
        except requests.RequestException as e:
            self._performance_stats['errors_total'] += 1
            print(f"Network error getting {artwork_type} for game {game_id}: {e} (error #{self._performance_stats['errors_total']})")
            raise
    
    def clear_cache(self):
        """Clear the API cache to free memory"""
        cache_stats = {
            'games_cached': len(self._game_cache),
            'artwork_cached': len(self._artwork_cache)
        }
        self._game_cache.clear()
        self._artwork_cache.clear()
        print(f"API cache cleared: {cache_stats['games_cached']} games, {cache_stats['artwork_cached']} artwork entries")
        return cache_stats
    
    def get_cache_stats(self):
        """Get current cache statistics"""
        return {
            'games_cached': len(self._game_cache),
            'artwork_cached': len(self._artwork_cache)
        }
    
    def _update_performance_stats(self, response_time: float):
        """Update performance monitoring statistics"""
        self._performance_stats['total_response_time'] += response_time
        self._performance_stats['fastest_response'] = min(self._performance_stats['fastest_response'], response_time)
        self._performance_stats['slowest_response'] = max(self._performance_stats['slowest_response'], response_time)
    
    def get_performance_stats(self):
        """Get comprehensive performance statistics"""
        stats = self._performance_stats.copy()
        
        if stats['api_calls_total'] > 0:
            stats['average_response_time'] = stats['total_response_time'] / (stats['api_calls_total'] - stats['api_calls_cached'])
            stats['cache_hit_rate'] = (stats['api_calls_cached'] / stats['api_calls_total']) * 100
            stats['error_rate'] = (stats['errors_total'] / stats['api_calls_total']) * 100
        else:
            stats['average_response_time'] = 0.0
            stats['cache_hit_rate'] = 0.0
            stats['error_rate'] = 0.0
        
        # Reset infinite values
        if stats['fastest_response'] == float('inf'):
            stats['fastest_response'] = 0.0
        
        return stats
    
    def print_performance_summary(self):
        """Print a comprehensive performance summary"""
        stats = self.get_performance_stats()
        print(f"\n=== SteamGridDB API Performance Summary ===")
        print(f"Total API Calls: {stats['api_calls_total']}")
        print(f"Cache Hits: {stats['api_calls_cached']} ({stats['cache_hit_rate']:.1f}%)")
        print(f"Average Response Time: {stats['average_response_time']:.2f}s")
        print(f"Fastest Response: {stats['fastest_response']:.2f}s")
        print(f"Slowest Response: {stats['slowest_response']:.2f}s")
        print(f"Total Errors: {stats['errors_total']} ({stats['error_rate']:.1f}%)")
        print(f"Timeouts: {stats['timeouts_total']}")
        print(f"Games Cached: {len(self._game_cache)}")
        print(f"Artwork Cached: {len(self._artwork_cache)}")


class SteamLibraryManager:
    """Manages Steam library integration"""
    
    def __init__(self, user_id: str = None):
        self.user_id = user_id
        self.grid_folder = self._find_grid_folder()
    
    def _find_grid_folder(self) -> Optional[Path]:
        """Locate Steam's grid artwork folder"""
        print(f"\n=== Searching for Steam grid folder ===")
        
        if self.user_id:
            print(f"Looking for user ID: {self.user_id}")
            
            # Comprehensive cross-platform Steam paths including Steam Deck, portable, and custom installs
            steam_paths = [
                # Windows default paths
                Path.home() / "AppData" / "Local" / "Steam" / "userdata" / self.user_id / "config" / "grid",
                Path("C:/Program Files (x86)/Steam/userdata") / self.user_id / "config" / "grid", 
                Path("C:/Program Files/Steam/userdata") / self.user_id / "config" / "grid",
                # Common drive installations
                Path("D:/Steam/userdata") / self.user_id / "config" / "grid",
                Path("E:/Steam/userdata") / self.user_id / "config" / "grid",
                Path("F:/Steam/userdata") / self.user_id / "config" / "grid",
                Path("G:/Steam/userdata") / self.user_id / "config" / "grid",
                # Portable Steam installations
                Path("C:/Games/Steam/userdata") / self.user_id / "config" / "grid",
                Path("D:/Games/Steam/userdata") / self.user_id / "config" / "grid",
                Path("E:/Games/Steam/userdata") / self.user_id / "config" / "grid",
                # Custom installation directories
                Path.home() / "Steam" / "userdata" / self.user_id / "config" / "grid",
                Path.home() / "Games" / "Steam" / "userdata" / self.user_id / "config" / "grid",
                Path.home() / "Documents" / "Steam" / "userdata" / self.user_id / "config" / "grid",
                # Steam Deck paths
                Path.home() / ".local" / "share" / "Steam" / "userdata" / self.user_id / "config" / "grid",
                Path("/home/deck/.local/share/Steam/userdata") / self.user_id / "config" / "grid",
                Path("/home/deck/.steam/steam/userdata") / self.user_id / "config" / "grid",
                # Linux paths (various distributions)
                Path.home() / ".steam" / "steam" / "userdata" / self.user_id / "config" / "grid",
                Path("/usr/share/steam/userdata") / self.user_id / "config" / "grid",
                Path("/opt/steam/userdata") / self.user_id / "config" / "grid",
                Path.home() / ".var" / "app" / "com.valvesoftware.Steam" / "home" / ".local" / "share" / "Steam" / "userdata" / self.user_id / "config" / "grid",  # Flatpak
            ]
            
            for path in steam_paths:
                print(f"Checking: {path}")
                if path.exists():
                    print(f"✅ Found grid folder: {path}")
                    return path
                else:
                    # Check if parent directories exist to give better feedback
                    if path.parent.exists():  # config folder exists
                        print(f"⚠️ Config folder exists but grid missing: {path.parent}")
                        print(f"💡 Creating grid folder...")
                        try:
                            path.mkdir(parents=True, exist_ok=True)
                            print(f"✅ Created grid folder: {path}")
                            return path
                        except Exception as e:
                            print(f"❌ Failed to create grid folder: {e}")
                    elif path.parent.parent.exists():  # userdata/userid folder exists
                        print(f"⚠️ User folder exists but config missing: {path.parent.parent}")
                    elif path.parent.parent.parent.exists():  # userdata folder exists
                        print(f"⚠️ Userdata folder exists but user ID missing: {path.parent.parent.parent}")
                        # List available user folders
                        try:
                            user_folders = [d.name for d in path.parent.parent.parent.iterdir() if d.is_dir() and d.name.isdigit()]
                            if user_folders:
                                print(f"📂 Available user IDs: {', '.join(user_folders)}")
                                print(f"💡 Your profile uses: {self.user_id}")
                        except:
                            pass
                    else:
                        print(f"❌ Not found: {path}")
        else:
            # Auto-detect by finding any userdata folder - comprehensive search
            steam_base_paths = [
                # Windows default locations
                Path.home() / "AppData" / "Local" / "Steam" / "userdata",
                Path("C:/Program Files (x86)/Steam/userdata"),
                Path("C:/Program Files/Steam/userdata"),
                # All drive letters for Steam installations
                Path("D:/Steam/userdata"),
                Path("E:/Steam/userdata"),
                Path("F:/Steam/userdata"),
                Path("G:/Steam/userdata"),
                Path("H:/Steam/userdata"),
                # Common custom paths
                Path("C:/Games/Steam/userdata"),
                Path("D:/Games/Steam/userdata"),
                Path("E:/Games/Steam/userdata"),
                Path.home() / "Steam" / "userdata",
                Path.home() / "Games" / "Steam" / "userdata",
                Path.home() / "Documents" / "Steam" / "userdata",
                # Portable installations
                Path("C:/PortableApps/Steam/userdata"),
                Path("D:/PortableApps/Steam/userdata"),
                # Steam Deck and Linux
                Path.home() / ".local" / "share" / "Steam" / "userdata",
                Path("/home/deck/.local/share/Steam/userdata"),
                Path.home() / ".steam" / "steam" / "userdata",
                Path("/usr/share/steam/userdata"),
                Path("/opt/steam/userdata"),
                # Flatpak Steam (Linux)
                Path.home() / ".var" / "app" / "com.valvesoftware.Steam" / "home" / ".local" / "share" / "Steam" / "userdata",
            ]
            
            for base_path in steam_base_paths:
                print(f"Checking base path: {base_path}")
                if base_path.exists():
                    print(f"Found userdata folder, checking user subdirectories...")
                    for user_folder in base_path.iterdir():
                        if user_folder.is_dir() and user_folder.name.isdigit():
                            grid_path = user_folder / "config" / "grid"
                            print(f"  Checking user {user_folder.name}: {grid_path}")
                            if grid_path.exists():
                                self.user_id = user_folder.name
                                print(f"✅ Found grid folder: {grid_path} (User ID: {self.user_id})")
                                return grid_path
                            else:
                                print(f"  ❌ No grid folder for user {user_folder.name}")
                else:
                    print(f"❌ Base path not found: {base_path}")
        
        print(f"❌ No Steam grid folder found!")
        print(f"💡 Troubleshooting suggestions:")
        print(f"   1. Make sure Steam is installed")
        print(f"   2. Launch Steam at least once to create user folders")
        print(f"   3. Check if Steam ID '{self.user_id}' is correct")
        print(f"   4. Run 'DIAGNOSE_STEAM_FOLDERS.bat' for detailed analysis")
        return None
    
    def get_steam_filename(self, appid: int, artwork_type: str, extension: str) -> str:
        """Generate proper Steam filename for artwork"""
        # Steam's exact naming conventions
        filename_map = {
            "grid": f"{appid}p.{extension}",  # Portrait grid (vertical)
            "grid_horizontal": f"{appid}.{extension}",  # Horizontal grid (landscape)
            "hero": f"{appid}_hero.{extension}",  # Hero banner
            "logo": f"{appid}_logo.{extension}",  # Logo
            "icon": f"{appid}_icon.{extension}"   # Icon
        }
        
        # Debug: Print the filename being generated
        filename = filename_map.get(artwork_type, f"{appid}.{extension}")
        print(f"  Generated filename: {filename} for {artwork_type}")
        
        return filename
    
    def backup_existing(self, filepath: Path) -> bool:
        """Create backup of existing artwork"""
        if filepath.exists():
            try:
                backup_path = filepath.with_suffix(f".backup{filepath.suffix}")
                shutil.copy2(filepath, backup_path)
                return True
            except Exception as e:
                print(f"Failed to backup {filepath}: {e}")
                return False
        return True
    
    def install_artwork(self, appid: int, artwork_type: str, image_data: bytes) -> bool:
        """Install artwork to Steam library"""
        if not self.grid_folder:
            print("ERROR: Steam grid folder not found")
            return False
        
        try:
            # Determine if image has transparency
            from PIL import Image
            import io
            
            pil_image = Image.open(io.BytesIO(image_data))
            has_transparency = pil_image.mode in ('RGBA', 'LA') or 'transparency' in pil_image.info
            
            # Choose format based on content
            if has_transparency:
                # Keep as PNG for transparency (logos especially need this)
                extension = "png"
                final_data = image_data
                print(f"  Keeping as PNG (has transparency): {len(image_data)} bytes")
            else:
                # Convert to JPG for better compression
                pil_image = pil_image.convert('RGB')
                jpg_buffer = io.BytesIO()
                pil_image.save(jpg_buffer, format='JPEG', quality=95)
                extension = "jpg"
                final_data = jpg_buffer.getvalue()
                print(f"  Converting to JPG: {len(final_data)} bytes")
            
            filename = self.get_steam_filename(appid, artwork_type, extension)
            filepath = self.grid_folder / filename
            
            # Remove ALL existing files for this appid + artwork_type (including backups)
            print(f"  Cleaning up existing {artwork_type} files for AppID {appid}...")
            
            # Find the specific pattern for this artwork type
            if artwork_type == "grid":
                patterns_to_clean = [f"{appid}p*"]  # Only clean portrait grids (vertical)
            elif artwork_type == "grid_horizontal":
                # Clean horizontal grids - be specific to avoid conflicts
                patterns_to_clean = [f"{appid}.jpg", f"{appid}.png", f"{appid}.jpeg"]
            elif artwork_type == "hero":
                patterns_to_clean = [f"{appid}_hero*"]
            elif artwork_type == "logo":
                patterns_to_clean = [f"{appid}_logo*"]
            elif artwork_type == "icon":
                patterns_to_clean = [f"{appid}_icon*"]
            else:
                patterns_to_clean = [f"{appid}*"]
            
            print(f"  Using cleanup patterns: {patterns_to_clean}")
            
            # Find and delete all matching files
            import glob
            total_removed = 0
            for pattern in patterns_to_clean:
                full_pattern = str(self.grid_folder / pattern)
                print(f"  Searching for: {full_pattern}")
                matching_files = glob.glob(full_pattern)
                print(f"  Found {len(matching_files)} files matching pattern '{pattern}'")
                
                for file_path in matching_files:
                    file_name = Path(file_path).name
                    print(f"  Removing existing file: {file_name}")
                    try:
                        Path(file_path).unlink()
                        total_removed += 1
                    except Exception as e:
                        print(f"  Failed to remove {file_name}: {e}")
            
            print(f"  Total files removed: {total_removed}")
            
            # Write new artwork (no backup needed since we cleared everything)
            with open(filepath, 'wb') as f:
                f.write(final_data)
            
            print(f"  Installed: {filename}")
            return True
            
        except Exception as e:
            print(f"Failed to install {artwork_type} for AppID {appid}: {e}")
            return False


class ArtworkDownloader:
    """Handles artwork downloading and management"""
    
    def __init__(self, download_dir: Path = None):
        # Use professional cache directory if not specified
        if download_dir is None:
            try:
                from vapor_paths import vapor_paths
                self.download_dir = vapor_paths.artwork_cache_dir
            except ImportError:
                # Fallback for standalone use
                self.download_dir = Path("artwork_preview")
        else:
            self.download_dir = download_dir
            
        self.download_dir.mkdir(parents=True, exist_ok=True)
    
    def download_image(self, url: str, filename: str = None) -> Optional[bytes]:
        """Download image from URL"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            if filename:
                filepath = self.download_dir / filename
                filepath.parent.mkdir(parents=True, exist_ok=True)
                with open(filepath, 'wb') as f:
                    f.write(response.content)
            
            return response.content
            
        except requests.RequestException as e:
            print(f"Failed to download {url}: {e}")
            return None
    
    def preview_artwork(self, game_name: str, artwork_options: Dict[str, List[Dict]]) -> None:
        """Save artwork options for preview"""
        game_dir = self.download_dir / game_name.replace(":", "").replace(" ", "_")
        game_dir.mkdir(parents=True, exist_ok=True)
        
        for art_type, options in artwork_options.items():
            type_dir = game_dir / art_type
            type_dir.mkdir(parents=True, exist_ok=True)
            
            for i, option in enumerate(options, 1):
                url = option.get("url", "")
                if url:
                    extension = url.split(".")[-1].split("?")[0]
                    filename = f"option_{i}.{extension}"
                    filepath = type_dir / filename
                    
                    print(f"  Downloading {art_type} option {i}...")
                    image_data = self.download_image(url)
                    if image_data:
                        with open(filepath, 'wb') as f:
                            f.write(image_data)


def is_steam_running() -> bool:
    """Check if Steam is currently running"""
    import psutil
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and 'steam' in proc.info['name'].lower():
            return True
    return False
