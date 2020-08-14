import asyncio
from enum import Enum
from aenum import MultiValueEnum

import aiohttp
import discord
from discord.ext import commands
import datetime

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

    class StatCategory(Enum):
        main = "main"
        solo = "solo"
        squad = "squad"
        general = "general"
        best = "best"

    class Stat(MultiValueEnum):
        wins = "wins", "win", "w"
        crown_wins = "crownwins", "crownwin", "crown_win", "crown_wins", "cw", "cws"
        damage = "damage", "dmg"
        assists = "assists", "assist", "ass"
        matches = "matches", "match", "ma"
        chests_broken = "chests_broken", "cb", "chestsbroken", "chest_broken", "chestbroken"
        crown_pickups = "crown_pickups", "crownpickups", "crown_pickup", "crownpickup", "cp", "cps"
        damage_done = "damage_done", "damagedone", "dmgdone", "dmgd"
        kills = "kills", "kill", "k", "ks"
        fusions = "fusions", "fusion", "f", "fs"
        revives = "revives", "revive", "rv", "rvs"
        time_played = "time_played", "timeplayed", "tmpd", "tmp"
        weapon_headshot_damage = "weapon_headshot_damage", "weaponheadshotdamage", "wpnhdshtdmg", "hdshtdmg"
        weapon_body_damage = "weapon_body_damage", "weaponbodydamage", "wpnbdydmg"
        damage_by_items = "damage_by_items", "dmg_by_items", "damagebyitems", "itmdmdg", "itemdamage", "item_damage"
        avg_kills_per_match = "avg_kills_per_match", "avg_kills", "avgkills"
        avg_dmg_per_kill = "avg_dmg_per_kill", "avg_damage_per_kill", "avgdamageperkill", "avgdmgkill"
        losses = "losses", "loss", "l", "ls"
        winrate = "winrate", "wnr"
        kd = "kd"
        headshot_accuracy = "headshot_accuracy", "hdshtacc"

    class Platforms(Enum):
        uplay = "pc"
        xbl = "xbl"
        psn = "psn"

    def __init__(self, bot):
        self.bot = bot
        if not 'HyperscapeUsers' in self.bot.data.keys():
            self.bot.data['HyperscapeUsers'] = {"profiles":{}, "discords": {}}
            self.bot.data_manager.save_data()
        print(f"{self.bot.OK} {self.bot.TIMELOG()} Loaded Hyperscape Stats Cog.")

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
                author_url = f"https://tabstats.com/hyperscape/player/{profile.player_name.lower()}/{profile.player_id}",
                title = f"{profile.player_name}'s Stats Profile",
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
                desc = f"There are no stat profiles linked for {user.mention},\n but they can use `{self.bot.prefix}profile link` to get started."
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
            platform = self.Platforms(platform).name
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
            platform = self.Platforms(platform).name
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
                        "value": "\n".join(f"`{i}`" for i in list(self.StatCategory.__dict__['_member_map_'])),
                        "inline": False
                    },
                    {
                        "name": "Individual Stats",
                        "value": "\n".join(f"`{i}`" for i in list(self.Stat.__dict__['_member_map_'])),
                        "inline": False
                    }
                ]
            )
            await ctx.send(embed = embed)
        else:
            try:
                # Try to find a category for the user input
                try:
                    category = self.StatCategory(category.lower())
                except:
                    category = self.Stat(category.lower())
            except:
                # If the category does not exist, return an error
                embed = self.bot.embed_util.get_embed(
                    title = "Category Not Found",
                    desc = "Please view valid category inputs below.",
                    fields = [
                        {
                            "name": "Stat Categorys",
                            "value": "\n".join(f"`{i}`" for i in list(self.StatCategory.__dict__['_member_map_'])),
                            "inline": False
                        },
                        {
                            "name": "Individual Stats",
                            "value": "\n".join(f"`{i}`" for i in list(self.Stat.__dict__['_member_map_'])),
                            "inline": False
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
                if type(category) == self.StatCategory:
                    embed = self.bot.embed_util.get_embed(
                        title = f"{category.name.capitalize()} Stats",
                        thumbnail = profile.avatar_url,
                        fields = self.bot.data_manager.get_stat_category_fields(category.name, profile)
                    )
                elif type(category) == self.Stat:
                    embed = self.bot.embed_util.get_embed(
                        title = f"{' '.join(i.capitalize() for i in category.name.split('_'))} Stat",
                        thumbnail = profile.avatar_url,
                        desc = getattr(profile, category.name)
                    )
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
                    desc = f"There are no stat profiles linked for {user.mention},\n but they can use `{self.bot.prefix}profile link` to get started."
                )
                await ctx.send(embed = embed)


def setup(bot):
    """Setup

    The function called by Discord.py when adding another file in a multi-file project.
    """
    bot.add_cog(HyperscapeStats(bot))
