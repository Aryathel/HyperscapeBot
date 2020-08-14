import discord
from discord.ext import commands
import datetime

"""Class | Custom Help Command

Contains all of the features for a custom help message depending on certain
values set when defining a command in the first place.
"""
class TheHelpCommand(commands.MinimalHelpCommand):
    async def send_bot_help(self, mapping):
        """Help | General Bot

        Send a help list for all of the bot commands.

        NOTE: Will be paginated at a later date.
        """
        fields = []
        for cog in mapping.keys():
            if cog:
                command_list = await self.filter_commands(mapping[cog], sort = True)
                if len(command_list) > 0:
                    fields.append({
                        "name": cog.qualified_name,
                        "value": f"{cog.description}\nCommands:\n" + ", ".join(f"`{command}`" for command in command_list),
                        "inline": False
                    })
        embed = self.context.bot.embed_util.get_embed(
            title = "Command Help",
            desc = f"A listing of all available commands sorted by grouping.\nTo learn more about specific commands, use `{self.clean_prefix}help <command>`",
            fields = fields,
            author = self.context.message.author
        )
        await self.get_destination().send(embed = embed)

    async def send_cog_help(self, cog):
        """Help | Cog Specific

        Sends help for all commands contained within a cog, by
        cog name.
        """
        embed = self.context.bot.embed_util.get_embed(
            title = f"{cog.qualified_name} Help",
            desc = f"{cog.description}\nTo learn more about specific commands, use `{self.clean_prefix}help <command>`",
            author = self.context.message.author,
            fields = [{
                "name": "Commands",
                "value": "\n".join("`{1.qualified_name}`".format(self, command) for command in cog.walk_commands() if not command.hidden),
                "inline": False
            }]
        )
        await self.get_destination().send(embed = embed)

    async def send_group_help(self, group):
        """Help | Grouped Commands

        Sends help message for all commands grouped in a parent command.
        """
        command_list = group.walk_commands()
        command_activation = []
        command_example = []
        for command in command_list:
            if "`" + command.qualified_name + " " + command.signature + "` - {}".format(command.help) not in command_activation and not command.hidden:
                command_activation.append("`" + command.qualified_name + " " + command.signature + "` - {}".format(command.help))
                if command.brief:
                    command_example.append("`" + self.clean_prefix + command.qualified_name + " " + command.brief + "`")
                else:
                    command_example.append("`" + self.clean_prefix + command.qualified_name + "`")

        fields = []
        if group.aliases:
            fields.append({
                "name": "Aliases",
                "value": ", ".join('`{}`'.format(alias) for alias in group.aliases),
                "inline": False
            })
        fields.append({
            "name": "Commands",
            "value": "\n".join(command_activation),
            "inline": False
        })
        fields.append({
            "name": "Examples",
            "value": "\n".join(command_example),
            "inline": False
        })

        embed = self.context.bot.embed_util.get_embed(
            title = f"'{group.qualified_name.capitalize()}' Help",
            desc = f"{group.help}\n\nFor more information on each command, use `{self.clean_prefix}help [command]`.",
            fields = fields,
            author = self.context.message.author
        )
        await self.get_destination().send(embed = embed)

    async def send_command_help(self, command):
        """Help | Command Specific

        Send help for a specific given single command.
        """
        fields = []
        if command.aliases:
            fields.append({
                "name": "Aliases",
                "value": ", ".join('`{}`'.format(alias) for alias in command.aliases),
                "inline": False
            })
        fields.append({
            "name": "Usage",
            "value": "`" + self.clean_prefix + command.qualified_name + " " + command.signature + "`",
            "inline": False
        })
        if command.brief:
            fields.append({
                "name": "Example",
                "value": "`" + self.clean_prefix + command.qualified_name + " " + command.brief + "`",
                "inline": False
            })
        else:
            fields.append({
                "name": "Example",
                "value": "`" + self.clean_prefix + command.qualified_name + "`",
                "inline": False
            })
        embed = self.context.bot.embed_util.get_embed(
            title = f"'{command.name.capitalize()}' Help",
            desc = f"{command.help}",
            fields = fields,
            author = self.context.message.author
        )
        await self.get_destination().send(embed = embed)

"""Cog | Class Loader

Loads the custom help command class above.
"""
class LoadHelp(commands.Cog, name = "Help"):
    """
    Lists all available commands, sorted by the Cog they are in.
    """
    def __init__(self, bot):
        self._original_help_command = bot.help_command
        bot.help_command = TheHelpCommand()
        bot.help_command.cog = self
        print(f"{bot.OK} {bot.TIMELOG()} Loaded Help Cog.")

def setup(bot):
    """Setup

    The function called by Discord.py when adding another file in a multi-file project.
    """
    bot.add_cog(LoadHelp(bot))
