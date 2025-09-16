# 🚦 RushHour Discord Bot  

RushHour is a fun, interactive Discord bot game where players race against time, money, and unexpected events to reach their destination. Players can choose different transport options, encounter random events, and track their wins and losses over time.  

## ✨ Features  
- 🎲 Randomized starting scenarios (time, money, distance)  
- 🚌 Multiple transport choices with varying costs and speeds  
- ⚡ Random events that affect gameplay (gain/lose money or time)  
- 📊 Persistent win/loss tracking across games  
- 🔎 Commands to check your active game status or record  

## 🛠️ Commands  
- `!hello` – Greet the bot
- `!help` - Shows the command message
- `!play` – Start a new game or resume an existing one  
- `!status` – View current game stats  
- `!record` – See your total wins and losses  

## 🚀 Getting Started  
1. Clone this repo:  
   ```bash
   git clone https://github.com/your-username/RushHour.git
   cd RushHour
2. Install dependencies:
   ```bash
   pip install discord.py python-dotenv
3. Create an `.env` file with your bot token:
   ```bash
   DISCORD_TOKEN=your_token_here
4. Install dependencies:
   ```bash
   python3 bot.py

## 🗂️ File Structure
- `bot.py` - Main bot logic
- `rushhour_games.json` - Stores active games
- `rushhour_stats.json` - Stores player win/loss records

⚠️ **Note**: This is a work-in-progress project. More features and improvements will be added later!
