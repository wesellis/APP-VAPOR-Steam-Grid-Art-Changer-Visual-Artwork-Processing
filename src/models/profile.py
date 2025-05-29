#!/usr/bin/env python3
"""
Profile Management Module for VAPOR
Handles profile creation, editing, deletion, and Steam ID conversion
"""

import json
import re
import time
import webbrowser
from pathlib import Path

# GUI imports
import tkinter as tk
from tkinter import messagebox
import requests


class ProfileManager:
    """Handles profile creation, editing, and deletion"""
    
    def __init__(self, config_dir):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
    
    def load_all_profiles(self):
        """Load all existing profiles"""
        profiles = {}
        if self.config_dir.exists():
            for config_file in self.config_dir.glob("*.json"):
                try:
                    with open(config_file, 'r') as f:
                        profile = json.load(f)
                        profiles[config_file.stem] = profile
                except Exception as e:
                    print(f"Error loading profile {config_file}: {e}")
        return profiles
    
    def save_profile(self, name, profile_data):
        """Save a profile to disk"""
        profile_path = self.config_dir / f"{name}.json"
        try:
            with open(profile_path, 'w') as f:
                json.dump(profile_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving profile {name}: {e}")
            return False
    
    def delete_profile(self, name):
        """Delete a profile"""
        profile_path = self.config_dir / f"{name}.json"
        try:
            if profile_path.exists():
                profile_path.unlink()
            return True
        except Exception as e:
            print(f"Error deleting profile {name}: {e}")
            return False
    
    def convert_steam_id(self, steam_id_input):
        """Convert Steam ID to both 64-bit and 32-bit formats"""
        steam_id_str = str(steam_id_input).strip()
        
        # If it's a URL, extract the ID
        url_match = re.search(r'steamcommunity\.com/profiles/(\d+)', steam_id_str)
        if url_match:
            steam_id_str = url_match.group(1)
        
        # If it's already 64-bit (17 digits)
        if steam_id_str.isdigit() and len(steam_id_str) == 17:
            steam_id_64 = steam_id_str
            # Convert to 32-bit (subtract the base constant)
            steam_id_32 = str(int(steam_id_64) - 76561197960265728)
        # If it's 32-bit (shorter)
        elif steam_id_str.isdigit() and len(steam_id_str) < 17:
            steam_id_32 = steam_id_str
            # Convert to 64-bit (add the base constant)
            steam_id_64 = str(int(steam_id_32) + 76561197960265728)
        else:
            raise ValueError(f"Invalid Steam ID format: {steam_id_input}")
        
        return steam_id_64, steam_id_32


class ProfileDialog:
    """Dialog for creating/editing profiles"""
    
    def __init__(self, parent, title, profile_manager, existing_profile=None, profile_data=None):
        self.parent = parent
        self.profile_manager = profile_manager
        self.existing_profile = existing_profile
        self.result = None
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("600x700")  # Taller for scrolling
        self.dialog.configure(bg='#1e2124')
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (700 // 2)
        self.dialog.geometry(f"600x700+{x}+{y}")
        
        self.setup_dialog()
        
        # Load existing data if editing
        if profile_data:
            self.load_profile_data(profile_data)
    
    def setup_dialog(self):
        """Setup the profile dialog"""
        # Title
        title_label = tk.Label(self.dialog, text="👤 Profile Configuration", 
                              font=("Arial", 18, "bold"), fg='#ffffff', bg='#1e2124')
        title_label.pack(pady=(20, 30))
        
        # Create main container with scrollbar
        main_container = tk.Frame(self.dialog, bg='#1e2124')
        main_container.pack(fill='both', expand=True, padx=30, pady=(0, 20))
        
        # Canvas and scrollbar for scrolling
        canvas = tk.Canvas(main_container, bg='#2c2f33', highlightthickness=0)
        scrollbar_dialog = tk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg='#2c2f33')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_dialog.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar_dialog.pack(side="right", fill="y")
        
        # Form frame
        form_frame = tk.Frame(self.scrollable_frame, bg='#2c2f33', relief='solid', bd=2)
        form_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Profile name
        tk.Label(form_frame, text="Profile Name:", font=("Arial", 12, "bold"), 
                fg='#ffffff', bg='#2c2f33').pack(anchor='w', padx=20, pady=(20, 5))
        
        self.name_var = tk.StringVar()
        self.name_entry = tk.Entry(form_frame, textvariable=self.name_var, font=("Arial", 11), 
                                  bg='#36393f', fg='#ffffff', insertbackground='#ffffff')
        self.name_entry.pack(fill='x', padx=20, pady=(0, 15))
        
        # Steam ID
        tk.Label(form_frame, text="Steam ID (64-bit or profile URL):", font=("Arial", 12, "bold"), 
                fg='#ffffff', bg='#2c2f33').pack(anchor='w', padx=20, pady=(0, 5))
        
        # Steam ID help
        steam_id_help = tk.Label(form_frame, 
                                text="Find yours at: https://steamcommunity.com/my/profile (look in URL) or https://steamid.io", 
                                font=("Arial", 9), fg='#43b581', bg='#2c2f33', cursor='hand2')
        steam_id_help.pack(anchor='w', padx=20)
        steam_id_help.bind("<Button-1>", lambda e: webbrowser.open("https://steamid.io"))
        
        self.steam_id_var = tk.StringVar()
        self.steam_id_entry = tk.Entry(form_frame, textvariable=self.steam_id_var, font=("Arial", 11), 
                                      bg='#36393f', fg='#ffffff', insertbackground='#ffffff')
        self.steam_id_entry.pack(fill='x', padx=20, pady=(5, 15))
        
        # Steam Web API Key
        tk.Label(form_frame, text="Steam Web API Key:", font=("Arial", 12, "bold"), 
                fg='#ffffff', bg='#2c2f33').pack(anchor='w', padx=20, pady=(0, 5))
        
        api_help = tk.Label(form_frame, text="Get yours at: https://steamcommunity.com/dev/apikey", 
                           font=("Arial", 9), fg='#43b581', bg='#2c2f33', cursor='hand2')
        api_help.pack(anchor='w', padx=20)
        api_help.bind("<Button-1>", lambda e: webbrowser.open("https://steamcommunity.com/dev/apikey"))
        
        self.steam_api_var = tk.StringVar()
        self.steam_api_entry = tk.Entry(form_frame, textvariable=self.steam_api_var, font=("Arial", 11), 
                                       bg='#36393f', fg='#ffffff', insertbackground='#ffffff')
        self.steam_api_entry.pack(fill='x', padx=20, pady=(5, 15))
        
        # SteamGridDB API Key
        tk.Label(form_frame, text="SteamGridDB API Key:", font=("Arial", 12, "bold"), 
                fg='#ffffff', bg='#2c2f33').pack(anchor='w', padx=20, pady=(0, 5))
        
        grid_help = tk.Label(form_frame, text="Get yours at: https://www.steamgriddb.com/profile/preferences/api", 
                            font=("Arial", 9), fg='#43b581', bg='#2c2f33', cursor='hand2')
        grid_help.pack(anchor='w', padx=20)
        grid_help.bind("<Button-1>", lambda e: webbrowser.open("https://www.steamgriddb.com/profile/preferences/api"))
        
        self.grid_api_var = tk.StringVar()
        self.grid_api_entry = tk.Entry(form_frame, textvariable=self.grid_api_var, font=("Arial", 11), 
                                      bg='#36393f', fg='#ffffff', insertbackground='#ffffff')
        self.grid_api_entry.pack(fill='x', padx=20, pady=(5, 30))
        
        # Additional instructions
        instructions_text = """📝 Instructions:
• Profile Name: Choose any name to identify this profile
• Steam ID: Your 17-digit Steam ID or profile URL
• Steam Web API: Required to load your game library
• SteamGridDB API: Required to download artwork

🔒 Your API keys are stored locally and never shared."""
        
        instructions_label = tk.Label(form_frame, text=instructions_text, 
                                     font=("Arial", 10), fg='#99aab5', bg='#2c2f33',
                                     justify='left', wraplength=500)
        instructions_label.pack(anchor='w', padx=20, pady=(0, 20))
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Buttons
        button_frame = tk.Frame(self.dialog, bg='#1e2124')
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="💾 Save Profile", command=self.save_profile,
                 font=("Arial", 14, "bold"), bg='#43b581', fg='white', relief='flat',
                 padx=30, pady=12, cursor='hand2').pack(side='left', padx=15)
        
        tk.Button(button_frame, text="❌ Cancel", command=self.dialog.destroy,
                 font=("Arial", 14, "bold"), bg='#f04747', fg='white', relief='flat',
                 padx=30, pady=12, cursor='hand2').pack(side='left', padx=15)
    
    def load_profile_data(self, profile_data):
        """Load existing profile data into form"""
        self.name_var.set(profile_data.get('profile_name', ''))
        self.steam_id_var.set(profile_data.get('steam_id', ''))
        self.steam_api_var.set(profile_data.get('steam_web_api_key', ''))
        self.grid_api_var.set(profile_data.get('steamgrid_api_key', ''))
    
    def save_profile(self):
        """Save the profile with enhanced validation and error recovery"""
        # Enhanced input validation with specific error messages
        validation_errors = self.validate_all_inputs()
        if validation_errors:
            error_message = "Please fix the following issues:\n\n" + "\n".join(f"• {error}" for error in validation_errors)
            messagebox.showerror("Validation Errors", error_message)
            return
        
        # Get validated inputs
        name = self.name_var.get().strip()
        steam_id = self.steam_id_var.get().strip()
        steam_api = self.steam_api_var.get().strip()
        grid_api = self.grid_api_var.get().strip()
        
        # Convert Steam ID with enhanced error handling
        try:
            steam_id_64, steam_id_32 = self.profile_manager.convert_steam_id(steam_id)
        except ValueError as e:
            messagebox.showerror("Invalid Steam ID", 
                f"Steam ID validation failed:\n{str(e)}\n\nPlease check your Steam ID format and try again.")
            return
        
        # Check for duplicate names (if not editing existing)
        existing_profiles = self.profile_manager.load_all_profiles()
        if self.existing_profile != name and name in existing_profiles:
            messagebox.showerror("Duplicate Name", 
                f"A profile named '{name}' already exists.\n\nPlease choose a different name.")
            return
        
        # Create profile data
        profile_data = {
            'profile_name': name,
            'steam_id': steam_id_64,
            'steam_id_32': steam_id_32,
            'steam_web_api_key': steam_api,
            'steamgrid_api_key': grid_api,
            'created_date': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Delete old profile if renaming
        if self.existing_profile and self.existing_profile != name:
            self.profile_manager.delete_profile(self.existing_profile)
        
        # Save profile with enhanced error handling
        if self.profile_manager.save_profile(name, profile_data):
            messagebox.showinfo("Success", f"Profile '{name}' saved successfully!\n\nYou can now select this profile to start processing.")
            self.result = name
            self.dialog.destroy()
        else:
            messagebox.showerror("Save Error", 
                f"Failed to save profile '{name}'.\n\nPlease check file permissions and try again.")
    
    def validate_all_inputs(self):
        """Enhanced validation with specific error messages"""
        errors = []
        
        # Profile name validation
        name = self.name_var.get().strip()
        if not name:
            errors.append("Profile name is required")
        elif len(name) < 2:
            errors.append("Profile name must be at least 2 characters")
        elif len(name) > 50:
            errors.append("Profile name must be 50 characters or less")
        elif not re.match(r'^[a-zA-Z0-9_\-\s]+$', name):
            errors.append("Profile name can only contain letters, numbers, spaces, hyphens, and underscores")
        
        # Steam ID validation
        steam_id = self.steam_id_var.get().strip()
        if not steam_id:
            errors.append("Steam ID is required")
        elif not self.is_valid_steam_id_format(steam_id):
            errors.append("Steam ID must be 17 digits, shorter number, or steamcommunity.com profile URL")
        
        # Steam API key validation
        steam_api = self.steam_api_var.get().strip()
        if not steam_api:
            errors.append("Steam Web API Key is required")
        elif len(steam_api) != 32 or not re.match(r'^[A-Fa-f0-9]+$', steam_api):
            errors.append("Steam Web API Key must be 32 hexadecimal characters")
        
        # SteamGridDB API key validation
        grid_api = self.grid_api_var.get().strip()
        if not grid_api:
            errors.append("SteamGridDB API Key is required")
        elif len(grid_api) < 20 or len(grid_api) > 100:
            errors.append("SteamGridDB API Key appears to be invalid length")
        
        return errors
    
    def is_valid_steam_id_format(self, steam_id):
        """Check if Steam ID has valid format"""
        steam_id = steam_id.strip()
        
        # Check for Steam profile URL
        if 'steamcommunity.com/profiles/' in steam_id:
            url_match = re.search(r'steamcommunity\.com/profiles/(\d+)', steam_id)
            if url_match:
                extracted_id = url_match.group(1)
                return len(extracted_id) == 17 and extracted_id.isdigit()
        
        # Check for direct Steam ID (64-bit or 32-bit)
        if steam_id.isdigit():
            return len(steam_id) == 17 or (len(steam_id) >= 8 and len(steam_id) <= 10)
        
        return False
