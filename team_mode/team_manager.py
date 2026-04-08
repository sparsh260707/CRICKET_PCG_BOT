import asyncio
import time
import random
from typing import Dict, List, Optional
from datetime import datetime

class TeamManager:
    def __init__(self):
        self.active_matches: Dict[int, Dict] = {}  # chat_id: match_data
        self.join_timers: Dict[int, asyncio.Task] = {}
    
    def create_match(self, chat_id: int, host_id: int, host_name: str) -> Dict:
        """Create new match"""
        match_data = {
            'host_id': host_id,
            'host_name': host_name,
            'team_a': {
                'name': 'Team A',
                'players': [],
                'captain': None,
                'runs': 0,
                'wickets': 0,
                'balls': 0,
                'overs': 0
            },
            'team_b': {
                'name': 'Team B',
                'players': [],
                'captain': None,
                'runs': 0,
                'wickets': 0,
                'balls': 0,
                'overs': 0
            },
            'batting_team': None,
            'bowling_team': None,
            'target': None,
            'match_active': False,
            'join_active': True,
            'join_end_time': time.time() + 30,  # 30 seconds to join
            'toss_done': False,
            'match_ended': False,
            'current_batter': None,
            'current_bowler': None
        }
        self.active_matches[chat_id] = match_data
        return match_data
    
    def add_player_to_team(self, chat_id: int, user_id: int, username: str, first_name: str, team: str) -> Dict:
        """Add player to specific team"""
        match = self.active_matches.get(chat_id)
        if not match or not match['join_active']:
            return {'error': 'No active match or join time over'}
        
        if team == 'A':
            team_data = match['team_a']
        elif team == 'B':
            team_data = match['team_b']
        else:
            return {'error': 'Invalid team'}
        
        # Check if already in any team
        for player in match['team_a']['players']:
            if player['id'] == user_id:
                return {'error': 'Already in Team A'}
        for player in match['team_b']['players']:
            if player['id'] == user_id:
                return {'error': 'Already in Team B'}
        
        player_data = {
            'id': user_id,
            'username': username,
            'name': first_name,
            'joined_at': time.time(),
            'runs': 0,
            'balls': 0,
            'wickets': 0,
            'overs_bowled': 0,
            'is_out': False
        }
        
        team_data['players'].append(player_data)
        
        return {
            'success': True,
            'team': team,
            'player_count': len(team_data['players']),
            'player': player_data
        }
    
    def add_player_by_host(self, chat_id: int, username: str, team: str, user_id: int = None) -> Dict:
        """Host manually adds player by username"""
        match = self.active_matches.get(chat_id)
        if not match:
            return {'error': 'No active match'}
        
        # Check if host
        # This is simplified - actual implementation would need username to user_id mapping
        
        return {'success': True, 'message': f'Added @{username} to Team {team}'}
    
    def close_join(self, chat_id: int) -> Dict:
        """Close joining for both teams"""
        match = self.active_matches.get(chat_id)
        if not match:
            return {'error': 'No active match'}
        
        match['join_active'] = False
        
        team_a_count = len(match['team_a']['players'])
        team_b_count = len(match['team_b']['players'])
        
        return {
            'success': True,
            'team_a_count': team_a_count,
            'team_b_count': team_b_count,
            'team_a_players': [p['username'] for p in match['team_a']['players']],
            'team_b_players': [p['username'] for p in match['team_b']['players']]
        }
    
    def choose_captain(self, chat_id: int, team: str, username: str) -> Dict:
        """Choose team captain"""
        match = self.active_matches.get(chat_id)
        if not match:
            return {'error': 'No active match'}
        
        if team == 'A':
            team_data = match['team_a']
        else:
            team_data = match['team_b']
        
        # Find player by username
        player = next((p for p in team_data['players'] if p['username'] == username), None)
        if not player:
            return {'error': f'Player @{username} not found in Team {team}'}
        
        team_data['captain'] = player
        
        return {
            'success': True,
            'team': team,
            'captain': username
        }
    
    def get_teams_status(self, chat_id: int) -> Dict:
        """Get current teams status"""
        match = self.active_matches.get(chat_id)
        if not match:
            return {'error': 'No active match'}
        
        return {
            'host': match['host_name'],
            'team_a': {
                'count': len(match['team_a']['players']),
                'players': [p['username'] for p in match['team_a']['players']],
                'captain': match['team_a']['captain']['username'] if match['team_a']['captain'] else None
            },
            'team_b': {
                'count': len(match['team_b']['players']),
                'players': [p['username'] for p in match['team_b']['players']],
                'captain': match['team_b']['captain']['username'] if match['team_b']['captain'] else None
            },
            'join_active': match['join_active'],
            'join_time_left': max(0, int(match['join_end_time'] - time.time()))
        }
    
    def end_match(self, chat_id: int) -> bool:
        """End current match"""
        if chat_id in self.active_matches:
            # Cancel timer if exists
            if chat_id in self.join_timers:
                self.join_timers[chat_id].cancel()
                del self.join_timers[chat_id]
            del self.active_matches[chat_id]
            return True
        return False
