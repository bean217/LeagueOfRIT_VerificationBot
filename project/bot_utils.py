import responses


def get_unverified_members(guild):
    return [m for m in guild.members if len(m.roles) < 2]


def get_guild(client, guild_id):
    guild = client.get_guild(guild_id)#[g for g in client.guilds if int(g.id) == int(guild_id+1)]
    # check to see if bot has access to the guild
    if not guild:
        raise Exception(f'Bot does not have access to guild with id: {guild_id}')
    return guild


async def start_verification(user):
    try:
        response = responses.handle_join(user)
        await user.send(response)
    except Exception as e:
        print(e)


async def send_message(message, user_message='', is_private=True):
    try:
        response = responses.handle_response(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)
