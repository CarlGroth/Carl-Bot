import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding=sys.stdout.encoding, errors="backslashreplace", line_buffering=True)
import discord
import asyncio
import inspect
import math
import requests
import datetime
import re
import json
import aiohttp
import time
import statistics
import random
import markovify

from googleapiclient.discovery import build
from fuzzywuzzy import fuzz
from responses import *
from sensitivedata import *
from datetime import datetime, timedelta

client = discord.Client()


aliased_commands = {
    "info":"i",
    "temp":"weather",
    "temperature":"weather",
    "choice":"choose",
    "dice":"roll",
    "affixes":"affix",
    "m+":"affix",
    "8ball":"eightball",
    "pickmyhero":"pickmygold",
    "pick":"choose",
    "current_year":"date"
}


loaded_commands = [
    "ping",
    "bread",
    "say",
    "ban",
    "weather",
    "affix",
    "timer",
    "i",
    "postcount",
    "search",
    "nicknames",
    "ignorechannel",
    "roll",
    "poll",
    "mute",
    "unmute",
    "asdban",
    "bio",
    "spook",
    "speak",
    "tag",
    "forceban",
    "choose",
    "m",
    "avatar",
    "retard",
    "sicklad",
    "cts",
    "ae",
    "sc",
    "uptime",
    "pickmyspec",
    "pickmyclass",
    "pickmygold",
    "g",
    "d",
    "help",
    "date",
    "sc",
    "wl",
    "echo",
    "bl",
    "eightball"
]


CARL_DISCORD_ID = '106429844627169280'


def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    return res['items']

def load_json(filename):
    with open(filename, encoding='utf-8') as infile:
        return json.load(infile)

def write_json(filename, contents):
    with open(filename, 'w') as outfile:
        json.dump(contents, outfile, indent=2)

