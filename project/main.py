import os
from dotenv import load_dotenv

import bot

def main():
    load_dotenv()
    TOKEN = os.getenv('BOT_TOKEN')
    URL = os.getenv('BOT_URL')
    GUILD_ID = int(os.getenv('GUILD_ID'))

    # run the bot
    bot.run_discord_bot(TOKEN, GUILD_ID)

if __name__ == "__main__":
    main()