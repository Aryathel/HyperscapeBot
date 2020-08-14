import discord
from discord.ext import commands
import datetime

"""Cog | Error Handler

This cog handles all errors for the bot, preventing
the runtime from crashing or forcing bot exit.

NOTE: All commands are restricted to server use only by default,
remove the `@commands.guild_only()` line before any command that
should also be able to be used in a DM.
"""
class Errors(commands.Cog, name = "Error Handling"):
    """
    Commands relating to bot error handling.
    """
    def __init__(self, bot):
        self.bot = bot
        print(f"{bot.OK} {bot.TIMELOG()} Loaded Error Cog.")

    @commands.guild_only()
    @commands.command(name = "broken", aliases = ['borked'], help = "Used to report when the bot has stopped working.", brief = "")
    async def err_report(self, ctx):
        """Command | Report Broken Bot

        This command is used to report when the bot is broken or stopped working,
        it prints some useful information to the console and attempts to
        ping the owner of the bot.
        """
        if self.bot.delete_commands:
            await ctx.message.delete()

        user = self.bot.get_user(self.bot.broken_user_id)
        embed = self.bot.embed_util.get_embed(
            title = "I'm broken!",
            desc = f"Come fix me {user.mention}!",
            author = ctx.author
        )
        await ctx.send(content = user.mention, embed = embed)

        self.print_log(type = self.bot.WARN, message = "Received 'broken' Command", ctx = ctx)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Listener | Command Error Handler

        Take in command specific errors and return response to user
        based on error.

        If the error is not in the list of directly handled errors,
        reply with the command error, and send a log of the error to
        the log channel.
        """
        if self.bot.delete_commands:
            await ctx.message.delete()

        if isinstance(error, commands.CommandNotFound):
            self.print_log(type = self.bot.WARN, message = "Command Not Found", ctx = ctx)
            embed = self.bot.embed_util.get_embed(
                title = "Command Not Found",
                author = ctx.author
            )
            await ctx.send(embed = embed)
            embed = self.bot.embed_util.update_embed(
                embed = embed,
                author = ctx.author,
                ts = True
            )
            await self.bot.log_channel.send(embed = embed)

        elif isinstance(error, commands.BadArgument) and "not found" in str(error):
            self.print_log(type = self.bot.ERR, message = f"{str(error).split(' ')[0]} Not Found", ctx = ctx, err = error)
            embed = self.bot.embed_util.get_embed(
                title =  f"{str(error).split(' ')[0]} Not Found",
                author = ctx.author,
                fields = [{
                    "name": "Received",
                    "value": "`" + str(error).split('\"')[1] + "`",
                    "inline": False
                }]
            )
            await ctx.send(embed = embed)
            embed = self.bot.embed_util.update_embed(
                embed = embed,
                author = ctx.author,
                ts = True
            )
            await self.bot.log_channel.send(embed = embed)

        elif isinstance(error, commands.CheckFailure):
            self.print_log(
                type = self.bot.WARN,
                message = "User attempted to use command without permission",
                ctx = ctx
            )

            embed = self.bot.embed_util.get_embed(
                title = "Permission Denied",
                desc = f"I'm sorry {ctx.author.name}, I'm afraid I can't to that.",
                author = ctx.author
            )
            await ctx.send(embed = embed)
            embed = self.bot.embed_util.update_embed(
                embed = embed,
                author = ctx.author,
                ts = True
            )
            await self.bot.log_channel.send(embed = embed)

        elif isinstance(error, commands.MissingRequiredArgument):
            error = str(error).split(" ")
            error[0] = '`' + error[0] + '`'
            error = " ".join(error)

            self.print_log(type = self.bot.ERR, message = "Missing required parameter", err = error, ctx = ctx)

            embed = self.bot.embed_util.get_embed(
                title = "Missing Required Parameter",
                desc = error.split(' ')[0],
                author = ctx.author
            )
            await ctx.send(embed = embed)
            embed = self.bot.embed_util.update_embed(
                embed = embed,
                author = ctx.author,
                ts = True
            )
            await self.bot.log_channel.send(embed = embed)

        else:
            embed = self.bot.embed_util.get_embed(
                title = "Command Failed",
                desc = str(error),
                author = ctx.author
            )
            await ctx.send(embed = embed)
            embed = self.bot.embed_util.update_embed(
                embed = embed,
                author = ctx.author,
                ts = True
            )
            await self.bot.log_channel.send(embed = embed)

            await self.err_report(ctx)
            self.print_log(type = self.bot.ERR, message = error)

    @commands.Cog.listener()
    async def on_error(self, error):
        """Listener | Global Error Handler

        The generalized handler for all errors taht happen in the bot,
        preventing suspension of runtime should something go wrong.
        """
        self.print_log(type = self.bot.ERR, message = error)

    def print_log(self, type, message, err = None, ctx = None):
        print(f"{type} {self.bot.TIMELOG()} {message}:")
        if err:
            print(f"{' ' * 35} Error: {err}")
        if ctx:
            failed_com = ctx.message.content.split(' ')
            if len(failed_com) > 1:
                print(f"{' ' * 35} Command: {failed_com[0]} | Args: {' '.join(failed_com[1:])}")
            else:
                print(f"{' ' * 35} Command: {failed_com[0]}")
            print(f"{' ' * 35} Author: {ctx.author} | ID: {ctx.author.id}")
            print(f"{' ' * 35} Channel: {ctx.channel} | ID: {ctx.channel.id}")

def setup(bot):
    """Setup

    The function called by Discord.py when adding another file in a multi-file project.
    """
    bot.add_cog(Errors(bot))
