#!/usr/bin/env python3
"""
VAPOR - Visual Artwork Processing & Organization Resource
Professional Edition v2.0 - Main Launcher

Author: Wesley Ellis - wes@wesellis.com
"""

# VAPOR v2.0 - Distribution Entry Point
from version import get_version_string, get_full_version_info

if __name__ == "__main__":
    print(f"🎆 Welcome to {get_version_string()}!")
    print("🎮 Steam Grid Artwork Manager with Revolutionary Features")
    print("🚀 Auto-Enhance All Games + Performance Optimizations + World-Class Status\n")
    
    # Import and run the main application
    from steam_grid_artwork_manager import main
    main()
