import discord
from discord.ext import commands
import datetime

"""Cog | Template

This is a template put in place to be used
when creating a new Cog file.

NOTE: All commands are restricted to server use only by default,
remove the `@commands.guild_only()` line before any command that
should also be able to be used in a DM.
"""
class New(commands.Cog, name = "New"):
    """
    This comment will show up in the help message, be careful.
    """
    def __init__(self, bot):
        self.bot = bot
        print(f"{self.bot.OK} {self.bot.TIMELOG()} Loaded New Cog.")

    def cog_unload():
        print(f"{self.bot.OK} {self.bot.TIMELOG()} Unloaded New Cog.")

    @commands.guild_only()
    @commands.command(name = "SAMPLE", help = "Just a placeholder.", brief = "If parameters then examples here")
    async def sample(self, ctx):
        """Command | Sample

        This is a template for a standard command.
        """
        pass

    @commands.Cog.listener()
    async def on_message(self, message):
        """Listener | Sample

        This is a template for a standard message listener.
        """
        if not message.author.bot:
            pass

def setup(bot):
    """Setup

    The function called by Discord.py when adding another file in a multi-file project.
    """
    bot.add_cog(New(bot))
