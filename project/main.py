import os
import sys
from dotenv import load_dotenv

import bot

def main():
    # load environment variables
    load_dotenv()
    # set deployment environment variable
    os.environ['DEPLOY'] = "True" if '-d' in sys.argv or '--deploy' in sys.argv else ""
    # fetch the Discord bot token
    TOKEN = os.getenv('BOT_TOKEN')
    # URL Bot's invite URL
    URL = os.getenv('BOT_URL')
    # Guild ID of the server being moderated on
    GUILD_ID = int(os.getenv('GUILD_ID'))

    # run the bot
    bot.run_discord_bot(TOKEN, GUILD_ID)

if __name__ == "__main__":
    main()