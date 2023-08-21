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
        """Fetches the server/guild object
        """
        # get the server being considered
        guild = bot_utils.get_guild(client, guild_id)

        # get all members who are not yet verified
        unverified = [m for m in guild.members if len(m.roles) < 2]

        # for each unverified member, start their verification process
        for member in unverified:
            try:
                await bot_utils.start_verification(member, unverified_users)
            except Exception as e:
                print(e, f'({member})')

        print(f'{client.user} is now running!')



    @client.event
    async def on_member_join(member):
        """When a member joins, start the verification process for them
            @param member: discord.Member object of user that joined the server
        """
        # ignore users from other servers
        if str(member.guild.id) != str(guild_id):
            return

        print(member, "joined")

        # send new member a verification message
        if len(member.roles) < 2 and member.id not in unverified_users.keys():
            await bot_utils.start_verification(member, unverified_users)



    @client.event
    async def on_member_remove(member):
        """When an unverified user leaves the server, stop tracking their verification state
            @param member: discord.Member object of user that left the server
        """
        # ignore users from other servers
        if str(member.guild.id) != str(guild_id):
            return

        print(member, "left")
        
        # stop tracking user's verification state
        if member.id in unverified_users.keys():
            unverified_users.pop(member.id)



    @client.event
    async def on_message(message):
        """Only responds to private messages for the user verification process
            @param message: discord.Message object of the message that was sent
        """
        # only consider non-bot messages
        if message.author == client.user or str(message.channel.type) != "private":
            return

        # TODO: could be removed later
        # Console message to record information about a received private message
        print(f"{str(message.author)} said: '{str(message.content)}' ({str(message.channel)})")

        # Don't respond to messages of users that have already been verified
        if message.author.id not in unverified_users.keys():
            print("user has already been verified")
            return
            
        # get the User object associated with an unverified user
        user_state = unverified_users.get(message.author.id)
        
        # process message
        try:
            await bot_utils.handle_unverified_dm(user=user_state, message=message, unverified_users=unverified_users)
        except Exception as e:
            print(e)
            print(traceback.format_exc())
    
    # run the bot
    client.run(token)