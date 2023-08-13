import discord

import bot_utils
from bot_utils import send_message, start_verification
from bot_utils import get_unverified_members

from verification_state import User



def run_discord_bot(token, guild_id):
    # setup client
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    client = discord.Client(intents=intents)


    unverified_users = dict()


    @client.event
    async def on_ready():
        guild = bot_utils.get_guild(client, guild_id)

        print("Roles:", guild.roles)

        for m in get_unverified_members(guild):
            print(m)
            for r in m.roles:
                print(f'\t{r}')

        print(f'{client.user} is now running!')


    @client.event
    async def on_member_join(member):
        print(member, "joined")

        # send new member a verification message
        if len(member.roles) < 2:
            unverified_users.update({member.id: User(member)})
            await start_verification(member)



    @client.event
    async def on_member_remove(member):
        print(member, "left")
        
        for i, user in enumerate(unverified_users):
            if user.id == member.id and member.id in unverified_users.keys():
                unverified_users.pop(member.id)



    @client.event
    async def on_message(message):
        # only consider non-bot messages
        if message.author == client.user:
            return

        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)

        print(f"{username} said: '{user_message}' ({channel})")
        # print("Members:",[m for m in message.guild.members if not m.bot])

        if user_message != '':
            if user_message[0] == '?':
                user_message = user_message[1:]
                await send_message(message, user_message, is_private=True)
            elif user_message[0] == '!':
                await send_message(message, user_message, is_private=False)


    client.run(token)