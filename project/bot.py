import discord
import traceback

import bot_utils
from bot_utils import get_unverified_members


def run_discord_bot(token, guild_id):
    # setup client
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    client = discord.Client(intents=intents)

    # keep track of all users who are not yet verified
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
            bot_utils.add_new_unverified(member, unverified_users)
            await bot_utils.handle_new(unverified_users.get(member.id))



    @client.event
    async def on_member_remove(member):
        print(member, "left")
        
        if member.id in unverified_users.keys():
            unverified_users.pop(member.id)



    @client.event
    async def on_message(message):
        # only consider non-bot messages
        if message.author == client.user or str(message.channel.type) != "private":
            return

        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)

        print(f"{username} said: '{user_message}' ({channel})")
        # print("Members:",[m for m in message.guild.members if not m.bot])


        # attempt to fetch User object
        if message.author.id not in unverified_users.keys():
            print("user has already been verified")
            return
            
        user_state = unverified_users.get(message.author.id)
        
        # process message
        try:
            await bot_utils.handle_unverified_dm(user=user_state, message=message, unverified_users=unverified_users)
        except Exception as e:
            print(e)
            print(traceback.format_exc())


        # if user_message != '':
        #     if user_message[0] == '?':
        #         user_message = user_message[1:]
        #         await send_message(message, user_message, is_private=True)
        #     elif user_message[0] == '!':
        #         await send_message(message, user_message, is_private=False)


    client.run(token)