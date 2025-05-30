#!/usr/bin/env python3
"""
UI Components Module for VAPOR
Handles main UI setup, menus, and display screens
"""

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from pathlib import Path
import requests
import io
from threading import Thread
import time


class MainUIManager:
    """Manages the main UI components and screens"""
    
    def __init__(self, parent_app):
        self.app = parent_app
        self.root = parent_app.root
    
    def setup_main_ui(self):
        """Setup the main application UI structure"""
        # Main header with VAPOR logo
        self.app.header_frame = tk.Frame(self.root, bg='#2c2f33', height=100)
        self.app.header_frame.pack(fill='x', padx=10, pady=5)
        self.app.header_frame.pack_propagate(False)
        
        # Load and display VAPOR logo
        try:
            logo_paths = [
                Path("assets/Vapor_Logo.png"),  # New assets directory
                Path("Vapor_Logo.png"),  # Legacy location
                Path(sys.executable).parent / "assets" / "Vapor_Logo.png",  # Next to exe in assets
                Path(sys.executable).parent / "Vapor_Logo.png",  # Next to exe (legacy)
                Path(__file__).parent.parent / "assets" / "Vapor_Logo.png",  # Relative to script
            ]
            
            logo_found = False
            for logo_path in logo_paths:
                if logo_path.exists():
                    logo_image = Image.open(logo_path)
                    # Resize logo to fit header (max height 80px)
                    logo_height = 80
                    aspect_ratio = logo_image.width / logo_image.height
                    logo_width = int(logo_height * aspect_ratio)
                    logo_image = logo_image.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
                    self.app.logo_photo = ImageTk.PhotoImage(logo_image)
                    
                    logo_label = tk.Label(self.app.header_frame, image=self.app.logo_photo, bg='#2c2f33')
                    logo_label.pack(side='left', padx=25, pady=10)
                    logo_found = True
                    break
            
            if not logo_found:
                # Fallback if logo not found
                title_label = tk.Label(self.app.header_frame, text="VAPOR", 
                                      font=("Arial", 18, "bold"), fg='#ffffff', bg='#2c2f33')
                title_label.pack(side='left', padx=25, pady=20)
        except Exception as e:
            print(f"Error loading logo: {e}")
            # Fallback title
            title_label = tk.Label(self.app.header_frame, text="VAPOR", 
                                  font=("Arial", 18, "bold"), fg='#ffffff', bg='#2c2f33')
            title_label.pack(side='left', padx=25, pady=20)
        
        # Subtitle with line break for better spacing
        subtitle_label = tk.Label(self.app.header_frame, text="Visual Artwork Processing\n& Organization Resource", 
                                 font=("Arial", 10), fg='#99aab5', bg='#2c2f33', justify='left')
        subtitle_label.pack(side='left', padx=(10, 0), pady=15)
        
        # Profile indicator and switcher
        profile_frame = tk.Frame(self.app.header_frame, bg='#2c2f33')
        profile_frame.pack(side='left', padx=(50, 0), pady=25)
        
        self.app.profile_label = tk.Label(profile_frame, text="No Profile Selected", 
                                         font=("Arial", 12), fg='#99aab5', bg='#2c2f33')
        self.app.profile_label.pack()
        
        self.app.change_profile_btn = tk.Button(profile_frame, text="Change Profile", 
                                               font=("Arial", 10), bg='#43b581', fg='white',
                                               command=self.show_profile_selection, relief='flat',
                                               padx=10, pady=4, cursor='hand2')
        # Enhanced hover effects
        self.app.change_profile_btn.bind("<Enter>", lambda e: self.app.change_profile_btn.configure(relief='raised'))
        self.app.change_profile_btn.bind("<Leave>", lambda e: self.app.change_profile_btn.configure(relief='flat'))
        self.app.change_profile_btn.pack(pady=(5, 0))
        
        # Game search and author info
        right_frame = tk.Frame(self.app.header_frame, bg='#2c2f33')
        right_frame.pack(side='right', padx=25, pady=25)
        
        # Game search
        search_frame = tk.Frame(right_frame, bg='#2c2f33')
        search_frame.pack(anchor='e')
        
        tk.Label(search_frame, text="Search Game:", font=("Arial", 10), 
                fg='#ffffff', bg='#2c2f33').pack(side='left', padx=(0, 5))
        
        self.app.search_var = tk.StringVar()
        self.app.search_entry = tk.Entry(search_frame, textvariable=self.app.search_var, 
                                        font=("Arial", 10), bg='#36393f', fg='#ffffff',
                                        insertbackground='#ffffff', width=20)
        self.app.search_entry.pack(side='left', padx=(0, 5))
        self.app.search_entry.bind('<Return>', self.app.search_game)
        
        search_btn = tk.Button(search_frame, text="GO", command=self.app.search_game,
                              font=("Arial", 10, "bold"), bg='#43b581', fg='white',
                              relief='flat', padx=12, pady=2, cursor='hand2')
        # Enhanced hover effects
        search_btn.bind("<Enter>", lambda e: search_btn.configure(relief='raised'))
        search_btn.bind("<Leave>", lambda e: search_btn.configure(relief='flat'))
        search_btn.pack(side='left')
        
        # Progress bar area
        self.app.progress_frame = tk.Frame(self.root, bg='#36393f', height=50)
        self.app.progress_frame.pack(fill='x', padx=10, pady=5)
        self.app.progress_frame.pack_propagate(False)
        
        self.app.progress_var = tk.StringVar(value="Welcome to VAPOR - Visual Artwork Processing & Organization Resource")
        self.app.progress_label = tk.Label(self.app.progress_frame, textvariable=self.app.progress_var, 
                                          font=("Arial", 12, "bold"), fg='#ffffff', bg='#36393f')
        self.app.progress_label.pack(pady=15)
        
        # Main content area
        self.app.content_frame = tk.Frame(self.root, bg='#1e2124')
        self.app.content_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Bottom button area - ALWAYS VISIBLE
        self.app.button_frame = tk.Frame(self.root, bg='#2c2f33', height=80)
        self.app.button_frame.pack(fill='x', padx=10, pady=5)
        self.app.button_frame.pack_propagate(False)
    
    def show_main_menu(self):
        """Show the main menu"""
        self.app.clear_content()
        self.app.progress_var.set("Choose an option to get started")
        
        # Main container
        main_frame = tk.Frame(self.app.content_frame, bg='#1e2124')
        main_frame.pack(expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text="🎨 VAPOR Professional", 
                              font=("Arial", 24, "bold"), fg='#ffffff', bg='#1e2124')
        title_label.pack(pady=(100, 50))
        
        subtitle_label = tk.Label(main_frame, text="Transform your Steam library with professional artwork management", 
                                 font=("Arial", 14), fg='#43b581', bg='#1e2124')
        subtitle_label.pack(pady=(0, 50))
        
        # Menu buttons
        button_container = tk.Frame(main_frame, bg='#1e2124')
        button_container.pack(pady=30)
        
        # Profile Management
        profile_btn = tk.Button(button_container, text="👤 Manage Profiles",
                               font=("Arial", 16, "bold"), bg='#7289da', fg='white',
                               command=self.app.main_screens_manager.show_profile_management, relief='flat',
                               padx=40, pady=15, cursor='hand2')
        # Enhanced hover effects
        profile_btn.bind("<Enter>", lambda e: profile_btn.configure(relief='raised'))
        profile_btn.bind("<Leave>", lambda e: profile_btn.configure(relief='flat'))
        profile_btn.pack(pady=10, fill='x')
        
        # Select Profile & Start
        profiles = self.app.profile_manager.load_all_profiles()
        if profiles:
            start_btn = tk.Button(button_container, text="🎮 Select Profile & Start",
                                 font=("Arial", 16, "bold"), bg='#43b581', fg='white',
                                 command=self.show_profile_selection, relief='flat',
                                 padx=40, pady=15, cursor='hand2')
            # Enhanced hover effects
            start_btn.bind("<Enter>", lambda e: start_btn.configure(relief='raised'))
            start_btn.bind("<Leave>", lambda e: start_btn.configure(relief='flat'))
            start_btn.pack(pady=10, fill='x')
        
        # Exit
        exit_btn = tk.Button(button_container, text="❌ Exit",
                            font=("Arial", 16, "bold"), bg='#f04747', fg='white',
                            command=self.root.quit, relief='flat',
                            padx=40, pady=15, cursor='hand2')
        # Enhanced hover effects
        exit_btn.bind("<Enter>", lambda e: exit_btn.configure(relief='raised'))
        exit_btn.bind("<Leave>", lambda e: exit_btn.configure(relief='flat'))
        exit_btn.pack(pady=10, fill='x')
    
    def show_profile_selection(self):
        """Show profile selection for starting artwork management"""
        self.app.clear_content()
        self.app.progress_var.set("Select a profile to start artwork management")
        
        # Main container
        main_frame = tk.Frame(self.app.content_frame, bg='#1e2124')
        main_frame.pack(expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text="🎮 Select Profile", 
                              font=("Arial", 20, "bold"), fg='#ffffff', bg='#1e2124')
        title_label.pack(pady=(50, 30))
        
        # Profiles list
        profiles = self.app.profile_manager.load_all_profiles()
        if profiles:
            profiles_frame = tk.Frame(main_frame, bg='#2c2f33', relief='solid', bd=2)
            profiles_frame.pack(pady=20, padx=50, fill='x')
            
            tk.Label(profiles_frame, text="Choose a profile to continue:", 
                    font=("Arial", 14, "bold"), fg='#ffffff', bg='#2c2f33').pack(pady=(15, 10))
            
            for profile_name, profile_data in profiles.items():
                profile_button = tk.Button(profiles_frame, 
                                         text=f"🔹 {profile_name} ({profile_data.get('steam_id', 'Unknown')})",
                                         font=("Arial", 12), bg='#43b581', fg='white',
                                         command=lambda p=profile_name: self.app.select_profile(p),
                                         relief='flat', padx=20, pady=8, cursor='hand2')
                # Enhanced hover effects
                profile_button.bind("<Enter>", lambda e, btn=profile_button: btn.configure(relief='raised'))
                profile_button.bind("<Leave>", lambda e, btn=profile_button: btn.configure(relief='flat'))
                profile_button.pack(pady=5, padx=20, fill='x')
            
            tk.Label(profiles_frame, text="", bg='#2c2f33').pack(pady=5)
        
        # Buttons
        button_container = tk.Frame(main_frame, bg='#1e2124')
        button_container.pack(pady=30)
        
        back_btn = tk.Button(button_container, text="🏠 Back to Main Menu",
                           font=("Arial", 14, "bold"), bg='#99aab5', fg='white',
                           command=self.show_main_menu, relief='flat',
                           padx=30, pady=12, cursor='hand2')
        # Enhanced hover effects
        back_btn.bind("<Enter>", lambda e: back_btn.configure(relief='raised'))
        back_btn.bind("<Leave>", lambda e: back_btn.configure(relief='flat'))
        back_btn.pack()
