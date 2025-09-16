import discord
from discord.ext import commands
import os
import json
import random
from dotenv import load_dotenv

# Load token
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.reactions = True

bot = commands.Bot(command_prefix='!', intents=intents)

GAME_FILE = 'rushhour_games.json'
STATS_FILE = 'rushhour_stats.json'

# Helper functions
def load_json(file):
    try:
        with open(file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)

# Scenarios
SCENARIOS = [
    {"description": "You are late for class. Point B is 5 km away. You have $10 and 60 minutes.", "distance": 5, "time": 60, "money": 10},
    {"description": "It's raining heavily. Point B is 3 km away. You have $5 and 30 minutes.", "distance": 3, "time": 30, "money": 5},
    {"description": "You have an urgent meeting. Point B is 7 km away. You have $20 and 50 minutes.", "distance": 7, "time": 50, "money": 20},
    {"description": "You're running errands. Point B is 4 km away. You have $8 and 45 minutes.", "distance": 4, "time": 45, "money": 8},
    {"description": "You need to catch a bus. Point B is 6 km away. You have $15 and 70 minutes.", "distance": 6, "time": 70, "money": 15},
    {"description": "You're late for work. Point B is 10 km away. You have $25 and 90 minutes.", "distance": 10, "time": 90, "money": 25},
    {"description": "Your car broke down. Point B is 2 km away. You have $3 and 20 minutes.", "distance": 2, "time": 20, "money": 3},
    {"description": "You are helping a friend move. Point B is 8 km away. You have $12 and 80 minutes.", "distance": 8, "time": 80, "money": 12},
    {"description": "You forgot an important item at home. Point B is 5 km away. You have $7 and 55 minutes.", "distance": 5, "time": 55, "money": 7},
    {"description": "You are going shopping. Point B is 6 km away. You have $30 and 70 minutes.", "distance": 6, "time": 70, "money": 30},
]

# Transport options with emoji
TRANSPORT = {
    "🚌": {"name": "bus", "time": 1.5, "money": 2, "distance": 1},
    "🚕": {"name": "taxi", "time": 1, "money": 5, "distance": 1},
    "🚶": {"name": "walk", "time": 2, "money": 0, "distance": 1},
}
QUIT_EMOJI = "❌"
RESUME_EMOJI = "✅"

# Random events
EVENTS = [
    {"description": "You got robbed!", "money": -3, "time": -5},
    {"description": "You found a $10 bill on the street!", "money": 10, "time": 0},
    {"description": "A kind stranger paid your fare!", "money": 0, "time": -2},
    {"description": "You gave charity to a homeless person.", "money": -2, "time": 0},
    {"description": "Traffic is light. You saved 3 minutes!", "money": 0, "time": 3},
    {"description": "Your wallet fell out of your pocket!", "money": -5, "time": 0},
    {"description": "You helped an elderly person cross the street. Lost 3 minutes.", "money": 0, "time": -3},
    {"description": "You got a free coffee from a cafe. Gained $5!", "money": 5, "time": 0},
    {"description": "Subway is delayed! Lost 7 minutes.", "money": 0, "time": -7},
    {"description": "You ran into an old friend and chatted. Lost 5 minutes but found $2!", "money": 2, "time": -5},
    {"description": "Street performer gives you a tip. Gained $3!", "money": 3, "time": 0},
    {"description": "You tripped and fell! Lost 2 minutes and $1 for damages.", "money": -1, "time": -2},
    {"description": "You caught a free ride with a friend. Saved $5 and 3 minutes!", "money": 5, "time": 3},
    {"description": "Your bike chain broke. Lost 10 minutes fixing it.", "money": 0, "time": -10},
    {"description": "A sudden rain shower slows you down. Lost 4 minutes.", "money": 0, "time": -4},
]

# Helper to format transport costs for footer
def transport_footer():
    return " | ".join(f"{emoji} {t['name'].capitalize()} — {t['time']} min, ${t['money']}" 
                      for emoji, t in TRANSPORT.items()) + f" | {QUIT_EMOJI} Quit"

