#!/usr/bin/env python3
"""
VAPOR - Visual Artwork Processing & Organization Resource
Professional Steam Grid Artwork Manager

Author: Wesley Ellis - wes@wesellis.com
"""

# Import version information
from version import __version__, __app_name__, __full_name__, get_version_string, get_full_version_info

# Import path management and logging
from vapor_paths import vapor_paths, ensure_vapor_directories
from vapor_logging import log_startup, log_shutdown, log_info, log_error, log_exception, log_warning

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import requests
from PIL import Image, ImageTk
import io
import sys
import os
import subprocess
import psutil
from pathlib import Path
from threading import Thread, Event
import time
import json
import webbrowser
import re
import shutil

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import our modules
from steam_game_cache import SmartSteamLoader, SteamGameCache
from steam_library_analyzer import SteamLibraryAnalyzer
from steamgrid_lib import SteamGridAPI, SteamLibraryManager, ArtworkDownloader
from models.profile import ProfileManager, ProfileDialog
from ui.main_ui import MainUIManager
from ui.main_screens import MainScreensManager
from ui.artwork_display import ArtworkDisplayManager


class VaporArtworkManager:
    def __init__(self, root):
        self.root = root
        self.root.title(get_version_string())
        # Steam Deck optimized resolution (1280x800 native, but use 1200x800 for UI space)
        self.root.geometry("1200x800")
        self.root.configure(bg='#1e2124')
        
        # Set window icon
        self.set_window_icon()
        
        # Initialize professional directory structure
        ensure_vapor_directories()
        log_startup(get_full_version_info())
        log_info("Initializing VAPOR with professional directory structure")
        vapor_paths.print_paths()
        
        # Center window on screen
        self.center_window()
        
        # Make window resizable for different screen sizes
        self.root.minsize(1000, 600)  # Minimum usable size
        
        # Bind to window resize events for responsive design
        self.root.bind('<Configure>', self.on_window_resize)
        
        # Initialize managers with proper paths
        self.profile_manager = ProfileManager(vapor_paths.profiles_dir)
        
        # Initialize UI managers
        self.main_ui_manager = MainUIManager(self)
        self.main_screens_manager = MainScreensManager(self)
        self.artwork_display_manager = ArtworkDisplayManager(self)
        
        # Application state
        self.current_profile = None
        self.games = []
        self.current_game_index = 0
        self.current_game = None
        self.current_artwork_options = {}
        self.processing_active = False
        self.stop_event = Event()
        self.image_refs = []  # Keep image references
        self.selected_artwork = {}  # Track selected artwork: {category: {index: artwork_data}}
        self.auto_enhance_mode = False  # Track auto-enhancement mode
        self.auto_enhance_stats = {}  # Track auto-enhancement statistics
        
        # Component references
        self.steamgrid_api = None
        self.steam_library_manager = None
        self.artwork_downloader = None
        self.steam_loader = None
        
        # Responsive design state
        self.window_width = 1200  # Default width
        self.images_per_row = 4   # Default for Steam Deck
        
        # Initialize directories using professional paths
        self.preview_dir = vapor_paths.artwork_cache_dir
        log_info(f"Artwork cache directory: {self.preview_dir}")
        
        # Log initialization
        log_info(f"VAPOR initialized with {len(self.games) if hasattr(self, 'games') else 0} games loaded")
        
        # Setup UI
        self.main_ui_manager.setup_main_ui()
        self.main_ui_manager.show_main_menu()
        
        # Initialize responsive design after UI is ready
        self.root.after(100, self.initialize_responsive_design)
    
    def center_window(self):
        """Center the window on the screen"""
        # Update to ensure we have accurate dimensions
        self.root.update_idletasks()
        
        # Get window dimensions
        width = 1200
        height = 800
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate center position
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        # Set window position
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        print(f"🖥️ Centered window: {width}x{height} at position ({x}, {y})")
        print(f"🖥️ Screen resolution: {screen_width}x{screen_height}")
        log_info(f"Window centered at {x},{y} on {screen_width}x{screen_height} screen")
    
    def set_window_icon(self):
        """Set the window icon using the VAPOR logo"""
        try:
            # Try to load the icon from various locations
            icon_paths = [
                Path("assets/Vapor_Icon.png"),  # New assets directory
                Path("assets/Vapor_Logo.png"),  # Fallback to logo in assets
                Path("Vapor_Icon.png"),  # Legacy location (current directory)
                Path("Vapor_Logo.png"),  # Legacy logo location
                Path(sys.executable).parent / "assets" / "Vapor_Icon.png",  # Next to .exe in assets
                Path(sys.executable).parent / "Vapor_Icon.png",  # Next to .exe (legacy)
                Path(__file__).parent.parent / "assets" / "Vapor_Icon.png",  # Relative to script in assets
                Path(__file__).parent.parent / "Vapor_Icon.png",  # Relative to script (legacy)
            ]
            
            for icon_path in icon_paths:
                if icon_path.exists():
                    try:
                        # Load and set icon
                        icon_image = Image.open(icon_path)
                        # Convert to appropriate size for icon
                        icon_image = icon_image.resize((32, 32), Image.Resampling.LANCZOS)
                        icon_photo = ImageTk.PhotoImage(icon_image)
                        self.root.iconphoto(True, icon_photo)
                        log_info(f"Window icon set from: {icon_path}")
                        return
                    except Exception as e:
                        log_warning(f"Failed to load icon from {icon_path}: {e}")
                        continue
            
            log_warning("No suitable icon file found - using default icon")
            
        except Exception as e:
            log_error(f"Error setting window icon: {e}")
            # Silently continue - not critical for functionality
    
    def initialize_responsive_design(self):
        """Initialize responsive design based on current window size"""
        # Get current window dimensions
        self.root.update_idletasks()  # Ensure window is fully rendered
        self.window_width = self.root.winfo_width()
        
        # Calculate initial images per row
        if self.window_width >= 1800:
            self.images_per_row = 5
        elif self.window_width >= 1200:
            self.images_per_row = 4
        else:
            self.images_per_row = 3
        
        print(f"🎮 Initialized for {self.window_width}px width → {self.images_per_row} images per row")
    
    def on_window_resize(self, event):
        """Handle window resize events for responsive design"""
        # Only respond to root window resize events
        if event.widget != self.root:
            return
        
        # Update window width and calculate responsive images per row
        self.window_width = event.width
        
        # Calculate optimal images per row based on window width
        # Steam Deck (1200px): 4 images per row
        # Desktop (1920px): 5 images per row
        # Smaller screens: 3 images per row
        if self.window_width >= 1800:
            self.images_per_row = 5
        elif self.window_width >= 1200:
            self.images_per_row = 4
        else:
            self.images_per_row = 3
        
        # Refresh artwork display if currently showing
        if hasattr(self, 'artwork_scroll_frame') and self.artwork_scroll_frame.winfo_exists():
            self.artwork_display_manager.display_artwork_professional()
    
    def clear_content(self):
        """Clear the content and button areas with enhanced memory management"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        for widget in self.button_frame.winfo_children():
            widget.destroy()
        self.image_refs = []  # Clear image references
        self.selected_artwork = {}  # Clear selections
        
        # Enhanced memory management - force garbage collection
        import gc
        gc.collect()
    
    def select_profile(self, profile_name):
        """Select a profile and start the artwork manager"""
        profiles = self.profile_manager.load_all_profiles()
        self.current_profile = profiles[profile_name]
        self.profile_label.config(text=f"Profile: {profile_name}", fg='#43b581')
        
        # Initialize components with enhanced performance
        self.steam_loader = SmartSteamLoader(
            api_key=self.current_profile['steam_web_api_key'],
            steam_id=self.current_profile['steam_id']
        )
        
        self.steamgrid_api = SteamGridAPI(self.current_profile['steamgrid_api_key'])
        
        # Optional: Check for updates (non-blocking)
        self.check_for_updates_if_enabled()
        
        # Use 32-bit Steam ID for folder detection
        steam_id_32 = self.current_profile.get('steam_id_32', self.current_profile['steam_id'])
        self.steam_library_manager = SteamLibraryManager(user_id=steam_id_32)
        self.artwork_downloader = ArtworkDownloader(self.preview_dir)
        
        # Save as active profile using proper path
        active_profile_file = vapor_paths.active_profile_file
        with open(active_profile_file, 'w') as f:
            f.write(profile_name)
        log_info(f"Active profile set to: {profile_name}")
        log_info(f"Profile file: {active_profile_file}")
        
        # Start the artwork manager
        self.show_artwork_manager()
    
    def show_artwork_manager(self):
        """Show the main artwork management interface"""
        self.clear_content()
        
        # Check cache status first
        cache_status = self.steam_loader.get_cache_status()
        
        if cache_status['exists'] and cache_status['is_valid']:
            self.progress_var.set(f"📄 Using cached games ({cache_status['game_count']} games, {cache_status['age_hours']:.1f}h old)")
            self.load_from_cache()
        else:
            self.progress_var.set("Loading your Steam games from API...")
            self.load_steam_games()
    
    def load_from_cache(self):
        """Load games from cache"""
        def load_thread():
            try:
                games = self.steam_loader.load_games(force_refresh=False)
                if games:
                    self.games = sorted(games, key=lambda x: x['playtime_forever'], reverse=True)
                    self.root.after(0, self.main_screens_manager.show_artwork_interface)
                else:
                    self.root.after(0, self.main_screens_manager.show_error_screen)
            except Exception as e:
                self.root.after(0, lambda: self.main_screens_manager.show_error_screen(str(e)))
        
        Thread(target=load_thread, daemon=True).start()
    
    def load_steam_games(self):
        """Load games from Steam API"""
        def load_thread():
            try:
                games = self.steam_loader.load_games(force_refresh=True)
                if games:
                    self.games = sorted(games, key=lambda x: x['playtime_forever'], reverse=True)
                    self.root.after(0, self.main_screens_manager.show_artwork_interface)
                else:
                    self.root.after(0, self.main_screens_manager.show_error_screen)
            except Exception as e:
                self.root.after(0, lambda: self.main_screens_manager.show_error_screen(str(e)))
        
        Thread(target=load_thread, daemon=True).start()
    
    def refresh_games_from_api(self):
        """Force refresh games from Steam API"""
        self.progress_var.set("🔄 Refreshing games from Steam API...")
        
        # Clear the current interface to show we're loading
        self.clear_content()
        
        # Show loading screen
        loading_frame = tk.Frame(self.content_frame, bg='#1e2124')
        loading_frame.pack(expand=True)
        
        title_label = tk.Label(loading_frame, text="🔄 Refreshing from Steam API", 
                              font=("Arial", 18, "bold"), fg='#43b581', bg='#1e2124')
        title_label.pack(pady=(150, 30))
        
        status_label = tk.Label(loading_frame, text="Fetching fresh game data from Steam...", 
                               font=("Arial", 12), fg='#ffffff', bg='#1e2124')
        status_label.pack(pady=10)
        
        # Progress bar
        progress_bar = ttk.Progressbar(loading_frame, mode='indeterminate', length=400)
        progress_bar.pack(pady=20)
        progress_bar.start()
        
        # Then load the games
        self.load_steam_games()
    
    def start_artwork_processing(self):
        """Start processing artwork for games"""
        if not self.games:
            messagebox.showwarning("No Games", "Please load your Steam games first")
            return
        
        # Initialize processing state
        self.processing_active = True
        self.stop_event.clear()
        self.current_game_index = 0
        self.selected_artwork = {}
        
        # Start processing the first game
        self.process_next_game()
    
    def start_auto_enhance_all(self):
        """Start auto-enhancement mode - automatically process all games with best artwork"""
        if not self.games:
            messagebox.showwarning("No Games", "Please load your Steam games first")
            return
        
        # Process ALL games (not just played ones) for comprehensive enhancement
        total_games = len(self.games)
        
        # Calculate more accurate time estimate based on actual performance
        estimated_seconds = total_games * 1.5  # 1.5 seconds per game average
        estimated_minutes = int(estimated_seconds // 60)
        
        if estimated_minutes < 1:
            time_text = f"{int(estimated_seconds)} seconds"
        elif estimated_minutes < 60:
            time_text = f"{estimated_minutes} minutes"
        else:
            hours = estimated_minutes // 60
            mins = estimated_minutes % 60
            time_text = f"{hours}h {mins}m"
        
        confirm_text = f"""🚀 Auto-Enhance All Games

