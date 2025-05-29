#!/usr/bin/env python3
"""
Main Screens UI Manager for VAPOR
Handles all major interface screens and navigation
"""

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from pathlib import Path
import requests
import io
from threading import Thread
import time


class MainScreensManager:
    """Manages all main application screens and interfaces"""
    
    def __init__(self, parent_app):
        self.app = parent_app
        self.root = parent_app.root
    
    def show_artwork_interface(self):
        """Show the main artwork management interface"""
        self.app.clear_content()
        
        # Welcome screen
        welcome_frame = tk.Frame(self.app.content_frame, bg='#1e2124')
        welcome_frame.pack(expand=True)
        
        title_label = tk.Label(welcome_frame, text="🎨 VAPOR Ready!", 
                              font=("Arial", 20, "bold"), fg='#43b581', bg='#1e2124')
        title_label.pack(pady=(50, 20))
        
        # Calculate game statistics
        total_games = len(self.app.games)
        total_playtime = sum(game['playtime_forever'] for game in self.app.games)
        total_hours = total_playtime // 60
        
        # Most played game
        most_played = self.app.games[0] if self.app.games else None
        most_played_hours = most_played['playtime_forever'] // 60 if most_played else 0
        
        # Games with significant playtime (>1 hour)
        played_games = [g for g in self.app.games if g['playtime_forever'] > 60]
        unplayed_games = total_games - len(played_games)
        
        # Cache status
        cache_status = self.app.steam_loader.get_cache_status()
        cache_info = "📄 Using cached data" if cache_status['is_valid'] else "🌐 Fresh from Steam API"
        
        # Build comprehensive info text
        info_text = f"""
✅ Profile: {self.app.current_profile.get('profile_name', 'Unknown')}
📚 Total Games: {total_games:,} games in library
⏱️ Total Playtime: {total_hours:,} hours ({total_playtime:,} minutes)
🏆 Most Played: {most_played['name'] if most_played else 'None'} ({most_played_hours:,}h)
🎮 Played Games: {len(played_games):,} games (>1 hour)
📦 Unplayed Games: {unplayed_games:,} games (ready for artwork!)
{cache_info} - {cache_status.get('age_hours', 0):.1f} hours old

🎯 Ready to enhance your Steam library with professional artwork!

Games are sorted by playtime - most played first.
Click 'Start Processing' to begin installing artwork.
        """
        
        info_label = tk.Label(welcome_frame, text=info_text, 
                             font=("Arial", 11), fg='#ffffff', bg='#1e2124',
                             justify='center')
        info_label.pack(pady=15)
        
        # Control buttons
        controls_frame = tk.Frame(self.app.button_frame, bg='#2c2f33')
        controls_frame.pack(fill='x', pady=10)
        
        start_btn = tk.Button(controls_frame, text="🎮 Start Processing Games",
                             font=("Arial", 14, "bold"), bg='#43b581', fg='white',
                             command=self.app.start_artwork_processing, relief='flat',
                             padx=30, pady=12, cursor='hand2')
        # Enhanced hover effects
        start_btn.bind("<Enter>", lambda e: start_btn.configure(relief='raised'))
        start_btn.bind("<Leave>", lambda e: start_btn.configure(relief='flat'))
        start_btn.pack(side='left', padx=10)
        
        auto_enhance_btn = tk.Button(controls_frame, text="🚀 Auto-Enhance All Games",
                                   font=("Arial", 14, "bold"), bg='#9b59b6', fg='white',
                                   command=self.app.start_auto_enhance_all, relief='flat',
                                   padx=30, pady=12, cursor='hand2')
        # Enhanced hover effects
        auto_enhance_btn.bind("<Enter>", lambda e: auto_enhance_btn.configure(relief='raised'))
        auto_enhance_btn.bind("<Leave>", lambda e: auto_enhance_btn.configure(relief='flat'))
        auto_enhance_btn.pack(side='left', padx=10)
        
        # Show refresh button if using cached data
        cache_status = self.app.steam_loader.get_cache_status()
        if cache_status['is_valid']:
            tk.Button(controls_frame, text="🔄 Refresh from Steam API",
                     font=("Arial", 12, "bold"), bg='#faa61a', fg='white',
                     command=self.app.refresh_games_from_api, relief='flat',
                     padx=20, pady=12, cursor='hand2').pack(side='left', padx=10)
        
        tk.Button(controls_frame, text="🏠 Main Menu",
                 font=("Arial", 14, "bold"), bg='#99aab5', fg='white',
                 command=self.app.main_ui_manager.show_main_menu, relief='flat',
                 padx=30, pady=12, cursor='hand2').pack(side='right', padx=10)
    
    def show_game_processing_screen(self, game_name, appid):
        """Show game processing screen"""
        self.app.clear_content()
        
        # Main container
        main_frame = tk.Frame(self.app.content_frame, bg='#1e2124')
        main_frame.pack(expand=True)
        
        # Game info
        title_label = tk.Label(main_frame, text=f"🎮 {game_name}", 
                              font=("Arial", 20, "bold"), fg='#ffffff', bg='#1e2124')
        title_label.pack(pady=(100, 20))
        
        info_label = tk.Label(main_frame, text=f"Steam App ID: {appid}", 
                             font=("Arial", 12), fg='#99aab5', bg='#1e2124')
        info_label.pack(pady=5)
        
        # Loading message
        self.app.loading_label = tk.Label(main_frame, text="🔍 Searching for artwork...", 
                                         font=("Arial", 14), fg='#43b581', bg='#1e2124')
        self.app.loading_label.pack(pady=30)
        
        # Progress bar
        self.app.artwork_progress = ttk.Progressbar(main_frame, mode='indeterminate', length=400)
        self.app.artwork_progress.pack(pady=20)
        self.app.artwork_progress.start()
        
        # Control buttons
        controls_frame = tk.Frame(self.app.button_frame, bg='#2c2f33')
        controls_frame.pack(fill='x', pady=10)
        
        tk.Button(controls_frame, text="⏭️ Skip This Game",
                 font=("Arial", 12, "bold"), bg='#faa61a', fg='white',
                 command=self.app.skip_current_game, relief='flat',
                 padx=20, pady=8, cursor='hand2').pack(side='left', padx=10)
        
        tk.Button(controls_frame, text="🛑 Stop Processing",
                 font=("Arial", 12, "bold"), bg='#f04747', fg='white',
                 command=self.app.stop_artwork_processing, relief='flat',
                 padx=20, pady=8, cursor='hand2').pack(side='left', padx=10)
    
    def show_no_artwork_found(self, game_name):
        """Show when no artwork is found"""
        if hasattr(self.app, 'artwork_progress') and self.app.artwork_progress:
            self.app.artwork_progress.stop()
        
        self.app.clear_content()
        
        no_art_frame = tk.Frame(self.app.content_frame, bg='#1e2124')
        no_art_frame.pack(expand=True)
        
        title_label = tk.Label(no_art_frame, text="❌ No Artwork Found", 
                              font=("Arial", 18, "bold"), fg='#f04747', bg='#1e2124')
        title_label.pack(pady=(150, 30))
        
        info_text = f"""Game: {game_name}

This game was not found in SteamGridDB's database.
This can happen with very new games or obscure titles.

Click 'Next Game' to continue."""
        
        info_label = tk.Label(no_art_frame, text=info_text, 
                             font=("Arial", 12), fg='#ffffff', bg='#1e2124',
                             justify='center')
        info_label.pack(pady=20)
        
        # Control buttons
        controls_frame = tk.Frame(self.app.button_frame, bg='#2c2f33')
        controls_frame.pack(fill='x', pady=10)
        
        tk.Button(controls_frame, text="⏭️ Next Game",
                 font=("Arial", 12, "bold"), bg='#43b581', fg='white',
                 command=self.app.skip_current_game, relief='flat',
                 padx=20, pady=8, cursor='hand2').pack(side='left', padx=10)
        
        tk.Button(controls_frame, text="🛑 Stop Processing",
                 font=("Arial", 12, "bold"), bg='#f04747', fg='white',
                 command=self.app.stop_artwork_processing, relief='flat',
                 padx=20, pady=8, cursor='hand2').pack(side='left', padx=10)
    
    def show_artwork_error(self, error_message):
        """Show artwork search error"""
        if hasattr(self.app, 'artwork_progress') and self.app.artwork_progress:
            self.app.artwork_progress.stop()
        
        self.app.clear_content()
        
        error_frame = tk.Frame(self.app.content_frame, bg='#1e2124')
        error_frame.pack(expand=True)
        
        title_label = tk.Label(error_frame, text="❌ Artwork Search Error", 
                              font=("Arial", 18, "bold"), fg='#f04747', bg='#1e2124')
        title_label.pack(pady=(150, 30))
        
        error_text = f"""An error occurred while searching for artwork:

{error_message}

Click 'Next Game' to continue."""
        
        error_label = tk.Label(error_frame, text=error_text, 
                              font=("Arial", 12), fg='#ffffff', bg='#1e2124',
                              justify='center')
        error_label.pack(pady=20)
        
        # Control buttons
        controls_frame = tk.Frame(self.app.button_frame, bg='#2c2f33')
        controls_frame.pack(fill='x', pady=10)
        
        tk.Button(controls_frame, text="⏭️ Next Game",
                 font=("Arial", 12, "bold"), bg='#43b581', fg='white',
                 command=self.app.skip_current_game, relief='flat',
                 padx=20, pady=8, cursor='hand2').pack(side='left', padx=10)
        
        tk.Button(controls_frame, text="🛑 Stop Processing",
                 font=("Arial", 12, "bold"), bg='#f04747', fg='white',
                 command=self.app.stop_artwork_processing, relief='flat',
                 padx=20, pady=8, cursor='hand2').pack(side='left', padx=10)
    
    def show_error_screen(self, error="Unknown error"):
        """Show error screen"""
        self.app.clear_content()
        
        error_frame = tk.Frame(self.app.content_frame, bg='#1e2124')
        error_frame.pack(expand=True)
        
        title_label = tk.Label(error_frame, text="❌ Error", 
                              font=("Arial", 18, "bold"), fg='#f04747', bg='#1e2124')
        title_label.pack(pady=(150, 30))
        
        error_label = tk.Label(error_frame, text=f"An error occurred:\n\n{error}", 
                              font=("Arial", 12), fg='#ffffff', bg='#1e2124',
                              justify='center')
        error_label.pack(pady=20)
        
        tk.Button(error_frame, text="🏠 Back to Main Menu",
                 font=("Arial", 12, "bold"), bg='#99aab5', fg='white',
                 command=self.app.main_ui_manager.show_main_menu, relief='flat',
                 padx=20, pady=8, cursor='hand2').pack(pady=20)
    
    def show_profile_management(self):
        """Show profile management interface"""
        self.app.clear_content()
        self.app.progress_var.set("Manage your profiles")
        
        # Main container
        main_frame = tk.Frame(self.app.content_frame, bg='#1e2124')
        main_frame.pack(expand=True, fill='both')
        
        # Title
        title_label = tk.Label(main_frame, text="👤 Profile Management", 
                              font=("Arial", 20, "bold"), fg='#ffffff', bg='#1e2124')
        title_label.pack(pady=(30, 20))
        
        # Profiles list frame
        list_frame = tk.Frame(main_frame, bg='#2c2f33', relief='solid', bd=2)
        list_frame.pack(fill='both', expand=True, padx=50, pady=20)
        
        # Profiles list with scrollbar
        list_header = tk.Label(list_frame, text="Existing Profiles:", 
                              font=("Arial", 16, "bold"), fg='#ffffff', bg='#2c2f33')
        list_header.pack(pady=(15, 10))
        
        # Scrollable frame for profiles
        scroll_container = tk.Frame(list_frame, bg='#2c2f33')
        scroll_container.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        scrollbar = tk.Scrollbar(scroll_container)
        scrollbar.pack(side='right', fill='y')
        
        self.app.profile_listbox = tk.Listbox(scroll_container, yscrollcommand=scrollbar.set,
                                             font=("Arial", 12), bg='#36393f', fg='#ffffff',
                                             selectbackground='#43b581', height=10)
        self.app.profile_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.app.profile_listbox.yview)
        
        # Load profiles into listbox
        self.app.refresh_profile_list()
        
        # Buttons
        button_frame = tk.Frame(self.app.button_frame, bg='#2c2f33')
        button_frame.pack(fill='x', pady=10)
        
        # Profile action buttons
        tk.Button(button_frame, text="➕ Create New Profile",
                 font=("Arial", 12, "bold"), bg='#43b581', fg='white',
                 command=self.app.create_profile_dialog, relief='flat',
                 padx=20, pady=8, cursor='hand2').pack(side='left', padx=5)
        
        tk.Button(button_frame, text="✏️ Edit Profile",
                 font=("Arial", 12, "bold"), bg='#faa61a', fg='white',
                 command=self.app.edit_profile_dialog, relief='flat',
                 padx=20, pady=8, cursor='hand2').pack(side='left', padx=5)
        
        tk.Button(button_frame, text="🗑️ Delete Profile",
                 font=("Arial", 12, "bold"), bg='#f04747', fg='white',
                 command=self.app.delete_profile_dialog, relief='flat',
                 padx=20, pady=8, cursor='hand2').pack(side='left', padx=5)
        
        tk.Button(button_frame, text="🧪 Test APIs",
                 font=("Arial", 12, "bold"), bg='#9b59b6', fg='white',
                 command=self.app.test_profile_apis, relief='flat',
                 padx=20, pady=8, cursor='hand2').pack(side='left', padx=5)
        
        tk.Button(button_frame, text="🏠 Back to Main Menu",
                 font=("Arial", 12, "bold"), bg='#99aab5', fg='white',
                 command=self.app.main_ui_manager.show_main_menu, relief='flat',
                 padx=20, pady=8, cursor='hand2').pack(side='right', padx=10)
    
    def show_installation_progress(self, installations):
        """Show artwork installation progress"""
        self.app.clear_content()
        
        install_frame = tk.Frame(self.app.content_frame, bg='#1e2124')
        install_frame.pack(expand=True)
        
        game_name = self.app.current_game['name']
        title_label = tk.Label(install_frame, text=f"🛠️ Installing Artwork for {game_name}", 
                              font=("Arial", 18, "bold"), fg='#43b581', bg='#1e2124')
        title_label.pack(pady=(150, 30))
        
        self.app.install_status_label = tk.Label(install_frame, text="Preparing installation...", 
                                               font=("Arial", 12), fg='#ffffff', bg='#1e2124')
        self.app.install_status_label.pack(pady=20)
        
        # Progress bar
        self.app.install_progress = ttk.Progressbar(install_frame, mode='indeterminate', length=400)
        self.app.install_progress.pack(pady=20)
        self.app.install_progress.start()
    
    def show_installation_results(self, success_count, total_count):
        """Show installation results"""
        if hasattr(self.app, 'install_progress'):
            self.app.install_progress.stop()
        
        self.app.clear_content()
        
        results_frame = tk.Frame(self.app.content_frame, bg='#1e2124')
        results_frame.pack(expand=True)
        
        game_name = self.app.current_game['name']
        
        if success_count == total_count:
            title_text = f"✅ Artwork Installed Successfully!"
            title_color = '#43b581'
            result_text = f"All {success_count} artwork pieces were installed for {game_name}"
        elif success_count > 0:
            title_text = f"⚠️ Partial Installation"
            title_color = '#faa61a'
            result_text = f"{success_count} of {total_count} artwork pieces were installed for {game_name}"
        else:
            title_text = f"❌ Installation Failed"
            title_color = '#f04747'
            result_text = f"No artwork could be installed for {game_name}"
        
        title_label = tk.Label(results_frame, text=title_text, 
                              font=("Arial", 18, "bold"), fg=title_color, bg='#1e2124')
        title_label.pack(pady=(150, 30))
        
        result_label = tk.Label(results_frame, text=result_text, 
                               font=("Arial", 12), fg='#ffffff', bg='#1e2124')
        result_label.pack(pady=20)
        
        # Continue to next game after 2 seconds
        self.root.after(2000, self.app.continue_to_next_game)
    
    def show_installation_error(self, error_message):
        """Show installation error"""
        if hasattr(self.app, 'install_progress'):
            self.app.install_progress.stop()
        
        self.app.clear_content()
        
        error_frame = tk.Frame(self.app.content_frame, bg='#1e2124')
        error_frame.pack(expand=True)
        
        title_label = tk.Label(error_frame, text="❌ Installation Error", 
                              font=("Arial", 18, "bold"), fg='#f04747', bg='#1e2124')
        title_label.pack(pady=(150, 30))
        
        error_text = f"Installation failed: {error_message}"
        error_label = tk.Label(error_frame, text=error_text, 
                              font=("Arial", 12), fg='#ffffff', bg='#1e2124')
        error_label.pack(pady=20)
        
        # Continue to next game after 2 seconds
        self.root.after(2000, self.app.continue_to_next_game)
    
    def artwork_processing_complete(self):
        """Show processing completion"""
        self.app.processing_active = False
        
        self.app.clear_content()
        
        complete_frame = tk.Frame(self.app.content_frame, bg='#1e2124')
        complete_frame.pack(expand=True)
        
        title_label = tk.Label(complete_frame, text="🎉 Processing Complete!", 
                              font=("Arial", 20, "bold"), fg='#43b581', bg='#1e2124')
        title_label.pack(pady=(150, 30))
        
        success_text = f"""Congratulations! You've processed all {len(self.app.games)} games.

Your Steam library now has enhanced artwork!

🚀 You can now restart Steam to see your new artwork."""
        
        success_label = tk.Label(complete_frame, text=success_text, 
                                font=("Arial", 12), fg='#ffffff', bg='#1e2124',
                                justify='center')
        success_label.pack(pady=20)
        
        # Control buttons
        controls_frame = tk.Frame(self.app.button_frame, bg='#2c2f33')
        controls_frame.pack(fill='x', pady=10)
        
        tk.Button(controls_frame, text="🏠 Main Menu",
                 font=("Arial", 12, "bold"), bg='#99aab5', fg='white',
                 command=self.app.main_ui_manager.show_main_menu, relief='flat',
                 padx=20, pady=8, cursor='hand2').pack(side='left', padx=10)
    
    def show_game_selection_dialog(self, matches, search_term):
        """Show dialog to select from multiple game matches"""
        # Create selection dialog
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Select Game - '{search_term}'")
        dialog.geometry("600x400")
        dialog.configure(bg='#1e2124')
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (dialog.winfo_screenheight() // 2) - (400 // 2)
        dialog.geometry(f"600x400+{x}+{y}")
        
        # Title
        title_label = tk.Label(dialog, text=f"Found {len(matches)} games matching '{search_term}'", 
                              font=("Arial", 16, "bold"), fg='#ffffff', bg='#1e2124')
        title_label.pack(pady=20)
        
        # Scrollable list
        list_frame = tk.Frame(dialog, bg='#2c2f33')
        list_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        
        listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                            font=("Arial", 12), bg='#36393f', fg='#ffffff',
                            selectbackground='#43b581', height=15)
        listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=listbox.yview)
        
        # Populate list
        for i, (game_index, game) in enumerate(matches):
            playtime = game['playtime_forever'] // 60
            display_text = f"{game['name']} ({playtime}h played) - Position {game_index + 1}"
            listbox.insert(tk.END, display_text)
        
        # Buttons
        button_frame = tk.Frame(dialog, bg='#1e2124')
        button_frame.pack(pady=20)
        
        def select_game():
            selection = listbox.curselection()
            if selection:
                selected_match = matches[selection[0]]
                self.app.current_game_index = selected_match[0]
                self.app.current_game = selected_match[1]
                
                if self.app.processing_active:
                    dialog.destroy()
                    self.app.process_next_game()
                else:
                    dialog.destroy()
                    messagebox.showinfo("Game Selected", 
                                       f"Selected: {selected_match[1]['name']}\n" +
                                       f"Position: {selected_match[0] + 1} of {len(self.app.games)}")
            else:
                messagebox.showwarning("No Selection", "Please select a game from the list.")
        
        tk.Button(button_frame, text="🎮 Select Game", command=select_game,
                 font=("Arial", 12, "bold"), bg='#43b581', fg='white',
                 relief='flat', padx=20, pady=8, cursor='hand2').pack(side='left', padx=10)
        
        tk.Button(button_frame, text="❌ Cancel", command=dialog.destroy,
                 font=("Arial", 12, "bold"), bg='#f04747', fg='white',
                 relief='flat', padx=20, pady=8, cursor='hand2').pack(side='left', padx=10)
        
        # Double-click to select
        listbox.bind('<Double-1>', lambda e: select_game())
    
    def show_auto_enhance_progress(self):
        """Show auto-enhancement progress screen"""
        self.app.clear_content()
        
        # Main container
        main_frame = tk.Frame(self.app.content_frame, bg='#1e2124')
        main_frame.pack(expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text="🚀 Auto-Enhancing Your Library", 
                              font=("Arial", 20, "bold"), fg='#9b59b6', bg='#1e2124')
        title_label.pack(pady=(80, 30))
        
        # Current game info
        self.app.auto_current_game_label = tk.Label(main_frame, text="Preparing to start...", 
                                                   font=("Arial", 16, "bold"), fg='#ffffff', bg='#1e2124')
        self.app.auto_current_game_label.pack(pady=10)
        
        # Progress stats frame
        stats_frame = tk.Frame(main_frame, bg='#2c2f33', relief='solid', bd=2)
        stats_frame.pack(pady=20, padx=50, fill='x')
        
        stats_title = tk.Label(stats_frame, text="Progress Statistics", 
                              font=("Arial", 14, "bold"), fg='#ffffff', bg='#2c2f33')
        stats_title.pack(pady=(10, 5))
        
        # Stats labels
        self.app.auto_processed_label = tk.Label(stats_frame, text="Processed: 0", 
                                                font=("Arial", 12), fg='#43b581', bg='#2c2f33')
        self.app.auto_processed_label.pack(pady=2)
        
        self.app.auto_successful_label = tk.Label(stats_frame, text="Successful: 0", 
                                                 font=("Arial", 12), fg='#43b581', bg='#2c2f33')
        self.app.auto_successful_label.pack(pady=2)
        
        self.app.auto_failed_label = tk.Label(stats_frame, text="Failed/No Artwork: 0", 
                                              font=("Arial", 12), fg='#faa61a', bg='#2c2f33')
        self.app.auto_failed_label.pack(pady=2)
        
        self.app.auto_skipped_label = tk.Label(stats_frame, text="Skipped (0 playtime): 0", 
                                              font=("Arial", 12), fg='#99aab5', bg='#2c2f33')
        self.app.auto_skipped_label.pack(pady=(2, 10))
        
        # Progress bar
        self.app.auto_progress = ttk.Progressbar(main_frame, mode='indeterminate', length=500)
        self.app.auto_progress.pack(pady=20)
        self.app.auto_progress.start()
        
        # Status message
        self.app.auto_status_label = tk.Label(main_frame, text="Starting auto-enhancement...", 
                                             font=("Arial", 12), fg='#ffffff', bg='#1e2124')
        self.app.auto_status_label.pack(pady=10)
        
        # Control buttons
        controls_frame = tk.Frame(self.app.button_frame, bg='#2c2f33')
        controls_frame.pack(fill='x', pady=10)
        
        tk.Button(controls_frame, text="🛑 Stop Auto-Enhancement",
                 font=("Arial", 12, "bold"), bg='#f04747', fg='white',
                 command=self.stop_auto_enhancement, relief='flat',
                 padx=20, pady=8, cursor='hand2').pack(side='left', padx=10)
    
    def update_auto_enhance_progress(self, current_game, stats):
        """Update the auto-enhancement progress display"""
        if hasattr(self.app, 'auto_current_game_label'):
            self.app.auto_current_game_label.config(text=f"🎮 Now Processing: {current_game}")
        
        if hasattr(self.app, 'auto_processed_label'):
            self.app.auto_processed_label.config(text=f"Processed: {stats['processed']}/{stats['total_games']}")
        
        if hasattr(self.app, 'auto_successful_label'):
            self.app.auto_successful_label.config(text=f"Successful: {stats['successful']}")
        
        if hasattr(self.app, 'auto_failed_label'):
            self.app.auto_failed_label.config(text=f"Failed/No Artwork: {stats['failed']}")
        
        if hasattr(self.app, 'auto_skipped_label'):
            self.app.auto_skipped_label.config(text=f"Skipped (0 playtime): {stats['skipped']}")
        
        if hasattr(self.app, 'auto_status_label'):
            self.app.auto_status_label.config(text=f"Processing {current_game}...")
    
    def show_auto_enhance_complete(self, stats):
        """Show auto-enhancement completion screen"""
        if hasattr(self.app, 'auto_progress'):
            self.app.auto_progress.stop()
        
        self.app.processing_active = False
        self.app.auto_enhance_mode = False
        
        self.app.clear_content()
        
        complete_frame = tk.Frame(self.app.content_frame, bg='#1e2124')
        complete_frame.pack(expand=True)
        
        # Success title
        title_label = tk.Label(complete_frame, text="🎉 Auto-Enhancement Complete!", 
                              font=("Arial", 20, "bold"), fg='#43b581', bg='#1e2124')
        title_label.pack(pady=(80, 30))
        
        # Results summary
        success_rate = (stats['successful'] / stats['processed'] * 100) if stats['processed'] > 0 else 0
        
        results_text = f"""🏆 Enhancement Results:

✅ Successfully Enhanced: {stats['successful']} games
❌ Failed/No Artwork: {stats['failed']} games
⏭️ Skipped (0 playtime): {stats['skipped']} games
📊 Success Rate: {success_rate:.1f}%

🚀 Your Steam library has been enhanced!
Restart Steam to see your new artwork."""
        
        results_label = tk.Label(complete_frame, text=results_text, 
                                font=("Arial", 14), fg='#ffffff', bg='#1e2124',
                                justify='center')
        results_label.pack(pady=20)
        
        # Control buttons
        controls_frame = tk.Frame(self.app.button_frame, bg='#2c2f33')
        controls_frame.pack(fill='x', pady=10)
        
        tk.Button(controls_frame, text="🎆 View Library",
                 font=("Arial", 12, "bold"), bg='#43b581', fg='white',
                 command=self.app.main_ui_manager.show_main_menu, relief='flat',
                 padx=20, pady=8, cursor='hand2').pack(side='left', padx=10)
        
        tk.Button(controls_frame, text="🔄 Enhance More Games",
                 font=("Arial", 12, "bold"), bg='#9b59b6', fg='white',
                 command=self.show_artwork_interface, relief='flat',
                 padx=20, pady=8, cursor='hand2').pack(side='left', padx=10)
        
        tk.Button(controls_frame, text="🏠 Main Menu",
                 font=("Arial", 12, "bold"), bg='#99aab5', fg='white',
                 command=self.app.main_ui_manager.show_main_menu, relief='flat',
                 padx=20, pady=8, cursor='hand2').pack(side='right', padx=10)
    
    def stop_auto_enhancement(self):
        """Stop the auto-enhancement process"""
        self.app.processing_active = False
        self.app.auto_enhance_mode = False
        self.app.stop_event.set()
        
        if hasattr(self.app, 'auto_progress'):
            self.app.auto_progress.stop()
        
        # Show confirmation
        messagebox.showinfo("Auto-Enhancement Stopped", 
                           "Auto-enhancement has been stopped.\n\nYou can restart it anytime from the main interface.")
        
        # Return to main interface
        self.show_artwork_interface()
