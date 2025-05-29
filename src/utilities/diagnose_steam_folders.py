#!/usr/bin/env python3
"""
Steam Grid Folder Diagnostic Tool
Author: Wesley Ellis - wes@wesellis.com

This tool helps find your Steam grid folder for artwork installation.
"""

import os
from pathlib import Path

def find_steam_grid_folders():
    """Find all possible Steam grid folders on the system"""
    print("🔍 Steam Grid Folder Diagnostic Tool")
    print("=" * 50)
    
    # Load profile to get both Steam IDs
    try:
        import json
        # Try to get the active profile
        try:
            with open('../active_profile.txt', 'r') as f:
                active_profile = f.read().strip()
            with open(f'../user_configs/{active_profile}.json', 'r') as f:
                profile = json.load(f)
        except:
            # Try to find any profile
            config_dir = Path('../user_configs')
            if config_dir.exists():
                for config_file in config_dir.glob('*.json'):
                    with open(config_file, 'r') as f:
                        profile = json.load(f)
                    break
            else:
                raise FileNotFoundError("No profiles found")
        
        steam_id_64 = profile.get('steam_id', '76561197960531009')
        steam_id_32 = profile.get('steam_id_32', '265281')
    except:
        # Fallback values based on console output
        steam_id_64 = "76561197960531009"
        steam_id_32 = "265281"
    
    print(f"Profile Steam ID (64-bit): {steam_id_64}")
    print(f"Profile Steam ID (32-bit): {steam_id_32}")
    print(f"Looking for folder with: {steam_id_32} (32-bit for local files)")
    print()
    
    # Common Steam installation paths
    steam_base_paths = [
        Path.home() / "AppData" / "Local" / "Steam",
        Path("C:/Program Files (x86)/Steam"),
        Path("C:/Program Files/Steam"),
        Path("D:/Steam"),
        Path("E:/Steam"),
        Path("F:/Steam"),
    ]
    
    found_any = False
    
    for base_path in steam_base_paths:
        print(f"🔍 Checking: {base_path}")
        
        if base_path.exists():
            print(f"   ✅ Steam folder exists")
            
            # Check for userdata folder
            userdata_path = base_path / "userdata"
            if userdata_path.exists():
                print(f"   ✅ userdata folder exists: {userdata_path}")
                
                # Check for your specific user ID (32-bit)
                user_folder = userdata_path / steam_id_32
                if user_folder.exists():
                    print(f"   ✅ Your user folder exists: {user_folder}")
                    
                    # Check for config folder
                    config_folder = user_folder / "config"
                    if config_folder.exists():
                        print(f"   ✅ config folder exists: {config_folder}")
                        
                        # Check for grid folder
                        grid_folder = config_folder / "grid"
                        if grid_folder.exists():
                            print(f"   🎯 GRID FOLDER FOUND: {grid_folder}")
                            print(f"   📁 Folder contains {len(list(grid_folder.iterdir()))} files")
                            found_any = True
                        else:
                            print(f"   ❌ grid folder missing: {grid_folder}")
                            print(f"   💡 Creating grid folder...")
                            try:
                                grid_folder.mkdir(parents=True, exist_ok=True)
                                print(f"   ✅ Grid folder created: {grid_folder}")
                                found_any = True
                            except Exception as e:
                                print(f"   ❌ Failed to create grid folder: {e}")
                    else:
                        print(f"   ❌ config folder missing: {config_folder}")
                else:
                    print(f"   ❌ Your user folder missing: {user_folder}")
                    
                # List all user folders found
                print(f"   📂 Found these user folders:")
                try:
                    for user_dir in userdata_path.iterdir():
                        if user_dir.is_dir() and user_dir.name.isdigit():
                            print(f"      - {user_dir.name}")
                except:
                    print(f"      (Could not list user folders)")
                    
            else:
                print(f"   ❌ userdata folder missing: {userdata_path}")
        else:
            print(f"   ❌ Steam folder not found")
        
        print()
    
    print("=" * 50)
    if found_any:
        print("✅ SUCCESS: Found at least one grid folder!")
        print("Your Steam Grid Artwork Manager should now work.")
    else:
        print("❌ PROBLEM: No grid folders found.")
        print()
        print("🔧 SOLUTIONS:")
        print("1. Make sure Steam is installed")
        print("2. Launch Steam at least once to create user folders")
        print("3. Check if your Steam ID is correct in the profile")
        print("4. Try running Steam as administrator once")
        print()
        print("💡 Manual folder creation:")
        print("You can manually create the folder at:")
        for base_path in steam_base_paths:
            if base_path.exists():
                manual_path = base_path / "userdata" / steam_id_32 / "config" / "grid"
                print(f"   {manual_path}")
                break

if __name__ == "__main__":
    find_steam_grid_folders()
    input("\\nPress Enter to close...")
