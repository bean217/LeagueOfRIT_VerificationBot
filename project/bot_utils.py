import discord
import re
import os
import email.utils
from typing import Union

import verification_state as vs
from verification_state import User, Verification_State, Token




#########################################
#     Arbitrary Bot Utility Methods     #
#########################################


def get_unverified_members(guild):
    return [m for m in guild.members if len(m.roles) < 2]


def get_guild(client, guild_id):
    guild = client.get_guild(guild_id)#[g for g in client.guilds if int(g.id) == int(guild_id+1)]
    # check to see if bot has access to the guild
    if not guild:
        raise Exception(f'Bot does not have access to guild with id: {guild_id}')
    return guild




############################################
#     EMAIL/SMTP/SSL Setup and Methods     #
############################################


import smtplib, ssl
PORT: int = 465
CONTEXT: ssl.SSLContext = ssl.create_default_context()

from dotenv import load_dotenv
load_dotenv()
EMAIL_USER: str = os.getenv('EMAIL_USER')
EMAIL_PASS: str = os.getenv('EMAIL_PASS')
SMTP_ADDR: str = os.getenv('SMTP_ADDR') or 'smtp.gmail.com'


def send_email(recipient, token):
    with smtplib.SMTP_SSL(host=SMTP_ADDR, port=PORT, context=CONTEXT) as server:
        server.login(user=EMAIL_USER, password=EMAIL_PASS)
        server.sendmail(EMAIL_USER, recipient, vs.VERIF_EMAIL_CONTENT(recipient, token))


async def send_verif_email(user: User, email: str):
    # attempt to send email
    try:
        verif_token = Token(6)
        send_email(email, verif_token)
        user.verif_token = verif_token
        # record the user's email
        user.responses.update({Verification_State.EMAIL_Q: email})
        # sending token was successful, so put user into verif_token state
        user.set_state(Verification_State.VERIF_SENT)
        await user.send(user.msg)
    except smtplib.SMTPException:
        # email was invalid, so tell the user they need to use an appropriate email
        await user.send(Verification_State.INVALID_EMAIL_RESP.msg)




##########################################
#     Direc Message-Handling Methods     #
##########################################


async def handle_new(user: User):
    """Handles messages from user in the "NEW" state
        @param user: User object associated with user's verification state
    """
    # send user the new user message
    await user.send(user.msg)
    user.set_state(Verification_State.STUDENT_Q)
    # send user the first question asking if they are a student
    await user.send(user.msg)


async def start_verification(member: discord.Member, unverified_users: dict):
    """Starts the verification process for a particular unverified user
        @param user: User object associated with user's verification state
    """
    unverified_users.update({member.id: User(member)})
    await handle_new(unverified_users.get(member.id))


async def handle_student_q(user: User, message: str):
    """Handles messages from user in the "STUDENT_Q" state
        @param user: User object associated with user's verification state
        @param message: string of the message sent by the user
    """
    msg = message.lower()
    # check if user said valid response
    if re.match(r"^(y(es)?)|(no?)$", msg):
        # check if user said yes or no
        if re.match(r"^y(es)?", msg):
            # get the next question
            user.set_state(Verification_State.NAME_Q)
            await user.send(user.msg)
        else:
            # inform user steps for not being an RIT student
            user.set_state(Verification_State.STUDENT_NOT)
            await user.send(user.msg)
    else:
        # user provided invalid response, so let them know
        await user.send(Verification_State.STUDENT_Q_INVALID.msg)


async def handle_name_q(user: User, message: str):
    """Handles messages from user in the "NAME_Q"
        @param user: User object associated with user's verification state
        @param message: string of the message sent by the user
    """
    # record name response
    user.responses.update({user.state: message})
    # set user to year question state
    user.set_state(Verification_State.YEAR_Q)
    # send them the year question
    await user.send(user.msg)


async def handle_year_q(user: User, message: str):
    """Handles messages from user in the "YEAR_Q"
        @param user: User object associated with user's verification state
        @param message: string of the message sent by the user
    """
    if bool(re.match(r"[1-5]$", message)):
        user.responses.update({user.state: vs.year_q_answers[int(message)-1]})
    else:
        # user answered with "other"
        user.responses.update({user.state: message})
    # set user to discovery question
    user.set_state(Verification_State.DISCOVERY_Q)
    # send user the discovery question
    await user.send(user.msg)


async def handle_discovery_q(user: User, message: str):
    """Handles messages from user in the "DISCOVERY_Q"
        @param user: User object associated with user's verification state
        @param message: string of the message sent by the user
    """
    if bool(re.match(r"[1-5]$", message)):
        if int(message) == 5:
            # user answered with "Poster"
            user.set_state(Verification_State.POSTER_Q)
        else:
            user.responses.update({user.state: vs.discovery_q_answers[int(message)-1]})
            user.set_state(Verification_State.EMAIL_Q)
    else:
        # user answered with "other"
        user.set_state(Verification_State.EMAIL_Q)

    # send user the appropriate response message
    await user.send(user.msg)