# Pick a random event
def random_event():
    if random.random() < 0.4:  # 40% chance an event occurs
        return random.choice(EVENTS)
    return None

# When bot is ready
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

# Hello command
@bot.command()
async def hello(ctx):
    await ctx.send(f"Hi {ctx.author.mention}! Ready for RushHour? Type `!play` to start!")

# Start game
@bot.command()
async def play(ctx):
    games = load_json(GAME_FILE)
    stats = load_json(STATS_FILE)
    user_id = str(ctx.author.id)

    # If a game already exists, offer to resume or quit
    if user_id in games:
        game = games[user_id]
        embed = discord.Embed(
            title="⚠️ Game Already In Progress",
            description=(
                f"{ctx.author.mention}, you already have a game!\n\n"
                f"React {RESUME_EMOJI} to continue your game.\n"
                f"React {QUIT_EMOJI} to quit and start a new game."
            ),
            color=discord.Color.orange()
        )
        msg = await ctx.send(embed=embed)
        await msg.add_reaction(RESUME_EMOJI)
        await msg.add_reaction(QUIT_EMOJI)
        game["message_id"] = msg.id
        game["channel_id"] = msg.channel.id
        save_json(GAME_FILE, games)
        return

    # New game
    scenario = random.choice(SCENARIOS)
    user_stats = stats.get(user_id, {"wins": 0, "losses": 0})
    embed = discord.Embed(
        title="🚦 RushHour Game Started!",
        description=scenario["description"],
        color=discord.Color.green()
    )
    embed.add_field(
        name="Your Stats",
        value=f"Time: {scenario['time']} min\nMoney: ${scenario['money']}\nDistance: {scenario['distance']} km"
    )
    embed.set_footer(text=transport_footer())
    msg = await ctx.send(f"{ctx.author.mention}", embed=embed)

    for emoji in list(TRANSPORT.keys()) + [QUIT_EMOJI]:
        await msg.add_reaction(emoji)

    games[user_id] = {
        "name": ctx.author.name,
        "distance_left": scenario["distance"],
        "time_left": scenario["time"],
        "money_left": scenario["money"],
        "message_id": msg.id,
        "channel_id": msg.channel.id
    }
    stats[user_id] = user_stats  # ensure stats exist
    save_json(GAME_FILE, games)
    save_json(STATS_FILE, stats)