class CarlBot(discord.Client):
    def __init__(self):
        super().__init__()
        self.prefix = '!'
        self.taglist = load_json("taglist.json")
        self.token = token
        self.breadcount = load_json("bread.json")
        self.postcountdata = load_json("postcount.json")
        self.userinfo = load_json('users.json')
        self.biodata = load_json('bio.json')
        self.retardcoins = load_json('retard.json')
        self.sickladcoins = load_json('sicklad.json')
        self.whitelist = load_json('whitelist.json')
        self.blacklist = load_json('blacklist.json')
        self.home = load_json('weather.json')
        self.aiosession = aiohttp.ClientSession(loop=self.loop)
        self.ignore = load_json('ignore.json')
        self.starttime = time.time() + 7200


    def fix_postcount(self, author):
        try:
            self.postcountdata[author.id] += 1
            write_json('postcount.json', self.postcountdata)
        except KeyError:
            self.postcountdata[author.id] = 1
            write_json('postcount.json', self.postcountdata)
        except IndexError:
            self.postcountdata[author.id] = 1
            write_json('postcount.json', self.postcountdata)
    def log(self, message):
        with open("logs/{}.txt".format(message.author.id), "a", encoding="utf-8") as f:
            f.write("{}\n".format(message.clean_content))
    # maybe one day
    # async def add_bio(message):
    #     bio_add = ""
    #     if message.attachments:
    #         bio_add += f"{message.attachments[0]['url']} "
    #     bio_add += message.content[7:]
    #     self.biodata[message.author.id] = bio_add
    #     write_json('bio.json', self.biodata)
    #     if message.author.id in self.biodata:
    #         await self.send_message(message.channel, "Bio succesfully replaced")
    #     else:
    #         await self.send_message(message.channel, "Bio succesfully added")



    async def userfix(self, member):
        if member.id not in self.userinfo:
            self.userinfo[member.id] = {"names": [member.name],
                                        "roles": [x.name for x in member.roles if x.name != "@everyone"]}
        write_json('users.json', self.userinfo)
    async def on_member_ban(self, member):
        general_channel = discord.utils.get(member.server.channels, name="general")
        await self.send_message(general_channel, f"**{member.name}#{member.discriminator}** was just banned from the server.")
    async def on_member_unban(self, server, user):
        general_channel = discord.utils.get(server.channels, name="general")
        await self.send_message(general_channel, f"**{user.name}#{user.discriminator}** was just unbanned from the server.")
    async def on_member_update(self, before, after,):
        log_channel = discord.utils.get(before.server.channels, name='log')
        if before.display_name != after.display_name:
            await self.send_message(log_channel, ":spy: **{0}#{1}** changed their nickname:\n**Before:** {2}\n**+After:** {3}".format(before.name, before.discriminator, before.display_name, after.display_name))
            await self.userfix(before)
            if after.display_name not in self.userinfo[before.id]["names"]:
                self.userinfo[before.id]["names"].append(after.display_name)
            else:
                #duplicate nicknames are lame
                old_index = self.userinfo[before.id]["names"].index(after.display_name)
                self.userinfo[before.id]["names"].pop(old_index)
                self.userinfo[before.id]["names"].append(after.display_name)
            write_json('users.json', self.userinfo)
        elif before.roles != after.roles:
            await self.userfix(before)
            self.userinfo[before.id]["roles"] = [x.name for x in after.roles if x.name != "@everyone"]
            write_json('users.json', self.userinfo)
            if len(before.roles) < len(after.roles):
                #role added
                s = set(before.roles)
                newrole = [x for x in after.roles if x not in s]
                await self.send_message(log_channel, ":warning: **{}** had the role **{}** added.".format(before.display_name, newrole[0].name))
            else:
                s = set(after.roles)
                newrole = [x for x in before.roles if x not in s]
                await self.send_message(log_channel, ":warning: **{}** had the role **{}** removed.".format(before.display_name, newrole[0].name))

    async def on_member_join(self, member):
        log_channel = discord.utils.get(member.server.channels, name='log')
        await self.send_message(log_channel, ":white_check_mark: **{0.name}#{0.discriminator}** *({0.id})* Joined the server at `{1}`<@{2}> <@{3}> :white_check_mark:".format(member, time.strftime("%Y-%m-%d %H:%M:%S (central carl time)."), CARL_DISCORD_ID, "158370770068701184"))
        if member.id not in self.userinfo:
            await self.userfix(member)
        else:
            allRoles = member.server.roles
            checkthis = self.userinfo[member.id]["roles"]
            rolestobeadded = [x for x in allRoles if x.name in checkthis]
            await self.add_roles(member, *rolestobeadded)
            await asyncio.sleep(1)
            await self.change_nickname(member, self.userinfo[member.id]["names"][-1])

    async def on_member_remove(self, member):
        log_channel = discord.utils.get(member.server.channels, name='log')
        fmt = ":wave: **{0}#{1}** *({2})* left the server at `{3}`<@{4}> <@{5}> :wave:"
        await self.send_message(log_channel, fmt.format(member.name, member.discriminator, member.id, time.strftime("%Y-%m-%d %H:%M:%S (central carl time)."), CARL_DISCORD_ID, "158370770068701184"))
    async def on_message_delete(self, message):
        if message.channel.id == "267085455047000065":
            return
        if message.channel.is_private:
            return
        if message.author.id == self.user.id:
            return
        if message.clean_content.startswith(self.prefix):
            return
        if message.clean_content.startswith('$'):
            return
        if message.author.id == "106429844627169280":
            if message.content.startswith("++"):
                return
        destination = discord.utils.get(message.server.channels, name='log')
        poststring = ":x: `{1}` **{0}** Deleted their message:  ```{2}``` in `{3}`".format(message.author.display_name, time.strftime("%H:%M:%S"), message.clean_content, message.channel)
        if message.attachments:
            poststring += "\n{}".format(message.attachments[0]['url'])

        await self.send_message(destination, poststring)

    async def on_message_edit(self, before, after):
        log_channel = discord.utils.get(before.server.channels, name='log')
        if before.channel.id == "267085455047000065":
            return
        if before.channel.is_private:
            return
        if before.clean_content == after.clean_content:
            return
        if before.author.id in [self.user.id, "283540074837049354"]:
            return
        if before.clean_content.startswith('$'):
            return
        if before.author.id == "106429844627169280":
            if before.content.startswith("++"):
                return
        fmt = ":pencil2: `{}` **{}** edited their message:\n**Before:** {}\n**+After:** {}"
        await self.send_message(log_channel, fmt.format(time.strftime("%H:%M:%S"), before.author.name, before.clean_content, after.clean_content))


    async def on_ready(self):
        print('connected!\n')
        print('Username: ' + self.user.name)
        print('ID: ' + self.user.id)
        print('--Server List--')
        for server in self.servers:
            print(server.name)
        member_list = self.get_all_members()
        for member in member_list:
            if member.id not in self.userinfo:
                self.userinfo[member.id] = {"names": [member.name],
                                            "roles": [x.name for x in member.roles if x.name != "@everyone"]}
            elif member.name not in self.userinfo[member.id]["names"]:
                self.userinfo[member.id]["names"].append(member.name)
        write_json('users.json', self.userinfo)

    async def cmd_ping(self, channel, message):
        msg = await self.send_message(channel, "pong!")
        q_time = message.timestamp
        m_time = msg.timestamp
        diff_time = m_time - q_time
        d_time = diff_time.microseconds / 1000
        await self.edit_message(msg, "pong! {}ms".format(int(d_time)))
    async def cmd_eightball(self, channel, author):
        response = random.choice(responses)
        await self.send_message(channel, f":8ball: | {response}, **{author.display_name}**")
    async def cmd_bl(self, mentions, author, leftover_args):
        if author.id != CARL_DISCORD_ID:
            return
        if not mentions:
            return
        BLACKED = []
        if leftover_args[0] in ['+', 'add']:
            fmt = "Blacklisted **{}.**"
            for usr in mentions:
                self.blacklist[usr.id] = usr.name
                BLACKED.append(usr.display_name)
            BLACKED = ', '.join(BLACKED)
            write_json('blacklist.json', self.blacklist)
        elif leftover_args[0] in ['-', 'del']:
            fmt = "Removed **{}** from the blacklist."
            for usr in mentions:
                if usr.id in self.blacklist:
                    del self.blacklist[usr.id]
                    BLACKED.append(usr.display_name)
            BLACKED = ', '.join(BLACKED)
            write_json('blacklist.json', self.blacklist)
        await self.send_message(discord.Object(id='249336368067510272'), fmt.format(BLACKED))

    async def cmd_wl(self, mentions, author, leftover_args):
        if author.id != CARL_DISCORD_ID:
            return
        if not mentions:
            return
        whitelisted = []
        if leftover_args[0] in ['+', 'add']:
            fmt = "Whitelisted **{}.**"
            for usr in mentions:
                self.whitelist[usr.id] = usr.name
                whitelisted.append(usr.display_name)
            whitelisted = ', '.join(whitelisted)
            write_json('whitelist.json', self.whitelist)
        elif leftover_args[0] in ['-', 'del']:
            fmt = "Removed **{}** from the whitelist."
            for usr in mentions:
                if usr.id in self.whitelist:
                    del self.whitelist[usr.id]
                    whitelisted.append(usr.display_name)
            whitelisted = ', '.join(whitelisted)
            write_json('whitelist.json', self.whitelist)
        else:
            return
        await self.send_message(discord.Object(id='249336368067510272'), fmt.format(whitelisted))

    async def cmd_date(self, channel):
        await self.send_message(channel, "It's {0}".format(time.strftime("%Y-%m-%d\n%H:%M:%S (central carl time).")))
    async def cmd_help(self, author, channel, leftover_args):
        if len(leftover_args) == 0:
            user = author
            em_before = discord.Embed(title="Help", description="Processing command...", colour=0x42f4dc)
            em_before.set_author(name=user.name, icon_url=user.avatar_url)
            em_after = discord.Embed(title="Success", description="Check your direct messages.", colour=0x14e818)
            em_after.set_author(name=user.name, icon_url=user.avatar_url)
            help_embed = await self.send_message(channel, embed=em_before)
            await asyncio.sleep(0.1)
            await self.send_message(author, "Check out the commands on github: https://github.com/CarlGroth/Carl-Bot#carl-bot\nOr PM Carl if you have any unanswered questions")
            await self.edit_message(help_embed, embed=em_after)
        else:
            return
    async def cmd_d(self, author, channel, message):
        language = 'en'
        definitions = {}
        try:
            url = 'https://od-api.oxforddictionaries.com/api/v1/entries/' + language + '/' + message.content[3:].lower()
            r = requests.get(url, headers = {'app_id': app_id, 'app_key': app_key})
            jsonthing = r.json()
            wordname = message.content[3:].capitalize()
            pronounciation = jsonthing["results"][0]["lexicalEntries"][0]["pronunciations"][0]["phoneticSpelling"]
            user = author
            usercolor = user.color
            em = discord.Embed(title=wordname, description="/{}/".format(pronounciation), colour=usercolor)
            em.set_author(name=user.display_name, icon_url=user.avatar_url, url=user.avatar_url)
            x = jsonthing["results"][0]["lexicalEntries"]

            f = 0
            for i in x:
                word_type = jsonthing["results"][0]["lexicalEntries"][f]["lexicalCategory"]
                try:

                    d = jsonthing["results"][0]["lexicalEntries"][f]["entries"][0]["senses"][0]["definitions"]
                    d = ''.join(d)
                    definition = "{}\n".format( ''.join(i["entries"][0]["senses"][0]["definitions"]))
                    try:
                        definitions[word_type] += definition
                    except KeyError:
                        definitions[word_type] = definition
                    f += 1
                except IndexError:
                    pass
        except Exception as e:
            await self.send_message(message.channel, "No definition found, blame Oxford Dictionaries")
            return
        for box in definitions:
            em.add_field(name=box, value=definitions[box].capitalize(), inline=False)
        await self.send_message(message.channel, embed=em)
    async def cmd_g(self, author, channel, message):
        if author.id in self.blacklist:
            return
        user = author
        usercolor = user.color
        em = discord.Embed(title="Google search", description="", colour=usercolor)
        em.set_author(name=user.display_name, icon_url=user.avatar_url, url=user.avatar_url)
        postme = ''
        results = google_search(str(message.content[3:]), my_api_key, my_cse_id, num=4)
        url = results[0]['link']
        snippet = results[0]['snippet']
        em.add_field(name=url, value=snippet, inline=True)
        for i in range(1, 4):
            url = results[i]['link']
            postme += "{}\n".format(url)
        em.add_field(name="See also", value=postme, inline=True)
        await self.send_message(channel, embed=em)
    async def cmd_pickmyspec(self, channel):
        await self.send_message(channel, random.choice(WOW_SPECS))
    async def cmd_pickmyclass(self, channel):
        await self.send_message(channel, random.choice(WOW_CLASSES))
    async def cmd_uptime(self, channel):
        uptime = str(timedelta(seconds=((time.time() + 7200) - self.starttime)))
        uptime = re.sub("\.(.*)", "", uptime)
        currtime = time.strftime("%H:%M:%S", time.gmtime(time.time() + 7200))
        started_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(self.starttime))
        em = discord.Embed(title="Local time", description=currtime, colour=0x14e818)
        em.set_author(name=self.user.name, icon_url=self.user.avatar_url)
        em.add_field(name="Current uptime", value=uptime, inline=True)
        em.add_field(name="Start time", value=started_time, inline=True)
        await self.send_message(channel, embed=em)
    async def cmd_sc(self, message, channel):
        smallcaps_string = smallcaps(message.clean_content[4:])
        await self.send_message(message.channel, smallcaps_string)
    async def cmd_ae(self, message, channel):
        hehe = aesthetics(message.clean_content[4:])
        await self.send_message(channel, hehe)
    async def cmd_cts(self, leftover_args, channel):
        stream = " {1}\u3000{0}\n   {1}{0}\n\u3000 {0}\n   {0}{1}\n {0}\u3000{1}\n{0}\u3000\u3000{1}\n{0}\u3000\u3000{1}\n {0}\u3000{1}\n  {0} {1}\n\u3000  {1}\n\u3000{1} {0}\n {1}\u3000 {0}\n{1}\u3000\u3000{0}\n{1}   \u3000 {0}\n {1}\u3000  {0}\n\u3000{1}{0}\n     {0}{1}\n  {0}    {1}"
        if len(leftover_args) == 0:
            whale = "<:Whale:239954158772289537>"
            cookie = ":cookie:"
        elif len(leftover_args) == 1:
            whale = "<:Whale:239954158772289537>"
            cookie = str(leftover_args[0])
        elif len(leftover_args) == 2:
            whale = str(leftover_args[0])
            cookie = str(leftover_args[1])
        else:
            return
        await self.send_message(channel, stream.format(whale, cookie))
    async def cmd_sicklad(self, message, leftover_args, channel, author, mentions):
        if len(leftover_args) == 0:
            await self.send_message(channel, "You sure are.")
        elif leftover_args[0].lower() in ['leaderboard', 'leaderboards', 'top', 'highscore', 'highscores', 'hiscores']:
            ladboard = self.sickladcoins
            post_this = "**Current standings:**\n"
            rank = 1
            for w in sorted(ladboard, key=ladboard.get, reverse=True):
                if rank < 11:
                    try:
                        post_this += ("{0}. **{1}** = {2}\n".format(rank, self.get_server('207943928018632705').get_member(w).name, ladboard[w]))
                        rank += 1
                    except AttributeError:
                        continue
                else:
                    continue
            #this fucking sucks
            post_this += "**{0}** !sicklads in total spread across **{1}** sick lads.".format(sum(self.sickladcoins.values()),len(self.sickladcoins))
            await self.send_message(channel, post_this)
        if mentions[0].id == author.id:
            await self.send_message(channel, "You can't call yourself a sick lad, what the h*ck")
            return
        try:
            userID = mentions[0].id
            if not mentions:
                return
            elif userID not in self.sickladcoins:
                self.sickladcoins[userID] = 1
                write_json('sicklad.json', self.sickladcoins)
                await self.send_message(channel, "Welcome to the sicklad club, {0}".format(mentions[0].display_name))
            else:
                if len(leftover_args) == 1:
                    self.sickladcoins[userID] += 1
                    write_json('sicklad.json', self.sickladcoins)
                    await self.send_message(channel, "{0} thinks {1} is a sick lad, {1} is now a lvl {2} sicklad.".format(author.name.replace("_", "\_"), mentions[0].name.replace("_", "\_"), self.sickladcoins[userID]))
                else:
                    reason = ' '.join(leftover_args[1:])
                    self.sickladcoins[userID] += 1
                    write_json('sicklad.json', self.sickladcoins)
                    await self.send_message(channel, "{0} thinks {1} is a sick lad, reason: `{2}`\n{1} is now a lvl {3} sicklad.".format(author.name.replace("_", "\_"), mentions[0].name.replace("_", "\_"), reason, self.sickladcoins[userID]))
        except IndexError:
            return
        except UnboundLocalError:
            return
        except discord.HTTPException:
            return
    async def cmd_retard(self, message, leftover_args, channel, mentions):
        if len(leftover_args) == 0:
            await self.send_message(channel, "You sure are.")
        elif leftover_args[0].lower() in ['leaderboard', 'leaderboards', 'top', 'highscore', 'highscores', 'hiscores']:
            leaderboard = self.retardcoins
            post_this = "**Current standings:**\n"
            rank = 1
            for w in sorted(leaderboard, key=leaderboard.get, reverse=True):
                if rank < 11:
                    try:
                        post_this += ("{0}. **{1}** = {2}\n".format(rank, self.get_server('207943928018632705').get_member(w).name, leaderboard[w]))
                        rank += 1
                    except AttributeError:
                        continue
                else:
                    continue
            post_this += "**{0}** coins in total spread across **{1}** retards.".format(sum(self.retardcoins.values()),len(self.retardcoins))
            await self.send_message(channel, post_this)
        try:
            userID = mentions[0].id
            if userID == '':
                return
            elif userID not in self.retardcoins:
                self.retardcoins[userID] = 1
                write_json('retard.json', self.retardcoins)
                await self.send_message(channel, "Welcome to the retard club, **{0}**".format(mentions[0].display_name))
            else:
                if len(leftover_args) == 1:
                    self.retardcoins[userID] += 1
                    write_json('retard.json', self.retardcoins)
                    await self.send_message(message.channel, "**{0}** just tipped **{1} 1** retard coin, **{1}** now has **{2}** coins.".format(message.author.name.replace("_", "\_"), message.mentions[0].name.replace("_", "\_"), self.retardcoins[userID]))
                else:
                    reason = ' '.join(leftover_args[1:])
                    self.retardcoins[userID] += 1
                    write_json('retard.json', self.retardcoins)
                    await self.send_message(message.channel, "**{0}** just tipped **{1} 1** retard coin, reason: `{2}`\n**{1}** now has **{3}** coins.".format(message.author.name.replace("_", "\_"), message.mentions[0].name.replace("_", "\_"), reason, self.retardcoins[userID]))
        except:
            return
    async def cmd_avatar(self, message):
        if message.author.id != CARL_DISCORD_ID:
            return
        if message.attachments:
            avatar = message.attachments[0]['url']
        else:
            avatar = leftover_args[0].strip('<>')
        try:
            with aiohttp.Timeout(10):
                async with self.aiosession.get(avatar) as res:
                    await self.edit_profile(avatar=await res.read())
        except Exception as e:
            print(e)
    async def cmd_m(self, message, channel):
        if message.author.id == CARL_DISCORD_ID:
            await self.send_message(channel, "{}".format(eval(message.content[3:])))
    async def cmd_choose(self, channel, leftover_args):
        if len(leftover_args) == 0:
            return
        choices = leftover_args
        choices = ' '.join(choices)
        choices = choices.split(",")
        await self.send_message(channel, random.choice(choices))

    async def cmd_forceban(self, author, server, leftover_args):
        if author.id != CARL_DISCORD_ID:
            return
        for i in range(len(leftover_args)):
            await self.http.ban(leftover_args[i], server.id, 0)
    async def cmd_tag(self, channel, author, leftover_args, message):
        if message.mentions:
            return
        tagreturn = ' '.join(leftover_args[2:])
        taglist = self.taglist
        if leftover_args[0] == 'list':
            d = sorted(list(self.taglist.keys()))
            if sum(len(t) for t in d) < 1900:
                d = ', '.join(d)
                await self.send_message(author, d)
            else:
                tempmessage = []
                finalmessage = []
                #discord has a 2000 character word limit so we need to split it into multiple messages
                #this is a for loop that will build each message and temporarily store it
                #appends the temporary message to a list consisting of lists
                for tag in d:
                    if len(', '.join(tempmessage)) < 1800:
                        tempmessage.append(tag)
                    else:
                        formatted_tempmessage = ', '.join(tempmessage)
                        finalmessage.append(formatted_tempmessage)
                        tempmessage = []
                finalmessage.append(', '.join(tempmessage))
                for x in finalmessage:
                    if x != "":
                        await self.send_message(author, x)
        #with over 300 tags, taglist isn't always of help
        elif leftover_args[0] == "search":
            if len(leftover_args) < 2:
                return
            #since tags have to follow these rules, it would be pointless not to have your search
            #query follow it too
            query = re.sub("[^a-z0-9_-]", "", leftover_args[1].lower())
            tagreturn = ""
            #I only use this variable because it allows me to match the index of the tag with the tag itself
            #is it really stupid if it works? (yes)
            bad_coding_practice_variable = ""
            i = 1
            #this for loop simply returns us all the tags that are similar enough to our search term
            #it also does the formatting. I'm not sure why.
            for tag in sorted(taglist, reverse=False):
                if fuzz.partial_ratio(query, tag) > 80:
                    tagreturn += "{}. {}\n".format(i, tag)
                    bad_coding_practice_variable += "{}\n".format(tag)
                    i += 1
                else:
                    continue

            list_of_returns = tagreturn.splitlines()
            tempmessage = ""
            final_list = []
            xd = 0
            #similar to bio and taglist
            for line in list_of_returns:
                if xd < 14:
                    tempmessage += "{}\n".format(line)
                    xd += 1
                else:
                    tempmessage += "{}\n".format(line)
                    final_list.append(tempmessage)
                    tempmessage = ""
                    xd = 0
            final_list.append(tempmessage)

            if len(tagreturn) == 0:
                await self.send_message(channel, "Sorry, couldn't find any matching tags.")
            else:
                em = discord.Embed(title="Search results:", description=final_list[0], colour=0xffffff)
                em.set_author(name=author.name, icon_url=author.avatar_url, url=author.avatar_url)
                em.set_footer(text="{} results. (page {}/{})".format(i-1, 1, math.ceil((i-1)/15)))
                initial_message = await self.send_message(channel, embed=em)
                def check(mesg):
                    if mesg.content.isdigit():
                        return True
                    elif mesg.content.startswith("p"):
                        return True

                for p in range(5):
                    msg = await self.wait_for_message(author=author, timeout=15)
                    #if the message is a number, match it with the associated tag
                    if msg.content.isdigit():
                        listoflines = bad_coding_practice_variable.split('\n')
                        await self.send_message(message.channel, self.taglist[listoflines[int(msg.content)-1]])
                        return
                    #this is for pages
                    elif msg.content.startswith("p"):
                        try:
                            page_number = int(msg.content[1:])
                            em2 = discord.Embed(title="Search results:", description=final_list[page_number-1], colour=0xffffff)
                            em2.set_author(name=author.name, icon_url=author.avatar_url, url=author.avatar_url)
                            em2.set_footer(text="{} results. (page {}/{})".format(i-1, page_number, math.ceil((i-1)/15)))
                            await self.edit_message(initial_message, embed=em2)
                        except Exception as e:
                            print(e)
                            return
        elif leftover_args[0] == "+=":
            tagname = re.sub("[^a-z0-9_-]", "", leftover_args[1].lower())
            content = message.content[(9+len(leftover_args[1])):]
            if len(leftover_args) <= 2:
                await self.send_message(channel, "<:FailFish:235926308071276555>")
                return
            if (len(content) + len(self.taglist[tagname])) < 2000:
                try:
                    self.taglist[tagname] += "\n{}".format(content)
                except KeyError:
                    self.taglist[tagname] = content
                write_json('taglist.json', self.taglist)
                await self.send_message(channel, "`{}` was appended to the tag: {}".format(content, tagname))
            else:
                await self.send_message(channel, "that would make the tag too big, retard.")
        elif leftover_args[0] == '+':
            tagname = re.sub("[^a-z0-9_-]", "", leftover_args[1].lower())
            if len(leftover_args) <= 2:
                await self.send_message(channel, "<:FailFish:235926308071276555>")
                return
            if leftover_args[1] == 'list':
                await self.send_message(channel, "Nice try, motherfucker.")
                return
            if tagname in taglist:
                def check(mesg):
                    if mesg.content in ['r', 'y', 'yes', 'replace', 'c', 'n', 'no', 'cancel', 'a']:
                        return True
                await self.send_message(channel, "Tag already exists. **__r__**eplace, **__c__**ancel or **__a__**dd to? (r/c/a)")
                msg = await self.wait_for_message(author=author, check=check)
                #I added a bunch of aliases in case you savages can't follow instructions
                if msg.content.lower() in ['r', 'y', 'yes', 'replace']:
                    tagname = re.sub("[^a-z0-9_-]", "", leftover_args[1].lower())
                    self.taglist[tagname] = message.content[(7+len(leftover_args[1])):]
                    write_json('taglist.json', self.taglist)
                    await self.send_message(channel, "Tag succesfully replaced.")
                elif msg.content.lower() in ['c', 'n', 'no', 'cancel']:
                    await self.send_message(channel, "Tag not replaced.")
                elif msg.content.lower() == 'a':
                    tagname = re.sub("[^a-z0-9_-]", "", leftover_args[1].lower())
                    content = message.content[(8+len(leftover_args[1])):]
                    if (len(content) + len(self.taglist[tagname])) < 2000:
                        try:
                            self.taglist[tagname] += "\n{}".format(content)
                        except KeyError:
                            self.taglist[tagname] = "{}".format(content)
                        write_json('taglist.json', self.taglist)
                        await self.send_message(message.channel, "`{}` was appended to the tag: {}".format(content, tagname))
                else:
                    return
            elif (len(message.content) < 1750) and (len(tagname) < 50):
                tagname = re.sub("[^a-z0-9_-]", "", leftover_args[1].lower())
                if tagname == '':
                    return
                self.taglist[tagname] = message.content[(7+len(leftover_args[1])):]
                write_json('taglist.json', self.taglist)
                await self.send_message(message.channel, "tag `{0}` added".format(tagname))

            else:
                await self.send_message(message.channel, "too long <:gachiGASM:234404899511599104>")
        elif leftover_args[0] in ['-', 'del']:
            tagname = leftover_args[1]
            if tagname in taglist:
                del taglist[tagname]
                write_json('taglist.json', self.taglist)
                await self.send_message(channel, "tag `{0}` deleted".format(tagname))
            else:
                await self.send_message(channel, "tag `{0}` not found".format(tagname))
        else:
            tagname = leftover_args[0].lower()
            if tagname in self.taglist:
                await self.send_message(channel, self.taglist[tagname])
            else:
                await self.send_message(channel, "No such tag")
    async def cmd_echo(self, leftover_args, message):
        destination = message.channel_mentions[0]
        await self.send_message(destination, ' '.join(leftover_args[1:]))
    async def cmd_search(self, channel, author, leftover_args, message):
        taglist = self.taglist
        if len(leftover_args) < 1:
            return
        query = re.sub("[^a-z0-9_-]", "", leftover_args[0].lower())
        tagreturn = ""
        bad_coding_practice_variable = ""
        i = 1
        for tag in sorted(taglist, reverse=False):
            if fuzz.partial_ratio(query, tag) > 80:
                tagreturn += "{}. {}\n".format(i, tag)
                bad_coding_practice_variable += "{}\n".format(tag)
                i += 1
            else:
                continue
        list_of_returns = tagreturn.splitlines()
        tempmessage = ""
        final_list = []
        xd = 0
        for line in list_of_returns:
            if xd < 14:
                tempmessage += "{}\n".format(line)
                xd += 1
            else:
                tempmessage += "{}\n".format(line)
                final_list.append(tempmessage)
                tempmessage = ""
                xd = 0
        final_list.append(tempmessage)

        if len(tagreturn) == 0:
            await self.send_message(channel, "Sorry, couldn't find any matching tags.")
        else:
            em = discord.Embed(title="Search results:", description=final_list[0], colour=0xffffff)
            em.set_author(name=author.name, icon_url=author.avatar_url, url=author.avatar_url)
            em.set_footer(text="{} results. (page {}/{})".format(i-1, 1, math.ceil((i-1)/15)))
            initial_message = await self.send_message(channel, embed=em)
            def check(mesg):
                if mesg.content.isdigit():
                    return True
                elif mesg.content.startswith("p"):
                    return True

            for p in range(5):
                msg = await self.wait_for_message(author=author, timeout=15)
                #if the message is a number, match it with the associated tag
                if msg.content.isdigit():
                    listoflines = bad_coding_practice_variable.split('\n')
                    await self.send_message(message.channel, self.taglist[listoflines[int(msg.content)-1]])
                    return
                #this is for pages
                elif msg.content.startswith("p"):
                    try:
                        page_number = int(msg.content[1:])
                        em2 = discord.Embed(title="Search results:", description=final_list[page_number-1], colour=0xffffff)
                        em2.set_author(name=author.name, icon_url=author.avatar_url, url=author.avatar_url)
                        em2.set_footer(text="{} results. (page {}/{})".format(i-1, page_number, math.ceil((i-1)/15)))
                        await self.edit_message(initial_message, embed=em2)
                    except Exception as e:
                        print(e)
                        return
    async def cmd_speak(self, mentions, leftover_args, message, author, channel):
        repeats = 3
        if not mentions and len(leftover_args) == 0:
            victim = author.id
        elif not mentions and len(leftover_args) == 1:
            victim = author.id
            try:
                id_or_repeats = int(leftover_args[0])
                if id_or_repeats > 20:
                    repeats = 20
                    if id_or_repeats > 100000:
                        victim = id_or_repeats   
                else:
                    repeats = id_or_repeats
                    victim = author.id
            except:
                return
        elif mentions:
            victim = mentions[0].id
        else:
            return
        try:
            with open("logs/{}.txt".format(victim), encoding="utf-8") as f:
                text = f.read()
            text_model = markovify.NewlineText(text)
            speech = "**{}:**\n".format(author.name)
        except:
            await self.send_message(channel, f"No file matching {id_or_repeats}")
        for i in range(repeats):
            try:
                variablename = text_model.make_short_sentence(140, state_size=3).replace("@", "@ ")
                #print(variablename)
                try:
                    id_mention = re.search("<@ [!]?(.*)>", variablename)
                    id_mention = id_mention.group(1)
                    id_name = self.get_server("207943928018632705").get_member(str(id_mention)).name
                    add_this = re.sub("<@ [!]?.*>", id_name, variablename)
                    speech += "{}\n\n".format(add_this)
                except AttributeError:
                    speech += "{}\n\n".format(variablename)
            except KeyError:
                return
            except AttributeError:
                pass
        await self.send_message(channel, speech)
    async def cmd_spook(self, mentions, channel):
        if mentions:
            await self.send_message(channel, "you have been spooked, **{}** ! o no :skull_crossbones:".format(mentions[0].display_name))
        else:
            await self.send_message(channel, "boo!")
    async def cmd_bio(self, message, leftover_args):
        premium_member = False
        bio_appendage = ""
        if message.mentions:
            user = message.mentions[0]
        else:
            user = message.author
        if user.id in self.whitelist:
            premium_member = True
        if len(leftover_args) == 1 and not message.mentions and not message.attachments:
            await self.send_message(message.channel, "Empty bio <:FailFish:235926308071276555>")
            return
        elif message.attachments:
            bio_appendage += f"{message.attachments[0]['url']} "
        if leftover_args and not message.mentions:
            if leftover_args[0] == '+':
                bio_appendage += message.clean_content[7:]
                if message.author.id in self.biodata:
                    def check(mesg):
                        return True
                    await self.send_message(message.channel, "Bio already exists. **__r__**eplace, **__c__**ancel or **__a__**dd to? (r/c/a)")
                    msg = await self.wait_for_message(author=message.author, check=check)
                    if msg.content.lower() in ['r', 'y', 'yes', 'replace']:
                        self.biodata[message.author.id] = bio_appendage
                        write_json('bio.json', self.biodata)
                        await self.send_message(message.channel, "Bio succesfully replaced.")
                    elif msg.content.lower() in ['c', 'n', 'no', 'cancel']:
                        await self.send_message(message.channel, "Bio unchanged.")
                    elif msg.content.lower() == 'a':
                        if premium_member:
                            self.biodata[message.author.id] += "\n{}".format(bio_appendage)
                            write_json('bio.json', self.biodata)
                            await self.send_message(message.channel, "`{0}` was appended to {1.name}'s bio.".format(message.clean_content[7:], message.author))
                        elif not premium_member and (len(message.clean_content[7:]) + len(self.biodata[message.author.id])) < 2000:
                            self.biodata[message.author.id] += "\n{}".format(bio_appendage)
                            write_json('bio.json', self.biodata)
                            await self.send_message(message.channel, "`{0}` was appended to {1.name}'s bio.".format(message.clean_content[7:], message.author))
                        else:
                            return
                        
                    else:
                        return
                        
                else:
                    if len(message.content) < 1750 or premium_member:
                        self.biodata[message.author.id] = bio_appendage
                        write_json('bio.json', self.biodata)
                        await self.send_message(message.channel, "**{}'s** bio was added".format(message.author))
            elif leftover_args[0] == "+=":
                bio_appendage = message.clean_content[8:]
                if message.author.id not in self.whitelist:
                    if (len(bio_appendage) + len(self.biodata[message.author.id])) < 2000:
                        try:
                            self.biodata[message.author.id] += "\n{}".format(bio_appendage)
                        except KeyError:
                            self.biodata[message.author.id] = "{}".format(bio_appendage)
                        write_json('bio.json', self.biodata)
                        await self.send_message(message.channel, "`{0}` was appended to {1.name}'s bio.".format(bio_appendage, message.author))
                    else:
                        await self.send_message(message.channel, "Too long")
                else:
                    if len(leftover_args) == 1 and not message.attachments:
                        await self.send_message(message.channel, "retard <:FailFish:235926308071276555>")
                    try:
                        self.biodata[message.author.id] += "\n{}".format(bio_appendage)
                    except KeyError:
                        self.biodata[message.author.id] = "{}".format(bio_appendage)
                    write_json('bio.json', self.biodata)
                    await self.send_message(message.channel, "`{0}` was appended to {1.name}'s bio.".format(bio_appendage, message.author))
        else:
            bioname = user.id
            if bioname in self.biodata:
                if len(self.biodata[bioname]) < 1750:
                    print("hey, what the fuck")
                    await self.send_message(message.channel, "Bio for {0}:\n{1}".format(user.display_name, self.biodata[bioname]))
                else:
                    #Blame kinny T for this abomination
                    listOfLines = self.biodata[bioname]
                    listOfLines = listOfLines.splitlines()
                    tempmessage = "**Bio for {0}:**\n".format(user.display_name)
                    finalmessage = []
                    for line in listOfLines:
                        if len(tempmessage) < 1800:
                            tempmessage += "{}\n".format(line)
                        else:
                            finalmessage.append(tempmessage)
                            tempmessage = ""
                    finalmessage.append(tempmessage)
                    for x in finalmessage:
                        if x != "":
                            await self.send_message(message.channel, x)
                            asyncio.sleep(0.3)
            else:
                await self.send_message(message.channel, "User has not set a bio\nTo set a bio use `!bio +`, no mention required")
    async def cmd_asdban(self, author, message, channel):
        if author.id in self.whitelist:
            bannedusers = []
            for mention in message.mentions:
                if mention.id != author.id:
                    await self.ban(mention, delete_message_days=0)
                    bannedusers.append(mention.name)
                else:
                    await self.send_message(channel, "Can't ban yourself, dummy!")
                    return
            if len(bannedusers) > 0:
                await self.send_message(channel, "{} Just banned {}.".format(author.display_name, ', '.join(bannedusers)))
    async def cmd_mute(self, message, author, channel, mentions):
        if author.id not in self.whitelist:
            return
        muterole = discord.utils.get(message.server.roles, name='Stop being a faggot')
        if not mentions:
            return
        mutestring = []
        for user in message.mentions:
            await self.add_roles(user, muterole)
            mutestring.append(user.display_name)
        await self.send_message(channel, "**{}** just muted **{}**".format(message.author.display_name, ', '.join(mutestring)))
    async def cmd_unmute(self, message, author, channel, mentions):
        if author.id not in self.whitelist:
            return
        muterole = discord.utils.get(message.server.roles, name='Stop being a faggot')
        if not mentions:
            return
        mutestring = []
        for user in mentions:
            await self.remove_roles(user, muterole)
            mutestring.append(user.display_name)
        await self.send_message(channel, "**{}** just unmuted **{}**".format(author.display_name, ', '.join(mutestring)))
    async def cmd_poll(self, message, server, channel):
        msg = await self.send_message(channel, message.clean_content[5:])
        yes_thumb = discord.utils.get(server.emojis, id="287711899943043072")
        no_thumb = discord.utils.get(server.emojis, id="291798048009486336")
        await self.add_reaction(msg, yes_thumb)
        await self.add_reaction(msg, no_thumb)
    async def cmd_roll(self, message, leftover_args):
        try:
            if len(leftover_args) == 0:
                sides = 6
                rolls = 1
            elif len(leftover_args) == 1:
                sides = int(leftover_args[0])
                rolls = 1
            elif len(leftover_args) == 2:
                sides = int(leftover_args[0])
                rolls = int(leftover_args[1])
            else:
                return
            results = []
            if sides > 100000 or rolls > 100:
                return
            for i in range(rolls):
                diceRoll = random.randint(1, sides)
                results.append(diceRoll)
            median = statistics.median(results)
            mean = statistics.mean(results)
            await self.send_message(message.channel,
            "You rolled **{0}** **{1}-sided** dice, results:{2}\nMedian: **{3}**, mean: **{4:.2f}**".format(rolls, sides, results, median, mean))
        except:
            return
    async def cmd_ignorechannel(self, message, author):
        if author.id not in self.whitelist:
            return
        if not message.channel_mentions:
            return
        for channel_mention in message.channel_mentions:
            if channel_mention.id in self.ignore:
                del self.ignore[channel_mention.id]
            else:
                self.ignore[channel_mention.id] = channel_mention.name
        write_json('ignore.json', self.ignore)
    async def cmd_nicknames(self, message, author, channel, mentions):
        nicks = ""
        if mentions:
            user = mentions[0]
            if user.id == author.id:
                nicks += "**No mention required for yourself!**\n"
        else:
            user = author
        nicks += ', '.join(self.userinfo[user.id]["names"])
        await self.send_message(message.channel, "**Nickname history for {}#{}:**\n{}".format(user.name, user.discriminator, nicks.replace("_", "\_")))
    async def cmd_postcount(self, message, mentions, channel, author, leftover_args):
        user = author
        if len(leftover_args) == 0:
            await self.send_message(channel, "**{0}** has posted **{1}** messages.".format(user.display_name, self.postcountdata[user.id]))
        elif len(leftover_args) == 1:
            post_this = ""
            if mentions:
                user = mentions[0]
                await self.send_message(channel, "**{0}** has posted **{1}** messages.".format(user.display_name, self.postcountdata[user.id]))
            elif leftover_args[0].lower() in ['leaderboard', 'leaderboards', 'top', 'highscore', 'highscores', 'hiscores']:
                leaderboard = self.postcountdata
                rank = 1
                for w in sorted(leaderboard, key=leaderboard.get, reverse=True):
                    if rank <= 20:
                        try:
                            post_this += ("{0}. **{1}:** {2}\n".format(rank, self.get_server('207943928018632705').get_member(w).name, leaderboard[w]))
                            rank += 1
                        except AttributeError:
                            continue
                    else:
                        continue
                post_this += "\n**{0}** posts by **{1}** chatters.".format(sum(self.postcountdata.values()), len(self.postcountdata))
                em = discord.Embed(title="Current standings:", description=post_this, colour=0x14e818)
                em.set_author(name=self.user.name, icon_url=self.user.avatar_url)
                await self.send_message(channel, embed=em)
        else:
            return
    async def cmd_i(self, message, author, mentions):
        if message.mentions:
            user = mentions[0]
        else:
            user = author
        try:
            retard = "{}\nrank {}".format(self.retardcoins[user.id], (sorted(self.retardcoins, key=self.retardcoins.get, reverse=True).index(user.id)+1))
        except KeyError:
            retard = 0
        try:
            sicklad = "{}\nrank {}".format(self.sickladcoins[user.id], (sorted(self.sickladcoins, key=self.sickladcoins.get, reverse=True).index(user.id)+1))
        except KeyError:
            sicklad = 0
        try:
            postcount = "{}\nrank {}".format(self.postcountdata[user.id], (sorted(self.postcountdata, key=self.postcountdata.get, reverse=True).index(user.id)+1))
        except KeyError:
            postcount = "0 or bot"

        try:
            avatar = user.avatar_url
        except:
            avatar = user.default_avatar_url
        try:
            joined_at = user.joined_at
            days_since = "({} days ago)".format((datetime.today() - user.joined_at).days)
            days_after_creation = (user.joined_at - message.server.created_at).days
        except:
            joined_at = "User somehow doesn't have a join date.'"
            days_since = ""
        try:
            days_since_creation = "({} days ago)".format((datetime.today() - user.created_at).days)
        except Exception as e:
            print(e)
            days_since_creation = ""
        try:
            bio = self.biodata[user.id]
        except KeyError:
            bio = "User has not set a bio."
        try:
            if len(self.userinfo[user.id]["names"]) > 1:
                hmm = "Nicknames"
                nicks = '\n'.join(self.userinfo[user.id]["names"][-5:])
            else:
                hmm = "Nickname"
                nicks = user.display_name
        except KeyError:
            nicks = user.display_name
        if len(bio) > 750:
            bio = "User's bio too long - use `!bio` instead."


        usercolor = user.color
        created = re.sub("\.(.*)", "", str(user.created_at))
        joined_at = re.sub("\.(.*)", "", str(user.joined_at))
        em = discord.Embed(title="Userinfo", description=bio, colour=usercolor)
        em.set_author(name=user.name, icon_url=user.avatar_url, url=user.avatar_url)
        em.add_field(name="Name", value="{}#{}".format(user.name, user.discriminator), inline=True)
        em.add_field(name=hmm, value=nicks, inline=True)
        em.add_field(name="ID", value=user.id, inline=True)
        em.add_field(name="Postcount", value=postcount, inline=True)
        em.add_field(name="Retard coins", value=retard, inline=True)
        em.add_field(name="Sicklad", value=sicklad, inline=True)
        em.add_field(name="Created at", value="{} {}".format(created.replace(" ", "\n"), days_since_creation), inline=True)
        em.add_field(name="Joined at", value="{} {}\nThat's {} days after the server was created".format(joined_at.replace(" ", "\n"), days_since, days_after_creation), inline=True)
        #em.set_thumbnail(url=avatar)
        await self.send_message(message.channel, embed=em)
    async def cmd_pickmygold(self, channel):
        await self.send_message(channel, random.choice(OW_Heroes))
    async def cmd_timer(self, message, leftover_args):
        try:
            if leftover_args[0].isdigit() and len(leftover_args) == 1:
                print("isdigittriggered" + leftover_args[0])
                duration = int(leftover_args[0])
                timeUnit = "second"
                timePrint = duration
                firstUnit = None
            #elif len(args) == 1:
            #    a, b, firstDuration, firstUnit, cuntflaps = re.split("((\d+) ?([(h|m)])) ?((\d+) ?(m))? .*?", message.content)
            else:
                a, b, firstDuration, firstUnit, cuntflaps, secondDuration, secondUnit, g = re.split("((\d+) ?([(h|m)])) ?((\d+) ?(m))?.*?", message.clean_content)
                extratime = 0
                duration = int(firstDuration)
                if firstUnit in ['m', 'min', 'minute', 'minutes']:
                    duration = duration * 60
                    timeUnit = "minute"
                    timePrint = duration / 60
                elif firstUnit in ['h', 'hour', 'hours']:
                    duration = duration * 3600
                    try:
                        if secondUnit in ['m', 'min', 'minute', 'minutes']:
                            printme = re.sub("((\d)+ ?(h|hour|hours|m|min|minute|minutes)) ?((\d)+ ?(m|min|minute|minutes))? .*?", "", message.content[7:])
                            extratime = int(secondDuration)
                            timeUnit = "hour, {}-minute".format(extratime)
                            timePrint = duration / 3600
                        else:
                            timeUnit = "hour"
                            timePrint = duration / 3600
                    except IndexError:
                        timeUnit = "hour"
                        timePrint = duration / 3600
                else:
                    timePrint = duration
                    timeUnit = "second"
                #if len(leftover_args) >= 3:
            #7 days
            if duration < 604800:
                print("len of args: {}\n".format(len(leftover_args)))
                if len(leftover_args) == 1:
                    await self.send_message(message.channel, "{0:.0f}-{1} timer started.".format(timePrint, timeUnit))
                    await asyncio.sleep(duration)
                    await self.send_message(message.channel, "{} beep bop (how do timers talk?)".format(message.author.mention))
                #elif len(leftover_args) == 2 and firstUnit in ['m', 'min', 'minute', 'minutes','h', 'hour', 'hours']:
                #    await self.send_message(message.channel, "{0:.0f}-{1} timer started.".format(timePrint, timeUnit))
                #    await asyncio.sleep(duration)
                #    await self.send_message(message.channel, "{} beep-- bop (how do timers talk?)".format(message.author.mention))
                elif len(leftover_args) >= 2 and firstUnit in ['m', 'min', 'minute', 'minutes','h', 'hour', 'hours']:
                    printme = re.sub("((\d)+ ?(h|hour|hours|m|min|minute|minutes)) ?((\d)+ ?(m|min|minute|minutes))? .*?", "", message.content[7:])
                    try:
                        if secondUnit in ['m', 'min', 'minute', 'minutes'] and len(leftover_args) >= 4:
                            await self.send_message(message.channel, "{0:.0f}-{1} timer started.".format(timePrint, timeUnit))
                            await asyncio.sleep(duration + (extratime * 60))
                            await self.send_message(message.channel, "{} beep bop\n`{}`".format(message.author.mention, printme))
                        else:
                            await self.send_message(message.channel, "{0:.0f}-{1} timer started.".format(timePrint, timeUnit))
                            await asyncio.sleep(duration + (extratime * 60))
                            await self.send_message(message.channel, "{} beep bop\n`{}`".format(message.author.mention, printme))
                    except IndexError:
                        await self.send_message(message.channel, "{0:.0f}-{1} timer started.".format(timePrint, timeUnit))
                        await asyncio.sleep(duration + (extratime * 60))
                        await self.send_message(message.channel, "{} beep bop\n`{}`".format(message.author.mention, printme))
                else:
                    await self.send_message(message.channel, "{0:.0f}-{1} timer started.".format(timePrint, timeUnit))
                    await asyncio.sleep(duration)
                    await self.send_message(message.channel, "{} beepfsdfsdfbop\n`{}`".format(message.author.mention, message.content[7+len(leftover_args[0]):]))
            else:
                return
        except ValueError or KeyError:
            return
    async def cmd_affix(self, channel, author):
        nerd_epoch = datetime(year=2017, month=1, day=18, hour=8, minute=0, second=0, microsecond=0)
        EU_time = datetime.now()
        NA_time = EU_time - timedelta(weeks=2, hours=-16)
        EU_indexthis = EU_time - nerd_epoch
        NA_indexthis = NA_time - nerd_epoch
        E = EU_indexthis.days // 7
        N = NA_indexthis.days // 7
        E = E % 8
        N = N % 8
        usercolor = author.colour
        em = discord.Embed(title="Mythic+ affixes", description="", colour=usercolor)
        em.set_author(name=author.display_name, icon_url=author.avatar_url, url=author.avatar_url)
        em.add_field(name="+4", value="**EU:** {}\n**NA:** {}".format(AFFIX1[E], AFFIX1[N]), inline=True)
        em.add_field(name="+7", value="{}\n{}".format(AFFIX2[E], AFFIX2[N]), inline=True)
        em.add_field(name="+10", value="{}\n{}".format(AFFIX3[E], AFFIX3[N]), inline=True)
        E = (E + 1) % 8
        N = (N + 1) % 8
        em.add_field(name="Next week", value="**EU:**\n{}\n{}\n{}\n\n**NA:**\n{}\n{}\n{}".format(AFFIX1[E], AFFIX2[E], AFFIX3[E], AFFIX1[N], AFFIX2[N], AFFIX3[N]), inline=True)
        E = (E + 1) % 8
        N = (N + 1) % 8
        em.add_field(name="In two weeks", value="**EU:**\n{}\n{}\n{}\n\n**NA:**\n{}\n{}\n{}".format(AFFIX1[E], AFFIX2[E], AFFIX3[E], AFFIX1[N], AFFIX2[N], AFFIX3[N]), inline=True)
        E = (E + 1) % 8
        N = (N + 1) % 8
        em.add_field(name="In three weeks", value="**EU:**\n{}\n{}\n{}\n\n**NA:**\n{}\n{}\n{}".format(AFFIX1[E], AFFIX2[E], AFFIX3[E], AFFIX1[N], AFFIX2[N], AFFIX3[N]), inline=True)
        await self.send_message(channel, embed=em)
    async def cmd_weather(self, channel, author, leftover_args):
        user = author
        if len(leftover_args) == 0:
            try:
                city = self.home[author.id]
            except:
                return await self.send_message(channel, "No home set. To set a home, use `!weather home <location>`")
        else:
            city = ' '.join(leftover_args)
            if leftover_args[0].lower() == "home" and len(leftover_args) > 1:
                home = ' '.join(leftover_args[1:])
                self.home[author.id] = home
                write_json('weather.json', self.home)
                await self.send_message(channel, "Home set to **{}**".format(home))
                return
            elif leftover_args[0].lower() == "home" and len(leftover_args) == 1:
                await self.send_message(channel, "Your location has __not__ been changed, use `!weather home <location>` to set a home")
                return
        r = requests.get('http://api.openweathermap.org/data/2.5/weather?q='+city+weatherkey)
        json_object = r.json()
        temp_k = float(json_object['main']['temp'])
        temp_c = temp_k - 273.15
        temp_f = temp_c * (9/5) + 32
        city, country, weather, humidity, windspeed = json_object['name'],json_object['sys']['country'], json_object['weather'][0]['description'], json_object['main']['humidity'], json_object['wind']['speed']
        usercolor = author.color
        em = discord.Embed(title="Weather in {0}, {1}".format(city, country), description="", colour=usercolor)
        em.set_author(name=user.display_name, icon_url=user.avatar_url, url=user.avatar_url)
        em.add_field(name="Temperature", value="{0:.1f}°C\n{1:.1f}°F".format(temp_c, temp_f), inline=True)
        em.add_field(name="Description", value=pretty_weather(weather), inline=True)
        em.add_field(name="Humidity", value="{}%".format(humidity), inline=True)
        em.add_field(name="Wind speed", value="{}m/s\n{}".format(windspeed, beaufort_scale(windspeed)), inline=True)
        em.set_thumbnail(url=user.avatar_url)
        await self.send_message(channel, embed=em)
    async def cmd_ban(self, author, channel, mentions):
        if author.id == CARL_DISCORD_ID:
            if mentions[0] == self.user:
                await self.send_message(channel, "I'm sorry, Carl. I'm afraid I can't do that.")
            else:
                await self.send_message(channel, "**{}** was just banned from the server.".format(mentions[0].display_name))
        else:
            await self.send_message(channel, "Nope")
    async def cmd_bread(self, author, channel, mentions):
        user = mentions[0]
        em_before = discord.Embed(title="Bread", description="Sending bread...", colour=0x42f4dc)
        em_before.set_author(name=user.name, icon_url=user.avatar_url)
        em_success = discord.Embed(title="Success", description="Your bread was sent.", colour=0x14e818)
        em_success.set_author(name=user.name, icon_url=user.avatar_url)
        em_error = discord.Embed(title="Error", description="Bread could not be sent, try again later.", colour=0xff3b19)
        em_error.set_author(name=user.name, icon_url=user.avatar_url)
        xd = await self.send_message(channel, embed=em_before)
        try:
            fmt = "{0} just fed you :bread: bread :bread:, so far I've fed people {1} times.\n{2}"
            await self.send_message(user, fmt.format(author, self.breadcount["people fed"], "hello!"))
            await self.edit_message(xd, embed=em_success)
            self.breadcount["people fed"] += 1
            write_json('bread.json', self.breadcount)
        except IndexError:
            return
        except discord.HTTPException:
            await asyncio.sleep(0.1)
            await self.edit_message(xd, embed=em_error)



    async def cmd_say(self, channel, message, leftover_args):
        if message.mentions:
            return
        await self.delete_message(message)
        await self.send_message(channel, ' '.join(leftover_args))

    async def on_message(self, message):
        if message.author == self.user:
            return
        if message.channel.is_private:
            return
        if "@everyone" in message.content:
            return
        if "@here" in message.content:
            return
        if message.channel.id == "217375065346408449":
            if (message.content.startswith("http://") or message.content.startswith("https://") or message.attachments):
                return
            else:
                await self.delete_message(message)
                await self.send_message(message.author, "No text allowed in #meme-archive (links and file uploads only)")
        if random.randint(1, 10000) == 1:
            legendaryRole = discord.utils.get(message.server.roles, name='Legendary')
            await self.add_roles(message.author, legendaryRole)
            await self.send_message(message.channel, "{} just received a legendary item: **{}**".format(message.author.mention, random.choice(legendaries)))

        msg = message.content[1:]
        if len(msg.split()) < 1:
            return
        command, *args = msg.split()
        command = command.lower()
        if message.content.startswith(self.prefix):
            if message.channel.id in self.ignore and message.author.id not in self.whitelist:
                return
            if message.author.id in self.blacklist:
                return
            if command in loaded_commands:
                handler = getattr(self, "cmd_{}".format(command), None)
            elif command in aliased_commands:
                handler = getattr(self, "cmd_{}".format(aliased_commands[command]), None)
            else:
                tagname = re.sub("[^a-z0-9_-]", "", command)
                if tagname in self.taglist:
                    return await self.send_message(message.channel, self.taglist[tagname])
                else:
                    return

            handler_kwargs = {}
            argspec = inspect.signature(handler)
            params = argspec.parameters.copy()

            try:
                handler_kwargs = {}
                if params.pop('message', None):
                    handler_kwargs['message'] = message

                if params.pop('channel', None):
                    handler_kwargs['channel'] = message.channel

                if params.pop('author', None):
                    handler_kwargs['author'] = message.author

                if params.pop('server', None):
                    handler_kwargs['server'] = message.server

                if params.pop('mentions', None):
                    handler_kwargs['mentions'] = message.mentions

                if params.pop('leftover_args', None):
                    handler_kwargs['leftover_args'] = args
                try:
                    response = await handler(**handler_kwargs)
                except Exception as e:
                    print(f"exception in kwargs: {e}")
            except:
                print("welp")
        elif "carl" in message.content.lower():
            insensitive_carl = re.compile(re.escape('carl'), re.IGNORECASE)
            xd = await self.send_message(discord.Object(id="213720502219440128"), "<@106429844627169280>, you were mentioned!")
            await self.delete_message(xd)
            postme = insensitive_carl.sub('**__Carl__**', message.clean_content)
            await self.send_message(discord.Object(id="213720502219440128"), "**{}** in **<#{}>**:\n{}".format(message.author.display_name, message.channel.id, postme))
        else:
            self.fix_postcount(message.author)
            self.log(message)


if __name__ == '__main__':
    bot = CarlBot()
    bot.run(bot.token)