async def handle_poster_q(user: User, message: str):
    """Handles messages from user in the "POSTER_Q"
        @param user: User object associated with user's verification state
        @param message: string of the message sent by the user
    """
    message
    user.responses.update({user.state: message})
    user.set_state(Verification_State.EMAIL_Q)
    await user.send(user.msg)


async def handle_email_q(user: User, message: str):
    """Handles messages from user in the "EMAIL_Q"
        @param user: User object associated with user's verification state
        @param message: string of the message sent by the user
    """
    msg = message.split()
    # check to make sure message is just one continuous string
    if len(msg) != 1:
        await user.send(Verification_State.NON_EMAIL_RESP.msg)
        return
    
    # check to make sure string has an rit email format
    if not any([bool(re.match(r"^\S+@{d}$".format(d = domain), msg[0])) for domain in vs.rit_verified_domains]):
        await user.send(Verification_State.INVALID_EMAIL_RESP.msg)
        return

    # attempt to send email
    await send_verif_email(user, msg[0])


async def handle_verif_sent(user: User, message: str, unverified_users: list):
    """Handles messages from user in the "VERIF_SENT"
        @param user: User object associated with user's verification state
        @param message: string of the message sent by the user
    """
    if message == user.verif_token.code:
        # make sure code isn't timed out
        remaining_time = int(vs.TIMEOUT_MINS - (email.utils.parsedate_to_datetime(email.utils.formatdate()) - email.utils.parsedate_to_datetime(user.verif_token.datetime)).total_seconds() / 60)
        if remaining_time < 0:
            # the code for this user has timed out. Another must be sent.
            user.verif_token = None
            user.set_state(Verification_State.CODE_TIMEOUT)
            await user.send(user.msg)
        else:
            # user has been verified
            user.set_state(Verification_State.DONE)
            await user.send(user.msg)
            #TODO: Add finishing steps to validation (add data to the google sheet, give user the @Tiger role in the server, and remove them from the unverified_members list)
            # remove user from unverified list:
            unverified_users.pop(user.user.id)
    else:
        # verification failed
        await user.send(Verification_State.INCORRECT_CODE.msg)


async def handle_code_timeout(user: User):
    """Handles messages from user in the "CODE_TIMEOUT"
        @param user: User object associated with user's verification state
        @param message: string of the message sent by the user
    """
    await user.send(user.msg)


async def handle_command(user: User, command: str):
    """Handles user commands
        @param user: User object associated with user's verification state
        @param command: string of the command message sent by the user
    """
    command = command.split()

    if len(command) == 1:
        # command has no arguments
        if command[0] == "!resend" and (user.state == Verification_State.VERIF_SENT or user.state == Verification_State.CODE_TIMEOUT):
            # if the user has a token, check if they still have more time
            if user.verif_token is not None:
                remaining_time = int(vs.TIMEOUT_MINS - (email.utils.parsedate_to_datetime(email.utils.formatdate()) - email.utils.parsedate_to_datetime(user.verif_token.datetime)).total_seconds() / 60)
                if remaining_time > 0:
                    # if so, tell user they have to wait before sending another (state does not change)
                    await user.send(f"You must wait another {'minute' if remaining_time == 1 else f'{remaining_time} minutes'} before another can be sent.")
                    return

            # send the user another email
            await send_verif_email(user, user.responses.get(Verification_State.EMAIL_Q))

        elif command[0] == "!restart" and user.state != Verification_State.DONE:
            # put the user back into the new state and call the new state handler
            user.restart()
            await handle_new(user)


async def handle_unverified_dm(user: User, unverified_users: list, message: Union[None, discord.Message] = None):
    """Handles routing message/verification state for direct message handling 
        @param user: User object associated with user's verification state
        @param message: discord.Message of the message sent by the user, or None
    """
    # if message is None, then only handle messages for users in a "NEW" state
    if message is None:
        if user.state == Verification_State.NEW:
            await handle_new(user)
        return

    # convert the message content to a string
    msg = str(message.content)
    
    # if the message is empty, tell the user they can restart if they get stuck
    if len(msg) < 0:
        user.send("Please use the `!restart` command if you get stuck!")
        return

    # handle user commands
    if msg[0] == '!':
        # user issued a command
        await handle_command(user, msg)
        return
    
    # call handlers based on user verification state
    if user.state == Verification_State.STUDENT_Q:
        await handle_student_q(user, msg)
    elif user.state == Verification_State.NAME_Q:
        await handle_name_q(user, msg)
    elif user.state == Verification_State.YEAR_Q:
        await handle_year_q(user, msg)
    elif user.state == Verification_State.DISCOVERY_Q:
        await handle_discovery_q(user, msg)
    elif user.state == Verification_State.POSTER_Q:
        await handle_poster_q(user, msg)
    elif user.state == Verification_State.EMAIL_Q:
        await handle_email_q(user, msg)
    elif user.state == Verification_State.VERIF_SENT:
        await handle_verif_sent(user, msg, unverified_users)
    elif user.state == Verification_State.CODE_TIMEOUT:
        await handle_code_timeout(user)


def main():
    pass

if __name__ == "__main__":
    main()