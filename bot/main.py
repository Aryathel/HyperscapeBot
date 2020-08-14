"""Python Library Imports

Discord libraries for, well... Discord.

Datetime... do I really need to explain?

Ruamel.Yaml to allow comments to remain in YAML files when reading/writing them.

OS for file system and environment variable stuff.

Resources.Data for repetitive data file management, found in ./Resources/Data.py

Colorama for fancy colored logging.
"""

import discord
from discord.ext import commands
import datetime
from ruamel.yaml import YAML
import os
from Resources.Data import DataManager
from Resources.Utility import EmbedUtil
from Resources.APISession import APISession
from colorama import init
init()

yaml = YAML()

def get_prefix(bot, message):
    """Function | Dynamic Prefix Manager

    Allows for dynamically changing prefix by reading from
    config actively.

    'prefix' command can update the bot prefix in this way.
    """
    return bot.prefix

# Create the 'bot' instance, using the fucntion above for getting the prefix.
bot = commands.Bot(command_prefix=get_prefix, description="Heroicos_HM's Custom Bot", case_insensitive = True)

# Remove the help command to leave room for implementing a custom one.
bot.remove_command('help')

# Save the yaml tool to the bot.
bot.yaml = yaml

"""Setup | Initial Data Loading/Prep

Create a DataManager instance, then load:
- Config.yml
- Permissions.yml
- ./Data/data_storage.json

Then create an instance of the Embed tool.
"""
bot.data_manager = DataManager(bot)
bot.data_manager.load_config()
bot.data_manager.load_permissions()
bot.data_manager.load_data()

bot.api = APISession()

bot.embed_util = EmbedUtil(bot)

# List of extension files to load.
extensions = [
    'Cogs.Errors',
    'Cogs.General',
    'Cogs.Help',
    'Cogs.HyperscapeStats'
]
# Load the extension files listed above.
for extension in extensions:
    bot.load_extension(extension)

print(f"{bot.OK} {bot.TIMELOG()} Connecting to Discord...")

@bot.event
async def on_ready():
    """Listener | On Discord Connection

    Triggered when the bot successfully connects with Discord.

    Sets up the remaining initial configuration for the bot and loads all Cogs.
    """
    # Get the log channel object first, this allows for compartmentalized errors.
    bot.log_channel = bot.get_channel(bot.log_channel_id)

    print(f"{bot.OK} {bot.TIMELOG()} Logged in as {bot.user} and connected to Discord! (ID: {bot.user.id})")

    # Set the playing status of the bot to what is set in the config.
    if bot.show_game_status:
        game = discord.Game(name = bot.game_to_show.format(prefix = bot.prefix))
        await bot.change_presence(activity = game)

    # Create online message.
    embed = bot.embed_util.get_embed(
        title = bot.online_message.format(username = bot.user.name),
        ts = True
    )
    # Set the log channel object to a bot variable for later use.
    await bot.log_channel.send(embed = embed)

    # Set the bot start time for use in the uptime command.
    bot.start_time = bot.embed_ts()

@bot.check
async def command_permissions(ctx):
    """Check | Global Permission Manager

    This is attached to all commands.

    When a comand is used this function will use the permissions imported
    from Permissions.yml to verify that a user is/is not allowed
    to use a command.
    """
    # Administrators are always allowed to use the command.
    if ctx.author.guild_permissions.administrator:
        return True
    else:
        # Finding permission name scheme of a command.
        name = ctx.command.name
        if ctx.command.parent:
            command = ctx.command
            parent_exists = True
            while parent_exists == True:
                name = ctx.command.parent.name + '-' + name
                command = ctx.command.parent
                if not command.parent:
                    parent_exists = False

        """Checking command permissions

        For each role ID listed for a command, check if the user has that role id.

        If they do, allow command usage, otherwise, proceed to checking next role on the list.

        If the user does not have any of the roles, deny the command usage.
        """
        if name in ctx.bot.permissions.keys():
            for permission in ctx.bot.permissions[name]:
                try:
                    role = ctx.guild.get_role(int(permission))
                    if role in ctx.author.roles:
                        return True
                except Exception as e:
                    print(e)
            return False
        else:
            return True

try:
    bot.run(bot.TOKEN, bot = True, reconnect = True)
except discord.LoginFailure:
    print(f"{bot.ERR} {bot.TIMELOG()} Invalid TOKEN Variable: {bot.TOKEN}")
    input("Press enter to continue.")
