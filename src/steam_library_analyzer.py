#!/usr/bin/env python3
"""
Steam Library Analyzer
Author: Wesley Ellis - wes@wesellis.com

Enhanced Steam library analysis with game details, reviews, and organization features
Inspired by steam_backlog_organizer but using Steam Web API instead of scraping
"""

import requests
import json
import time
from pathlib import Path
from typing import Dict, List, Optional
import csv
from datetime import datetime

class SteamLibraryAnalyzer:
    """Analyzes Steam library with detailed game information"""
    
    def __init__(self, steam_api_key: str, steam_id: str):
        self.steam_api_key = steam_api_key
        self.steam_id = steam_id
        self.detailed_games = []
        
    def get_detailed_library(self, games: List[Dict]) -> List[Dict]:
        """Get detailed information for all games in library"""
        print(f"📊 Analyzing {len(games)} games in detail...")
        
        detailed_games = []
        
        for i, game in enumerate(games, 1):
            print(f"  📋 Analyzing game {i}/{len(games)}: {game['name']}")
            
            detailed_game = self.get_game_details(game)
            detailed_games.append(detailed_game)
            
            # Rate limiting - be nice to Steam API
            time.sleep(0.5)
            
            # Progress update every 50 games
            if i % 50 == 0:
                print(f"    ✅ Processed {i}/{len(games)} games...")
        
        self.detailed_games = detailed_games
        return detailed_games
    
    def get_game_details(self, game: Dict) -> Dict:
        """Get detailed information for a single game"""
        appid = game['appid']
        
        # Start with basic info
        detailed = {
            'appid': appid,
            'name': game['name'],
            'playtime_forever': game.get('playtime_forever', 0),
            'playtime_hours': game.get('playtime_forever', 0) // 60,
            'last_played': game.get('last_played', 0),
            'img_icon_url': game.get('img_icon_url', ''),
            'img_logo_url': game.get('img_logo_url', ''),
        }
        
        # Get additional details from Steam Store API
        try:
            store_data = self.get_store_details(appid)
            if store_data:
                detailed.update(store_data)
        except Exception as e:
            print(f"    ⚠️ Failed to get store details for {game['name']}: {e}")
        
        return detailed
    
    def get_store_details(self, appid: int) -> Optional[Dict]:
        """Get game details from Steam Store API"""
        try:
            url = f"https://store.steampowered.com/api/appdetails"
            params = {'appids': appid, 'format': 'json'}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                app_data = data.get(str(appid), {})
                
                if app_data.get('success') and 'data' in app_data:
                    game_data = app_data['data']
                    
                    return {
                        'type': game_data.get('type', ''),
                        'short_description': game_data.get('short_description', ''),
                        'release_date': game_data.get('release_date', {}).get('date', ''),
                        'coming_soon': game_data.get('release_date', {}).get('coming_soon', False),
                        'developers': ', '.join(game_data.get('developers', [])),
                        'publishers': ', '.join(game_data.get('publishers', [])),
                        'categories': ', '.join([cat.get('description', '') for cat in game_data.get('categories', [])]),
                        'genres': ', '.join([genre.get('description', '') for genre in game_data.get('genres', [])]),
                        'price_initial': game_data.get('price_overview', {}).get('initial', 0) / 100 if game_data.get('price_overview') else 0,
                        'price_current': game_data.get('price_overview', {}).get('final', 0) / 100 if game_data.get('price_overview') else 0,
                        'discount_percent': game_data.get('price_overview', {}).get('discount_percent', 0),
                        'metacritic_score': game_data.get('metacritic', {}).get('score', 0),
                        'recommendations': game_data.get('recommendations', {}).get('total', 0),
                        'required_age': game_data.get('required_age', 0),
                        'platforms_windows': game_data.get('platforms', {}).get('windows', False),
                        'platforms_mac': game_data.get('platforms', {}).get('mac', False),
                        'platforms_linux': game_data.get('platforms', {}).get('linux', False),
                        'achievements_total': game_data.get('achievements', {}).get('total', 0) if game_data.get('achievements') else 0,
                        'steam_url': f"https://store.steampowered.com/app/{appid}/"
                    }
            
        except Exception as e:
            print(f"    ⚠️ Store API error for {appid}: {e}")
        
        return None
    
    def analyze_library(self) -> Dict:
        """Analyze the detailed library and provide insights"""
        if not self.detailed_games:
            return {}
        
        print("📈 Generating library insights...")
        
        total_games = len(self.detailed_games)
        played_games = [g for g in self.detailed_games if g['playtime_hours'] > 0]
        unplayed_games = [g for g in self.detailed_games if g['playtime_hours'] == 0]
        
        total_hours = sum(g['playtime_hours'] for g in self.detailed_games)
        total_value = sum(g.get('price_current', 0) for g in self.detailed_games if g.get('price_current'))
        
        # Genre analysis
        genre_counts = {}
        for game in self.detailed_games:
            genres = game.get('genres', '').split(', ')
            for genre in genres:
                if genre and genre != '':
                    genre_counts[genre] = genre_counts.get(genre, 0) + 1
        
        top_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Developer analysis
        dev_counts = {}
        for game in self.detailed_games:
            devs = game.get('developers', '').split(', ')
            for dev in devs:
                if dev and dev != '':
                    dev_counts[dev] = dev_counts.get(dev, 0) + 1
        
        top_developers = sorted(dev_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Most played games
        most_played = sorted(played_games, key=lambda x: x['playtime_hours'], reverse=True)[:20]
        
        # Highest rated unplayed games
        unplayed_rated = [g for g in unplayed_games if g.get('metacritic_score', 0) > 0]
        highest_rated_unplayed = sorted(unplayed_rated, key=lambda x: x.get('metacritic_score', 0), reverse=True)[:20]
        
        # Games by year
        year_counts = {}
        for game in self.detailed_games:
            release_date = game.get('release_date', '')
            if release_date:
                try:
                    # Extract year from various date formats
                    year = None
                    if ',' in release_date:
                        year = release_date.split(',')[-1].strip()
                    elif len(release_date) >= 4 and release_date[-4:].isdigit():
                        year = release_date[-4:]
                    
                    if year and year.isdigit():
                        year_counts[year] = year_counts.get(year, 0) + 1
                except:
                    pass
        
        top_years = sorted(year_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'total_games': total_games,
            'played_games': len(played_games),
            'unplayed_games': len(unplayed_games),
            'total_hours': total_hours,
            'total_value': total_value,
            'avg_price': total_value / total_games if total_games > 0 else 0,
            'completion_rate': (len(played_games) / total_games * 100) if total_games > 0 else 0,
            'top_genres': top_genres,
            'top_developers': top_developers,
            'most_played': most_played,
            'highest_rated_unplayed': highest_rated_unplayed,
            'games_by_year': top_years
        }
    
    def export_to_csv(self, filename: str = None) -> str:
        """Export detailed library to CSV file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"steam_library_detailed_{timestamp}.csv"
        
        filepath = Path(filename)
        
        print(f"💾 Exporting detailed library to {filename}...")
        
        # Define CSV columns
        columns = [
            'appid', 'name', 'playtime_hours', 'type', 'short_description',
            'release_date', 'developers', 'publishers', 'categories', 'genres',
            'price_current', 'discount_percent', 'metacritic_score', 'recommendations',
            'achievements_total', 'platforms_windows', 'platforms_mac', 'platforms_linux',
            'steam_url'
        ]
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=columns)
            writer.writeheader()
            
            for game in self.detailed_games:
                # Create row with only the columns we want
                row = {col: game.get(col, '') for col in columns}
                writer.writerow(row)
        
        print(f"✅ Exported {len(self.detailed_games)} games to {filename}")
        return str(filepath)
    
    def create_backlog_organizer(self, filename: str = None) -> str:
        """Create a backlog organizer CSV with prioritization"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"steam_backlog_organizer_{timestamp}.csv"
        
        filepath = Path(filename)
        
        print(f"📋 Creating backlog organizer CSV...")
        
        # Focus on unplayed games and games with low playtime
        backlog_candidates = [
            g for g in self.detailed_games 
            if g['playtime_hours'] < 2  # Less than 2 hours played
        ]
        
        # Sort by various factors for prioritization
        def calculate_priority_score(game):
            score = 0
            
            # Metacritic score (0-100)
            score += game.get('metacritic_score', 0) * 0.3
            
            # Recommendations (normalized)
            recs = game.get('recommendations', 0)
            if recs > 0:
                score += min(recs / 1000, 50) * 0.2  # Cap at 50 points
            
            # Recent release bonus (games from last 3 years)
            release_date = game.get('release_date', '')
            current_year = datetime.now().year
            try:
                if release_date:
                    year = None
                    if ',' in release_date:
                        year = int(release_date.split(',')[-1].strip())
                    elif len(release_date) >= 4 and release_date[-4:].isdigit():
                        year = int(release_date[-4:])
                    
                    if year and year >= current_year - 3:
                        score += 20 * 0.2
            except:
                pass
            
            # Price factor (higher price = potentially better game)
            price = game.get('price_current', 0)
            if price > 0:
                score += min(price, 60) * 0.1  # Cap at $60
            
            # Achievement count (more achievements = more content)
            achievements = game.get('achievements_total', 0)
            score += min(achievements / 10, 20) * 0.2  # Cap at 20 points
            
            return score
        
        # Calculate priority scores and sort
        for game in backlog_candidates:
            game['priority_score'] = calculate_priority_score(game)
        
        backlog_candidates.sort(key=lambda x: x['priority_score'], reverse=True)
        
        # Create CSV columns for backlog management
        columns = [
            'priority_rank', 'name', 'priority_score', 'playtime_hours', 
            'metacritic_score', 'recommendations', 'price_current',
            'release_date', 'genres', 'achievements_total',
            'status', 'notes', 'want_to_play', 'completed',
            'steam_url', 'appid'
        ]
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=columns)
            writer.writeheader()
            
            for i, game in enumerate(backlog_candidates, 1):
                row = {
                    'priority_rank': i,
                    'name': game.get('name', ''),
                    'priority_score': f"{game.get('priority_score', 0):.1f}",
                    'playtime_hours': game.get('playtime_hours', 0),
                    'metacritic_score': game.get('metacritic_score', ''),
                    'recommendations': game.get('recommendations', ''),
                    'price_current': f"${game.get('price_current', 0):.2f}" if game.get('price_current') else '',
                    'release_date': game.get('release_date', ''),
                    'genres': game.get('genres', ''),
                    'achievements_total': game.get('achievements_total', ''),
                    'status': '',  # User can fill this in
                    'notes': '',   # User can fill this in
                    'want_to_play': '',  # User can mark this
                    'completed': '',     # User can mark this
                    'steam_url': game.get('steam_url', ''),
                    'appid': game.get('appid', '')
                }
                writer.writerow(row)
        
        print(f"✅ Created backlog organizer with {len(backlog_candidates)} games in {filename}")
        return str(filepath)

def test_analyzer():
    """Test the Steam Library Analyzer"""
    print("🧪 Testing Steam Library Analyzer...")
    
    # This would use real API keys and data
    # analyzer = SteamLibraryAnalyzer(api_key, steam_id)
    # games = [...] # Load from cache or API
    # detailed = analyzer.get_detailed_library(games)
    # insights = analyzer.analyze_library()
    # csv_file = analyzer.export_to_csv()
    # backlog_file = analyzer.create_backlog_organizer()
    
    print("✅ Analyzer test complete!")

if __name__ == "__main__":
    test_analyzer()
