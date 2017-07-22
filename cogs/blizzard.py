import json
import discord
import asyncio
import inspect
import datetime
import time
import re
import random
import math
import aiohttp

from itertools import combinations
from discord.ext import commands
from cogs.utils import config, checks
from numpy.random import choice
from collections import Counter
from collections import defaultdict
from cogs.utils.formats import Plural
from fuzzywuzzy import process

AFFIX1 = ["Raging"    ,  "Teeming"  , "Bolstering", "Sanguine" , "Bursting"  , "Teeming"  , "Raging"    , "Bolstering", "Teeming"   , "Sanguine" , "Bolstering", "Bursting" ]
AFFIX2 = ["Volcanic"  ,  "Explosive", "Grievous"  , "Volcanic" , "Skittish"  , "Quaking"  , "Necrotic"  , "Skittish"  , "Necrotic"  , "Grievous" , "Explosive" , "Quaking"  ]
AFFIX3 = ["Tyrannical",  "Fortified", "Tyrannical", "Fortified", "Tyrannical", "Fortified", "Tyrannical", "Fortified" , "Tyrannical", "Fortified", "Tyrannical", "Fortified"]

def load_json(filename):
    with open(filename, encoding='utf-8') as infile:
        return json.load(infile)
def write_json(filename, contents):
    with open(filename, 'w') as outfile:
        json.dump(contents, outfile, ensure_ascii=True, indent=4)


def blizzard_time(dt):
    delta = dt
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    years, days = divmod(days, 365)

    if years:
        if days:
            return '%s and %s' % (Plural(year=years), Plural(day=days))
        return '%s' % Plural(year=years)

    if days:
        if hours:
            return '%s and %s' % (Plural(day=days), Plural(hour=hours))
        return '%s' % Plural(day=days)

    if hours:
        if minutes:
            return '%s and %s' % (Plural(hour=hours), Plural(minute=minutes))
        return '%s' % Plural(hour=hours)

    if minutes:
        if seconds:
            return '%s and %s' % (Plural(minute=minutes), Plural(second=seconds))
        return '%s' % Plural(minute=minutes)
    return '%s' % Plural(second=seconds)



def get_mythic_progression(player_dictionary):
    achievements = player_dictionary["achievements"]
    plus_two = 0
    plus_five = 0
    plus_ten = 0    
    plus_fifteen = 0

    if 11162 in achievements["achievementsCompleted"]:
        plus_fifteen += 1
        
    if 33096 in achievements["criteria"]:
        index = achievements["criteria"].index(33096)
        plus_two = achievements["criteriaQuantity"][index]

    if 33097 in achievements["criteria"]:
        index = achievements["criteria"].index(33097)
        plus_five = achievements["criteriaQuantity"][index]

    if 33098 in achievements["criteria"]:
        index = achievements["criteria"].index(33098)
        plus_ten = achievements["criteriaQuantity"][index]
		
    if 32028 in achievements["criteria"]:
        index = achievements["criteria"].index(32028)
        plus_fifteen = achievements["criteriaQuantity"][index]


    return {
        "plus_two": plus_two,
        "plus_five": plus_five,
        "plus_ten": plus_ten,
        "plus_fifteen": plus_fifteen
    }


OW_Heroes = [
    "Zenyatta",
    "Mercy",
    "Ana",
    "Symmetra",
    "Lucio",
    "D.Va",
    "Orisa",
    "Reinhardt",
    "Roadhog",
    "Winston",
    "Zarya",
    "Bastion",
    "Hanzo",
    "Junkrat",
    "Mei",
    "Torbjorn",
    "Widowmaker",
    "Genji lmao",
    "McCree",
    "Pharah",
    "Reaper",
    "Soldier: 76",
    "Sombra",
    "Tracer"
]

RTB_BUFFS = ["Shark Infested Waters", "Grand Melee", "Jolly Roger", "True Bearing", "Broadsides", "Buried Treasure"]

