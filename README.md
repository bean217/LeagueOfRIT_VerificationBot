# League of RIT Discord Verification Bot

## Description

The League of RIT Admin Bot (A.K.A. "LoRA Bot") aims to allow for new RIT student users of the League of RIT club Discord to verify their student email address without needing to manually contact server administrators/moderators for base role assignment.

This discord bot was built to only be used by a single discord server at a time. While limiting, this decision was made in order to limit the bot from being used on multiple discord servers since it is intended solely for the League of RIT Discord server. This may be updated in the future in order to allow predefined access to more than one server if the need rises (as determined by the League of RIT club Eboard).

This discord bot contains three main files:
1. `project/bot.py` defines all events used by the bot.
2. `project/bot_utils.py` defines all handler methods for the bot when an event is triggered
3. `project/verification_state.py` contains the definitions of all necessary classes/enums and data related to the workflow of the verification bot.

Please note that `bot.py` is solely dependent on `bot_utils.py` and `bot_utils.py` is solely dependent on `verification_state.py`.

## Setup Instructions

### Running Locally:
1. Obtain a Google Services Credentials JSON file and place it in the `/projects` directory. More information on doing this can be found here: https://medium.com/@jb.ranchana/write-and-append-dataframes-to-google-sheets-in-python-f62479460cf0

2. Create a python virtual environment with `python -m venv path/to/venv` and install dependencies with `python -m pip install -r requirements.txt`

3. Inside of the `project/` directory, create a `.env` file with the following structure:
```
# Discord Bot Information
BOT_TOKEN="BOT TOKEN CODE"
BOT_URL="BOT URL"
GUILD_ID="SERVER ID CODE"
# Verification Email Credentials
EMAIL_USER="EMAIL TO SEND VERIFCATION CODES"
EMAIL_PASS="EMAIL PASSWORD TO SEND VERIFICATION CODES"
SMTP_ADDR="DOMAIN OF SMTP SERVER"   // This is "smtp.google.com" by default
# Google Services Credentials
SHEET_KEY="KEY TO GOOGLE SHEET"
SHEET_NAME="NAME OF SHEET TAB"
GS_CREDS_FNAME="NAME OF GOOGLE SERVICES CREDENTIALS FILE IN /projects DIRECTORY"
```

4. Add the bot to your server with a link from the maintainer and run `project/main.py` to start the bot


## Usage Instructions

Assuming the bot has already been setup and is running properly, whenever a user enters the discord server, they will be sent a direct message by LoRA Bot on Discord asking them to answer a few questions and verify their RIT email.

Once a user has been verified, they will be given the `@Tiger` role on the League of RIT Discord server.

If a user is not an RIT student, they will need to contact a League of RIT Discord server admin/moderator to gain access to the server with the `@NON-RIT` role.

**Note that the bot considers all users with only the @everyone role as an unverified user.**
**Also note that whenever the bot is started up, all users who are unverified will receive a direct message asking for verification.**

## Credits

The League of RIT Discord Verification Bot was developed at the request of the League of RIT club president by Benjamin Piro, a current B.Sc./M.Sc. Computer Science student at the Rochester Institute of Technology.

He can be best contacted through his email: benpiro1118@gmail.com

## License

MIT License

Copyright (c) 2023 Benjamin Piro

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.