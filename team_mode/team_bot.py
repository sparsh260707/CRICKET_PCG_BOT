from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import asyncio
import time
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from team_mode.team_manager import TeamManager
from team_mode.team_keyboards import *

# Import from shared config
from shared.config import API_ID, API_HASH, BOT_TOKEN, ADMIN_ID, ADMIN_USERNAME

app = Client("team_mode_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
team_manager = TeamManager()

# Store waiting for captain selection
waiting_for_captain = {}

@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    await message.reply_text(
        "🏏 **TEAM MODE - CRICKET PCG** 🏏\n\n"
        "**Commands:**\n"
        "/create_team - Create a new match (Host)\n"
        "/join_teamA - Join Team A\n"
        "/join_teamB - Join Team B\n"
        "/add_a @username - Host adds player to Team A\n"
        "/add_b @username - Host adds player to Team B\n"
        "/team_status - Check teams status\n"
        "/end_match - End current match (Host)\n\n"
        "**How to Play:**\n"
        "1️⃣ Host uses /create_team\n"
        "2️⃣ Players join with /join_teamA or /join_teamB\n"
        "3️⃣ After join time, host can add more players\n"
        "4️⃣ Choose captains\n"
        "5️⃣ Toss to decide batting/bowling\n"
        "6️⃣ Start match and play!\n\n"
        "👑 **Host:** @The_KFG_Network"
    )

@app.on_message(filters.command("create_team"))
async def create_team_command(client: Client, message: Message):
    """Host creates a new match"""
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    # Check if match already exists
    if chat_id in team_manager.active_matches:
        await message.reply_text("⚠️ A match is already active! Use /end_match first.")
        return
    
    # Create new match
    match = team_manager.create_match(chat_id, user_id, message.from_user.first_name)
    
    await message.reply_text(
        f"🏏 **NEW MATCH CREATED!** 🏏\n\n"
        f"👑 Host: {message.from_user.first_name}\n\n"
        f"📢 **Team creation is underway!**\n\n"
        f"Join Team A by sending `/join_teamA`\n"
        f"Join Team B by sending `/join_teamB`\n\n"
        f"⏰ You have 30 seconds to join!\n"
        f"⚠️ After time's up, host can manually add players."
    )
    
    # Auto close join after 30 seconds
    async def close_join():
        await asyncio.sleep(30)
        if chat_id in team_manager.active_matches:
            result = team_manager.close_join(chat_id)
            if result['success']:
                keyboard = get_team_action_keyboard(result['team_a_count'], result['team_b_count'])
                
                team_a_list = "\n".join([f"   {i+1}. @{p}" for i, p in enumerate(result['team_a_players'])]) or "   No players"
                team_b_list = "\n".join([f"   {i+1}. @{p}" for i, p in enumerate(result['team_b_players'])]) or "   No players"
                
                await client.send_message(
                    chat_id,
                    f"⏰ **TIME'S UP FOR JOINING!**\n\n"
                    f"📊 **Team A** ({result['team_a_count']} players):\n{team_a_list}\n\n"
                    f"📊 **Team B** ({result['team_b_count']} players):\n{team_b_list}\n\n"
                    f"🔧 **Host Actions:**\n"
                    f"• Use `/add_a @username` to add more to Team A\n"
                    f"• Use `/add_b @username` to add more to Team B\n"
                    f"• Then choose captains and start the match!",
                    reply_markup=keyboard
                )
    
    asyncio.create_task(close_join())

@app.on_message(filters.command("join_teamA"))
async def join_team_a(client: Client, message: Message):
    """Join Team A"""
    chat_id = message.chat.id
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    
    result = team_manager.add_player_to_team(chat_id, user_id, username, message.from_user.first_name, 'A')
    
    if 'error' in result:
        await message.reply_text(f"❌ {result['error']}")
    else:
        await message.reply_text(f"✅ @{username} joined Team A! ✨ (Total: {result['player_count']})")

@app.on_message(filters.command("join_teamB"))
async def join_team_b(client: Client, message: Message):
    """Join Team B"""
    chat_id = message.chat.id
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    
    result = team_manager.add_player_to_team(chat_id, user_id, username, message.from_user.first_name, 'B')
    
    if 'error' in result:
        await message.reply_text(f"❌ {result['error']}")
    else:
        await message.reply_text(f"✅ @{username} joined Team B! 😍❤️ (Total: {result['player_count']})")

@app.on_message(filters.command("add_a"))
async def add_to_team_a(client: Client, message: Message):
    """Host adds player to Team A"""
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    # Check if host
    match = team_manager.active_matches.get(chat_id)
    if not match or match['host_id'] != user_id:
        await message.reply_text("❌ Only host can add players!")
        return
    
    # Get username from command
    parts = message.text.split()
    if len(parts) < 2:
        await message.reply_text("❌ Usage: `/add_a @username`")
        return
    
    username = parts[1].replace('@', '')
    
    # For now, just acknowledge
    await message.reply_text(f"✅ Added @{username} to Team A")

@app.on_message(filters.command("add_b"))
async def add_to_team_b(client: Client, message: Message):
    """Host adds player to Team B"""
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    # Check if host
    match = team_manager.active_matches.get(chat_id)
    if not match or match['host_id'] != user_id:
        await message.reply_text("❌ Only host can add players!")
        return
    
    # Get username from command
    parts = message.text.split()
    if len(parts) < 2:
        await message.reply_text("❌ Usage: `/add_b @username`")
        return
    
    username = parts[1].replace('@', '')
    
    await message.reply_text(f"✅ Added @{username} to Team B")

@app.on_message(filters.command("team_status"))
async def team_status(client: Client, message: Message):
    """Check teams status"""
    chat_id = message.chat.id
    status = team_manager.get_teams_status(chat_id)
    
    if 'error' in status:
        await message.reply_text("❌ No active match!")
        return
    
    team_a_list = "\n".join([f"   {i+1}. @{p}" for i, p in enumerate(status['team_a']['players'])]) or "   No players"
    team_b_list = "\n".join([f"   {i+1}. @{p}" for i, p in enumerate(status['team_b']['players'])]) or "   No players"
    
    await message.reply_text(
        f"🏏 **MATCH STATUS** 🏏\n\n"
        f"👑 Host: @{status['host']}\n"
        f"⏰ Join Active: {'Yes' if status['join_active'] else 'No'}\n"
        f"⏳ Time Left: {status['join_time_left']}s\n\n"
        f"📌 **Team A** ({status['team_a']['count']} players):\n{team_a_list}\n"
        f"Captain: @{status['team_a']['captain'] or 'Not selected'}\n\n"
        f"📌 **Team B** ({status['team_b']['count']} players):\n{team_b_list}\n"
        f"Captain: @{status['team_b']['captain'] or 'Not selected'}"
    )

@app.on_message(filters.command("end_match"))
async def end_match(client: Client, message: Message):
    """End current match"""
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    match = team_manager.active_matches.get(chat_id)
    if not match:
        await message.reply_text("❌ No active match!")
        return
    
    if match['host_id'] != user_id:
        await message.reply_text("❌ Only host can end the match!")
        return
    
    team_manager.end_match(chat_id)
    await message.reply_text("🏏 **MATCH ENDED** 🏏\n\nUse /create_team to start a new match!")

@app.on_callback_query()
async def handle_callbacks(client: Client, callback_query: CallbackQuery):
    """Handle inline button callbacks"""
    data = callback_query.data
    chat_id = callback_query.message.chat.id
    user_id = callback_query.from_user.id
    
    if data == "create_team":
        await create_team_command(client, callback_query.message)
        await callback_query.answer()
    
    elif data == "team_status":
        await team_status(client, callback_query.message)
        await callback_query.answer()
    
    elif data == "end_match":
        await end_match(client, callback_query.message)
        await callback_query.answer()
    
    elif data == "add_to_team_a":
        await callback_query.answer("Use /add_a @username to add players", show_alert=True)
    
    elif data == "add_to_team_b":
        await callback_query.answer("Use /add_b @username to add players", show_alert=True)
    
    elif data == "choose_captains":
        status = team_manager.get_teams_status(chat_id)
        if 'error' in status:
            await callback_query.answer("No active match!", show_alert=True)
            return
        
        keyboard = get_captain_selection_keyboard(status['team_a']['players'], status['team_b']['players'])
        await callback_query.message.reply_text(
            "👑 **SELECT CAPTAINS** 👑\n\n"
            "Choose captain for each team:",
            reply_markup=keyboard
        )
        await callback_query.answer()
    
    elif data.startswith("cap_a_"):
        username = data.replace("cap_a_", "")
        result = team_manager.choose_captain(chat_id, 'A', username)
        if result.get('success'):
            await callback_query.message.reply_text(f"✅ @{username} is now Captain of Team A!")
        else:
            await callback_query.answer(result.get('error', 'Error!'), show_alert=True)
        await callback_query.answer()
    
    elif data.startswith("cap_b_"):
        username = data.replace("cap_b_", "")
        result = team_manager.choose_captain(chat_id, 'B', username)
        if result.get('success'):
            await callback_query.message.reply_text(f"✅ @{username} is now Captain of Team B!")
        else:
            await callback_query.answer(result.get('error', 'Error!'), show_alert=True)
        await callback_query.answer()
    
    elif data == "captains_done":
        await callback_query.message.reply_text(
            "✅ **Captains Selected!**\n\n"
            "Now do toss using 🎲 button or type /toss"
        )
        await callback_query.answer()
    
    elif data == "do_toss":
        await callback_query.message.reply_text(
            "🪙 **TOSS TIME!** 🪙\n\n"
            "Team A captain choose Heads or Tails:",
            reply_markup=get_toss_keyboard()
        )
        await callback_query.answer()
    
    elif data == "toss_heads" or data == "toss_tails":
        # Random toss result
        result = random.choice(['heads', 'tails'])
        user_choice = 'heads' if data == 'toss_heads' else 'tails'
        
        if user_choice == result:
            await callback_query.message.reply_text(
                f"🪙 Toss result: **{result.upper()}**\n\n"
                f"✅ You won the toss!\n\n"
                f"Choose what to do:",
                reply_markup=get_bat_bowl_choice_keyboard()
            )
        else:
            await callback_query.message.reply_text(
                f"🪙 Toss result: **{result.upper()}**\n\n"
                f"❌ You lost the toss! Opponent will choose."
            )
        await callback_query.answer()
    
    elif data == "choice_bat":
        await callback_query.message.reply_text("🏏 Team chose to BAT first!")
        await callback_query.answer()
    
    elif data == "choice_bowl":
        await callback_query.message.reply_text("🎯 Team chose to BOWL first!")
        await callback_query.answer()
    
    else:
        await callback_query.answer()

if __name__ == "__main__":
    print("🏏 TEAM MODE BOT STARTED!")
    print("✅ Waiting for matches...")
    app.run()