def roll():
    die = [1, 2, 3, 4, 5, 6]
    return choice(die, 6)
def compute_score(outcome):
    counts = Counter(outcome)
    dd = defaultdict(list)
    [dd[v].append(k) for k, v in counts.items()]
    return dd[max(dd)]

def roll_the_bones():
    this_roll = roll()
    hmm = compute_score(this_roll)
    postme = ""
    for i in hmm:
         index = i-1
         postme += ":game_die:{}".format(RTB_BUFFS[index])
    return postme

WOW_CLASSES = [
    "Death Knight",
    "Druid",
    "Hunter",
    "Mage",
    "Monk",
    "Paladin",        
    "Priest",
    "Rogue", 
    "Shaman",
    "Warlock", 
    "Warrior", 
    "Demon Hunter"
    ]

WOW_SPECS = [
    "Blood",
    "Frost dk",
    "Unholy",
    "Havoc",
    "Vengeance",
    "Balance",
    "Feral",
    "Guardian",
    "Restoration Druid",
    "Beast Mastery",
    "Marksmanship",
    "Survival",
    "Arcane",
    "Fire",
    "Frost Mage",
    "Brewmaster",
    "Mistweaver",
    "Windwalker",
    "Holy Paladin",
    "Protection Paladin",
    "Retribution",
    "Discipline",
    "Holy Priest",
    "Shadow",
    "Assassination",
    "Outlaw",
    "Subtlety",
    "Elemental",
    "Enhancement",
    "Restoration Shaman",
    "Affliction",
    "Demonology",
    "Destruction",
    "Arms",
    "Fury",
    "Protection Warrior"
]






def id_to_boss(id):
    x = {
        1849 : "Skorpyron",
        1865 : "Chronomatic Anomaly",
        1867 : "Trilliax",
        1871 : "Spellblade Aluriel",
        1863 : "Star Augur Etraeus",
        1886 : "High Botanist Tel'arn",
        1842 : "Krosus",
        1862 : "Tichondrius",
        1872 : "Grand Magistrix Elisande",
        1866 : "Gul'dan"

    }
    return x[id]

async def get_wcl(character, server, region):
    url = r"https://www.warcraftlogs.com:443/v1/rankings/character/{}/{}/{}?api_key=a574df48a822ce7117aa29a901613025".format(character, server, region)
    async with aiohttp.get(url) as r:
        response = await r.json()
    
    parsedict = {}
    for fight in response:
        for value in fight:
            boss = fight["encounter"]
            boss = id_to_boss(boss)
            if fight["difficulty"] == 5:
                try:
                    parsedict[boss]["M"] = {"rank" : fight["rank"], "outOf" : fight["outOf"]}
                except:
                    parsedict[boss] = {}
                    parsedict[boss]["M"] = {"rank" : fight["rank"], "outOf" : fight["outOf"]}
            if fight["difficulty"] == 4:
                try:
                    parsedict[boss]["H"] = {"rank" : fight["rank"], "outOf" : fight["outOf"]}
                except:
                    parsedict[boss] = {}
                    parsedict[boss]["H"] = {"rank" : fight["rank"], "outOf" : fight["outOf"]}
            if fight["difficulty"] == 3:
                try:
                    parsedict[boss]["N"] = {"rank" : fight["rank"], "outOf" : fight["outOf"]}
                except:
                    parsedict[boss] = {}
                    parsedict[boss]["N"] = {"rank" : fight["rank"], "outOf" : fight["outOf"]}

    fancy_string = ""
    for boss in parsedict:
        fmt = "{}: {:.0f}% {}\n"
        for difficulty in parsedict[boss]:
            if parsedict[boss][difficulty]["rank"] == 1:
                percentile = 100.0
            else:
                percentile = math.floor(100 * (1 - (parsedict[boss][difficulty]["rank"]/parsedict[boss][difficulty]["outOf"])))
            if difficulty == "N":
                fancy_string += fmt.format(boss, percentile, difficulty)
                break
            elif difficulty == "H":
                fancy_string += fmt.format(boss, percentile, difficulty)
                break
            elif difficulty == "M":
                fancy_string += fmt.format(boss, percentile, difficulty)
                break
            else:
                fancy_string += "{}: N/A".format(difficulty)
                break
    return fancy_string
  
        

