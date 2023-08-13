from dotenv import dotenv_values

import bot

def main():
    secrets = dotenv_values(".env")
    TOKEN = secrets['BOT_TOKEN']
    URL = secrets['BOT_URL']
    GUILD_ID = int(secrets['GUILD_ID'])

    # run the bot
    bot.run_discord_bot(TOKEN, GUILD_ID)

if __name__ == "__main__":
    main()