# Reaction handler
@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    games = load_json(GAME_FILE)
    stats = load_json(STATS_FILE)
    user_id = str(user.id)
    if user_id not in games:
        return

    game = games[user_id]
    msg_id = game.get("message_id")
    if not msg_id or reaction.message.id != msg_id:
        return

    async def safe_remove_reaction():
        """Remove reaction safely to avoid rate limit crashes."""
        try:
            await reaction.remove(user)
        except discord.errors.HTTPException as e:
            if e.status == 429:  # Rate limited
                print(f"Rate limited when removing reaction for {user}. Skipping.")
            else:
                print(f"Failed to remove reaction: {e}")

    # Quit
    if reaction.emoji == QUIT_EMOJI:
        del games[user_id]
        save_json(GAME_FILE, games)
        embed = discord.Embed(
            title="❌ Game Quit",
            description=f"{user.mention} has quit the RushHour game. Type `!play` to start again.",
            color=discord.Color.red()
        )
        await reaction.message.edit(embed=embed)
        await safe_remove_reaction()
        return

    # Resume
    if reaction.emoji == RESUME_EMOJI:
        embed = discord.Embed(
            title="🚦 RushHour Game Resumed!",
            description=f"{user.mention}, your game is back on!",
            color=discord.Color.green()
        )
        embed.add_field(
            name="Your Stats",
            value=f"Time left: {game['time_left']} min\nMoney left: ${game['money_left']}\nDistance left: {game['distance_left']} km"
        )
        embed.set_footer(text=transport_footer())
        await reaction.message.edit(embed=embed)
        for emoji in TRANSPORT.keys():
            await reaction.message.add_reaction(emoji)
        await safe_remove_reaction()
        return

    if reaction.emoji not in TRANSPORT:
        return

    # Move stats
    choice = TRANSPORT[reaction.emoji]
    game["time_left"] -= choice["time"]
    game["money_left"] -= choice["money"]
    game["distance_left"] -= choice["distance"]

    # Random event
    event_msg = ""
    event = random_event()
    if event:
        game["time_left"] += event["time"]
        game["money_left"] += event["money"]
        parts = []
        if event["time"] != 0:
            parts.append(f"Time {'+' if event['time']>0 else ''}{event['time']} min")
        if event["money"] != 0:
            parts.append(f"Money {'+' if event['money']>0 else ''}${event['money']}")
        event_msg = f"\n💥 Event: {event['description']} ({', '.join(parts)})"

    embed = discord.Embed(color=discord.Color.blue())

    # End conditions
    if game["distance_left"] <= 0 and game["time_left"] >= 0:
        stats[user_id]["wins"] += 1
        embed.title = "🎉 You Made It!"
        embed.description = (
            f"{user.mention}, you reached Point B on time! Game finished.{event_msg}\n\n"
            f"⏱ Total Time Left: {game['time_left']} min\n💰 Money Remaining: ${game['money_left']}\n"
            f"🏆 Total Wins: {stats[user_id]['wins']} | ❌ Total Losses: {stats[user_id]['losses']}"
        )
        del games[user_id]
    elif game["time_left"] <= 0 or game["money_left"] < 0:
        stats[user_id]["losses"] += 1
        embed.title = "⚠️ Game Over"
        embed.description = (
            f"{user.mention}, you ran out of {'time' if game['time_left'] <= 0 else 'money'}! Game over.{event_msg}\n\n"
            f"⏱ Total Time Left: {max(game['time_left'],0)} min\n💰 Money Remaining: ${max(game['money_left'],0)}\n"
            f"🏆 Total Wins: {stats[user_id]['wins']} | ❌ Total Losses: {stats[user_id]['losses']}"
        )
        del games[user_id]
    else:
        embed.title = "🏃 Move Made"
        embed.description = f"{user.mention} chose **{choice['name']}**!{event_msg}"
        embed.add_field(
            name="Your Stats",
            value=f"Time left: {game['time_left']} min\nMoney left: ${game['money_left']}\nDistance left: {game['distance_left']} km"
        )
        embed.set_footer(text=transport_footer())

    save_json(GAME_FILE, games)
    save_json(STATS_FILE, stats)
    await reaction.message.edit(embed=embed)
    await safe_remove_reaction()

# Status command
@bot.command()
async def status(ctx):
    games = load_json(GAME_FILE)
    stats = load_json(STATS_FILE)
    user_id = str(ctx.author.id)
    embed = discord.Embed(title="📊 RushHour Status", color=discord.Color.yellow())

    if user_id in games:
        game = games[user_id]
        embed.description = f"{ctx.author.mention}'s current stats:"
        embed.add_field(name="Time left", value=f"{game['time_left']} min")
        embed.add_field(name="Money left", value=f"${game['money_left']}")
        embed.add_field(name="Distance left", value=f"{game['distance_left']} km")
    else:
        embed.description = f"{ctx.author.mention}, you have no active game."

    user_stats = stats.get(user_id, {"wins": 0, "losses": 0})
    embed.add_field(name="Wins", value=user_stats["wins"])
    embed.add_field(name="Losses", value=user_stats["losses"])
    embed.set_footer(text=transport_footer())
    await ctx.send(embed=embed)

# Record command
@bot.command()
async def record(ctx):
    stats = load_json(STATS_FILE)
    user_id = str(ctx.author.id)
    user_stats = stats.get(user_id, {"wins": 0, "losses": 0})

    embed = discord.Embed(
        title="📊 RushHour Record",
        description=f"{ctx.author.mention}'s record:",
        color=discord.Color.yellow()
    )
    embed.add_field(name="Wins", value=user_stats["wins"])
    embed.add_field(name="Losses", value=user_stats["losses"])
    await ctx.send(embed=embed)

bot.run(TOKEN)
