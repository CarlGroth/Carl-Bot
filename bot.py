import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding=sys.stdout.encoding, errors="backslashreplace", line_buffering=True)
import json
import asyncio
import aiohttp
import discord
import random
import math
import time
import requests
import statistics
import string
import re
import markovify
from googleapiclient.discovery import build
from responses import *
from sensitivedata import *
from datetime import datetime, timedelta
from fuzzywuzzy import fuzz

#comments are for pussies
client = discord.Client()

CARL_DISCORD_ID = '106429844627169280'


def load_json(filename):
    with open(filename, encoding='utf-8') as taglist:
        return json.load(taglist)

def write_json(filename, contents):
    with open(filename, 'w') as outfile:
        json.dump(contents, outfile, indent=2)


def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    return res['items']




class CarlBot(discord.Client):
    def __init__(self):
        super().__init__()
        self.prefix = '!'
        self.token = token
        self.tags = load_json('taglist.json')
        self.wcltoken = wcltoken
        self.bread = load_json('bread.json')
        self.bio = load_json('bio.json')
        self.retard = load_json('retard.json')
        self.postcount = load_json('postcount.json')
        self.sicklad = load_json('sicklad.json')
        self.whitelist = load_json('whitelist.json')
        self.blacklist = load_json('blacklist.json')
        self.home = load_json('weather.json')
        self.aiosession = aiohttp.ClientSession(loop=self.loop)
        self.userinfo = load_json('users.json')
        self.ignore = load_json('ignore.json')

    def is_carl():
        return message.author.id == CARL_DISCORD_ID

    async def on_ready(self):
        print('connected!\n')
        print('Username: ' + self.user.name)
        print('ID: ' + self.user.id)
        print('--Server List--')
        global starttime
        starttime = time.time() + 3600
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

    async def userfix(self, member):
        if member.id not in self.userinfo:
            self.userinfo[member.id] = {"names": [member.name],
                                        "roles": [x.name for x in member.roles if x.name != "@everyone"]}
        write_json('users.json', self.userinfo)

    async def say_message(self, channel, ogmsg, message_content):
        timedmsg = await self.send_message(channel, message_content)
        await self.delete_message(ogmsg)

    async def on_member_ban(self, member):
        await self.send_message(discord.Object(id="207943928018632705"), "**{}** was just banned from the server.".format(member.display_name))

    async def on_member_update(self, before, after):
        if before.nick != after.nick:
            await self.send_message(discord.Object(id="249336368067510272"), ":spy: **{0}#{1}** changed their nickname:\n**Before:** {2}\n**+After:** {3}".format(before.name, before.discriminator, before.display_name, after.display_name))
            await self.userfix(before)
            if after.display_name not in self.userinfo[before.id]["names"]:
                self.userinfo[before.id]["names"].append(after.display_name)
            else:
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
                await self.send_message(discord.Object(id="249336368067510272"), ":warning: **{}** had the role **{}** added.".format(before.display_name, newrole[0].name))
            else:
                s = set(after.roles)
                newrole = [x for x in before.roles if x not in s]
                await self.send_message(discord.Object(id="249336368067510272"), ":warning: **{}** had the role **{}** removed.".format(before.display_name, newrole[0].name))
    async def on_member_join(self, member):
        await self.send_message(discord.Object(id='249336368067510272'), ":white_check_mark: **{0}#{1}** *({2})* Joined the server at `{3}`<@{4}> <@{5}> :white_check_mark:".format(member.name, member.discriminator, member.id, time.strftime("%Y-%m-%d %H:%M:%S (central carl time)."), CARL_DISCORD_ID, "158370770068701184"))
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
        await self.send_message(discord.Object(id='249336368067510272'), ":wave: **{0}#{1}** *({2})* left the server at `{3}`<@{4}> <@{5}> :wave:".format(member.name, member.discriminator, member.id, time.strftime("%Y-%m-%d %H:%M:%S (central carl time)."), CARL_DISCORD_ID, "158370770068701184"))
    async def on_message_delete(self, message):
        if message.channel.id == "267085455047000065":
            return
        if message.channel.is_private:
            return
        if message.author.id in [self.user.id, "283540074837049354"]:
            return
        if message.clean_content.startswith(self.prefix):
            return
        if message.clean_content.startswith('$'):
            return
        if message.author.id == "106429844627169280":
            if message.content.startswith("++"):
                return
        destination = discord.Object(id='249336368067510272')
        poststring = ":x: `{1}` **{0}** Deleted their message:  ```{2}``` in `{3}`".format(message.author.name, time.strftime("%H:%M:%S"), message.clean_content, message.channel)
        if message.attachments:
            poststring += "\n{}".format(message.attachments[0]['url'])
        
        await self.send_message(destination, poststring)

    async def on_message_edit(self, before, after):
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
        await self.send_message(discord.Object(id='249336368067510272'), ":pencil2: `{}`, **{}** edited their message:\n**Before:** {}\n**+After:** {}".format(time.strftime("%H:%M:%S"), before.author.name, before.clean_content, after.clean_content))


    async def log(self, message):
        with open("logs/{}.txt".format(message.author.id), "a", encoding="utf-8") as f:
            f.write("{}\n".format(message.clean_content))
    
    async def on_message(self, message):
        #print(message.clean_content)
        if message.author == self.user:
            return
        if message.channel.is_private:
            print(message.content + " [author: {}]".format(message.author))
            return
        if "@everyone" in message.content:
            print("at everyone in sdmasoidj")
            return
        if "@here" in message.content:
            return
        if random.randint(1, 10000) == 1:
            legendaryRole = discord.utils.get(message.server.roles, name='Legendary')
            await self.add_roles(message.author, legendaryRole)
            await self.send_message(message.channel, "{} just received a legendary item: **{}**".format(message.author.mention, random.choice(legendaries)))
        if message.content.startswith(self.prefix):
            if message.channel.id in self.ignore and message.author.id not in self.whitelist:
                return
            if message.author.id in self.blacklist:
                return
            msg = message.content[1:]
            command, *args = msg.split()
            command = command.lower()
            print(command)
            if command == 'say':
                await self.say_message(message.channel, message, "{}".format(message.clean_content[5:]))
            elif command =='bread':
                user = message.mentions[0]
                em_before = discord.Embed(title="Bread", description="Sending bread...", colour=0x42f4dc)
                em_before.set_author(name=user.name, icon_url=user.avatar_url)
                em_success = discord.Embed(title="Success", description="Your bread was sent.", colour=0x14e818)
                em_success.set_author(name=user.name, icon_url=user.avatar_url)
                em_error = discord.Embed(title="Error", description="Bread could not be sent, try again later.", colour=0xff3b19)
                em_error.set_author(name=user.name, icon_url=user.avatar_url)
                xd = await self.send_message(message.channel, embed=em_before)
                try:
                    await self.send_message(user, "{0} just fed you :bread: bread :bread:, so far I've fed people {1} times.\n{2}".format(message.author, self.bread["people fed"], random.choice(listofbirds)))
                    await asyncio.sleep(0.1)
                    await self.edit_message(xd, embed=em_success)
                    self.bread["people fed"] += 1
                    write_json('bread.json', self.bread)
                except IndexError:
                    return
                except discord.HTTPException:
                    await asyncio.sleep(0.1)
                    await self.edit_message(xd, embed=em_error)
                except ValueError:
                    await self.send_message(message.channel, "Not even a number")
            elif command == 'ban':
                if message.author.id == CARL_DISCORD_ID:
                    if message.mentions[0] == self.user:
                        await self.send_message(message.channel, "I'm sorry, Carl. I'm afraid I can't do that.")
                    else:
                        await self.send_message(message.channel, "banned user {}.".format(args[0]))
                else:
                    await self.send_message(message.channel, "Nope")
            elif command in ['weather', 'temp', 'temperature']:
                user = message.author
                if len(args) == 0:
                    try:
                        city = self.home[user.id]
                    except Exception:
                        await self.send_message(message.channel, "No home set. To set a home, use `!weather home`")
                        return
                else:
                    city = ' '.join(args)
                    if args[0] == "home" and len(args) > 1:
                        home = ' '.join(args[1:])
                        self.home[user.id] = home
                        write_json('weather.json', self.home)
                        await self.send_message(message.channel, "Home set to: **{}**".format(home))
                        return
                    elif args[0] == "home" and len(args) == 1:
                        await self.send_message(message.channel, "haha very funny joke! :)")
                        return
                        
                r = requests.get('http://api.openweathermap.org/data/2.5/weather?q='+city+weatherkey)
                json_object = r.json()
                temp_k = float(json_object['main']['temp'])
                temp_c = temp_k - 273.15
                temp_f = temp_c * (9/5) + 32
                city, country, weather, humidity, windspeed = json_object['name'],json_object['sys']['country'], json_object['weather'][0]['description'], json_object['main']['humidity'], json_object['wind']['speed']
                usercolor = message.author.color
                em = discord.Embed(title="Weather in {0}, {1}".format(city, country), description="", colour=usercolor)
                em.set_author(name=user.display_name, icon_url=user.avatar_url, url=user.avatar_url)
                em.add_field(name="Temperature", value="{0:.1f}°C\n{1:.1f}°F".format(temp_c, temp_f), inline=True)
                em.add_field(name="Description", value=weather.capitalize(), inline=True)
                em.add_field(name="Humidity", value="{}%".format(humidity), inline=True)
                em.add_field(name="Wind speed", value="{}m/s".format(windspeed), inline=True)
                em.set_thumbnail(url=user.avatar_url)
                await self.send_message(message.channel, embed=em)
                    
            
            elif command in ['affix', 'affixes', 'm+']:
                #if message.author.id != CARL_DISCORD_ID:
                #    return
                nerd_epoch = datetime(year=2017, month=1, day=18, hour=8, minute=0, second=0, microsecond=0)
                EU_time = datetime.now()
                #NA is two weeks, 16 hours behind EU
                NA_time = EU_time - timedelta(weeks=2, hours=-16)
                #NA_time2 = EU_time - timedelta(weeks=2, hours=16)
                #NA_time3 = EU_time - timedelta(weeks=2, hours=-16)
                print("{}\n{}".format(EU_time, NA_time))
                EU_indexthis = EU_time - nerd_epoch
                NA_indexthis = NA_time - nerd_epoch
                E = EU_indexthis.days // 7
                N = NA_indexthis.days // 7
                user = message.author
                usercolor = message.server.get_member(user.id).colour
                em = discord.Embed(title="Mythic+ affixes", description="", colour=usercolor)
                em.set_author(name=user.display_name, icon_url=user.avatar_url, url=user.avatar_url)
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
                await self.send_message(message.channel, embed=em)
            elif command == 'ignorechannel':
                if message.author.id not in self.whitelist:
                    return
                if not message.channel_mentions:
                    return
                for channel_mention in message.channel_mentions:
                    if channel_mention.id in self.ignore:
                        del self.ignore[channel_mention.id]
                    else:
                        self.ignore[channel_mention.id] = channel_mention.name
                write_json('ignore.json', self.ignore)
            elif command in ['dice', 'roll']:
                try:
                    if len(args) == 0:
                        sides = 6
                        rolls = 1
                    elif len(args) == 1:
                        sides = int(args[0])
                        rolls = 1
                    elif len(args) == 2:
                        sides = int(args[0])
                        rolls = int(args[1])
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
                    "You rolled **{0}** **{1}-sided** dice, results:{2}\nMedian:**{3}**, mean:**{4:.2f}**".format(rolls, sides, results, median, mean))
                except discord.HTTPException:
                    return
                except ValueError:
                    return

            elif command == 'poll':
                msg = await self.send_message(message.channel, message.clean_content[5:])
                await self.add_reaction(msg, '👍')
                await self.add_reaction(msg, '👎')
            elif command == 'mute':
                if message.author.id not in self.whitelist:
                    return
                muterole = discord.utils.get(message.server.roles, name='Stop being a faggot')
                if not message.mentions:
                    return
                mutestring = []
                for user in message.mentions:
                    await self.add_roles(user, muterole)
                    mutestring.append(user.display_name)
                await self.send_message(message.channel, "**{}** just muted **{}**".format(message.author.display_name, ', '.join(mutestring)))
            elif command == 'unmute':
                if message.author.id not in self.whitelist:
                    return
                muterole = discord.utils.get(message.server.roles, name='Stop being a faggot')
                if not message.mentions:
                    return
                mutestring = []
                for user in message.mentions:
                    await self.remove_roles(user, muterole)
                    mutestring.append(user.display_name)
                await self.send_message(message.channel, "**{}** just unmuted **{}**".format(message.author.display_name, ', '.join(mutestring)))
            elif command in ['choice', 'choose']:
                if len(args) == 0:
                    return
                choices = args
                choices = ' '.join(choices)
                choices = choices.split(",")
                await self.send_message(message.channel, random.choice(choices))

            elif command == 'tag':
                if message.mentions:
                    return
                tagreturn = ' '.join(args[2:])
                taglist = self.tags
                if args[0] == 'list':
                    d = sorted(list(self.tags.keys()))
                    if sum(len(t) for t in d) < 1900:
                        d = ', '.join(d)
                        await self.send_message(message.author, d)
                    else:
                        print("long trigger")
                        tempmessage = []
                        finalmessage = []
                        for tag in d:
                            if len(', '.join(tempmessage)) < 1800:
                                tempmessage.append(tag)
                            else:
                                xd = ', '.join(tempmessage)
                                finalmessage.append(xd)
                                tempmessage = []
                        finalmessage.append(', '.join(tempmessage))
                        for x in finalmessage:
                            if x != "":
                                await self.send_message(message.author, x)
                elif args[0] == "search":
                    if len(args) < 2:
                        return
                    query = re.sub("[^a-z0-9_-]", "", args[1].lower())
                    tagreturn = ""
                    bad_coding_practice_variable = ""
                    i = 1
                    for tag in taglist:
                        if fuzz.partial_ratio(query, tag) > 80:
                            if i <= 15:
                                tagreturn += "{}. {}\n".format(i, tag)
                                bad_coding_practice_variable += "{}\n".format(tag)
                                i += 1
                            else:
                                i += 1
                        #elif fuzz.partial_ratio(query, tag) > 75:
                        #    tagreturn75 += "{}\n".format(tag)
                    if len(tagreturn) == 0:
                        await self.send_message(message.channel, "Sorry, couldn't find any matching tags.")
                    else:
                        em = discord.Embed(title="Search results (80+):", description=tagreturn, colour=0xffffff)
                        em.set_author(name=message.author.name, icon_url=message.author.avatar_url, url=message.author.avatar_url)
                        #em.add_field(name="Results (75+)", value=tagreturn75, inline=True)
                        em.set_footer(text="{} results. (page {}/{})".format(i-1, 1, math.ceil((i-1)/15)))
                        await self.send_message(message.channel, embed=em)
                        def check(mesg):
                            if mesg.content.isdigit():
                                return True
                        msg = await self.wait_for_message(author=message.author, check=check)
                        if msg.content.isdigit():
                            listoflines = bad_coding_practice_variable.split('\n')
                            print(listoflines[int(msg.content)-1])
                            await self.send_message(message.channel, self.tags[listoflines[int(msg.content)-1]])
                elif args[0] == "+=":
                    tagname = re.sub("[^a-z0-9_-]", "", args[1].lower())
                    content = message.content[(9+len(args[1])):]
                    if len(args) <= 2:
                        await self.send_message(message.channel, "<:FailFish:235926308071276555>")
                        return
                    if (len(content) + len(self.tags[tagname])) < 2000:
                        try:
                            self.tags[tagname] += "\n{}".format(content)
                        except KeyError:
                            self.tags[tagname] = "{}".format(content)
                        write_json('taglist.json', self.tags)
                        await self.send_message(message.channel, "`{}` was appended to the tag: {}".format(content, tagname))
                    else:
                        await self.send_message(message.channel, "that would make the tag too big, retard.")
                elif args[0] == '+':
                    tagname = re.sub("[^a-z0-9_-]", "", args[1].lower())
                    if len(args) <= 2:
                        await self.send_message(message.channel, "<:FailFish:235926308071276555>")
                        return
                    if args[1] == 'list':
                        await self.send_message(message.channel, "Nice try, motherfucker.")
                        return
                    if tagname   in taglist:
                        def check(mesg):
                            return True

                        await self.send_message(message.channel, "Tag already exists. Replace or add to tag? (y/n/a)")
                        msg = await self.wait_for_message(author=message.author, check=check)
                        if msg.content.lower() == 'y':
                            tagname = re.sub("[^a-z0-9_-]", "", args[1].lower())
                            self.tags[tagname] = message.content[(7+len(args[1])):]
                            write_json('taglist.json', self.tags)
                            await self.send_message(message.channel, "Tag succesfully replaced.")
                        elif msg.content.lower() == 'n':
                            await self.send_message(message.channel, "Tag not replaced.")
                        elif msg.content.lower() == 'a':
                            tagname = re.sub("[^a-z0-9_-]", "", args[1].lower())
                            content = message.content[(8+len(args[1])):]
                            if (len(content) + len(self.tags[tagname])) < 2000:
                                try:
                                    self.tags[tagname] += "\n{}".format(content)
                                except KeyError:
                                    self.tags[tagname] = "{}".format(content)
                                write_json('taglist.json', self.tags)
                                await self.send_message(message.channel, "`{}` was appended to the tag: {}".format(content, tagname))
                        else:
                            return
                    elif len(message.content) < 1750:
                        tagname = re.sub("[^a-z0-9_-]", "", args[1].lower())
                        if tagname == '':
                            return
                        self.tags[tagname] = message.content[(7+len(args[1])):]
                        write_json('taglist.json', self.tags)
                        await self.send_message(message.channel, "tag `{0}` added".format(tagname))
                    
                    else:
                        await self.send_message(message.channel, "too long <:gachiGASM:234404899511599104>")
                elif args[0] in ['-', 'del']:
                    tagname = args[1]
                    if tagname in taglist:
                        del taglist[tagname]
                        write_json('taglist.json', self.tags)
                        await self.send_message(message.channel, "tag `{0}` deleted".format(tagname))
                    else:
                        await self.send_message(message.channel, "tag `{0}` not found".format(tagname))
                else:
                    tagname = args[0].lower()
                    if tagname in self.tags:
                        await self.send_message(message.channel, self.tags[tagname])
                    else:
                        await self.send_message(message.channel, "No such tag")
            elif command == 'm':
                if message.author.id == CARL_DISCORD_ID:
                    await self.send_message(message.channel, "{}".format(eval(message.content[3:])))
            elif command == 'avatar':
                if message.author.id not in self.whitelist:
                    return
                if message.attachments:
                    avatar = message.attachments[0]['url']
                else:
                    avatar = args[0].strip('<>')
                try:
                    with aiohttp.Timeout(10):
                        async with self.aiosession.get(avatar) as res:
                            await self.edit_profile(avatar=await res.read())
                except Exception as e:
                    print(e)
            elif command == 'retard':
                if len(args) == 0:
                    await self.send_message(message.channel, "You sure are.")
                elif args[0].lower() in ['leaderboard', 'leaderboards', 'top', 'highscore', 'highscores', 'hiscores']:
                    leaderboard = self.retard
                    post_this = "**Current standings:**\n"
                    rank = 1
                    print(self.get_server('207943928018632705').get_member("98404146469699584"))
                    for w in sorted(leaderboard, key=leaderboard.get, reverse=True):
                        if rank < 11:
                            try:
                                post_this += ("{0}. **{1}** = {2}\n".format(rank, self.get_server('207943928018632705').get_member(w).name, leaderboard[w]))
                                rank += 1
                            except AttributeError:
                                continue
                        else:
                            continue
                    post_this += "**{0}** coins in total spread across **{1}** retards.".format(sum(self.retard.values()),len(self.retard))
                    await self.send_message(message.channel, post_this)
                try:
                    userID = ''.join(message.mentions[0].id)
                    userID = re.sub("[^0-9]", "", userID)
                    if userID == '':
                        return
                    elif userID not in self.retard:
                        self.retard[userID] = 1
                        write_json('retard.json', self.retard)
                        await self.send_message(message.channel, "Welcome to the retard club, {0}".format(args[0]))
                    else:
                        if len(args) == 1:
                            self.retard[userID] += 1
                            write_json('retard.json', self.retard)
                            await self.send_message(message.channel, "**{0}** just tipped **{1} 1** retard coin, **{1}** now has **{2}** coins.".format(message.author.name.replace("_", "\_"), message.mentions[0].name.replace("_", "\_"), self.retard[userID]))
                        else:
                            reason = ' '.join(args[1:])
                            self.retard[userID] += 1
                            write_json('retard.json', self.retard)
                            await self.send_message(message.channel, "**{0}** just tipped **{1} 1** retard coin, reason: `{2}`\n**{1}** now has **{3}** coins.".format(message.author.name.replace("_", "\_"), message.mentions[0].name.replace("_", "\_"), reason, self.retard[userID]))
                except IndexError:
                    return
                except UnboundLocalError:
                    return
                except discord.HTTPException:
                    return
            elif command == 'sc':
                smallcaps_string = smallcaps(message.clean_content[4:])
                await self.send_message(message.channel, smallcaps_string)
            elif command == 'bl':
                if message.author.id != CARL_DISCORD_ID:
                    return
                if not message.mentions:
                    return
                BLACKED = []
                if args[0] in ['+', 'add']:
                    fmt = "Blacklisted **{}.**"
                    for usr in message.mentions:
                        self.blacklist[usr.id] = usr.name
                        BLACKED.append(usr.display_name)
                    BLACKED = ', '.join(BLACKED)
                    write_json('blacklist.json', self.blacklist)
                elif args[0] in ['-', 'del']:
                    fmt = "Removed **{}** from the blacklist."
                    for usr in message.mentions:
                        if usr.id in self.blacklist:
                            del self.blacklist[usr.id]
                            BLACKED.append(usr.display_name)
                    BLACKED = ', '.join(BLACKED)
                    write_json('blacklist.json', self.blacklist)
                await self.send_message(discord.Object(id='249336368067510272'), fmt.format(BLACKED))
            elif command == 'wl':
                if message.author.id != CARL_DISCORD_ID:
                    return
                if not message.mentions:
                    return
                whitelisted = []
                if args[0] in ['+', 'add']:
                    fmt = "Whitelisted **{}.**"
                    for usr in message.mentions:
                        self.whitelist[usr.id] = usr.name
                        whitelisted.append(usr.display_name)
                    whitelisted = ', '.join(whitelisted)
                    write_json('whitelist.json', self.whitelist)
                elif args[0] in ['-', 'del']:
                    fmt = "Removed **{}** from the whitelist."
                    for usr in message.mentions:
                        if usr.id in self.whitelist:
                            del self.whitelist[usr.id]
                            whitelisted.append(usr.display_name)
                    whitelisted = ', '.join(whitelisted)
                    write_json('whitelist.json', self.whitelist)
                else:
                    return
                await self.send_message(discord.Object(id='249336368067510272'), fmt.format(whitelisted))
            elif command == 'asdban':
                if message.author.id in self.whitelist:
                    bannedusers = []
                    for mention in message.mentions:
                        await self.ban(mention, delete_message_days=0)
                        bannedusers.append(mention.name)
                    await self.send_message(message.channel, "{} Just banned {}.".format(message.author, ', '.join(bannedusers)))
            elif command == 'spook':
                if message.mentions:
                    await self.send_message(message.channel, "you have been spooked, **{}** ! o no :skull_crossbones:".format(message.mentions[0].display_name))
                else:
                    await self.send_message(message.channel, "boo!")
            elif command == 'bio':
                #if message.author.id != CARL_DISCORD_ID:
                #    return
                premium_member = False
                if message.mentions:
                    user = message.mentions[0]
                else:
                    user = message.author
                if user.id in self.whitelist:
                    premium_member = True
                if len(args) == 1 and not message.mentions:
                    await self.send_message(message.channel, "Empty bio <:FailFish:235926308071276555>")
                if args and not message.mentions:
                    if args[0] == '+':
                        if message.author.id in self.bio:
                            def check(mesg):
                                return True
                            await self.send_message(message.channel, "Bio already exists. **__r__**eplace, **__c__**ancel or **__a__**dd to? (r/c/a)")
                            msg = await self.wait_for_message(author=message.author, check=check)
                            if msg.content.lower() in ['r', 'y', 'yes', 'replace']:
                                self.bio[message.author.id] = message.clean_content[7:]
                                write_json('bio.json', self.bio)
                                await self.send_message(message.channel, "Bio succesfully replaced.")
                            elif msg.content.lower() in ['c', 'n', 'no', 'cancel']:
                                await self.send_message(message.channel, "Bio unchanged.")
                            elif msg.content.lower() == 'a':
                                if premium_member:
                                    self.bio[message.author.id] += "\n{}".format(message.clean_content[7:])
                                    write_json('bio.json', self.bio)
                                elif not premium_member and (len(message.clean_content[7:]) + len(self.bio[message.author.id])) < 2000:
                                    self.bio[message.author.id] += "\n{}".format(message.clean_content[7:])
                                    write_json('bio.json', self.bio)
                                else:
                                    return
                                await self.send_message(message.channel, "`{0}` was appended to {1.name}'s bio.".format(message.clean_content[7:], message.author))
                        else:
                            if len(message.content) < 1750 or premium_member:
                                self.bio[message.author.id] = message.clean_content[7:]
                                write_json('bio.json', self.bio)
                                await self.send_message(message.channel, "**{}'s** bio was added".format(message.author))
                    elif args[0] == "+=":
                        if message.author.id not in self.whitelist:
                            if (len(message.clean_content[8:]) + len(self.bio[message.author.id])) < 2000:
                                try:
                                    self.bio[message.author.id] += "\n{}".format(message.clean_content[8:])
                                except KeyError:
                                    self.bio[message.author.id] = "{}".format(message.clean_content[8:])
                                write_json('bio.json', self.bio)
                                await self.send_message(message.channel, "`{0}` was appended to {1.name}'s bio.".format(message.clean_content[8:], message.author))
                            else:
                                await self.send_message(message.channel, "Too long")
                        else:
                            if len(args) == 1:
                                await self.send_message(message.channel, "retard <:FailFish:235926308071276555>")
                            try:
                                self.bio[message.author.id] += "\n{}".format(message.clean_content[8:])
                            except KeyError:
                                self.bio[message.author.id] = "{}".format(message.clean_content[8:])
                            write_json('bio.json', self.bio)
                            await self.send_message(message.channel, "`{0}` was appended to {1.name}'s bio.".format(message.clean_content[8:], message.author))
                else:
                    bioname = user.id
                    print(bioname)
                    if bioname in self.bio:
                        if len(self.bio[bioname]) < 1750:
                            print("hey, what the fuck")
                            await self.send_message(message.channel, "Bio for {0}:\n{1}".format(message.author, self.bio[bioname]))
                        else:
                            listOfLines = self.bio[bioname]
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
                        print(bioname)
                        await self.send_message(message.channel, "User has not set a bio\nTo set a bio use `!bio +`, no mention required")

            elif command == 'speak':
                if not message.mentions and len(args) == 0:
                    victim = message.author.id
                elif not message.mentions and len(args) == 1:
                    print(args[0])
                    victim = args[0]
                else:
                    victim = message.mentions[0].id
                with open("logs/{}.txt".format(victim), encoding="utf-8") as f:
                    text = f.read()
                text_model = markovify.NewlineText(text)
                speech = "**{}:**\n".format(message.author.name)
                for i in range(3):
                    try:
                        variablename = text_model.make_short_sentence(140, state_size=3).replace("@", "@ ")
                        print(variablename)
                        try:
                            id_mention = re.search("<@ [!]?(.*)>", variablename)
                            print(id_mention)
                            id_mention = id_mention.group(1)
                            print(id_mention)
                            id_name = self.get_server("207943928018632705").get_member(str(id_mention)).name
                            print("id name = {}".format(id_name))
                            add_this = re.sub("<@ [!]?.*>", id_name, variablename)
                            print(add_this)
                            speech += "{}\n\n".format(add_this)
                        except AttributeError:
                            print("Attributeerror xd")
                            speech += "{}\n\n".format(variablename)
                    except KeyError:
                        return
                    except AttributeError:
                        pass
                        #speech += "Sentence couldn't be formed ¯\_(ツ)_/¯."
                if message.channel != self.get_channel("240315894385868801"):
                    await self.delete_message(message)
                    msg = await self.send_message(discord.Object(id="240315894385868801"), "<@{}>".format(message.author.id))
                    await self.delete_message(msg)
                await self.send_message(discord.Object(id="240315894385868801"), speech)
                
            elif command == 'sicklad':
                #if message.author.id != CARL_DISCORD_ID:
                #    return
                if len(args) == 0:
                    await self.send_message(message.channel, "You sure are.")
                elif args[0].lower() in ['leaderboard', 'leaderboards', 'top', 'highscore', 'highscores', 'hiscores']:
                    ladboard = self.sicklad
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
                    post_this += "**{0}** !sicklads in total spread across **{1}** sick lads.".format(sum(self.sicklad.values()),len(self.sicklad))
                    await self.send_message(message.channel, post_this)
                if message.mentions[0].id == message.author.id:
                    await self.send_message(message.channel, "You can't call yourself a sick lad, what the h*ck")
                try:
                    userID = ''.join(message.mentions[0].id)
                    userID = re.sub("[^0-9]", "", userID)
                    if userID == '':
                        return
                    elif userID not in self.sicklad:
                        self.sicklad[userID] = 1
                        write_json('sicklad.json', self.sicklad)
                        await self.send_message(message.channel, "Welcome to the sicklad club, {0}".format(message.mentions[0].display_name))
                    else:
                        if len(args) == 1:
                            self.sicklad[userID] += 1
                            write_json('sicklad.json', self.sicklad)
                            await self.send_message(message.channel, "{0} thinks {1} is a sick lad, {1} is now a lvl {2} sicklad.".format(message.author.name.replace("_", "\_"), message.mentions[0].name.replace("_", "\_"), self.sicklad[userID]))
                        else:
                            reason = ' '.join(args[1:])
                            self.sicklad[userID] += 1
                            write_json('sicklad.json', self.sicklad)
                            await self.send_message(message.channel, "{0} thinks {1} is a sick lad, reason: `{2}`\n{1} is now a lvl {3} sicklad.".format(message.author.name.replace("_", "\_"), message.mentions[0].name.replace("_", "\_"), reason, self.sicklad[userID]))
                except IndexError:
                    return
                except UnboundLocalError:
                    return
                except discord.HTTPException:
                    return
            elif command == '8ball':
                await self.send_message(message.channel, (responses[random.randint(0, 19)]))
            
            elif command in ['crossthestreams', 'cts']:
                stream = " {1}\u3000{0}\n   {1}{0}\n\u3000 {0}\n   {0}{1}\n {0}\u3000{1}\n{0}\u3000\u3000{1}\n{0}\u3000\u3000{1}\n {0}\u3000{1}\n  {0} {1}\n\u3000  {1}\n\u3000{1} {0}\n {1}\u3000 {0}\n{1}\u3000\u3000{0}\n{1}   \u3000 {0}\n {1}\u3000  {0}\n\u3000{1}{0}\n     {0}{1}\n  {0}    {1}"
                if len(args) == 0:
                    whale = "<:Whale:239954158772289537>"
                    cookie = ":cookie:"
                elif len(args) == 1:
                    whale = "<:Whale:239954158772289537>"
                    cookie = str(args[0])
                    print(args[0])
                elif len(args) == 2:
                    whale = str(args[0])
                    cookie = str(args[1])
                else:
                    return
                await self.send_message(message.channel, stream.format(whale, cookie))
            elif command == 'uptime':
                uptime = str(timedelta(seconds=((time.time() + 3600) - starttime)))
                uptime = re.sub("\.(.*)", "", uptime)
                currtime = time.strftime("%H:%M:%S", time.gmtime(time.time() + 3600))
                started_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(starttime))
                em = discord.Embed(title="Local time", description=currtime, colour=0x14e818)
                em.set_author(name=self.user.name, icon_url=self.user.avatar_url)
                em.add_field(name="Current uptime", value=uptime, inline=True)
                em.add_field(name="Start time", value=started_time, inline=True)
                await self.send_message(message.channel, embed=em)

            elif command == 'wcl':
                if len(args) == 3:
                    try:
                        charname, realm, region = args[0], args[1], args[2]
                        print(charname, realm, region)
                        r = requests.get('https://www.warcraftlogs.com:443/v1/rankings/character/'+charname+'/'+realm+'/'+region+'?metric=dps&api_key=a574df48a822ce7117aa29a901613025')
                        r_json = r.json()
                        #djcar = r_json.values()
                        print(r_json)
                        uglystring = "__**Parses for {} {}-{}**__\n\n".format(charname, realm, region)
                        tempstring = ""
                        powerlevel = 0
                        for i in range(len(r_json)):
                            diff = {3:'N', 4:'H', 5:'M'}
                            bosses = {
                                1853: 'Nythendra',
                                1873: 'Il\'gynoth',
                                1876: 'Elerethe Renferal',
                                1841: 'Ursoc',
                                1854: 'Dragons of Nightmare',
                                1877: 'Cenarius',
                                1864: 'Xavius',
                                1958: 'Odyn',
                                1962: 'Guarm',
                                2008: 'Helya'
                            }
                            boss = r_json[i]['encounter']
                            difficulty = r_json[i]['difficulty']
                            rank = r_json[i]['rank']
                            outOf = r_json[i]['outOf']
                            w_class = r_json[i]['class']
                            spec = r_json[i]['spec']
                            w_spec = load_json('specs.json')
                            percentile = 100 - (100 * (rank/outOf))
                            dps = r_json[i]['total']
                            wclshit = ("{0}  -  {1} **{2:.0f}%** ({3:,} dps, _rank {4}/{5}_) as {6}\n".format(diff[difficulty], bosses[boss], percentile, dps, rank, outOf, w_spec[str(w_class)]))
                            #if bosses[boss] in uglystring:
                            #    print("teehee")
                            if difficulty == 5:
                                uglystring += wclshit
                            elif difficulty == 4:
                                uglystring += wclshit
                        print(uglystring)
                        await self.send_message(message.channel, uglystring)
                    except ValueError:
                        print("keyerror")
                        return
            elif command == 'pickmyspec':
                await self.send_message(message.channel, random.choice(WOW_SPECS))
            elif command == 'pickmyclass':
                await self.send_message(message.channel, random.choice(WOW_CLASSES))
            elif command in  ['aesthetics', 'aesthetic', 'ae']:
                #if message.author.id != CARL_DISCORD_ID:
                #    return
                hehe = aesthetics(message.clean_content[len(command) + 2:])
                await self.send_message(message.channel, hehe)
            elif command == 'timer':
                print("len of args: {}\n".format(len(args)))
                try:
                    if args[0].isdigit() and len(args) == 1:
                        print("isdigittriggered" + args[0])
                        duration = int(args[0])
                        timeUnit = "second"
                        timePrint = duration
                        firstUnit = None
                    #elif len(args) == 1:
                    #    a, b, firstDuration, firstUnit, cuntflaps = re.split("((\d+) ?([(h|m)])) ?((\d+) ?(m))? .*?", message.content)
                    else:
                        print("At least this triggerd")
                        a, b, firstDuration, firstUnit, cuntflaps, secondDuration, secondUnit, g = re.split("((\d+) ?([(h|m)])) ?((\d+) ?(m))?.*?", message.content)
                        print("a = {}, b = {}, firstDuration = {}, firstUnit = {}, cuntflaps = {}, secondDuration = {}, secondUnit = {}, g = {}".format(a, b, firstDuration, firstUnit, cuntflaps, secondDuration, secondUnit, g))
                        extratime = 0
                        print("len of args was >=2")
                        duration = int(firstDuration)
                        if firstUnit in ['m', 'min', 'minute', 'minutes']:
                            print("firstUnit in m min minutes")
                            duration = duration * 60
                            timeUnit = "minute"
                            timePrint = duration / 60
                        elif firstUnit in ['h', 'hour', 'hours']:
                            duration = duration * 3600
                            try:
                                if secondUnit in ['m', 'min', 'minute', 'minutes']:
                                    printme = re.sub("((\d)+ ?(h|hour|hours|m|min|minute|minutes)) ?((\d)+ ?(m|min|minute|minutes))? .*?", "", message.content[7:])
                                    print(printme)
                                    extratime = int(secondDuration)
                                    timeUnit = "hour, {}-minute".format(extratime)
                                    timePrint = duration / 3600
                                else:
                                    print("timeUnit = \"hour\"", secondDuration)
                                    timeUnit = "hour"
                                    timePrint = duration / 3600
                            except IndexError:
                                timeUnit = "hour"
                                timePrint = duration / 3600
                        else:
                            timePrint = duration
                            timeUnit = "second"
                        #if len(args) >= 3:

                    if duration < 86453301:
                        print("len of args: {}\n".format(len(args)))
                        if len(args) == 1:
                            await self.send_message(message.channel, "{0:.0f}-{1} timer started.".format(timePrint, timeUnit))
                            await asyncio.sleep(duration)
                            await self.send_message(message.channel, "{} beep bop (how do timers talk?)".format(message.author.mention))
                        #elif len(args) == 2 and firstUnit in ['m', 'min', 'minute', 'minutes','h', 'hour', 'hours']:
                        #    await self.send_message(message.channel, "{0:.0f}-{1} timer started.".format(timePrint, timeUnit))
                        #    await asyncio.sleep(duration)
                        #    await self.send_message(message.channel, "{} beep-- bop (how do timers talk?)".format(message.author.mention))
                        elif len(args) >= 2 and firstUnit in ['m', 'min', 'minute', 'minutes','h', 'hour', 'hours']:
                            printme = re.sub("((\d)+ ?(h|hour|hours|m|min|minute|minutes)) ?((\d)+ ?(m|min|minute|minutes))? .*?", "", message.content[7:])
                            print(printme)
                            try:
                                if secondUnit in ['m', 'min', 'minute', 'minutes'] and len(args) >= 4:
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
                            await self.send_message(message.channel, "{} beepfsdfsdfbop\n`{}`".format(message.author.mention, message.content[7+len(args[0]):]))
                    else:
                        return
                except ValueError or KeyError:
                    return
            
            elif command in ['info', 'i']:
                if message.mentions:
                    user = message.mentions[0]
                else:
                    user = message.author
                try:
                    retard = "{}\nrank {}".format(self.retard[user.id], (sorted(self.retard, key=self.retard.get, reverse=True).index(user.id)+1))
                except KeyError:
                    retard = 0
                try:
                    sicklad = "{}\nrank {}".format(self.sicklad[user.id], (sorted(self.sicklad, key=self.sicklad.get, reverse=True).index(user.id)+1))
                except KeyError:
                    sicklad = 0
                try:
                    postcount = "{}\nrank {}".format(self.postcount[user.id], (sorted(self.postcount, key=self.postcount.get, reverse=True).index(user.id)+1))
                except KeyError:
                    postcount = "0 or bot"
                try:
                    joined_at = user.joined_at
                    days_since = "({} days ago)".format((datetime.today() - user.joined_at).days)
                except:
                    joined_at = "User somehow doesn't have a join date.'"
                    days_since = ""
                try:
                    days_since_creation = "({} days ago)".format((datetime.today() - user.created_at).days)
                except Exception as e:
                    print(e)
                    days_since_creation = ""
                try:
                    bio = self.bio[user.id]
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
                
                
                usercolor = message.server.get_member(user.id).colour
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
                em.add_field(name="Joined at", value="{} {}".format(joined_at.replace(" ", "\n"), days_since), inline=True)
                await self.send_message(message.channel, embed=em)
            elif command == 'postcount':
                user = message.author
                if len(args) == 0:
                    await self.send_message(message.channel, "**{0}** posts by **{1}** chatters.".format(sum(self.postcount.values()), len(self.postcount)))
                elif len(args) == 1:
                    post_this = ""
                    if message.mentions:
                        user = message.mentions[0]
                        await self.send_message(message.channel, "{0} has posted {1} messages.".format(user.display_name, self.postcount[user.id]))
                    elif args[0].lower() in ['leaderboard', 'leaderboards', 'top', 'highscore', 'highscores', 'hiscores']:
                        leaderboard = self.postcount
                        post_this = ""
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
                        post_this += "\n**{0}** posts by **{1}** chatters.".format(sum(self.postcount.values()), len(self.postcount))
                        em = discord.Embed(title="Current standings:", description=post_this, colour=0x14e818)
                        em.set_author(name=self.user.name, icon_url=self.user.avatar_url)
                        await self.send_message(message.channel, embed=em)
                else:
                    return
            
            elif command == 'd':
                #if message.author.id != CARL_DISCORD_ID:
                #    return
                language = 'en'
                definitions = {}
                try:
                    url = 'https://od-api.oxforddictionaries.com/api/v1/entries/' + language + '/' + message.content[3:].lower()
                    r = requests.get(url, headers = {'app_id': app_id, 'app_key': app_key})
                    jsonthing = r.json()
                    print(jsonthing)
                    
                    wordname = message.content[3:].capitalize()
                    pronounciation = jsonthing["results"][0]["lexicalEntries"][0]["pronunciations"][0]["phoneticSpelling"]
                    user = message.author
                    usercolor = message.server.get_member(user.id).colour
                    em = discord.Embed(title=wordname, description="/{}/".format(pronounciation), colour=usercolor)
                    em.set_author(name=user.display_name, icon_url=user.avatar_url, url=user.avatar_url)
                    x = jsonthing["results"][0]["lexicalEntries"]
                    xd = 1
                    for i in x:
                        print(i)
                        f = 0
                        #for sd in range(3):
                        word_type = jsonthing["results"][0]["lexicalEntries"][f]["lexicalCategory"]
                        print("this is the word type: " + word_type)
                        try:
                            
                            d = jsonthing["results"][0]["lexicalEntries"][f]["entries"][0]["senses"][0]["definitions"]
                            d = ''.join(d)
                            definition = "{}. {}\n".format(xd, ''.join(i["entries"][0]["senses"][0]["definitions"]))
                            try:
                                definitions[word_type] += definition
                            except KeyError:
                                definitions[word_type] = definition
                            xd += 1
                            f += 1
                        except IndexError:
                            pass
                except Exception as e:
                    await self.send_message(message.channel, e)
                    return
                for box in definitions:
                    em.add_field(name=box, value=definitions[box], inline=False)
                print(definitions)
                await self.send_message(message.channel, embed=em)
            elif command == 'convert':
                try:
                    if len(args) == 0:
                        await self.send_message(message.channel, "**Usage:** !convert <amount> <currency> <base currency(optional)>\nbase currency is USD by default, type !convert rates for all rates.")
                    elif args[0].isdigit() and len(args) == 1:
                        centiToFeet, centiToInch, feetToCm, inchToCm = converter(args[0])
                        await self.send_message(message.channel, "{0}cm = {1}'{2:.2f}\"\n{0}ft = {3:.2f}cm\n{0}in = {4:.2f}cm".format(args[0], centiToFeet, centiToInch, feetToCm, inchToCm))
                        return
                    elif args[0] == 'rates':
                        mm = requests.get("http://api.fixer.io/latest?base=USD")
                        mm = mm.json()
                        mm = mm['rates']
                        moneystring = 'All rates are compared to the dollar\n'
                        for i in sorted(mm, key=mm.get):
                            moneystring += i+" = "+str(mm[i])+"\n"
                        await self.send_message(message.channel, moneystring)
                    elif len(args) >= 2:
                        amount = args[0]
                        currency = args[1].upper()
                        if len(args) == 3:    
                            base_currency = args[2].upper()
                        else:
                            base_currency = 'USD'
                    m = requests.get("http://api.fixer.io/latest?base="+base_currency)
                    m = m.json()
                    rate_return = float(amount) / m['rates'][currency]
                    await self.send_message(message.channel, "**{0:,.2f} {1}** is equal to **{2:,.2f} {3}**".format(float(amount), currency, rate_return, base_currency))
                except KeyError:
                    print("Convert KeyError")
                    return
            
            elif command == 'help':
                if len(args) == 0:
                    user = message.author
                    em_before = discord.Embed(title="Help", description="Processing command...", colour=0x42f4dc)
                    em_before.set_author(name=user.name, icon_url=user.avatar_url)
                    em_after = discord.Embed(title="Success", description="Check your direct messages.", colour=0x14e818)
                    em_after.set_author(name=user.name, icon_url=user.avatar_url)
                    xd = await self.send_message(message.channel, embed=em_before)
                    await asyncio.sleep(0.1)
                    await self.send_message(message.author, HELP_MESSAGE1)
                    await self.send_message(message.author, HELP_MESSAGE2)
                    await self.edit_message(xd, embed=em_after)
                else:
                    return
            elif command == 'lvl':
                try:
                    lvl1 = int(args[0])
                    lvl2 = int(args[1])
                    if lvl1 >= 100 or lvl2 >= 100:
                        return
                    elif lvl1 < 1 or lvl2 < 1:
                        return
                    else:
                        await self.send_message(message.channel, "Difference in xp between level **{}** and **{}** is **{:,}**".format(lvl1, lvl2, abs(RUNESCAPE_LEVELS[lvl1-1] - RUNESCAPE_LEVELS[lvl2-1])))
                except ValueError:
                    return
            elif command == 'g':
                if message.author.id in self.blacklist:
                    await self.send_message(message.channel, "{} is blacklisted from the google command, wonder why".format(message.author.name))
                    return
                user = message.author
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
                await self.send_message(message.channel, embed=em)
            elif command == "ping":
                await self.send_message(message.channel, "pong!")
            elif command in ["date","current_year", "time"]:
                await self.send_message(message.channel, "It's {0}".format(time.strftime("%Y-%m-%d\n%H:%M:%S (central carl time).")))
            else:
                tagname = re.sub("[^a-z0-9_-]", "", command)
                if tagname in self.tags:
                    await self.send_message(message.channel, self.tags[tagname])
                else:
                    return
        elif "carl" in message.content.lower():
            insensitive_carl = re.compile(re.escape('carl'), re.IGNORECASE)
            xd = await self.send_message(discord.Object(id="213720502219440128"), "<@106429844627169280>, you were mentioned!")
            await self.delete_message(xd)
            postme = insensitive_carl.sub('**__Carl__**', message.clean_content)
            await self.send_message(discord.Object(id="213720502219440128"), "**{}** in **#{}**:\n{}".format(message.author.display_name, message.channel.name, postme))
        try:
            self.postcount[message.author.id] += 1
            write_json('postcount.json', self.postcount)
        except KeyError:
            self.postcount[message.author.id] = 1
            write_json('postcount.json', self.postcount)
        except IndexError:
            self.postcount[message.author.id] = 1
            write_json('postcount.json', self.postcount)
        else:
            await self.log(message)
            return

if __name__ == '__main__':
        bot = CarlBot()
        bot.run(token)