This will automatically install the best artwork for ALL {total_games} games in your library.

• Grid images (vertical & horizontal)
• Hero banners
• Logo overlays  
• Game icons

This includes both played and unplayed games for complete library enhancement.
Estimated time: {time_text} (about 1-2 seconds per game).

Do you want to continue?"""
        
        if not messagebox.askyesno("Confirm Auto-Enhancement", confirm_text):
            return
        
        # Initialize auto-enhancement state
        self.processing_active = True
        self.auto_enhance_mode = True
        self.stop_event.clear()
        self.current_game_index = 0
        self.selected_artwork = {}
        self.auto_enhance_stats = {
            'processed': 0,
            'skipped': 0,
            'successful': 0,
            'failed': 0,
            'total_games': total_games
        }
        
        # Show auto-enhance progress screen
        self.main_screens_manager.show_auto_enhance_progress()
        
        # Start auto-processing
        self.auto_process_next_game()
    
    def auto_process_next_game(self):
        """Auto-process the next game in the queue"""
        if not self.processing_active or self.stop_event.is_set():
            return
        
        # Process ALL games (no playtime filtering)
        while self.current_game_index < len(self.games):
            game = self.games[self.current_game_index]
                
            # Process this game
            self.current_game = game
            game_name = game['name']
            appid = game['appid']
            
            # Update progress
            self.auto_enhance_stats['processed'] += 1
            progress_text = f"Processing game {self.auto_enhance_stats['processed']}/{self.auto_enhance_stats['total_games']}: {game_name}"
            self.progress_var.set(progress_text)
            
            # Update auto-enhance screen
            self.main_screens_manager.update_auto_enhance_progress(game_name, self.auto_enhance_stats)
            
            # Start artwork search for auto-installation
            Thread(target=self.auto_search_and_install, args=(appid, game_name), daemon=True).start()
            return
        
        # All games processed - show final performance summary with optimizations
        if self.steamgrid_api:
            print(f"\n=== Final Performance Summary (Enhanced v2.0.1) ===")
            self.steamgrid_api.print_performance_summary()
            
            # Clear cache after big operations to free memory
            self.steamgrid_api.clear_cache()
            
            # Force garbage collection after processing
            import gc
            gc.collect()
        
        self.main_screens_manager.show_auto_enhance_complete(self.auto_enhance_stats)
    
    def auto_search_and_install(self, appid, game_name):
        """
        Search and automatically install best artwork for a game.
        
        This method handles the complete auto-enhancement workflow:
        1. Search for game in SteamGridDB
        2. Fetch artwork for all types (grid, hero, logo, icon)
        3. Select best quality options automatically
        4. Install artwork to Steam library folders
        5. Update statistics and continue to next game
        
        Args:
            appid (int): Steam application ID
            game_name (str): Display name of the game
            
        Returns:
            None: Updates auto_enhance_stats and continues processing
        """
        try:
            print(f"Auto-enhancing {game_name} (AppID: {appid})")
            
            # Search for game in SteamGridDB
            game_data = self.steamgrid_api.search_game(appid)
            
            if not game_data:
                print(f"Game not found in SteamGridDB: {game_name}")
                self.auto_enhance_stats['failed'] += 1
                self.root.after(0, self.continue_auto_processing)
                return
            
            steamgrid_id = game_data.get('id')
            print(f"Found game in SteamGridDB with ID: {steamgrid_id}")
            
            # Get artwork for all types with reasonable limits
            artwork_configs = {
                'grid': {'limit': 20},  # Reduced from 20 - first few are usually best
                'hero': {'limit': 15},  # Reduced from 10
                'logo': {'limit': 20},  # Reduced from 20
                'icon': {'limit': 20}   # Reduced from 20
            }
            
            installations_to_do = []
            
            for art_type, config in artwork_configs.items():
                try:
                    options = self.steamgrid_api.get_artwork(
                        steamgrid_id, art_type, 
                        limit=config['limit']
                    )
                    
                    if options:
                        if art_type == 'grid':
                            # Handle both vertical and horizontal grids
                            vertical_grids = self.artwork_display_manager.filter_vertical_grids(options)
                            horizontal_grids = self.artwork_display_manager.filter_horizontal_grids(options)
                            
                            if vertical_grids:
                                installations_to_do.append(('grid', vertical_grids[0]))
                            if horizontal_grids:
                                installations_to_do.append(('grid_horizontal', horizontal_grids[0]))
                        else:
                            # Use first (highest quality) option
                            installations_to_do.append((art_type, options[0]))
                            
                except Exception as e:
                    print(f"Error getting {art_type} artwork: {e}")
            
            if installations_to_do:
                # Install all artwork
                success_count = 0
                
                for install_type, artwork_option in installations_to_do:
                    try:
                        # Download artwork
                        image_url = artwork_option.get('url', '')
                        if not image_url:
                            print(f"No URL for {install_type} artwork, skipping")
                            continue
                        
                        response = requests.get(image_url, timeout=30)
                        response.raise_for_status()
                        image_data = response.content
                        
                        # Install to Steam library
                        if self.steam_library_manager.install_artwork(appid, install_type, image_data):
                            success_count += 1
                            print(f"✅ Successfully installed {install_type} artwork")
                        else:
                            print(f"⚠️  Failed to install {install_type} to Steam folder")
                            
                    except Exception as e:
                        print(f"❌ Error installing {install_type} artwork: {e}")
                        # Continue with next artwork type (graceful degradation)
                
                if success_count > 0:
                    self.auto_enhance_stats['successful'] += 1
                    print(f"✅ Successfully installed {success_count}/{len(installations_to_do)} artwork pieces for {game_name}")
                else:
                    self.auto_enhance_stats['failed'] += 1
                    print(f"❌ Failed to install artwork for {game_name}")
            else:
                self.auto_enhance_stats['failed'] += 1
                print(f"❌ No artwork found for {game_name}")
                
        except Exception as e:
            print(f"❌ Auto-enhance error for {game_name}: {e}")
            self.auto_enhance_stats['failed'] += 1
        
        # Continue to next game
        self.root.after(0, self.continue_auto_processing)
    
    def continue_auto_processing(self):
        """Continue to the next game in auto-enhancement mode"""
        if hasattr(self, 'auto_enhance_mode') and self.auto_enhance_mode:
            self.current_game_index += 1
            
            # Show performance summary every 10 games
            if self.auto_enhance_stats['processed'] % 10 == 0 and self.steamgrid_api:
                print(f"\n--- Performance Update (After {self.auto_enhance_stats['processed']} games) ---")
                self.steamgrid_api.print_performance_summary()
            
            # Small delay before next game
            self.root.after(1000, self.auto_process_next_game)
    
    def process_next_game(self):
        """Process the next game in the queue"""
        if not self.processing_active or self.stop_event.is_set():
            return
        
        if self.current_game_index >= len(self.games):
            self.main_screens_manager.artwork_processing_complete()
            return
        
        # Clear selections for new game
        self.selected_artwork = {}
        
        # Get current game
        self.current_game = self.games[self.current_game_index]
        game_name = self.current_game['name']
        appid = self.current_game['appid']
        
        self.progress_var.set(f"Processing game {self.current_game_index + 1}/{len(self.games)}: {game_name}")
        
        # Show game processing screen
        self.main_screens_manager.show_game_processing_screen(game_name, appid)
        
        # Start artwork search in background
        Thread(target=self.search_game_artwork, args=(appid, game_name), daemon=True).start()
    
    def search_game_artwork(self, appid, game_name, retry_count=0, max_retries=3):
        """Search for artwork for the current game with enhanced fetching and auto-retry"""
        import time
        start_time = time.time()
        
        try:
            print(f"Searching artwork for {game_name} (AppID: {appid}) - Attempt {retry_count + 1}")
            
            # Update loading message with retry info
            if retry_count > 0:
                self.root.after(0, lambda: self.loading_label.config(text=f"Retrying search... (attempt {retry_count + 1}/{max_retries + 1})"))
            else:
                self.root.after(0, lambda: self.loading_label.config(text="Finding game in SteamGridDB..."))
            
            # Search for game in SteamGridDB
            game_data = self.steamgrid_api.search_game(appid)
            
            if not game_data:
                print(f"Game not found in SteamGridDB: {game_name}")
                self.root.after(0, lambda: self.main_screens_manager.show_no_artwork_found(game_name))
                return
            
            steamgrid_id = game_data.get('id')
            print(f"Found game in SteamGridDB with ID: {steamgrid_id}")
            
            # Search for different types of artwork with enhanced limits + buffer for failures
            artwork_options = {}
            artwork_configs = {
            'grid': {'limit': 40, 'display_limit': 30, 'styles': None, 'types': None},  # Buffer for failures
            'hero': {'limit': 40, 'display_limit': 30, 'styles': None, 'types': None},  # Buffer for failures
            'logo': {'limit': 40, 'display_limit': 30, 'styles': None, 'types': None},  # Buffer for failures
            'icon': {'limit': 40, 'display_limit': 30, 'styles': None, 'types': None}   # Buffer for failures
            }
            
            total_types = len(artwork_configs)
            for index, (art_type, config) in enumerate(artwork_configs.items(), 1):
                self.root.after(0, lambda t=art_type, i=index, total=total_types: 
                                self.loading_label.config(text=f"Searching {t} artwork... ({i}/{total})"))
                
                try:
                    # Use enhanced get_artwork method
                    options = self.steamgrid_api.get_artwork(
                        steamgrid_id, art_type, 
                        styles=config['styles'],
                        types=config['types'],
                        limit=config['limit']
                    )
                    if options:
                        # Filter to display_limit (30) keeping the best quality ones
                        display_limit = config.get('display_limit', 30)
                        if len(options) > display_limit:
                            # Sort by quality metrics (votes, score) and take top 30
                            options = sorted(options, 
                                           key=lambda x: (x.get('votes', 0), x.get('score', 0)), 
                                           reverse=True)[:display_limit]
                        
                        artwork_options[art_type] = options
                        print(f"Found {len(options)} {art_type} options (capped at {display_limit})")
                        # Show immediate feedback for found artwork
                        self.root.after(0, lambda t=art_type, count=len(options), i=index, total=total_types:
                                        self.loading_label.config(text=f"Found {count} {t} options ({i}/{total})"))
                    else:
                        print(f"No {art_type} options found")
                except Exception as e:
                    print(f"Error getting {art_type} artwork: {e}")
                
                # Brief pause for UI feedback
                time.sleep(0.2)
            
            if not artwork_options:
                print(f"No artwork found for {game_name}")
                self.root.after(0, lambda: self.main_screens_manager.show_no_artwork_found(game_name))
                return
            
            # Store artwork options
            self.current_artwork_options = artwork_options
            
            print(f"Showing artwork selection screen...")
            # Performance timing
            elapsed_time = time.time() - start_time
            print(f"Artwork search completed in {elapsed_time:.2f} seconds")
            
            # Show artwork selection screen
            self.root.after(0, self.artwork_display_manager.show_artwork_selection)
            
        except Exception as e:
            print(f"Error searching artwork for {game_name}: {e}")
            import traceback
            traceback.print_exc()
            
            # Check if this is a retry-able error and we haven't exceeded max retries
            if self._should_retry_error(e) and retry_count < max_retries:
                # Enhanced exponential backoff with jitter to prevent thundering herd
                import random
                base_delay = 2 ** retry_count  # Exponential backoff: 1s, 2s, 4s
                jitter = random.uniform(0.5, 1.5)  # Add randomness
                retry_delay = int(base_delay * jitter)
                print(f"Will retry in {retry_delay} seconds with jitter... (attempt {retry_count + 1}/{max_retries})")
                
                # Show user-friendly retry message
                self.root.after(0, lambda: self.loading_label.config(
                    text=f"Network issue detected. Auto-retrying in {retry_delay}s..."))
                
                # Schedule retry with enhanced delay
                self.root.after(retry_delay * 1000, lambda: Thread(
                    target=self.search_game_artwork, 
                    args=(appid, game_name, retry_count + 1, max_retries), 
                    daemon=True).start())
            else:
                # Show final error after all retries exhausted
                error_msg = str(e)
                if retry_count > 0:
                    error_msg = f"Failed after {retry_count + 1} attempts: {error_msg}"
                self.root.after(0, lambda: self.main_screens_manager.show_artwork_error(error_msg))
    
    def _should_retry_error(self, error):
        """Determine if an error should trigger an automatic retry"""
        error_str = str(error).lower()
        
        # Retry-able errors (temporary network/server issues)
        retryable_indicators = [
            'timeout', 'connection', 'network', 'dns', 'resolve',
            'rate limit', '429', '503', '502', '504', '500',
            'temporary', 'unavailable', 'reset', 'refused'
        ]
        
        # Don't retry these (permanent errors)
        permanent_indicators = [
            '401', '403', '404', 'unauthorized', 'forbidden', 
            'not found', 'invalid api key', 'bad request', '400'
        ]
        
        # Check for permanent errors first
        for indicator in permanent_indicators:
            if indicator in error_str:
                return False
        
        # Check for retryable errors
        for indicator in retryable_indicators:
            if indicator in error_str:
                return True
        
        # Default: retry network-related exceptions
        import requests
        return isinstance(error, (requests.RequestException, ConnectionError, TimeoutError))
    
    def toggle_artwork_selection(self, category_key, index, artwork_option):
        """Toggle artwork selection without reloading images"""
        if category_key in self.selected_artwork and self.selected_artwork[category_key]['index'] == index:
            # Deselect
            del self.selected_artwork[category_key]
        else:
            # Select (one per category)
            self.selected_artwork[category_key] = {
                'index': index,
                'artwork': artwork_option
            }
        
        # Update button text
        selected_count = len(self.selected_artwork)
        self.install_selected_btn.config(text=f"🎯 Install Selected ({selected_count})")
        
        # Update selection visuals without reloading images
        self.artwork_display_manager.update_selection_visuals()
    
    def quick_install_artwork(self, category_key, index, artwork_option):
        """Quickly install a single artwork piece via double-click"""
        # Convert category key to installation type
        if category_key == 'grid_vertical':
            install_type = 'grid'
        elif category_key == 'grid_horizontal':
            install_type = 'grid_horizontal'
        else:
            install_type = category_key
        
        # Install just this one piece
        installations_to_do = [(install_type, artwork_option)]
        
        self.main_screens_manager.show_installation_progress(installations_to_do)
        Thread(target=self.install_artwork_thread, args=(installations_to_do,), daemon=True).start()
    
    def search_game(self, event=None):
        """Search for games and show all matches with enhanced context"""
        search_term = self.search_var.get().strip().lower()
        if not search_term or not self.games:
            return
        
        # Find matching games
        matches = []
        for i, game in enumerate(self.games):
            if search_term in game['name'].lower():
                matches.append((i, game))
        
        if matches:
            if len(matches) == 1:
                # Only one match - jump to it
                self.current_game_index = matches[0][0]
                self.current_game = matches[0][1]
                
                if self.processing_active:
                    # Enhanced progress context for search result
                    game_name = matches[0][1]['name']
                    self.progress_var.set(f"Jumped to game {matches[0][0] + 1} of {len(self.games)}: {game_name}")
                    self.process_next_game()
                else:
                    game_name = matches[0][1]['name']
                    messagebox.showinfo("Game Found", 
                                       f"Found: {game_name}\n" +
                                       f"Position: {matches[0][0] + 1} of {len(self.games)}")
            else:
                # Multiple matches - show selection dialog
                self.main_screens_manager.show_game_selection_dialog(matches, search_term)
        else:
            messagebox.showinfo("No Match", f"No games found matching '{search_term}'")
    
    def install_selected_artwork(self):
        """Install the selected artwork pieces"""
        if not self.selected_artwork:
            messagebox.showwarning("No Selection", "Please select some artwork first.")
            return
        
        # Convert selections to installation format
        installations_to_do = []
        for category_key, selection_data in self.selected_artwork.items():
            artwork = selection_data['artwork']
            
            # Convert category key to installation type
            if category_key == 'grid_vertical':
                install_type = 'grid'
            elif category_key == 'grid_horizontal':
                install_type = 'grid_horizontal'
            else:
                install_type = category_key
            
            installations_to_do.append((install_type, artwork))
        
        if installations_to_do:
            self.main_screens_manager.show_installation_progress(installations_to_do)
            Thread(target=self.install_artwork_thread, args=(installations_to_do,), daemon=True).start()
        else:
            self.skip_current_game()
    
    def auto_install_best(self):
        """Automatically install the best artwork for each category"""
        if not self.current_artwork_options:
            self.skip_current_game()
            return
        
        # Select first option from each category
        installations_to_do = []
        
        # Handle grids specially
        grid_options = self.current_artwork_options.get('grid', [])
        if grid_options:
            vertical_grids = self.artwork_display_manager.filter_vertical_grids(grid_options)
            horizontal_grids = self.artwork_display_manager.filter_horizontal_grids(grid_options)
            
            if vertical_grids:
                installations_to_do.append(('grid', vertical_grids[0]))
            if horizontal_grids:
                installations_to_do.append(('grid_horizontal', horizontal_grids[0]))
        
        # Handle other types
        for art_type in ['hero', 'logo', 'icon']:
            options = self.current_artwork_options.get(art_type, [])
            if options:
                installations_to_do.append((art_type, options[0]))
        
        if installations_to_do:
            self.main_screens_manager.show_installation_progress(installations_to_do)
            Thread(target=self.install_artwork_thread, args=(installations_to_do,), daemon=True).start()
        else:
            self.skip_current_game()
    
    def install_artwork_thread(self, installations):
        """Install artwork in background thread with enhanced progress feedback"""
        try:
            appid = self.current_game['appid']
            game_name = self.current_game['name']
            
            print(f"🛠️ Installing artwork for {game_name} (AppID: {appid})")
            
            success_count = 0
            total_count = len(installations)
            
            for index, (art_type, artwork_option) in enumerate(installations, 1):
                # Enhanced progress context
                progress_text = f"Installing {art_type} artwork ({index}/{total_count})..."
                self.root.after(0, lambda t=progress_text: self.install_status_label.config(text=t))
                
                try:
                    # Download artwork
                    image_url = artwork_option.get('url', '')
                    if not image_url:
                        continue
                    
                    response = requests.get(image_url, timeout=30)
                    response.raise_for_status()
                    image_data = response.content
                    
                    # Install to Steam library
                    if self.steam_library_manager.install_artwork(appid, art_type, image_data):
                        success_count += 1
                        print(f"✅ Successfully installed {art_type} artwork ({success_count}/{index})")
                        
                except Exception as e:
                    print(f"❌ Error installing {art_type} artwork: {e}")
                
                time.sleep(0.5)
            
            # Show results with enhanced context
            self.root.after(0, lambda: self.main_screens_manager.show_installation_results(success_count, total_count))
            
        except Exception as e:
            print(f"❌ Installation error: {e}")
            self.root.after(0, lambda: self.main_screens_manager.show_installation_error(str(e)))
    
    def continue_to_next_game(self):
        """Continue to the next game"""
        if self.processing_active and not self.stop_event.is_set():
            self.current_game_index += 1
            self.process_next_game()
    
    def skip_current_game(self):
        """Skip current game and move to next"""
        if not self.processing_active:
            return
        
        self.current_game_index += 1
        self.process_next_game()
    
    def stop_artwork_processing(self):
        """Stop artwork processing"""
        self.processing_active = False
        self.stop_event.set()
        self.main_screens_manager.show_artwork_interface()
    
    def refresh_profile_list(self):
        """Refresh the profile listbox"""
        self.profile_listbox.delete(0, tk.END)
        profiles = self.profile_manager.load_all_profiles()
        
        if not profiles:
            self.profile_listbox.insert(tk.END, "No profiles found. Create one to get started!")
        else:
            for name, profile in profiles.items():
                steam_id = profile.get('steam_id', 'Unknown')
                display_text = f"{name} (Steam ID: {steam_id})"
                self.profile_listbox.insert(tk.END, display_text)
    
    def create_profile_dialog(self):
        """Show profile creation dialog"""
        dialog = ProfileDialog(self.root, "Create New Profile", self.profile_manager)
        self.root.wait_window(dialog.dialog)
        self.refresh_profile_list()
    
    def edit_profile_dialog(self):
        """Show profile editing dialog"""
        selection = self.profile_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a profile to edit.")
            return
        
        profiles = self.profile_manager.load_all_profiles()
        profile_names = list(profiles.keys())
        selected_name = profile_names[selection[0]]
        
        dialog = ProfileDialog(self.root, "Edit Profile", self.profile_manager, 
                              existing_profile=selected_name, profile_data=profiles[selected_name])
        self.root.wait_window(dialog.dialog)
        self.refresh_profile_list()
    
    def delete_profile_dialog(self):
        """Show profile deletion confirmation"""
        selection = self.profile_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a profile to delete.")
            return
        
        profiles = self.profile_manager.load_all_profiles()
        profile_names = list(profiles.keys())
        selected_name = profile_names[selection[0]]
        
        if messagebox.askyesno("Confirm Deletion", 
                              f"Are you sure you want to delete the profile '{selected_name}'?\n\n" +
                              "This action cannot be undone."):
            if self.profile_manager.delete_profile(selected_name):
                messagebox.showinfo("Success", f"Profile '{selected_name}' deleted successfully.")
                self.refresh_profile_list()
            else:
                messagebox.showerror("Error", f"Failed to delete profile '{selected_name}'.")
    
    def check_for_updates_if_enabled(self):
        """Check for updates in background (non-blocking)"""
        def check_updates():
            try:
                from version import check_for_updates
                update_info = check_for_updates()
                
                if update_info.get('update_available', False):
                    def show_update_notification():
                        latest = update_info['latest_version']
                        download_url = update_info['download_url']
                        
                        result = messagebox.askyesno(
                            "Update Available",
                            f"VAPOR v{latest} is available!\n\n"
                            f"You're running v2.0.1\n"
                            f"Would you like to download the update?",
                            icon='info'
                        )
                        
                        if result:
                            webbrowser.open(download_url)
                    
                    # Show notification in main thread
                    self.root.after(0, show_update_notification)
            except Exception:
                # Fail silently - don't interrupt user experience
                pass
        
        # Run in background thread
        Thread(target=check_updates, daemon=True).start()
    
    def test_profile_apis(self):
        """Test APIs for selected profile"""
        selection = self.profile_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a profile to test.")
            return
        
        profiles = self.profile_manager.load_all_profiles()
        profile_names = list(profiles.keys())
        selected_name = profile_names[selection[0]]
        profile_data = profiles[selected_name]
        
        # Test APIs
        steam_result = self.test_steam_api(profile_data)
        steamgrid_result = self.test_steamgrid_api(profile_data)
        
        # Show results
        result_text = f"API Test Results for '{selected_name}':\n\n"
        result_text += f"Steam Web API: {'✅ PASS' if steam_result['success'] else '❌ FAIL'}\n"
        if not steam_result['success']:
            result_text += f"  Error: {steam_result['message']}\n"
        
        result_text += f"SteamGridDB API: {'✅ PASS' if steamgrid_result['success'] else '❌ FAIL'}\n"
        if not steamgrid_result['success']:
            result_text += f"  Error: {steamgrid_result['message']}\n"
        
        if steam_result['success'] and steamgrid_result['success']:
            result_text += "\n🎉 All tests passed! This profile is ready to use."
        else:
            result_text += "\n⚠️ Some tests failed. Please check your API keys and settings."
        
        messagebox.showinfo("API Test Results", result_text)
    
    def test_steam_api(self, profile_data):
        """Test Steam Web API"""
        try:
            steam_id = profile_data.get('steam_id', '')
            api_key = profile_data.get('steam_web_api_key', '')
            
            url = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
            params = {
                'key': api_key,
                'steamid': steam_id,
                'format': 'json',
                'include_appinfo': 1,
                'include_played_free_games': 1
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                games = data.get('response', {}).get('games', [])
                return {'success': True, 'message': f"Found {len(games)} games"}
            elif response.status_code == 429:
                return {'success': False, 'message': "Rate limited - try again later"}
            elif response.status_code == 403:
                return {'success': False, 'message': "Steam profile is private"}
            elif response.status_code == 401:
                return {'success': False, 'message': "Invalid Steam API key"}
            else:
                return {'success': False, 'message': f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def test_steamgrid_api(self, profile_data):
        """Test SteamGridDB API"""
        try:
            api_key = profile_data.get('steamgrid_api_key', '')
            
            # Test with a well-known game (Half-Life 2, Steam ID 220)
            url = "https://www.steamgriddb.com/api/v2/games/steam/220"
            headers = {'Authorization': f'Bearer {api_key}'}
            
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success', False):
                    return {'success': True, 'message': "API key valid"}
                else:
                    return {'success': False, 'message': "API returned error"}
            elif response.status_code == 401:
                return {'success': False, 'message': "Invalid SteamGridDB API key"}
            elif response.status_code == 429:
                return {'success': False, 'message': "Rate limited - try again later"}
            elif response.status_code == 403:
                return {'success': False, 'message': "API key lacks permissions"}
            else:
                return {'success': False, 'message': f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {'success': False, 'message': str(e)}


def main():
    """Main entry point"""
    print(f"🚀 Starting {get_full_version_info()}")
    print(f"📅 Build Date: 2025-02-28")
    print(f"🔧 Python Version: {sys.version}")
    print("🎮 Steam Grid Artwork Manager with World-Class Enhancements")
    print("\n" + "="*60)
    
    try:
        root = tk.Tk()
        app = VaporArtworkManager(root)
        
        # Setup shutdown handler
        def on_closing():
            """Handle application shutdown"""
            log_info("User initiated shutdown")
            log_shutdown()
            root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.mainloop()
        
    except KeyboardInterrupt:
        log_info("Application interrupted by user")
        log_shutdown()
    except Exception as e:
        log_exception(f"Unhandled exception in main: {e}")
        log_shutdown()
        raise
    finally:
        print("👋 VAPOR shutdown complete")
        # Final log shutdown in case it wasn't called
        try:
            log_shutdown()
        except:
            pass  # Don't fail on logging issues during shutdown

if __name__ == "__main__":
    main()
