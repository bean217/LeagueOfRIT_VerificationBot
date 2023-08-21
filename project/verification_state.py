import random
import math
import email.utils
import discord
from enum import Enum

TIMEOUT_MINS: int = 15
TIGER_ROLE_NAME = "Tigers"

rit_verified_domains = [
    "rit.edu",
    "g.rit.edu",
    "mail.rit.edu"
]


year_q_answers = [
    "Incoming First Year",
    "Second Year",
    "Third Year",
    "Fourth Year",
    "Fifth Year"
]


discovery_q_answers = [
    "RIT CampusGroups Page",
    "RIT Discord Student Hub",
    "Discord Discovery Tab",
    "Google Search",
    "Poster"
]


VERIF_EMAIL_CONTENT = lambda recipient, token: """Subject: League of RIT Discord Email Verification
From: RIT Email Verification Bot <benpiro1118@gmail.com>
To: """+recipient+"""
Date: """+token.datetime+"""

Please reply to the LoRA Discord Bot with the following:\t"""+token.code


msgs = [
    "Hello! Welcome to the League of RIT!\n\n" + \
    "I am the League of RIT Admin Verification Bot (LoRA Bot for short).\n\n" + \
    "In order to gain access to the League of RIT's official Discord, " + \
    "we need to verify a few things first.\n\n" + \
    "Once you have completed verification, you will be free to select your own roles.\n\n" + \
    "If at any point during the verification process you would like to restart, " + \
    "please use the command `!restart`.",

    "First thing's first: Are you an RIT student?\nPlease enter 'Yes' or 'No'.",

    "Please enter a valid response ('Yes' or 'No').",

    "Unfortunately since you are not an RIT student, you will need to contact " + \
    "@willie_ or @therealalpacadg in order to join the server as a Non-RIT member.\n\n" + \
    "If you believe you have made a mistake, please use the `!restart` command " + \
    "to redo the verification process.",

    "What is your name (first and last)?\n" + \
    "If you make a mistake, please use the `!restart` command.",

    "What year are you at RIT? Enter the number corresponding to your year:\n\t" + \
    "[1] Incoming First Year\n\t" + \
    "[2] Second Year\n\t" + \
    "[3] Third Year\n\t" + \
    "[4] Fourth Year\n\t" + \
    "[5] Fifth Year\n\n" + \
    "If none of these options describe you, please provide an alternative description.",

    "How did you find us? Enter the number corresponding to your answer:\n\t" + \
    "[1] RIT CampusGroups Page\n\t" + \
    "[2] RIT Discord Student Hub\n\t" + \
    "[3] Discord Discovery Tab\n\t" + \
    "[4] Google Search\n\t" + \
    "[5] Poster\n\n" + \
    "If none of these options are appropriate, please provide an alternative description.",

    "Where was this poster located?",

    "For verification purposes, what is your RIT email?",

    "A verification code has been sent to your email. Please enter the code you received. " + \
    "If for some reason you never received a code, please contact @willie_ or @therealalpacadg.",

    "Please enter only a single valid RIT email as your response.",

    "Please enter a valid RIT email as your response.",

    "The code you provided was incorrect. Enter the correct code, or use the `!resend` command to have new code sent.",

    "The code you entered had timed out. Please use the `!resend` command to have a new code sent.",

    "Incorrect verification codes have been entered past the retry limit. Please use the `!resend` command to have a new code sent.",

    "Your email have been verified! You have been assigned the @Tiger role in the league of RIT Discord.\n\n" + \
    "Now that verification is complete, LoRA Bot commands have bene disabled and " + \
    "I will no longer respond to further messages.\n\n" + \
    "Feel free to close this DM and enjoy the League of RIT!"
]

class Verification_State(Enum):
    NEW = 0
    STUDENT_Q = 1
    STUDENT_Q_INVALID = 2
    STUDENT_NOT = 3
    NAME_Q = 4
    YEAR_Q = 5
    DISCOVERY_Q = 6
    POSTER_Q = 7
    EMAIL_Q = 8
    VERIF_SENT = 9
    NON_EMAIL_RESP = 10
    INVALID_EMAIL_RESP = 11
    INCORRECT_CODE = 12
    CODE_TIMEOUT = 13
    NO_RETRIES = 14
    DONE = 15

    @property
    def msg(self):
        return msgs[self.value]


class Token:
    def __init__(self, length: int):
        digits = [i for i in range(0, 10)]
        self.code = ""
        for i in range(length):
            index = math.floor(random.random() * 10)
            self.code += str(digits[index])
        self.datetime = email.utils.formatdate()


class User():
    def __init__(self, user: discord.Member):
        # user data
        self.user = user
        self.__state_index = Verification_State.NEW.value
        self.responses = dict()
        self.verif_token = None
        self.remaining_tries = 3

    @property
    def state(self):
        return Verification_State(self.__state_index)

    @property
    def is_complete(self):
        return self.__state_index == len(Verification_State)

    @property
    def msg(self):
        return self.state.msg
    
    @property
    def id(self):
        return self.user.id
    
    @property
    def name(self):
        return self.user.name

    def set_state(self, value: Verification_State):
        self.__state_index = value.value

    def restart(self):
        self.__state_index = Verification_State.NEW.value
        self.responses = dict()
        self.verif_token = None
        self.remaining_tries = 3
    
    async def grant_tigers_role(self):
        role = [r for r in self.user.guild.roles if str(r.name) == TIGER_ROLE_NAME][0]
        await self.user.add_roles(role)

    async def send(self, msg):
        await self.user.send(msg)



def main():
    for v in Verification_State:
        print(v)
        print(f'\t{v.msg}')

if __name__ == "__main__":
    main()