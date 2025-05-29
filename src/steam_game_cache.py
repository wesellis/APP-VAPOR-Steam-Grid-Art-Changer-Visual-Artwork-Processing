#!/usr/bin/env python3
"""
Steam Game Library Cache Manager
Author: Wesley Ellis - wes@wesellis.com

Smart caching system for Steam game libraries to avoid repeated API calls
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional
import requests

class SteamGameCache:
    """Manages cached Steam game libraries"""
    
    def __init__(self, cache_dir: Path = None):
        # Use professional cache directory if not specified
        if cache_dir is None:
            try:
                from vapor_paths import vapor_paths
                self.cache_dir = vapor_paths.game_cache_dir
            except ImportError:
                # Fallback for standalone use
                self.cache_dir = Path("game_cache")
        else:
            self.cache_dir = cache_dir
        
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache settings
        self.cache_duration = 24 * 60 * 60  # 24 hours in seconds
        self.force_refresh_days = 7  # Force refresh after 7 days
    
    def get_cache_file(self, steam_id: str) -> Path:
        """Get cache file path for a Steam ID"""
        return self.cache_dir / f"games_{steam_id}.json"
    
    def is_cache_valid(self, steam_id: str) -> bool:
        """Check if cached data is still valid"""
        cache_file = self.get_cache_file(steam_id)
        
        if not cache_file.exists():
            return False
        
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
            
            cached_time = data.get('cached_at', 0)
            current_time = time.time()
            
            # Check if cache is within valid duration
            age_seconds = current_time - cached_time
            
            return age_seconds < self.cache_duration
            
        except Exception as e:
            print(f"Error reading cache: {e}")
            return False
    
    def get_cached_games(self, steam_id: str) -> Optional[List[Dict]]:
        """Get games from cache if valid"""
        if not self.is_cache_valid(steam_id):
            return None
        
        try:
            cache_file = self.get_cache_file(steam_id)
            with open(cache_file, 'r') as f:
                data = json.load(f)
            
            return data.get('games', [])
            
        except Exception as e:
            print(f"Error loading cached games: {e}")
            return None
    
    def cache_games(self, steam_id: str, games: List[Dict]) -> bool:
        """Cache games data"""
        try:
            cache_file = self.get_cache_file(steam_id)
            
            cache_data = {
                'steam_id': steam_id,
                'cached_at': time.time(),
                'game_count': len(games),
                'games': games
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            print(f"✅ Cached {len(games)} games for Steam ID {steam_id}")
            return True
            
        except Exception as e:
            print(f"Error caching games: {e}")
            return False
    
    def get_cache_info(self, steam_id: str) -> Dict:
        """Get information about cached data"""
        cache_file = self.get_cache_file(steam_id)
        
        if not cache_file.exists():
            return {
                'exists': False,
                'cached_at': None,
                'game_count': 0,
                'age_hours': 0,
                'is_valid': False
            }
        
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
            
            cached_time = data.get('cached_at', 0)
            current_time = time.time()
            age_seconds = current_time - cached_time
            age_hours = age_seconds / 3600
            
            return {
                'exists': True,
                'cached_at': cached_time,
                'game_count': data.get('game_count', 0),
                'age_hours': age_hours,
                'is_valid': self.is_cache_valid(steam_id)
            }
            
        except Exception as e:
            print(f"Error getting cache info: {e}")
            return {
                'exists': False,
                'cached_at': None,
                'game_count': 0,
                'age_hours': 0,
                'is_valid': False
            }
    
    def clear_cache(self, steam_id: str = None) -> bool:
        """Clear cache for specific user or all users"""
        try:
            if steam_id:
                # Clear specific user's cache
                cache_file = self.get_cache_file(steam_id)
                if cache_file.exists():
                    cache_file.unlink()
                    print(f"✅ Cleared cache for Steam ID {steam_id}")
                else:
                    print(f"No cache found for Steam ID {steam_id}")
            else:
                # Clear all cache files
                cache_files = list(self.cache_dir.glob("games_*.json"))
                for cache_file in cache_files:
                    cache_file.unlink()
                print(f"✅ Cleared {len(cache_files)} cache files")
            
            return True
            
        except Exception as e:
            print(f"Error clearing cache: {e}")
            return False
    
    def update_game_playtime(self, steam_id: str, appid: int, new_playtime: int) -> bool:
        """Update playtime for a specific game in cache"""
        try:
            games = self.get_cached_games(steam_id)
            if not games:
                return False
            
            # Find and update the game
            for game in games:
                if game.get('appid') == appid:
                    game['playtime_forever'] = new_playtime
                    break
            else:
                return False  # Game not found
            
            # Re-cache the updated data
            return self.cache_games(steam_id, games)
            
        except Exception as e:
            print(f"Error updating game playtime: {e}")
            return False
    
    def add_new_game(self, steam_id: str, game_data: Dict) -> bool:
        """Add a new game to cached data"""
        try:
            games = self.get_cached_games(steam_id)
            if games is None:
                return False
            
            # Check if game already exists
            appid = game_data.get('appid')
            for existing_game in games:
                if existing_game.get('appid') == appid:
                    return False  # Game already exists
            
            # Add new game
            games.append(game_data)
            
            # Re-cache
            return self.cache_games(steam_id, games)
            
        except Exception as e:
            print(f"Error adding new game: {e}")
            return False

class SmartSteamLoader:
    """Smart Steam library loader with caching"""
    
    def __init__(self, api_key: str, steam_id: str):
        self.api_key = api_key
        self.steam_id = steam_id
        self.cache = SteamGameCache()
    
    def load_games(self, force_refresh: bool = False) -> List[Dict]:
        """Load games with smart caching"""
        
        # Check cache first (unless force refresh)
        if not force_refresh:
            cached_games = self.cache.get_cached_games(self.steam_id)
            if cached_games is not None:
                print(f"📄 Using cached games ({len(cached_games)} games)")
                return cached_games
        
        # Load from API
        print("📡 Loading games from Steam API...")
        games = self._load_from_api()
        
        if games:
            # Cache the results
            self.cache.cache_games(self.steam_id, games)
        
        return games
    
    def _load_from_api(self) -> List[Dict]:
        """Load games from Steam Web API"""
        try:
            url = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
            params = {
                'key': self.api_key,
                'steamid': self.steam_id,
                'format': 'json',
                'include_appinfo': 1,
                'include_played_free_games': 1
            }
            
            response = requests.get(url, params=params, timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                steam_games = data.get('response', {}).get('games', [])
                
                # Convert to our format
                games = []
                for game in steam_games:
                    games.append({
                        'appid': game['appid'],
                        'name': game['name'],
                        'playtime_forever': game.get('playtime_forever', 0),
                        'img_icon_url': game.get('img_icon_url', ''),
                        'img_logo_url': game.get('img_logo_url', ''),
                        'last_played': game.get('rtime_last_played', 0)
                    })
                
                return games
            else:
                raise Exception(f"Steam API error: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"Error loading from Steam API: {e}")
            return []
    
    def get_cache_status(self) -> Dict:
        """Get cache status information"""
        return self.cache.get_cache_info(self.steam_id)
    
    def clear_cache(self) -> bool:
        """Clear cache for this user"""
        return self.cache.clear_cache(self.steam_id)
    
    def refresh_cache(self) -> List[Dict]:
        """Force refresh cache from API"""
        return self.load_games(force_refresh=True)

def test_cache_system():
    """Test the cache system"""
    print("🧪 Testing Steam Game Cache System")
    print("=" * 50)
    
    # Example usage
    cache = SteamGameCache()
    
    # Test data
    test_steam_id = "76561198123456789"
    test_games = [
        {"appid": 1091500, "name": "Cyberpunk 2077", "playtime_forever": 12000},
        {"appid": 1145360, "name": "Hades", "playtime_forever": 8500},
        {"appid": 418370, "name": "Fallout 4", "playtime_forever": 15000}
    ]
    
    # Test caching
    print("1. Testing cache storage...")
    cache.cache_games(test_steam_id, test_games)
    
    # Test cache retrieval
    print("2. Testing cache retrieval...")
    cached_games = cache.get_cached_games(test_steam_id)
    print(f"   Retrieved {len(cached_games) if cached_games else 0} games from cache")
    
    # Test cache info
    print("3. Testing cache info...")
    info = cache.get_cache_info(test_steam_id)
    print(f"   Cache exists: {info['exists']}")
    print(f"   Game count: {info['game_count']}")
    print(f"   Age: {info['age_hours']:.2f} hours")
    print(f"   Is valid: {info['is_valid']}")
    
    print("\n✅ Cache system test complete!")

if __name__ == "__main__":
    test_cache_system()
