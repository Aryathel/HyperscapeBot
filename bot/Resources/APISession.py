import asyncio
import datetime
import json

import aiohttp
import requests

class WeaponStat:
    def __init__(self, options, name):
        self.name = name

        self.kills = options.get('kills')
        self.damage = options.get('damage')
        self.headshot_damage = options.get('headshot_damage')
        self.fusions = options.get('fusions')
        self.hs_accuracy = options.get('hs_accuracy')

class HackStat:
    def __init__(self, options, name):
        self.name = name

        self.kills = options.get('kills')
        self.damage = options.get('damage')
        self.headshot_damage = options.get('headshot_damage')
        self.fusions = options.get('fusions')
        self.hs_accuracy = options.get('headshot_accuracy')

class Profile:
    def __init__(self, options):
        self.found = options.get('found', False)

        if self.found:
            self.player = options.get('player')
            self.player_id = self.player.get('p_id')
            self.player_user = self.player.get('p_user')
            self.player_name = self.player.get('p_name')
            self.platform = self.player.get('p_platform')

            self.profile_verified = options.get('custom').get('verified')
            self.profile_visitors = options.get('custom').get('visitors')

            self.last_refresh = datetime.datetime.fromtimestamp(options.get('refresh').get('utime'))

            stats = options.get('data').get('stats')

            self.wins = stats.get('wins')
            self.crown_wins = stats.get('crown_wins')
            self.damage = stats.get('damage')
            self.assists = stats.get('assists')
            self.matches = stats.get('matches')
            self.chests_broken = stats.get('chests_broken')
            self.crown_pickups = stats.get('crown_pickups')
            self.damage_done = stats.get('damage_done')
            self.kills = stats.get('kills')
            self.fusions = stats.get('fusions')
            self.last_rank = stats.get('last_rank')
            self.revives = stats.get('revives')
            self.time_played = stats.get('time_played')
            self.solo_crown_wins = stats.get('solo_crown_wins')
            self.squad_crown_wins = stats.get('squad_crown_wins')
            self.solo_last_rank = stats.get('solo_last_rank')
            self.squad_last_rank = stats.get('squad_last_rank')
            self.solo_time_played = stats.get('solo_time_played')
            self.squad_time_played = stats.get('squad_time_played')
            self.solo_matches = stats.get('solo_matches')
            self.squad_matches = stats.get('squad_matches')
            self.solo_wins = stats.get('solo_wins')
            self.squad_wins = stats.get('squad_wins')
            self.careerbest_fused_to_max = stats.get('careerbest_fused_to_max')
            self.careerbest_chests = stats.get('careerbest_chests')
            self.careerbest_shockwaved = stats.get('careerbest_shockwaved')
            self.careerbest_damage_done = stats.get('careerbest_damage_done')
            self.careerbest_revealed = stats.get('careerbest_revealed')
            self.careerbest_assists = stats.get('careerbest_assists')
            self.careerbest_damage_shielded = stats.get('careerbest_shielded')
            self.careerbest_long_range_final_blows = stats.get('careerbest_long_range_final_blows')
            self.careerbest_short_range_final_blows = stats.get('careerbest_short_range_final_blows')
            self.careerbest_kills = stats.get('careerbest_kills')
            self.careerbest_item_fused = stats.get('careerbest_item_fused')
            self.careerbest_critical_damage = stats.get('careerbest_critical_damage')
            self.careerbest_survival_time = stats.get('careerbest_survival_time')
            self.careerbest_healed = stats.get('careerbest_healed')
            self.careerbest_revives = stats.get('careerbest_revives')
            self.careerbest_snare_triggered = stats.get('careerbest_snare_triggered')
            self.careerbest_mines_triggered = stats.get('careerbest_mines_triggered')
            self.weapon_headshot_damage = stats.get('weapon_headshot_damage')
            self.weapon_body_damage = stats.get('weapon_body_damage')
            self.damage_by_items = stats.get('damage_by_items')
            self.avg_kills_per_match = stats.get('avg_kills_per_match')
            self.avg_dmg_per_kill = stats.get('avg_dmg_per_kill')
            self.losses = stats.get('losses')
            self.solo_losses = stats.get('solo_losses')
            self.squad_losses = stats.get('squad_losses')
            self.winrate = stats.get('winrate')
            self.solo_winrate = stats.get('solo_winrate')
            self.squad_winrate = stats.get('squad_winrate')
            self.crown_pickup_success_rate = stats.get('crown_pick_success_rate')
            self.kd = stats.get('kd')
            self.headshot_accuracy = stats.get('headshot_accuracy')

            weapons = options.get('data').get('weapons')
            self.dragonfly = WeaponStat(weapons.get('Dragon Fly'), 'Dragon Fly')
            self.mammoth = WeaponStat(weapons.get('Mammoth MK1'), 'Mammoth MK1')
            self.ripper = WeaponStat(weapons.get('The Ripper'), 'The Ripper')
            self.dtap = WeaponStat(weapons.get('D-Tap'), 'D-Tap')
            self.harpy = WeaponStat(weapons.get('Harpy'), 'Harpy')
            self.komodo = WeaponStat(weapons.get('Komodo'), 'Komodo')
            self.hexfire = WeaponStat(weapons.get('Hexfire'), 'Hexfire')
            self.riot = WeaponStat(weapons.get('Riot One'), 'Riot One')
            self.salvo = WeaponStat(weapons.get('Salvo EPL'), 'Salvo EPL')
            self.skybreaker = WeaponStat(weapons.get('Skybreaker'), 'Skybreaker')
            self.protocol = WeaponStat(weapons.get('Protocol V'), 'Protocol V')

            hacks = options.get('data').get('hacks')
            self.mine = HackStat(hacks.get('Mine'), 'Mine')
            self.slam = HackStat(hacks.get('Slam'), 'Slam')
            self.shockwave = HackStat(hacks.get('Shockwave'), 'Shockwave')
            self.wall = HackStat(hacks.get('Wall'), 'Wall')
            self.heal = HackStat(hacks.get('Heal'), 'Heal')
            self.reveal = HackStat(hacks.get('Reveal'), 'Reveal')
            self.teleport = HackStat(hacks.get('Teleport'), 'Teleport')
            self.ball = HackStat(hacks.get('Ball'), 'Ball')
            self.invis = HackStat(hacks.get('Invisibility'), 'Invisibility')
            self.armor = HackStat(hacks.get('Armor'), 'Armor')
            self.magnet = HackStat(hacks.get('Magnet'), 'Magnet')

            self.avatar_url = f"https://ubisoft-avatars.akamaized.net/{self.player_id}/default_146_146.png"
            self.url = f"https://tabstats.com/hyperscape/player/{self.player_name.lower()}/{self.player_id}"

            self.is_premium = options.get('social').get('is_premium')

