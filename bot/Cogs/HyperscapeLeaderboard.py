import discord
from discord.ext import commands, tasks
import datetime

"""Cog | Hyper Scape Leaderboards

This cog is put in place to manage and update the server leaderboards,
and provide commands for viewing the leaderboards.

NOTE: All commands are restricted to server use only by default,
remove the `@commands.guild_only()` line before any command that
should also be able to be used in a DM.
"""
class HyperscapeLeaderboard(commands.Cog, name = "HyperscapeLeaderboard"):
    """
    This Cog handles creating and updating the leaderboards regularly,
    and allows for leaderboards to be viewed via commands.
    """
    def __init__(self, bot):
        self.bot = bot
        if not 'HyperscapeLeaderboard' in self.bot.data.keys():
            self.bot.data['HyperscapeLeaderboard'] = {}
        self.leaderboard_update.start()
        print(f"{self.bot.OK} {self.bot.TIMELOG()} Loaded Hyperscape Leaderboard Cog")

    def cog_unload():
        self.leaderboard_update.cancel()
        print(f"{self.bot.OK} {self.bot.TIMELOG()} Unloaded Hyperscape Leaderboard Cog")

    @commands.guild_only()
    @commands.command(name = "SAMPLE", help = "Just a placeholder.", brief = "If parameters then examples here")
    async def sample(self, ctx):
        """Command | Sample

        This is a template for a standard command.
        """
        pass

    @tasks.loop(minutes = 2)
    async def leaderboard_update(self):
        self.bot.data_manager.update_leaderboards()

    @leaderboard_update.before_loop
    async def before_leaderboard_update(self):
        await self.bot.wait_until_ready()

def setup(bot):
    """Setup

    The function called by Discord.py when adding another file in a multi-file project.
    """
    bot.add_cog(HyperscapeLeaderboard(bot))
