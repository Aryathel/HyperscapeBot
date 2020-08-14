import asyncio

import aiohttp
import discord
from discord.ext import commands
import datetime

from Resources.Enums import StatCategory, WeaponStat, HackStat, Stat, Platforms

"""Cog | Hyperscape Stats

This Cog is in charge of handling all user lookup and stat reporting,
as well as caching user information locally to prevent excessive API requests.

NOTE: All commands are restricted to server use only by default,
remove the `@commands.guild_only()` line before any command that
should also be able to be used in a DM.
"""
class HyperscapeStats(commands.Cog, name = "Hyperscape Stats"):
    """
    Commands relating to getting and viewing Hyperscape profile stats.
    """
    def __init__(self, bot):
        self.bot = bot
        if not 'HyperscapeUsers' in self.bot.data.keys():
            self.bot.data['HyperscapeUsers'] = {"profiles":{}, "discords": {}}
            self.bot.data_manager.save_data()
        print(f"{self.bot.OK} {self.bot.TIMELOG()} Loaded Hyperscape Stats Cog.")

    def cog_unload():
        print(f"{self.bot.OK} {self.bot.TIMELOG()} Unloaded Hyperscape Stats Cog.")

    @commands.guild_only()
    @commands.group(name = "profile", aliases = ['p'], help = "Commands about player profiles.", invoke_without_command = True, case_insensitive = True)
    async def profile(self, ctx, user: discord.User = None):
        """Command | Check User Profile

        Check the linked hyperscape profile of a Discord user.

        Args
        ----------
        user - A discord.User class instance if given,
            set to the message author it not given
        """
        # Display the "Bot is typing..." message
        await ctx.trigger_typing()

        # If there was no user given,
        # set the user to the message author
        if not user:
            user = ctx.author

        # If that user has a linked profile
        if user.id in self.bot.data['HyperscapeUsers']['discords']:
            # Get the cached profile information
            prof_name = self.bot.data['HyperscapeUsers']['discords'][user.id].lower()
            profile = self.bot.data['HyperscapeUsers']['profiles'][prof_name]
            updated = await self.bot.data_manager.update_user_cache(prof_name, profile.platform)
            if not updated:
                embed = self.bot.embed_util.get_embed(
                    title = "Failed to Find User",
                    desc = f"User `{prof_name}` was not able to be found on the `{profile.platform}` platform, please try again."
                )
                await ctx.send(embed = embed)
                return
            else:
                profile = self.bot.data['HyperscapeUsers']['profiles'][prof_name]

            # Create a response showing basic user stats
            embed = self.bot.embed_util.get_embed(
                author_url = profile.url,
                title = f"{profile.player_name}'s Stats Profile",
                thumbnail = profile.avatar_url,
                desc = f"*For more information on specific stats, use `{self.bot.prefix}stats`*",
                fields = [
                    {
                        "name": "Kills",
                        "value": profile.kills,
                        "inline": True
                    },
                    {
                        "name": "Assists",
                        "value": profile.assists,
                        "inline": True
                    },
                    {
                        "name": "KD",
                        "value": profile.kd,
                        "inline": True
                    },
                    {
                        "name": "Wins",
                        "value": profile.wins,
                        "inline": True
                    },
                    {
                        "name": "Losses",
                        "value": profile.losses,
                        "inline": True
                    },
                    {
                        "name": "Winrate",
                        "value": profile.winrate,
                        "inline": True
                    },
                    {
                        "name": "Crown Wins",
                        "value": profile.crown_wins,
                        "inline": True
                    },
                    {
                        "name": "Crown Pickups",
                        "value": profile.crown_pickups,
                        "inline": True
                    },
                    {
                        "name": "Crown Success",
                        "value": profile.crown_pickup_success_rate,
                        "inline": True
                    }
                ]
            )
            embed.set_author(
                name = user.name,
                icon_url = user.avatar_url,
                url = profile.avatar_url
            )
            await ctx.send(embed = embed)

        else:
            # If the user does not have a linked profile
            embed = self.bot.embed_util.get_embed(
                title = "No Profile Registered",
                desc = f"There are no stat profiles linked for {user.mention},\n but they can use `{self.bot.prefix}profile link Username` to get started."
            )
            await ctx.send(embed = embed)

    @commands.guild_only()
    @profile.command(name = "link", aliases = ['l'], help = "Link your Hyperscape stats to Discord.", brief = "Username")
    async def profile_link(self, ctx, name, platform = "pc"):
        """Command | Profile Linking

        This command allows Discor dusers to link their stats from
        Hyperscape to their Discord profile through the bot.

        Args
        ----------
        name - The search string of a username to look for.
        platform - The platform to look for the user on, either
            `pc`, `xbl`, or `psn`
        """
        await ctx.trigger_typing()
        # Make sure platform is valid
        try:
            platform = Platforms(platform).name
        except:
            embed = self.bot.embed_util.get_embed(
                title = "Invalid Platform",
                desc = f"You entered {platform} as the platform, platforms are limited to the following options:\n`pc`\n`psn`\n`xbl`"
            )
            await ctx.send(embed = embed)
            return

        if not name:
            name = ctx.author.name

        # Get user profile
        updated = await self.bot.data_manager.update_user_cache(name, platform)
        if not updated:
            embed = self.bot.embed_util.get_embed(
                title = "Failed to Find User",
                desc = f"User `{name}` was not able to be found on the `{platform}` platform, please try again."
            )
            await ctx.send(embed = embed)
        else:
            # Send profile search response
            profile = self.bot.data['HyperscapeUsers']['profiles'][name.lower()]

            # Ask the user if the found profile is theirs
            embed = self.bot.embed_util.get_embed(
                title = profile.player_name,
                author_url = profile.url,
                desc = "Is this your profile?",
                thumbnail = profile.avatar_url
            )
            msg = await ctx.send(embed = embed)

            # Add yes/no reactions to the message
            emojis = ['✅', '❌']
            for emoji in emojis:
                await msg.add_reaction(emoji)

            # wait for a user to add either response, or timeout after 60 seconds
            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in emojis and reaction.message.id == msg.id

            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
            except asyncio.TimeoutError:
                await msg.clear_reactions()
                embed = self.bot.embed_util.get_embed(
                    title = "Selection Timed Out"
                )
                await msg.edit(embed = embed)
                await asyncio.sleep(10)
                await ctx.message.delete()
                await msg.delete()
            else:
                if str(reaction.emoji) == '❌':
                    await ctx.message.delete()
                    await msg.delete()
                elif str(reaction.emoji) == '✅':
                    self.bot.data['HyperscapeUsers']['discords'][ctx.author.id] = profile.player_name
                    self.bot.data_manager.save_data()
                    await msg.clear_reactions()
                    embed = self.bot.embed_util.get_embed(
                        title = profile.player_name,
                        author_url = profile.url,
                        desc = f"{ctx.author.mention}'s profile is now linked to [{profile.player_name}]({profile.url}).\n\n*Use `{self.bot.prefix}profile` to view basic stats.*",
                        thumbnail = profile.avatar_url
                    )
                    await msg.edit(embed = embed)

    @commands.guild_only()
    @commands.command(name = "search", aliases = ['s'], help = "Search for a user's profile.\nUse `pc` for pc, `psn` for playstation, and `xbl` for xbox.", brief = "Username uplay")
    async def sample(self, ctx, name, platform = "pc"):
        """Command | Search User

        Search for a hyperscape user's profile.

        Args
        ----------
        name - The search string of a username to look for.
        platform - The platform to look for the user on, either
            `pc`, `xbl`, or `psn`
        """
        await ctx.trigger_typing()
        # Make sure platform is valid
        try:
            platform = Platforms(platform).name
        except:
            embed = self.bot.embed_util.get_embed(
                title = "Invalid Platform",
                desc = f"You entered {platform} as the platform, platforms are limited to the following options:\n`pc`\n`psn`\n`xbl`"
            )
            await ctx.send(embed = embed)
            return

        # Get user profile
        updated = await self.bot.data_manager.update_user_cache(name, platform)
        if not updated:
            embed = self.bot.embed_util.get_embed(
                title = "Failed to Find User",
                desc = f"User `{name}` was not able to be found on the `{platform}` platform, please try again."
            )
            await ctx.send(embed = embed)
        else:
            # Send profile search response
            profile = self.bot.data['HyperscapeUsers']['profiles'][name.lower()]
            embed = self.bot.embed_util.get_embed(
                author = profile.player_name,
                author_url = profile.url,
                thumbnail = profile.avatar_url,
                title = "Stats Profile",
                desc = f"*For more information on specific stats, use `{self.bot.prefix}stats`*",
                fields = [
                    {
                        "name": "Kills",
                        "value": profile.kills,
                        "inline": True
                    },
                    {
                        "name": "Assists",
                        "value": profile.assists,
                        "inline": True
                    },
                    {
                        "name": "KD",
                        "value": profile.kd,
                        "inline": True
                    },
                    {
                        "name": "Wins",
                        "value": profile.wins,
                        "inline": True
                    },
                    {
                        "name": "Losses",
                        "value": profile.losses,
                        "inline": True
                    },
                    {
                        "name": "Winrate",
                        "value": profile.winrate,
                        "inline": True
                    },
                    {
                        "name": "Crown Wins",
                        "value": profile.crown_wins,
                        "inline": True
                    },
                    {
                        "name": "Crown Pickups",
                        "value": profile.crown_pickups,
                        "inline": True
                    },
                    {
                        "name": "Crown Success",
                        "value": profile.crown_pickup_success_rate,
                        "inline": True
                    }
                ]
            )
            await ctx.send(embed = embed)

    @commands.guild_only()
    @commands.group(name = "stat", aliases = ['stats'], help = "Get information on specific stats for a user.")
    async def stats(self, ctx, category = None, user:discord.User = None):
        """Command | Stat Search

        Used to search up stats for a specific user,
        or to view list of available categories otherwise.

        Args
        ----------
        category - the category of stat to search,
            found in the StatCategory enum.
        user - A discord.User mention to find  alinked profile for
        """
        await ctx.trigger_typing()

        # This is trigger if no arguments are passed,
        # returns a list of valid categories if none are given
        if not category:
            embed = self.bot.embed_util.get_embed(
                title = "Category Not Found",
                desc = "Please view valid category inputs below.",
                fields = [
                    {
                        "name": "Stat Categorys",
                        "value": "\n".join(f"`{i}`" for i in list(StatCategory.__dict__['_member_map_'])),
                        "inline": True
                    },
                    {
                        "name": "Weapon Stats",
                        "value": f"`{self.bot.prefix}stat WeaponName`",
                        "inline": True
                    },
                    {
                        "name": "Hack Stats",
                        "value": f"`{self.bot.prefix}stat HackName`",
                        "inline": True
                    },
                    {
                        "name": "Individual Stats",
                        "value": "\n".join(f"`{i}`" for i in list(Stat.__dict__['_member_map_'])),
                        "inline": False
                    }
                ]
            )
            await ctx.send(embed = embed)
        else:
            try:
                # Try to find a category for the user input
                try:
                    category = StatCategory(category.lower())
                except:
                    try:
                        category = Stat(category.lower())
                    except:
                        try:
                            category = WeaponStat(category.lower())
                        except:
                            category = HackStat(category.lower())
            except:
                # If the category does not exist, return an error
                embed = self.bot.embed_util.get_embed(
                    title = "Category Not Found",
                    desc = "Please view valid category inputs below.",
                    fields = [
                        {
                            "name": "Stat Categorys",
                            "value": "\n".join(f"`{i}`" for i in list(StatCategory.__dict__['_member_map_'])),
                            "inline": True
                        },
                        {
                            "name": "Individual Stats",
                            "value": "\n".join(f"`{i}`" for i in list(Stat.__dict__['_member_map_'])),
                            "inline": True
                        },
                        {
                            "name": "Weapon Stats",
                            "value": f"{self.bot.prefix}stat WeaponName",
                            "inline": True
                        },
                        {
                            "name": "Hack Stats",
                            "value": f"{self.bot.prefix}stat HackName",
                            "inline": True
                        }
                    ]
                )
                await ctx.send(embed = embed)
                return

            # If the program reaches this point, there is a stat category.
            # if there is not  auser passed, the user is the command author
            if not user:
                user = ctx.author

            # if the user in question has a linked stat profile
            if user.id in self.bot.data['HyperscapeUsers']['discords']:
                # Get the cached profile information
                prof_name = self.bot.data['HyperscapeUsers']['discords'][user.id].lower()
                profile = self.bot.data['HyperscapeUsers']['profiles'][prof_name]
                updated = await self.bot.data_manager.update_user_cache(prof_name, profile.platform)
                if not updated:
                    embed = self.bot.embed_util.get_embed(
                        title = "Failed to Find User",
                        desc = f"User `{prof_name}` was not able to be found on the `{profile.platform}` platform, please try again."
                    )
                    await ctx.send(embed = embed)
                    return
                else:
                    profile = self.bot.data['HyperscapeUsers']['profiles'][prof_name]

                # return stat results
                if type(category) == StatCategory:
                    embed = self.bot.embed_util.get_embed(
                        title = f"{category.name.capitalize()} Stats",
                        thumbnail = profile.avatar_url,
                        fields = self.bot.data_manager.get_stat_category_fields(category.name, profile),
                        author_url = profile.url
                    )
                elif type(category) == Stat:
                    embed = self.bot.embed_util.get_embed(
                        title = f"{' '.join(i.capitalize() for i in category.name.split('_'))} Stat",
                        thumbnail = profile.avatar_url,
                        desc = getattr(profile, category.name),
                        author_url = profile.url
                    )
                elif type(category) == WeaponStat:
                    embed = self.bot.data_manager.get_weapon_stat_embed(category.name, profile)
                elif type(category) == HackStat:
                    embed = self.bot.data_manager.get_hack_stat_embed(category.name, profile)

                embed.set_author(
                    name = user.name,
                    icon_url = user.avatar_url,
                    url = profile.url
                )
                await ctx.send(embed = embed)
            else:
                # If the user does not have a linked profile
                embed = self.bot.embed_util.get_embed(
                    title = "No Profile Registered",
                    desc = f"There are no stat profiles linked for {user.mention},\n but they can use `{self.bot.prefix}profile link Username` to get started."
                )
                await ctx.send(embed = embed)


def setup(bot):
    """Setup

    The function called by Discord.py when adding another file in a multi-file project.
    """
    bot.add_cog(HyperscapeStats(bot))