class APISession:
    def __init__(self):
        pass

    async def get_profile(self, username, platform = "uplay"):
        async with aiohttp.ClientSession() as session:
            id = await self.search_user_by_name(session, username, platform)
            if not id:
                return None
            profile = await self.get_profile_by_id(session, id)
            if profile.found:
                if profile.last_refresh < datetime.datetime.now() - datetime.timedelta(minutes = 10):
                    await self.update_player_by_id(session, id)
                    profile = await self.get_profile_by_id(session, id)
                return profile
            else:
                return None

    async def search_user_by_name(self, session, username, platform = "uplay"):
        async with session.get(f"https://hypers.apitab.com/search/{platform}/{username}") as r:
            if r.status == 200:
                res = await r.json()
                if type(res['players']) == dict:
                    top_res = list(res['players'].keys())[0]
                else:
                    return None
                return top_res

    async def get_profile_by_id(self, session, id):
        async with session.get(f"https://hypers.apitab.com/player/{id}?u=89031276") as r:
            if r.status == 200:
                res = await r.json()
                return Profile(res)

    async def update_player_by_id(self, session, id):
        async with session.get(f"https://hypers.apitab.com/update/{id}?u=89031276") as r:
            pass

if __name__ == "__main__":
    username = input("Input the username you would like to search: ")
    api = APISession()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(api.get_profile(username))