class Blizzard:

    def __init__(self, bot):
        self.bot = bot
        self.realms = load_json('realms.json')

    @commands.command()
    async def pickmyspec(self):
        await self.bot.say(random.choice(WOW_SPECS))

    @commands.command()
    async def pickmyclass(self):
        await self.bot.say(random.choice(WOW_CLASSES))

    @commands.command()
    async def pickmygold(self):
        await self.bot.say(random.choice(OW_Heroes))

    @commands.command(pass_context=True)
    async def wcl(self, ctx, character : str, server : str, region : str):
        await get_wcl(character, server, region)
    @commands.command(pass_context=True, aliases=['pug'])
    async def armory(self, ctx):
        leftover_args = ctx.message.content.split()
        leftover_args = leftover_args[1:]
        if len(leftover_args) >= 4:
            realm = "-".join(leftover_args[1:-1]).lower()
        else:
            realm = leftover_args[-2].lower()
        zone = leftover_args[-1].lower()
        if zone.lower() in ["na", "oce", "america", "br", "merica", "murica", "us"]:
            zone = "us"
        elif zone.lower() in ["europe", "uk", "eur", "euro", "de", "fr", "ru", "sp", "eu"]:
            zone = "eu"
        else:
            await self.bot.send_message(ctx.message.channel, 'Zone "{}" not recognized, please use eu or us.'.format(leftover_args[-1].replace("@", "@\u200b")))
            return
        locales = {"us":"en_US","eu":"en_GB","kr":"ko_KR","tw":"zh_TW"}
        locale = locales[zone]
        replaced = False
        if realm.lower() not in self.realms[zone] and zone in locales:
            realm2 = process.extractOne(realm.lower(), self.realms[zone])
            fmt = "{} was replaced by {}. ratio: {}%".format(realm, realm2[0], realm2[1])
            realm = realm2[0]
            replaced = True
        name = leftover_args[0].lower()
        url = "https://"+zone+".api.battle.net/wow/character/"+realm+"/"+name+"?fields=items&locale="+locale+"&apikey="+"ff5hn9c45m89csed7h2vbt97zkrcsyqf"
        async with aiohttp.get(url) as r:
            response = await r.json()
            if "status" in response:
                if response["status"] == 'nok':
                    await self.bot.say("Could not fetch character info, error: `{}`".format(response["reason"]))
                    if not ctx.message.channel.is_private:
                        await self.bot.delete_message(ctx.message)
                    return

        url = "https://"+zone+".api.battle.net/wow/character/"+realm+"/"+name+"?fields=progression&locale="+locale+"&apikey="+"ff5hn9c45m89csed7h2vbt97zkrcsyqf"
        async with aiohttp.get(url) as r:
            progressionresponse = await r.json()
        try:
            avatar_url = progressionresponse["thumbnail"]
            avatar_url = "https://render-api-eu.worldofwarcraft.com/static-render/"+zone+"/"+avatar_url
        except:
            avatar_url = None
        items = response["items"]
        artifact = response["items"]["mainHand"] if response["items"]["mainHand"]["artifactTraits"] != [] else response["items"]["offHand"]
        enchant_slots = ["finger1", "finger2", "back", "neck"]
        enchants = 0
        equipped_gems = 0
        total_gems = 0
        LEG_WITH_SOCKET = [
                            132369, 132410, 137044, 132444, 132449, 132452, 132460, 133973, 133974, 137037, 137038, 137039, 137040,
                            137041, 137042, 137043, 132378, 137045, 137046, 137047, 137048, 137049, 137050, 137051, 137052, 137054, 137055,
                            137220, 137223, 137276, 137382, 138854
                        ]
        for i in items:
            if i in enchant_slots:
                if "enchant" in items[i]["tooltipParams"]:
                    enchants += 1
            if i not in ['averageItemLevel', 'averageItemLevelEquipped']:
                if 1808 in items[i]["bonusLists"] or items[i]["id"] in LEG_WITH_SOCKET:
                    total_gems += 1
                    if "gem0" in items[i]["tooltipParams"]:
                        equipped_gems += 1
        
        traits = -3
        for i in artifact["artifactTraits"]:
            if i["rank"] != 0:
                traits += i["rank"]
        legendaries = {}
        ilvllist = []
        for i in items:
            if i in ['averageItemLevel', 'averageItemLevelEquipped']:   
                ilvllist.append(items[i])
                continue
            if items[i]["quality"] == 5:
                legendaries[i] = items[i]
        legendary_string = ""
        if legendaries != {}:
            for k, v in legendaries.items():
                print(k, v)
                legendary_string += "[{}](http://www.wowhead.com/item={})\n".format(v["name"], v["id"])
        else:
            legendary_string = "No legendaries"
        ilvl = "{0}/{1}".format(*ilvllist)
        emerald_nightmare = progressionresponse["progression"]["raids"][35]
        en_progress = {
            "N":0,
            "H":0,
            "M":0
        }
        for i in emerald_nightmare["bosses"]:
            if i["normalKills"] != 0:
                en_progress["N"] += 1
            if i["heroicKills"] != 0:
                en_progress["H"] += 1
            if i["mythicKills"] != 0:
                en_progress["M"] += 1
        trial_of_valor = progressionresponse["progression"]["raids"][36]
        tov_progress = {
            "N":0,
            "H":0,
            "M":0
        }
        for i in trial_of_valor["bosses"]:
            if i["normalKills"] != 0:
                tov_progress["N"] += 1
            if i["heroicKills"] != 0:
                tov_progress["H"] += 1
            if i["mythicKills"] != 0:
                tov_progress["M"] += 1

        nighthold = progressionresponse["progression"]["raids"][37]
        nh_progress = {
            "N":0,
            "H":0,
            "M":0
        }
        for i in nighthold["bosses"]:
            if i["normalKills"] != 0:
                nh_progress["N"] += 1
            if i["heroicKills"] != 0:
                nh_progress["H"] += 1
            if i["mythicKills"] != 0:
                nh_progress["M"] += 1

        tomb = progressionresponse["progression"]["raids"][38]
        tos_progress = {
            "N":0,
            "H":0,
            "M":0
        }
        for i in tomb["bosses"]:
            if i["normalKills"] != 0:
                tos_progress["N"] += 1
            if i["heroicKills"] != 0:
                tos_progress["H"] += 1
            if i["mythicKills"] != 0:
                tos_progress["M"] += 1

        url = "https://"+zone+".api.battle.net/wow/character/"+realm+"/"+name+"?fields=progression+achievements&locale="+locale+"&apikey="+"ff5hn9c45m89csed7h2vbt97zkrcsyqf"
        async with aiohttp.get(url) as r:
            rx = await r.json()
        wcl_url = "https://www.warcraftlogs.com/character/{}/{}/{}".format(zone, realm, name)
        armory_url = "https://worldofwarcraft.com/{}/character/{}/{}".format(locale, realm, name)
        mythicplus = get_mythic_progression(rx) or ""
        prog1 = "N: {}/7\nH: {}/7\nM: {}/7".format(en_progress["N"], en_progress["H"], en_progress["M"])
        prog2 = "N: {}/3\nH: {}/3\nM: {}/3".format(tov_progress["N"], tov_progress["H"], tov_progress["M"])
        prog3 = "N: {}/10\nH: {}/10\nM: {}/10".format(nh_progress["N"], nh_progress["H"], nh_progress["M"])
        prog4 = "N: {}/9\nH: {}/9\nM: {}/9".format(tos_progress["N"], tos_progress["H"], tos_progress["M"])
        print(legendary_string)
        print(ilvl, enchants, equipped_gems, total_gems, traits)
        print(prog1, prog2, prog3, prog4)
        print("+2   : {}\n+5   : {}\n+10 : {}\n+15 : {}".format(mythicplus["plus_two"], mythicplus["plus_five"], mythicplus["plus_ten"], mythicplus["plus_fifteen"]))
        #wcl = await get_wcl(name, realm, zone)
        e = discord.Embed(title="Pug info", description="[Warcraftlogs]({})\n[Armory]({})".format(wcl_url, armory_url), colour=0xffffff)
        e.set_thumbnail(url=avatar_url)
        e.add_field(name="Legendaries", value=legendary_string, inline=True)
        e.add_field(name="Gear", value="ilvl: {}\nEnchants: {}/4\nGems: {}/{}\nTraits: {}".format(ilvl, enchants, equipped_gems, total_gems, traits), inline=True)
        e.add_field(name="EN", value=prog1, inline=True)
        e.add_field(name="TOV", value=prog2, inline=True)
        e.add_field(name="NH", value=prog3, inline=True)
        e.add_field(name="TOS", value=prog4, inline=True)
        e.add_field(name="M+", value="+2   : {}\n+5   : {}\n+10 : {}\n+15 : {}".format(mythicplus["plus_two"], mythicplus["plus_five"], mythicplus["plus_ten"], mythicplus["plus_fifteen"]), inline=True)
        #e.add_field(name="wcl", value=wcl, inline=True)
        #e.add_field(name=, value="{}/4".format(enchants), inline=True)
        if replaced:            
            await self.bot.say(fmt, embed=e)
        else:
            await self.bot.say(embed=e)




    @commands.command(pass_context=True, aliases=['invasions'])
    async def invasion(self, ctx):
        eu_anchor = datetime.datetime(year=2017, month=5, day=26, hour=22, minute=30, second=0, microsecond=0)
        na_anchor = datetime.datetime(year=2017, month=5, day=26, hour=12, minute=0, second=0, microsecond=0)
        eu_seconds_since = datetime.datetime.utcnow() - eu_anchor
        eu_seconds_after_start = math.floor(eu_seconds_since.total_seconds() % 66600)
        na_seconds_since = datetime.datetime.utcnow() - na_anchor
        na_seconds_after_start = math.floor(na_seconds_since.total_seconds() % 66600)
        if eu_seconds_after_start < 21600: # invasion is active
            time_left = 21600 - eu_seconds_after_start
            dt = datetime.timedelta(seconds=time_left)
            printme = blizzard_time(dt)
            eufmt = "<:greentick:318044721807360010> There is an invasion going on. Time left: {}.".format(printme)
            if time_left < 1800:
                eufmt += " :hourglass_flowing_sand:"
        elif eu_seconds_after_start >= 21600:
            time_left = 66600 - eu_seconds_after_start
            dt = datetime.timedelta(seconds=time_left)
            printme = blizzard_time(dt)
            eufmt = "<:redtick:318044813444251649> There is no invasion going on right now, next one in {}.".format(printme)
            
        if na_seconds_after_start < 21600: # invasion is active
            time_left = 21600 - na_seconds_after_start
            dt = datetime.timedelta(seconds=time_left)
            naprintme = blizzard_time(dt)
            nafmt = "<:greentick:318044721807360010> There is an invasion going on. Time left: {}.".format(naprintme)
            if time_left < 1800:
                nafmt += " :hourglass_flowing_sand:"
        elif na_seconds_after_start >= 21600:
            time_left = 66600 - na_seconds_after_start
            dt = datetime.timedelta(seconds=time_left)
            naprintme = blizzard_time(dt)
            nafmt = "<:redtick:318044813444251649> There is no invasion going on right now, next one in {}.".format(naprintme)

        await self.bot.say("**EU: **{}\n**NA: **{}".format(eufmt, nafmt))

    @commands.command(pass_context=True, aliases=["m+", "affixes"])
    async def affix(self, ctx):
        nerd_epoch = datetime.datetime(year=2017, month=1, day=18, hour=7, minute=0, second=0, microsecond=0)
        EU_time = datetime.datetime.utcnow()
        NA_time = EU_time - datetime.timedelta(hours=-16)
        EU_indexthis = EU_time - nerd_epoch
        NA_indexthis = NA_time - nerd_epoch
        E = EU_indexthis.days // 7
        N = NA_indexthis.days // 7
        E = (E+2) % 12
        N = (N+2) % 12
        author = ctx.message.author
        usercolor = author.colour
        em = discord.Embed(title="Affix information", description="http://www.wowhead.com/affixes", colour=usercolor)
        em.set_author(name="Mythic+ affixes", icon_url="https://i.imgur.com/m7PjTW0.png", url="http://www.wowhead.com/affixes")
        if E != N:
            em.add_field(name="+4", value="**EU:** {}\n**NA:** {}".format(AFFIX1[E], AFFIX1[N]), inline=True)
            em.add_field(name="+7", value="{}\n{}".format(AFFIX2[E], AFFIX2[N]), inline=True)
            em.add_field(name="+10", value="{}\n{}".format(AFFIX3[E], AFFIX3[N]), inline=True)
        else:
            em.add_field(name="+4", value="**EU & NA:**\n{}".format(AFFIX1[E]), inline=True)
            em.add_field(name="+7", value="\u200b\n{}".format(AFFIX2[E]), inline=True)
            em.add_field(name="+10", value="\u200b\n{}".format(AFFIX3[E]), inline=True)
        E = (E + 1) % 12
        N = (N + 1) % 12
        if E != N:
            em.add_field(name="Next week", value="**EU:**\n{}\n{}\n{}\n\n**NA:**\n{}\n{}\n{}".format(AFFIX1[E], AFFIX2[E], AFFIX3[E], AFFIX1[N], AFFIX2[N], AFFIX3[N]), inline=True)
            E = (E + 1) % 12
            N = (N + 1) % 12
            em.add_field(name="In two weeks", value="**EU:**\n{}\n{}\n{}\n\n**NA:**\n{}\n{}\n{}".format(AFFIX1[E], AFFIX2[E], AFFIX3[E], AFFIX1[N], AFFIX2[N], AFFIX3[N]), inline=True)
            E = (E + 1) % 12
            N = (N + 1) % 12
            em.add_field(name="In three weeks", value="**EU:**\n{}\n{}\n{}\n\n**NA:**\n{}\n{}\n{}".format(AFFIX1[E], AFFIX2[E], AFFIX3[E], AFFIX1[N], AFFIX2[N], AFFIX3[N]), inline=True)
        else:
            em.add_field(name="Next week", value="**EU & NA:**\n{}\n{}\n{}\n\n".format(AFFIX1[E], AFFIX2[E], AFFIX3[E]), inline=True)
            E = (E + 1) % 12
            em.add_field(name="In two weeks", value="**EU & NA:**\n{}\n{}\n{}\n\n".format(AFFIX1[E], AFFIX2[E], AFFIX3[E]), inline=True)
            E = (E + 1) % 12
            em.add_field(name="In three weeks", value="**EU & NA:**\n{}\n{}\n{}\n\n".format(AFFIX1[E], AFFIX2[E], AFFIX3[E]), inline=True)
            
        
        await self.bot.send_message(ctx.message.channel, embed=em)

    @commands.command(pass_context=True)
    async def rtb(self, ctx):
        if ctx.message.channel.is_default:
            try:
                destination = discord.utils.find(lambda m: "bot" in m.name, ctx.message.server.channels)
                xd = await self.bot.send_message(destination, ctx.message.author.mention)
                await self.bot.delete_message(ctx.message)
            except:
                destination = ctx.message.channel
            
        else:
            destination = ctx.message.channel
        await self.bot.send_message(destination, roll_the_bones())


def setup(bot):
    bot.add_cog(Blizzard(bot))