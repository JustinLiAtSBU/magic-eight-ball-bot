# When you and your friends can't figure out what to do on Discord
## Installing dependencies
pip install -r requirements.txt

## Environment variables
Create a `.env` file in the root directory.

#### Discord token
You can find this in the developer portal.

    DISCORD_TOKEN='YOUR_TOKEN_HERE'

#### Friends
This environment variable is used to add a personal touch to the bot. The value
is a mapping of Discord usernames to real names, delimited by commas. The mapping
will be used by the bot. Whenever a command comes from a username in this environment
variable, the bot will respond with the real name it's mapped to.

    FRIENDS='FRIEND_ONE_USERNAME:REAL_NAME,FRIEND_TWO_USERNAME:REALNAME'
