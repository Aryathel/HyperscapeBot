import discord
from discord.ext import commands
import datetime
from math import trunc

"""Cog | General Commands

This Cog contains a list of commands that almost every program
should utilize.

NOTE: All commands are restricted to server use only by default,
remove the `@commands.guild_only()` line before any command that
should also be able to be used in a DM.
"""
class General(commands.Cog, name = "General"):
    """
    A general set of commands.
    """
    def __init__(self, bot):
        self.bot = bot
        print(f"{bot.OK} {bot.TIMELOG()} Loaded General Cog.")

    @commands.guild_only()
    @commands.command(name = "prefix", help = "Changes the command prefix for the bot.", brief = "?")
    async def prefix(self, ctx, prefix: str):
        if self.bot.delete_commands:
            await ctx.message.delete()

        old = self.bot.prefix
        self.bot.config['Prefix'] = prefix
        with open('./Config.yml', 'w') as file:
            self.bot.yaml.dump(self.bot.config, file)

        self.bot.prefix = prefix
        if self.bot.show_game_status:
            game = discord.Game(name = self.bot.game_to_show.format(prefix = self.bot.prefix))
            await self.bot.change_presence(activity = game)

        embed = self.bot.embed_util.get_embed(
            title = "Prefix Updated",
            desc = f"New Prefix: `{self.bot.prefix}`",
            fields = [
                {"name": "New", "value": f"{self.bot.prefix}command", "inline": True},
                {"name": "Old", "value": f"{old}command", "inline": True},
            ],
            author = ctx.author
        )
        await ctx.send(embed = embed)
        embed = self.bot.embed_util.update_embed(embed, ts = True, author = ctx.author)
        await self.bot.log_channel.send(embed = embed)

    @commands.guild_only()
    @commands.command(name = "restart", help = "Restarts the bot.", brief = "")
    async def restart(self, ctx):
        """Command | Restarts the bot.

        Sends a message to the log channel, adds a reaction to the message, then
        attempts to gracefully disconnect from Discord.

        Either a Batch or Shell script (depending on operating system) will then
        re-activate the bot, which allows the bot to take in file updates on the fly.
        """
        embed = self.bot.embed_util.get_embed(
            title = self.bot.restarting_message.format(username = self.bot.user.name),
            ts = True,
            author = ctx.author
        )
        await self.bot.log_channel.send(embed = embed)

        await ctx.message.add_reaction('✅')
        await self.bot.close()

    @commands.guild_only()
    @commands.command(name='uptime', help = 'Returns the amount of time the bot has been online.')
    async def uptime(self, ctx):
        """Command | Get Bot Uptime

        As the name implies... this returns the amount of time the
        bot has been online, given that the `bot.start_time` value
        was set in `main.py` in the `on_ready` function.
        """
        if self.bot.delete_commands:
            await ctx.message.delete()

        seconds = trunc((self.bot.embed_ts() - self.bot.start_time).total_seconds())
        hours = trunc(seconds / 3600)
        seconds = trunc(seconds - (hours * 3600))
        minutes = trunc(seconds / 60)
        seconds = trunc(seconds - (minutes * 60))

        embed = self.bot.embed_util.get_embed(
            title = f":alarm_clock: {self.bot.user.name} Uptime",
            desc = f"{hours} Hours\n{minutes} Minutes\n{seconds} Seconds",
            ts = True,
            author = ctx.author
        )
        await ctx.send(embed = embed)

    @commands.guild_only()
    @commands.command(name='ping', aliases=['pong'], help = 'Gets the current latency of the bot.')
    async def ping(self, ctx):
        """Command | Get Bot Ping

        Returns two values, the ping of the Discord bot to the API,
        and the ping time it takes from when the original message is sent
        to when the bot successfully posts its response.
        """
        if self.bot.delete_commands:
            await ctx.message.delete()

        embed = self.bot.embed_util.get_embed(
            title = ":ping_pong: Pong!",
            desc = "Calculating ping time...",
            author = ctx.author
        )
        m = await ctx.send(embed = embed)

        embed = self.bot.embed_util.update_embed(
            embed = embed,
            desc = "Message latency is {} ms\nDiscord API Latency is {} ms".format(
                trunc((m.created_at - ctx.message.created_at).total_seconds() * 1000),
                trunc(self.bot.latency * 1000)
            )
        )
        await m.edit(embed = embed)

    @commands.guild_only()
    @commands.command(name='invite', help = 'Returns the server invite link.', brief = "")
    async def invite(self, ctx):
        """Command | Get Server Invite

        Returns a static invite link which is set in the Config.yml file.
        """
        if self.bot.delete_commands:
            await ctx.message.delete()

        embed = self.bot.embed_util.get_embed(
            title = "Invite Link",
            desc = f"{self.bot.invite_link}",
            author = ctx.author
        )
        await ctx.send(embed = embed)

def setup(bot):
    """Setup

    The function called by Discord.py when adding another file in a multi-file project.
    """
    bot.add_cog(General(bot))
