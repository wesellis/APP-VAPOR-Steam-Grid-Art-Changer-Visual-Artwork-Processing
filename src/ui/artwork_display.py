#!/usr/bin/env python3
"""
Artwork Display UI Manager for VAPOR
Handles artwork selection, browsing, and display interfaces
"""

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import requests
import io
from threading import Thread
import time
import gc


class ArtworkDisplayManager:
    """Manages artwork display and selection interfaces"""
    
    def __init__(self, parent_app):
        self.app = parent_app
        self.root = parent_app.root
    
    def show_artwork_selection(self):
        """Show artwork selection interface with professional section titles"""
        if hasattr(self.app, 'artwork_progress') and self.app.artwork_progress:
            self.app.artwork_progress.stop()
        
        self.app.clear_content()
        
        # Game title
        game_name = self.app.current_game['name']
        title_label = tk.Label(self.app.content_frame, text=f"🎨 Select Artwork for {game_name}", 
                              font=("Arial", 18, "bold"), fg='#ffffff', bg='#1e2124')
        title_label.pack(pady=(10, 5))
        
        # Enhanced progress context
        progress_text = f"Processing game {self.app.current_game_index + 1} of {len(self.app.games)}: {game_name}"
        progress_label = tk.Label(self.app.content_frame, text=progress_text, 
                                 font=("Arial", 12), fg='#99aab5', bg='#1e2124')
        progress_label.pack(pady=5)
        
        # Enhanced instructions with double-click info
        instructions = tk.Label(self.app.content_frame, 
                               text="💡 Click artwork to select (green highlight) or Double-click to instantly install • Use 'Install Selected' for multiple pieces", 
                               font=("Arial", 12), fg='#faa61a', bg='#1e2124')
        instructions.pack(pady=10)
        
        # Create scrollable artwork area with proper canvas setup
        canvas_container = tk.Frame(self.app.content_frame, bg='#1e2124')
        canvas_container.pack(fill='both', expand=True, padx=0, pady=5)
        
        # Canvas and scrollbar
        self.app.artwork_canvas = tk.Canvas(canvas_container, bg='#1e2124', highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_container, orient="vertical", command=self.app.artwork_canvas.yview)
        
        # Scrollable frame that will contain all artwork
        self.app.artwork_scroll_frame = tk.Frame(self.app.artwork_canvas, bg='#1e2124')
        
        # Configure scrolling
        self.app.artwork_scroll_frame.bind(
            "<Configure>",
            lambda e: self.app.artwork_canvas.configure(scrollregion=self.app.artwork_canvas.bbox("all"))
        )
        
        # Create window in canvas
        canvas_window = self.app.artwork_canvas.create_window((0, 0), window=self.app.artwork_scroll_frame, anchor="nw")
        
        # Configure canvas scrolling
        self.app.artwork_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        self.app.artwork_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # CRITICAL: Update canvas window width when canvas resizes
        def configure_canvas_window(event):
            canvas_width = event.width
            self.app.artwork_canvas.itemconfig(canvas_window, width=canvas_width)
        
        self.app.artwork_canvas.bind('<Configure>', configure_canvas_window)
        
        # Mouse wheel scrolling
        def on_mousewheel(event):
            self.app.artwork_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.app.artwork_canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # Display artwork categories with professional titles
        self.display_artwork_professional()
        
        # Control buttons - ALWAYS AT BOTTOM
        controls_frame = tk.Frame(self.app.button_frame, bg='#2c2f33')
        controls_frame.pack(fill='x', pady=10)
        
        auto_install_btn = tk.Button(controls_frame, text="✨ Auto-Install Best",
                                   font=("Arial", 12, "bold"), bg='#43b581', fg='white',
                                   command=self.app.auto_install_best, relief='flat',
                                   padx=20, pady=8, cursor='hand2')
        # Enhanced hover effects
        auto_install_btn.bind("<Enter>", lambda e: auto_install_btn.configure(relief='raised'))
        auto_install_btn.bind("<Leave>", lambda e: auto_install_btn.configure(relief='flat'))
        auto_install_btn.pack(side='left', padx=10)
        
        self.app.install_selected_btn = tk.Button(controls_frame, text="🎯 Install Selected (0)",
                                                 font=("Arial", 12, "bold"), bg='#7289da', fg='white',
                                                 command=self.app.install_selected_artwork, relief='flat',
                                                 padx=20, pady=8, cursor='hand2')
        # Enhanced hover effects
        self.app.install_selected_btn.bind("<Enter>", lambda e: self.app.install_selected_btn.configure(relief='raised'))
        self.app.install_selected_btn.bind("<Leave>", lambda e: self.app.install_selected_btn.configure(relief='flat'))
        self.app.install_selected_btn.pack(side='left', padx=10)
        
        next_btn = tk.Button(controls_frame, text="⏭️ Next Game",
                           font=("Arial", 12, "bold"), bg='#faa61a', fg='white',
                           command=self.app.skip_current_game, relief='flat',
                           padx=20, pady=8, cursor='hand2')
        # Enhanced hover effects
        next_btn.bind("<Enter>", lambda e: next_btn.configure(relief='raised'))
        next_btn.bind("<Leave>", lambda e: next_btn.configure(relief='flat'))
        next_btn.pack(side='left', padx=10)
        
        stop_btn = tk.Button(controls_frame, text="🛑 Stop Processing",
                           font=("Arial", 12, "bold"), bg='#f04747', fg='white',
                           command=self.app.stop_artwork_processing, relief='flat',
                           padx=20, pady=8, cursor='hand2')
        # Enhanced hover effects
        stop_btn.bind("<Enter>", lambda e: stop_btn.configure(relief='raised'))
        stop_btn.bind("<Leave>", lambda e: stop_btn.configure(relief='flat'))
        stop_btn.pack(side='left', padx=10)
    
    def display_artwork_professional(self):
        """Display artwork in 5x2 FULL WIDTH layout for MAXIMUM screen usage"""
        # Clear existing content with memory cleanup
        for widget in self.app.artwork_scroll_frame.winfo_children():
            widget.destroy()
        
        # Force garbage collection after clearing many images
        gc.collect()
        
        # Filter and separate grid images
        grid_options = self.app.current_artwork_options.get('grid', [])
        vertical_grids = [opt for opt in grid_options if opt.get('width') == 600 and opt.get('height') == 900]
        horizontal_grids = []
        for opt in grid_options:
            width = opt.get('width', 0)
            height = opt.get('height', 0)
            if width and height:
                ratio = width / height
                if 2.0 <= ratio <= 2.3:  # Horizontal ratio
                    horizontal_grids.append(opt)
        
        # Simplified artwork category names (user-friendly)
        categories = [
            ('grid_vertical', {'title': 'Vertical Grid Images', 'color': '#43b581', 'options': vertical_grids}),
            ('grid_horizontal', {'title': 'Horizontal Grid Images', 'color': '#4a9eff', 'options': horizontal_grids}),
            ('hero', {'title': 'Hero Images', 'color': '#9b59b6', 'options': self.app.current_artwork_options.get('hero', [])}),
            ('logo', {'title': 'Logo Images', 'color': '#faa61a', 'options': self.app.current_artwork_options.get('logo', [])}),
            ('icon', {'title': 'Icon Images', 'color': '#f04747', 'options': self.app.current_artwork_options.get('icon', [])})
        ]
        
        for category_key, category_info in categories:
            options = category_info['options']
            if options:
                self.create_artwork_section_5x2(category_key, category_info, options)
    
    def create_artwork_section_5x2(self, category_key, category_info, options):
        """Create responsive artwork section that adapts to window size"""
        # Main section frame - ABSOLUTE MINIMAL padding for maximum width usage
        section_frame = tk.Frame(self.app.artwork_scroll_frame, bg='#2c2f33', relief='solid', bd=1)
        section_frame.pack(fill='x', pady=3, padx=2)  # MINIMAL padding
        
        # Header
        header_frame = tk.Frame(section_frame, bg=category_info['color'], height=35)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text=f"🔥 {category_info['title']} ({len(options)} found)",
                              font=("Arial", 12, "bold"), fg='#ffffff', bg=category_info['color'])
        title_label.pack(pady=8)
        
        # Images container - FULL WIDTH with minimal padding
        images_container = tk.Frame(section_frame, bg='#2c2f33')
        images_container.pack(fill='x', padx=2, pady=3)
        
        # RESPONSIVE: Use dynamic images per row based on window size and artwork type
        if category_key == 'grid_vertical':
            images_per_row = 6  # Always 6 for vertical grids for better proportions
        else:
            images_per_row = getattr(self.app, 'images_per_row', 4)  # Default responsive for other types
        total_images = len(options)  # Show ALL images found
        total_rows = (total_images + images_per_row - 1) // images_per_row  # Calculate needed rows
        
        # Create as many rows as needed to show ALL artwork
        for row in range(total_rows):
            row_frame = tk.Frame(images_container, bg='#2c2f33')
            row_frame.pack(fill='x', pady=2)
            
            for col in range(images_per_row):
                image_index = row * images_per_row + col
                if image_index < total_images:  # Show all available images
                    option = options[image_index]
                    self.create_artwork_item_responsive(row_frame, category_key, option, image_index)
    
    def create_artwork_item_responsive(self, parent, category_key, artwork_option, index):
        """Create responsive artwork items that adapt to window size"""
        original_width = artwork_option.get('width', 300)
        original_height = artwork_option.get('height', 200)
        
        # RESPONSIVE WIDTH: Calculate based on window size and images per row
        window_width = getattr(self.app, 'window_width', 1200)
        images_per_row = getattr(self.app, 'images_per_row', 4)
        
        if category_key == 'grid_vertical':
            # Vertical grids: Final 5px wider
            DISPLAY_WIDTH = 171  # 166 + 5px
            DISPLAY_HEIGHT = 257  # 171 × 1.5 = 256.5 → 257px
        else:
            # Other artwork types: Final 5px wider
            if images_per_row == 4:
                DISPLAY_WIDTH = 261  # 256 + 5px
            else:
                DISPLAY_WIDTH = 211  # 206 + 5px
        
        # Calculate heights based on aspect ratios
        if category_key == 'grid_vertical':
            # Height already calculated above
            pass
        elif category_key == 'grid_horizontal':
            # Horizontal 92:43 ratio = 2.14:1
            DISPLAY_HEIGHT = int(DISPLAY_WIDTH / 2.14)
        elif category_key == 'hero':
            # Hero 96:31 ratio = 3.1:1  
            DISPLAY_HEIGHT = int(DISPLAY_WIDTH / 3.1)
        elif category_key == 'icon':
            # Icons 1:1 ratio
            DISPLAY_HEIGHT = DISPLAY_WIDTH
        else:  # logos
            # Logos: maintain aspect ratio, cap at reasonable height
            if original_height > 0:
                aspect_ratio = original_width / original_height
                max_height = int(DISPLAY_WIDTH * 0.8)  # Max 80% of width for logos
                DISPLAY_HEIGHT = min(int(DISPLAY_WIDTH / aspect_ratio), max_height)
            else:
                DISPLAY_HEIGHT = int(DISPLAY_WIDTH * 0.6)
        
        # Create item frame with responsive sizing
        item_frame = tk.Frame(parent, bg='#36393f', relief='solid', bd=2, 
                             width=DISPLAY_WIDTH + 12, height=DISPLAY_HEIGHT + 25)
        # Store category and index for selection updates
        item_frame.artwork_category = category_key
        item_frame.artwork_index = index
        
        # Reduced spacing to fit better
        item_frame.pack(side='left', padx=3, pady=1)  # 6px total spacing (3px each side)
        item_frame.pack_propagate(False)
        
        # Check if selected
        is_selected = (category_key in self.app.selected_artwork and 
                      self.app.selected_artwork[category_key]['index'] == index)
        
        if is_selected:
            item_frame.config(bg='#43b581', bd=3)
        
        # Loading label
        loading_label = tk.Label(item_frame, text="Loading...", 
                                font=("Arial", 9), fg='#ffffff', bg=item_frame.cget('bg'))
        loading_label.pack(expand=True)
        
        # Download and display with connection reuse
        def download_and_display():
            try:
                image_url = artwork_option.get('url', '')
                if not image_url:
                    return
                
                # Use session for connection pooling if available
                session = getattr(self.app, '_image_session', None)
                if not session:
                    session = requests.Session()
                    session.headers.update({'User-Agent': 'VAPOR/2.0'})
                    self.app._image_session = session
                
                response = session.get(image_url, timeout=10, stream=True)
                response.raise_for_status()
                
                image = Image.open(io.BytesIO(response.content))
                image = image.resize((DISPLAY_WIDTH, DISPLAY_HEIGHT), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                
                def update_ui():
                    try:
                        if item_frame.winfo_exists():
                            loading_label.destroy()
                            
                            # Clickable image with double-click installation
                            image_btn = tk.Button(item_frame, image=photo, bg=item_frame.cget('bg'),
                                                command=lambda: self.app.toggle_artwork_selection(category_key, index, artwork_option),
                                                relief='flat', cursor='hand2')
                            # Add double-click for instant installation
                            image_btn.bind("<Double-Button-1>", lambda e: self.app.quick_install_artwork(category_key, index, artwork_option))
                            image_btn.pack(pady=2)
                            image_btn.image = photo
                            self.app.image_refs.append(photo)
                            
                            # Enhanced info label with quality indicators
                            votes = artwork_option.get('votes', 0)
                            score = artwork_option.get('score', 0)
                            if votes > 0 and score > 0:
                                info_text = f"{original_width}×{original_height} • ⭐{score:.1f} ({votes} votes)"
                            else:
                                info_text = f"{original_width}×{original_height}"
                            info_label = tk.Label(item_frame, text=info_text,
                                                 font=("Arial", 7), fg='#99aab5', bg=item_frame.cget('bg'))
                            info_label.pack()
                    except:
                        pass
                
                self.root.after(0, update_ui)
                
            except Exception as e:
                def show_error():
                    try:
                        if item_frame.winfo_exists():
                            loading_label.config(text="Failed", fg='#f04747')
                    except:
                        pass
                self.root.after(0, show_error)
        
        Thread(target=download_and_display, daemon=True).start()
    
    def update_selection_visuals(self):
        """Update visual selection indicators without reloading images"""
        # Walk through all artwork frames and update their selection state
        if hasattr(self.app, 'artwork_scroll_frame') and self.app.artwork_scroll_frame.winfo_exists():
            self._update_frame_selection_recursive(self.app.artwork_scroll_frame)
    
    def _update_frame_selection_recursive(self, parent_frame):
        """Recursively update selection visuals for all artwork frames"""
        for child in parent_frame.winfo_children():
            # Check if this is an artwork item frame
            if hasattr(child, 'artwork_category') and hasattr(child, 'artwork_index'):
                category_key = child.artwork_category
                index = child.artwork_index
                
                # Check if selected
                is_selected = (category_key in self.app.selected_artwork and 
                              self.app.selected_artwork[category_key]['index'] == index)
                
                # Update frame appearance
                if is_selected:
                    child.config(bg='#43b581', bd=3)
                else:
                    child.config(bg='#36393f', bd=2)
                
                # Update any child labels to match background
                for subchild in child.winfo_children():
                    if isinstance(subchild, tk.Label):
                        subchild.config(bg=child.cget('bg'))
            
            # Recursively check children
            self._update_frame_selection_recursive(child)
    
    def create_artwork_item_full_width(self, parent, category_key, artwork_option, index):
        """Create FULL WIDTH artwork items - 355px wide each, perfect screen usage!"""
        original_width = artwork_option.get('width', 300)
        original_height = artwork_option.get('height', 200)
        
        # OPTIMIZED WIDTH: Smaller vertical display now that we show ALL artwork
        DISPLAY_WIDTH = 280  # Reduced from 355px for better grid display
        
        # Calculate heights based on aspect ratios
        if category_key == 'grid_vertical':
            # Vertical 2:3 ratio - smaller for better overview
            DISPLAY_HEIGHT = int(DISPLAY_WIDTH * 1.5)  # 280 * 1.5 = 420px
        elif category_key == 'grid_horizontal':
            # Horizontal 92:43 ratio = 2.14:1
            DISPLAY_HEIGHT = int(DISPLAY_WIDTH / 2.14)  # 280 / 2.14 = 131px
        elif category_key == 'hero':
            # Hero 96:31 ratio = 3.1:1  
            DISPLAY_HEIGHT = int(DISPLAY_WIDTH / 3.1)  # 280 / 3.1 = 90px
        elif category_key == 'icon':
            # Icons 1:1 ratio
            DISPLAY_HEIGHT = DISPLAY_WIDTH  # 280 x 280px - Reasonable icon size
        else:  # logos
            # Logos: maintain aspect ratio, cap at 250px height
            if original_height > 0:
                aspect_ratio = original_width / original_height
                DISPLAY_HEIGHT = min(int(DISPLAY_WIDTH / aspect_ratio), 250)
            else:
                DISPLAY_HEIGHT = 200
        
        # Create item frame with EXACT sizing for full width usage
        item_frame = tk.Frame(parent, bg='#36393f', relief='solid', bd=2, 
                             width=DISPLAY_WIDTH + 12, height=DISPLAY_HEIGHT + 25)
        item_frame.pack(side='left', padx=1, pady=1)  # MINIMAL padding
        item_frame.pack_propagate(False)
        
        # Check if selected
        is_selected = (category_key in self.app.selected_artwork and 
                      self.app.selected_artwork[category_key]['index'] == index)
        
        if is_selected:
            item_frame.config(bg='#43b581', bd=3)
        
        # Loading label
        loading_label = tk.Label(item_frame, text="Loading...", 
                                font=("Arial", 9), fg='#ffffff', bg=item_frame.cget('bg'))
        loading_label.pack(expand=True)
        
        # Download and display with connection reuse
        def download_and_display():
            try:
                image_url = artwork_option.get('url', '')
                if not image_url:
                    return
                
                # Use session for connection pooling if available
                session = getattr(self.app, '_image_session', None)
                if not session:
                    session = requests.Session()
                    session.headers.update({'User-Agent': 'VAPOR/2.0'})
                    self.app._image_session = session
                
                response = session.get(image_url, timeout=10, stream=True)
                response.raise_for_status()
                
                image = Image.open(io.BytesIO(response.content))
                image = image.resize((DISPLAY_WIDTH, DISPLAY_HEIGHT), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                
                def update_ui():
                    try:
                        if item_frame.winfo_exists():
                            loading_label.destroy()
                            
                            # Clickable image with double-click installation
                            image_btn = tk.Button(item_frame, image=photo, bg=item_frame.cget('bg'),
                                                command=lambda: self.app.toggle_artwork_selection(category_key, index, artwork_option),
                                                relief='flat', cursor='hand2')
                            # Add double-click for instant installation
                            image_btn.bind("<Double-Button-1>", lambda e: self.app.quick_install_artwork(category_key, index, artwork_option))
                            image_btn.pack(pady=2)
                            image_btn.image = photo
                            self.app.image_refs.append(photo)
                            
                            # Enhanced info label with quality indicators
                            votes = artwork_option.get('votes', 0)
                            score = artwork_option.get('score', 0)
                            if votes > 0 and score > 0:
                                info_text = f"{original_width}×{original_height} • ⭐{score:.1f} ({votes} votes)"
                            else:
                                info_text = f"{original_width}×{original_height}"
                            info_label = tk.Label(item_frame, text=info_text,
                                                 font=("Arial", 7), fg='#99aab5', bg=item_frame.cget('bg'))
                            info_label.pack()
                    except:
                        pass
                
                self.root.after(0, update_ui)
                
            except Exception as e:
                def show_error():
                    try:
                        if item_frame.winfo_exists():
                            loading_label.config(text="Failed", fg='#f04747')
                    except:
                        pass
                self.root.after(0, show_error)
        
        Thread(target=download_and_display, daemon=True).start()
    
    def filter_vertical_grids(self, grid_options):
        """Filter for vertical grid images (600x900)"""
        return [opt for opt in grid_options if opt.get('width') == 600 and opt.get('height') == 900]
    
    def filter_horizontal_grids(self, grid_options):
        """Filter for horizontal grid images (92:43 ratio, primarily 920x430)"""
        horizontal = []
        for opt in grid_options:
            width = opt.get('width', 0)
            height = opt.get('height', 0)
            if width and height:
                ratio = width / height
                # 92:43 = 2.14, allow some tolerance
                if 2.0 <= ratio <= 2.3:
                    horizontal.append(opt)
        return horizontal
