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



############################
#     Record User Data     #
############################

import json
from datetime import datetime
import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe
from google.oauth2.service_account import Credentials
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

GS_KEY = os.getenv('GS_KEY')
SHEET_KEY = os.getenv('SHEET_KEY')
SHEET_NAME = os.getenv('SHEET_NAME')
IS_LOCAL = bool(os.getenv('IS_LOCAL'))

scopes = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive']

credentials = None
# If running in a local environment:
if IS_LOCAL:
    # treat GS_KEY as a file
    credentials = Credentials.from_service_account_file(GS_KEY, scopes=scopes)
# otherwise, if running in a deployment:
else:
    # treat GS_KEY as a json dict
    key = GS_KEY.strip()                                    # remove extra whitespace
    key = re.sub(r"\\\\", r"\\", key)                       # remove double '\'
    key = re.sub(r"\\\"", "\"", key)                        # replace '\"' with '"'
    key = re.sub(r"\s*(\\n)*\s*{\s*(\\n)*\s*", "{", key)    # remove remaining newlines from between '{' and '}'
    key = re.sub(r"\s*(\\n)*\s*}\s*(\\n)*\s*", "}", key)    
    key = re.sub(r"\"\s*,\s*\\n*\s*\"", "\", \"", key)      # remove newlines surrounding key-value pairs
    key = re.sub(r"\"\s*:\s*(\\n)*\s*\"", "\": \"", key)    # remove newlines between key-value pairs

    # print(key)
    # with open('./gs_key.json', 'w') as f:
    #     key = GS_KEY.strip()
    #     key = re.sub(r"\\\\", r"\\", key)
    #     key = re.sub(r"\\\"", "\"", key)
    #     key = re.sub(r"\s*(\\n)*\s*{\s*(\\n)*\s*", "{", key)
    #     key = re.sub(r"\s*(\\n)*\s*}\s*(\\n)*\s*", "}", key)
    #     key = re.sub(r"\s*\\n*\s*\}\s*\\n*\s*", "}", key)
    #     key = re.sub(r"\"\s*,\s*\\n*\s*\"", "\", \"", key)

    #     # key = re.sub(r"\{\s*\\n\s*\"", )

    #     # key = re.sub(r"\\n", "", key)
    #     # key = re.sub(r"\\\"", "\"", key)
    #     # key = re.sub(r"\\", r"\\\\", key)
    #     print(key)
    #     #print(re.sub('\n  ', '', key))
    #     #key = re.sub("\\n", "", key)
    #     #key = re.sub("\\\"", "", key)
    #     f.write(key)
    # credentials = Credentials.from_service_account_file("./gs_key.json", scopes=scopes)
    credentials = Credentials.from_service_account_info(json.loads(key), scopes=scopes)


gc = gspread.authorize(credentials)

gauth = GoogleAuth()
drive = GoogleDrive(gauth)


def handle_record_data(user: User):
    print(user.responses.keys())
    name = user.responses.get(Verification_State.NAME_Q)
    email = user.responses.get(Verification_State.EMAIL_Q)
    year = user.responses.get(Verification_State.YEAR_Q)
    discovery = user.responses.get(Verification_State.DISCOVERY_Q)
    poster = None if Verification_State.POSTER_Q not in user.responses.keys() else user.responses.get(Verification_State.POSTER_Q)
    if poster is not None:
        discovery += ": " + poster

    print(f"{user.id} ({user.name}) = [name: {name}, email: {email}, year: {year}, discovery: {discovery}]")

    # open google sheet
    gs = gc.open_by_key(SHEET_KEY)
    # select work sheet
    ws = gs.worksheet(SHEET_NAME)
    print(ws)
    df = pd.DataFrame({
        'a': str(user.join_datetime.strftime("%m/%d/%Y, %H:%M:%S")),
        'b': [email],
        'c': [name],
        'd': [year],
        'e': [f'{user.name} ({user.id})'],
        'f': [discovery],
        'g': ['GREEN']
    })
    df_values = df.values.tolist()
    gs.values_append(SHEET_NAME, {'valueInputOption': 'USER_ENTERED'}, {'values': df_values})



###########################################
#     Direct Message-Handling Methods     #
###########################################


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
    """Handles messages from user in the "NAME_Q" state
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
    """Handles messages from user in the "YEAR_Q" state
        @param user: User object associated with user's verification state
        @param message: string of the message sent by the user
    """
    # special case for handling answering this question
    user.get_year_q_answer(message)
    # set user to discovery question
    user.set_state(Verification_State.DISCOVERY_Q)
    # send user the discovery question
    await user.send(user.msg)


async def handle_discovery_q(user: User, message: str):
    """Handles messages from user in the "DISCOVERY_Q" state
        @param user: User object associated with user's verification state
        @param message: string of the message sent by the user
    """
    if bool(re.match(r"^[1-5]$", message)):
        # record user's multiple choice response
        user.responses.update({user.state: vs.discovery_q_answers[int(message)-1]})
        # if they chose poster, handle setting the user's next state accordingly
        if int(message) == 5:
            # user answered with "Poster"
            user.set_state(Verification_State.POSTER_Q)
        else:
            user.set_state(Verification_State.EMAIL_Q)
    else:
        # record user's 'other' response
        user.responses.update({user.state: message})
        # user answered with "other"
        user.set_state(Verification_State.EMAIL_Q)

    # send user the appropriate response message
    await user.send(user.msg)


async def handle_poster_q(user: User, message: str):
    """Handles messages from user in the "POSTER_Q" state
        @param user: User object associated with user's verification state
        @param message: string of the message sent by the user
    """
    user.responses.update({user.state: message})
    user.set_state(Verification_State.EMAIL_Q)
    await user.send(user.msg)


async def handle_email_q(user: User, message: str):
    """Handles messages from user in the "EMAIL_Q" state
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
    """Handles messages from user in the "VERIF_SENT" state
        @param user: User object associated with user's verification state
        @param message: string of the message sent by the user
    """
    if message == user.verif_token.code and user.remaining_tries > 0:
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
            verified_user = unverified_users.pop(user.id)
            # grant the user the tigers role
            await verified_user.grant_tigers_role()
            # handle recording user's data
            handle_record_data(verified_user)
    else:
        # verification failed
        if user.remaining_tries > 0:
            user.remaining_tries -= 1
            await user.send(Verification_State.INCORRECT_CODE.msg)
        else:
            await user.send(Verification_State.NO_RETRIES.msg)


async def handle_code_timeout(user: User):
    """Handles messages from user in the "CODE_TIMEOUT" state
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