"""Resource | Data Manager

This class manages all of the loading and
saving of the config, permissions, and data.
"""
import pickle
import os
import aiohttp
from discord import Color
from colorama import Fore
import datetime

class DataManager:
    """Class | Data Manager

    This class is in charge of a variety of functions
    pertaining to monotonous data management,
    as well as loading and saving data to and from
    the data storage file.

    Args
    ----------
    bot - The discord.Client object of the bot connection.
    """
    def __init__(self, bot):
        self.bot = bot

    def load_config(self):
        """Setup | Bot Config

        Loading Config variables into bot attributes.

        See 'Config.yml' for specifics on each setting.
        """
        with open("./Config.yml", 'r') as file:
            config = self.bot.yaml.load(file)

        # Save config files to the bot.
        self.bot.config = config

        # Main Settings
        self.bot.TOKEN               = os.getenv(config['Token Env Var'])
        self.bot.prefix              = config['Prefix']
        self.bot.online_message      = config['Online Message']
        self.bot.restarting_message  = config['Restarting Message']
        self.bot.data_file           = os.path.abspath(config['Data File'])
        self.bot.show_game_status    = config['Game Status']['Active']
        self.bot.game_to_show        = config['Game Status']['Game']
        self.bot.log_channel_id      = config['Log Channel']
        self.bot.broken_user_id      = config['Broken User ID']
        self.bot.invite_link         = config['Server Invite']

        # Embed Options
        self.bot.embed_color = Color.from_rgb(
            config['Embed Settings']['Color']['r'],
            config['Embed Settings']['Color']['g'],
            config['Embed Settings']['Color']['b']
        )
        self.bot.footer =              config['Embed Settings']['Footer']['Text']
        self.bot.footer_image =        config['Embed Settings']['Footer']['Icon URL']
        self.bot.delete_commands =     config['Embed Settings']['Delete Commands']
        self.bot.show_command_author = config['Embed Settings']['Show Author']
        self.bot.embed_ts =            lambda: datetime.datetime.now(datetime.timezone.utc)

        # Logging Variables
        self.bot.OK = f"{Fore.GREEN}[OK]{Fore.RESET}  "
        self.bot.WARN = f"{Fore.YELLOW}[WARN]{Fore.RESET}"
        self.bot.ERR = f"{Fore.RED}[ERR]{Fore.RESET} "
        self.bot.TIMELOG = lambda: datetime.datetime.now().strftime('[%m/%d/%Y | %I:%M:%S %p]')

    def load_permissions(self):
        """Setup | Command Permissions

        Loading Permission variables into bot attributes.

        See 'Permissions.yml' for specifics on each setting.
        """
        bot_permissions = {}
        with open("./Permissions.yml", 'r') as file:
            permissions = self.bot.yaml.load(file)
            # Raw permission input is formatted to have role IDs in place.
            roles = dict(permissions['Roles'])
            for key in permissions.keys():
                if not key in (None, 'Roles'):
                    bot_permissions[key] = []
                    for permission in permissions[key]:
                        bot_permissions[key].append(permission.format(**roles))

        self.bot.permissions = permissions

    def save_data(self):
        """Data | Saving

        Open the data file and save the bot's data to it.

        Overwrites previous data in file.
        """
        with open(self.bot.data_file, 'wb+') as save_file:
            try:
                pickle.dump(self.bot.data, save_file)
            except Exception as e:
                print('Could not save data: ' + str(e))

    def load_data(self):
        """Data | Loading

        Check if the data file exists, if it does, load it, if not, create it.

        If the data file exists but has not data, give it a new empty data object.
        """
        if os.path.exists(self.bot.data_file):
            with open(self.bot.data_file, 'rb') as file:
                #content = file.read()
                #if len(content) == 0:
                #    self.bot.data = {}
                #    self.save_data()
                #else:
                #    self.bot.data = json.loads(content)
                self.bot.data = pickle.load(file)
        else:
            self.bot.data = {}
            self.save_data()

    async def update_user_cache(self, name, platform = "uplay"):
        """Function | Update User Stat Profile

        This function is used to handle the updating of the given name's
        stat data within the data cache. The data can only be updated every 10 minutes,
        so this is how it is handled.

        Args
        ----------
        name - The profile name to update
        platform - The platform the user's profile is on, either `uplay`,
            `xbl`, or `psn`.
        """
        if name.lower() in self.bot.data['HyperscapeUsers']['profiles']:
            profile = self.bot.data['HyperscapeUsers']['profiles'][name.lower()]
            if datetime.datetime.now() - datetime.timedelta(minutes = 10) > profile.last_refresh:
                async with aiohttp.ClientSession() as session:
                    await self.bot.api.update_player_by_id(session, profile.player_id)
                    self.bot.data['HyperscapeUsers']['profiles'][name.lower()] = await self.bot.api.get_profile_by_id(session, profile.player_id)
                    self.save_data()
            return True
        else:
            profile = await self.bot.api.get_profile(name, platform)
            if profile:
                self.bot.data['HyperscapeUsers']['profiles'][name.lower()] = profile
                self.save_data()
                return True
            else:
                return False

    def get_stat_category_fields(self, name, profile):
        """Function | Get Stat Category Embed Fields

        This function returns a list of field elements to be used
        in the created of embed responses when a user searches an entire stat
        category instead of a singular stat.

        Args
        ----------
        name - The name of the stat category being searched
        profile - An instance of the Profile class found in './Resources/APISession.py'
        """
        if name == "main":
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
        elif name == "solo":
            fields = [
                {
                    "name": "Solo Winrate",
                    "value": profile.solo_winrate,
                    "inline": True
                },
                {
                    "name": "Solo Wins",
                    "value": profile.solo_wins,
                    "inline": True
                },
                {
                    "name": "Solo Losses",
                    "value": profile.solo_losses,
                    "inline": True
                },
                {
                    "name": "Solo Matches",
                    "value": profile.solo_matches,
                    "inline": True
                },
                {
                    "name": "Crown Wins",
                    "value": profile.solo_crown_wins,
                    "inline": True
                },
                {
                    "name": "Time Played",
                    "value": profile.solo_time_played,
                    "inline": True
                }
            ]
        elif name == "squad":
            fields = [
                {
                    "name": "Squad Winrate",
                    "value": profile.squad_winrate,
                    "inline": True
                },
                {
                    "name": "Squad Wins",
                    "value": profile.squad_wins,
                    "inline": True
                },
                {
                    "name": "Squad Losses",
                    "value": profile.squad_losses,
                    "inline": True
                },
                {
                    "name": "Squad Matches",
                    "value": profile.squad_matches,
                    "inline": True
                },
                {
                    "name": "Crown Wins",
                    "value": profile.squad_crown_wins,
                    "inline": True
                },
                {
                    "name": "Time Played",
                    "value": profile.squad_time_played,
                    "inline": True
                }
            ]
        elif name == "general":
            fields = [
                {
                    "name": "Kills",
                    "value": profile.kills,
                    "inline": True
                },
                {
                    "name": "Matches",
                    "value": profile.matches,
                    "inline": True
                },
                {
                    "name": "Avg. Kills per Match",
                    "value": profile.avg_kills_per_match,
                    "inline": True
                },
                {
                    "name": "Avg. Damage per Kill",
                    "value": profile.avg_dmg_per_kill,
                    "inline": True
                },
                {
                    "name": "Headshot Accuracy",
                    "value": profile.headshot_accuracy,
                    "inline": True
                },
                {
                    "name": "Headshot Damage",
                    "value": profile.weapon_headshot_damage,
                    "inline": True
                },
                {
                    "name": "Weapon Damage",
                    "value": profile.weapon_headshot_damage + profile.weapon_body_damage,
                    "inline": True
                },
                {
                    "name": "Hack Damage",
                    "value": profile.damage_by_items,
                    "inline": True
                },
                {
                    "name": "Chests Broken",
                    "value": profile.chests_broken,
                    "inline": True
                },
                {
                    "name": "Fusions",
                    "value": profile.fusions,
                    "inline": True
                },
                {
                    "name": "Revives",
                    "value": profile.revives,
                    "inline": True
                },
                {
                    "name": "Time Played",
                    "value": profile.time_played,
                    "inline": True
                }
            ]
        elif name == "best":
            fields = [
                {
                    "name": "Most Kills",
                    "value": profile.careerbest_kills,
                    "inline": True
                },
                {
                    "name": "Long Range Kills",
                    "value": profile.careerbest_long_range_final_blows,
                    "inline": True
                },
                {
                    "name": "Short Range Kills",
                    "value": profile.careerbest_short_range_final_blows,
                    "inline": True
                },
                {
                    "name": "Damage Done",
                    "value": profile.careerbest_damage_done,
                    "inline": True
                },
                {
                    "name": "Headshot Damage",
                    "value": profile.careerbest_critical_damage,
                    "inline": True
                },
                {
                    "name": "Assists",
                    "value": profile.careerbest_assists,
                    "inline": True
                },
                {
                    "name": "Healed",
                    "value": profile.careerbest_healed,
                    "inline": True
                },
                {
                    "name": "Survival Time",
                    "value": profile.careerbest_survival_time,
                    "inline": True
                },
                {
                    "name": "Items Fused",
                    "value": profile.careerbest_item_fused,
                    "inline": True
                },
                {
                    "name": "Maximum Fusion",
                    "value": profile.careerbest_fused_to_max,
                    "inline": True
                },
                {
                    "name": "Revealed",
                    "value": profile.careerbest_revealed,
                    "inline": True
                }
            ]
        elif name == "weapons":
            fields = [
                {
                    "name": f"{profile.dragonfly.name} Kills",
                    "value": profile.dragonfly.kills,
                    "inline": True
                },
                {
                    "name": f"{profile.mammoth.name} Kills",
                    "value": profile.mammoth.kills,
                    "inline": True
                },
                {
                    "name": f"{profile.ripper.name} Kills",
                    "value": profile.ripper.kills,
                    "inline": True
                },
                {
                    "name": f"{profile.dtap.name} Kills",
                    "value": profile.dtap.kills,
                    "inline": True
                },
                {
                    "name": f"{profile.harpy.name} Kills",
                    "value": profile.harpy.kills,
                    "inline": True
                },
                {
                    "name": f"{profile.komodo.name} Kills",
                    "value": profile.komodo.kills,
                    "inline": True
                },
                {
                    "name": f"{profile.hexfire.name} Kills",
                    "value": profile.hexfire.kills,
                    "inline": True
                },
                {
                    "name": f"{profile.riot.name} Kills",
                    "value": profile.riot.kills,
                    "inline": True
                },
                {
                    "name": f"{profile.salvo.name} Kills",
                    "value": profile.salvo.kills,
                    "inline": True
                },
                {
                    "name": f"{profile.skybreaker.name} Kills",
                    "value": profile.skybreaker.kills,
                    "inline": True
                },
                {
                    "name": f"{profile.protocol.name} Kills",
                    "value": profile.protocol.kills,
                    "inline": True
                }
            ]
        elif name == "hacks":
            fields = [
                {
                    "name": f"{profile.mine.name} Fusions",
                    "value": profile.mine.fusions,
                    "inline": True
                },
                {
                    "name": f"{profile.slam.name} Fusions",
                    "value": profile.slam.fusions,
                    "inline": True
                },
                {
                    "name": f"{profile.shockwave.name} Fusions",
                    "value": profile.shockwave.fusions,
                    "inline": True
                },
                {
                    "name": f"{profile.wall.name} Fusions",
                    "value": profile.wall.fusions,
                    "inline": True
                },
                {
                    "name": f"{profile.heal.name} Fusions",
                    "value": profile.heal.fusions,
                    "inline": True
                },
                {
                    "name": f"{profile.teleport.name} Fusions",
                    "value": profile.teleport.fusions,
                    "inline": True
                },
                {
                    "name": f"{profile.ball.name} Fusions",
                    "value": profile.ball.fusions,
                    "inline": True
                },
                {
                    "name": f"{profile.invis.name} Fusions",
                    "value": profile.invis.fusions,
                    "inline": True
                },
                {
                    "name": f"{profile.armor.name} Fusions",
                    "value": profile.armor.fusions,
                    "inline": True
                },
                {
                    "name": f"{profile.magnet.name} Fusions",
                    "value": profile.magnet.fusions,
                    "inline": True
                }
            ]

        return fields

    def get_weapon_stat_embed(self, name, profile):
        """Function | Get Weapon Stat Embed

        This function returns information on the stats a person has
        for a specific chosen weapon

        Args
        ----------
        name - The name of the weapon searched
        profile - profile - An instance of the Profile class found in './Resources/APISession.py'
        """
        stat = getattr(profile, name)
        embed = self.bot.embed_util.get_embed(
            title = f"{stat.name} Stats",
            thumbnail = profile.avatar_url,
            author_url = profile.url,
            fields = [
                {
                    "name": "Kills",
                    "value": stat.kills,
                    "inline": True
                },
                {
                    "name": "Damage",
                    "value": stat.damage,
                    "inline": True
                },
                {
                    "name": "Headshot Damage",
                    "value": stat.headshot_damage,
                    "inline": True
                },
                {
                    "name": "Fusions",
                    "value": stat.fusions,
                    "inline": True
                },
                {
                    "name": "Headshot Accuracy",
                    "value": f"{stat.hs_accuracy}%",
                    "inline": True
                }
            ]
        )

        return embed

    def get_hack_stat_embed(self, name, profile):
        """Function | Get Hack Stat Embed

        This function returns information on the stats a person has
        for a specific chosen hack

        Args
        ----------
        name - The name of the hack searched
        profile - profile - An instance of the Profile class found in './Resources/APISession.py'
        """
        stat = getattr(profile, name)
        embed = self.bot.embed_util.get_embed(
            title =f"{stat.name} Stats",
            thumbnail = profile.avatar_url,
            author_url = profile.url,
            fields = [
                {
                    "name": "Kills",
                    "value": stat.kills,
                    "inline": True
                },
                {
                    "name": "Damage",
                    "value": stat.damage,
                    "inline": True
                },
                {
                    "name": "Fusions",
                    "value": stat.fusions,
                    "inline": True
                }
            ]
        )

        return embed

    def update_leaderboards(self):
        pass
