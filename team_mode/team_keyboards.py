from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu_keyboard():
    """Main game menu keyboard"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏏 Create Team", callback_data="create_team")],
        [InlineKeyboardButton("📊 Team Status", callback_data="team_status")],
        [InlineKeyboardButton("❌ End Match", callback_data="end_match")]
    ])

def get_team_action_keyboard(team_a_count, team_b_count):
    """Team action keyboard after join closes"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"➕ Add to Team A ({team_a_count})", callback_data="add_to_team_a")],
        [InlineKeyboardButton(f"➕ Add to Team B ({team_b_count})", callback_data="add_to_team_b")],
        [InlineKeyboardButton("👑 Choose Captains", callback_data="choose_captains")],
        [InlineKeyboardButton("🎲 Toss", callback_data="do_toss")],
        [InlineKeyboardButton("🏏 Start Match", callback_data="start_match")]
    ])

def get_captain_selection_keyboard(team_a_players, team_b_players):
    """Captain selection keyboard"""
    keyboard = []
    
    # Team A players
    if team_a_players:
        keyboard.append([InlineKeyboardButton(f"📌 Team A Captain", callback_data="noop")])
        for player in team_a_players[:5]:  # Max 5 buttons
            keyboard.append([InlineKeyboardButton(f"👤 {player}", callback_data=f"cap_a_{player}")])
    
    # Team B players
    if team_b_players:
        keyboard.append([InlineKeyboardButton(f"📌 Team B Captain", callback_data="noop")])
        for player in team_b_players[:5]:
            keyboard.append([InlineKeyboardButton(f"👤 {player}", callback_data=f"cap_b_{player}")])
    
    keyboard.append([InlineKeyboardButton("✅ Done", callback_data="captains_done")])
    
    return InlineKeyboardMarkup(keyboard)

def get_toss_keyboard():
    """Toss selection keyboard"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🪙 Heads", callback_data="toss_heads")],
        [InlineKeyboardButton("🪙 Tails", callback_data="toss_tails")]
    ])

def get_bat_bowl_choice_keyboard():
    """Choose bat or bowl after winning toss"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏏 Bat First", callback_data="choice_bat")],
        [InlineKeyboardButton("🎯 Bowl First", callback_data="choice_bowl")]
    ])
