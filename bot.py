import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding=sys.stdout.encoding, errors="backslashreplace", line_buffering=True)
import json
import asyncio
import discord
import random
import math
import time
import requests
import statistics
import re
from googleapiclient.discovery import build
from responses import *
from sensitivedata import *
import datetime
import markovify

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
    # noinspection PyMethodOverriding
    def run(self):
        loop = asyncio.get_event_loop()
        try:
            loop.create_task(self.log_on())
            loop.run_until_complete(self.start(self.token))
            loop.run_until_complete(self.connect())
        except Exception:
            loop.run_until_complete(self.close())
            pending = asyncio.Task.all_tasks()
            gathered = asyncio.gather(*pending)
            try:
                gathered.cancel()
                loop.run_forever()
                gathered.exception()
            except:
                pass
        finally:
            loop.close()

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


    async def log_on(self):
        await client.start(self.token)

    async def timed_message(self, channel, ogmsg, message_content):
        timedmsg = await self.send_message(channel, message_content)
        await asyncio.sleep(1200)
        await self.delete_message(ogmsg)
        await self.delete_message(timedmsg)

    async def say_message(self, channel, ogmsg, message_content):
        timedmsg = await self.send_message(channel, message_content)
        await self.delete_message(ogmsg)

    async def on_member_join(self, member):
        await self.send_message(discord.Object(id='249336368067510272'), "**{}** Joined the server at `{}`<@{}>".format(member.name, time.strftime("%Y-%m-%d %H:%M:%S (central carl time)."), CARL_DISCORD_ID))
    async def on_member_remove(self, member):
        await self.send_message(discord.Object(id='249336368067510272'), "**{}** left the server at `{}`<@{}>".format(member.name, time.strftime("%Y-%m-%d %H:%M:%S (central carl time)."), CARL_DISCORD_ID))
    async def on_message_delete(self, message):
        #if message.author.id != CARL_DISCORD_ID:
        #    return
        if message.channel.is_private:
            return
        if message.author.id == self.user.id:
            return
        if message.content.startswith(self.prefix):
            return
        await self.send_message(discord.Object(id='249336368067510272'), "**{}** Deleted their message at {} ```{}``` in `{}`".format(message.author.name, time.strftime("%Y-%m-%d %H:%M:%S (central carl time)."), message.content, message.channel))

    async def on_message_edit(self, before, after):
        if before.channel.is_private:
            return
        if before.content == after.content:
            return
        if before.author.id == self.user.id:
            return
        await self.send_message(discord.Object(id='249336368067510272'), "at {}, **{}** edited their message from `{}` to `{}`".format(time.strftime("%Y-%m-%d %H:%M:%S (central carl time)."), before.author.name, before.content, after.content))


    async def log(self, message):
        with open("logs/{}.txt".format(message.author.id), "a", encoding="utf-8") as f:
            f.write("{}\n".format(message.content))

    async def on_message(self, message):
        if message.author == self.user:
            return
        if message.channel.is_private:
            print(message.content + " [author: {}]".format(message.author))
            return
        if "@everyone" in message.content:
            print("at everyone in sdmasoidj")
            return
        if random.randint(1, 10000) == 1:
            legendaryRole = discord.utils.get(message.server.roles, name='Legendary')
            await self.add_roles(message.author, legendaryRole)
            await self.send_message(message.channel, "{} just received a legendary item: **{}**".format(message.author.mention, random.choice(legendaries)))
        if message.author.id in self.blacklist:
            for mention in message.mentions:
                if mention.id == CARL_DISCORD_ID:
                    await self.delete_message(message)
                    await self.send_message(message.channel, "fuck off, {}".format(message.author.name))
                    return
        try:
            self.postcount[message.author.id] += 1
            write_json('postcount.json', self.postcount)
        except KeyError:
            self.postcount[message.author.id] = 1
            write_json('postcount.json', self.postcount)
        except IndexError:
            self.postcount[message.author.id] = 1
            write_json('postcount.json', self.postcount)
        if message.content.startswith(self.prefix):
            if message.author.id in self.blacklist:
                return
            msg = message.content[1:]
            command, *args = msg.split()
            command = command.lower()
            print(command)
            if command == 'say':
                await self.say_message(message.channel, message, "{}".format(message.content[5:]))
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
                    await self.timed_message(message.channel, message, "Not even a number")
            elif command == 'ban':
                if message.author.id == CARL_DISCORD_ID:
                    if message.mentions[0] == self.user:
                        await self.timed_message(message.channel, message, "I'm sorry, Carl. I'm afraid I can't do that.")
                    else:
                        await self.timed_message(message.channel, message, "banned user {}.".format(args[0]))
                else:
                    await self.timed_message(message.channel, message, "Nope")
            elif command in ['weather', 'temp', 'temperature', 'temp']:
                if len(args) == 0:
                    await self.timed_message(message.channel, message, "Parameters: city name and country code (optional) divided by comma, use ISO 3166 country codes")
                city = ' '.join(args)
                r = requests.get('http://api.openweathermap.org/data/2.5/weather?q='+city+weatherkey)
                json_object = r.json()
                temp_k = float(json_object['main']['temp'])
                temp_c = temp_k - 273.15
                temp_f = temp_c * (9/5) + 32
                try:
                    city = int(city)
                    CtoF = city * (9/5) + 32
                    FtoC = (city - 32) * (5/9)
                    await self.timed_message(message.channel, message, "{0}°C is {1:.1f}°F\n{0}°F is {2:.1f}°C".format(city, CtoF, FtoC))
                except ValueError:
                    city, country, weather = json_object['name'],json_object['sys']['country'], json_object['weather'][0]['description']
                    await self.timed_message(message.channel, message, "Weather in {0}, {1}: {2:.1f}°C/{3:.1f}°F, {4}.".format(city, country, temp_c, temp_f, weather))
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
                    await self.timed_message(message.channel, message, 
                    "You rolled {0} {1}-sided dice, results:{2}\nMedian:{3}, mean:{4:.2f}".format(rolls, sides, results, median, mean))
                except discord.HTTPException:
                    return
                except ValueError:
                    return
            elif command in ['eu', 'na']:
                euRole = discord.utils.get(message.server.roles, name='EU')
                naRole = discord.utils.get(message.server.roles, name='NA')
                if command == 'eu':
                    await self.add_roles(message.author, euRole)
                else:
                    await self.add_roles(message.author, naRole)
            elif command in ['choice', 'choose']:
                if len(args) == 0:
                    return
                choices = args
                choices = ' '.join(choices)
                choices = choices.split(",")
                await self.timed_message(message.channel, message, random.choice(choices))
            elif command == 'id':
                listofid = ''
                for mention in message.mentions:
                    listofid += mention.name+": "+mention.id+"\n"
                await self.timed_message(message.channel, message,
                 "Server ID: {}\nChannel ID: {}\n`{}`".format(message.server.id, message.channel.id, listofid))
            elif command == 'tag':
                if message.mentions != []:
                    return
                tagreturn = ' '.join(args[2:])
                taglist = self.tags
                if args[0] == 'list':
                    d = ', '.join(sorted(list(self.tags.keys())))
                    await self.send_message(message.author, d)
                elif args[0] == "+=":
                    tagname = re.sub("[^a-z0-9_-]", "", args[1].lower())
                    content = message.content[(9+len(args[1])):]
                    if (len(content) + len(self.tags[tagname])) < 2000:
                        try:
                            self.tags[tagname] += "\n{}".format(content)
                        except KeyError:
                            self.tags[tagname] = "{}".format(content)
                        write_json('taglist.json', self.tags)
                        await self.send_message(message.channel, "\"{}\" was appended to the tag: {}".format(content, tagname))
                    else:
                        await self.send_message(message.channel, "that would make the tag too big, retard.")
                elif args[0] in ['+', 'add']:
                    if len(args) <= 2:
                        await self.timed_message(message.channel, message, "<:FailFish:235926308071276555>")
                        return
                    if args[2] == 'list':
                        return
                    if message.author.id == CARL_DISCORD_ID:
                        tagname = re.sub("[^a-z0-9_-]", "", args[1].lower())
                        if tagname == '':
                            return
                        self.tags[tagname] = message.content[(7+len(args[1])):]
                        write_json('taglist.json', self.tags)
                        await self.timed_message(message.channel, message, "tag `{0}` added".format(tagname))
                    elif len(message.content) < 1500:
                        tagname = re.sub("[^a-z0-9_-]", "", args[1].lower())
                        if tagname == '':
                            return
                        self.tags[tagname] = message.content[(7+len(args[1])):]
                        write_json('taglist.json', self.tags)
                        await self.timed_message(message.channel, message, "tag `{0}` added".format(tagname))
                    else:
                        await self.timed_message(message.channel, message, "too long <:gachiGASM:234404899511599104>")
                elif args[0] in ['-', 'del']:
                    tagname = args[1]
                    if tagname in taglist:
                        del taglist[tagname]
                        write_json('taglist.json', self.tags)
                        await self.timed_message(message.channel, message, "tag `{0}` deleted".format(tagname))
                    else:
                        await self.timed_message(message.channel, message, "tag `{0}` not found".format(tagname))
                else:
                    tagname = args[0].lower()
                    if tagname in self.tags:
                        await self.timed_message(message.channel, message, self.tags[tagname])
                    else:
                        await self.timed_message(message.channel, message, "No such tag")
            elif command == 'm':
                if message.author.id == CARL_DISCORD_ID:
                    await self.send_message(message.channel, "{}".format(eval(message.content[3:])))
            elif command == 'retard':
                if len(args) == 0:
                    await self.timed_message(message.channel, message, "You sure are.")
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
                    await self.timed_message(message.channel, message, post_this)
                try:
                    userID = ''.join(message.mentions[0].id)
                    userID = re.sub("[^0-9]", "", userID)
                    if userID == '':
                        return
                    elif userID not in self.retard:
                        self.retard[userID] = 1
                        write_json('retard.json', self.retard)
                        await self.timed_message(message.channel, message, "Welcome to the retard club, {0}".format(args[0]))
                    else:
                        if len(args) == 1:
                            self.retard[userID] += 1
                            write_json('retard.json', self.retard)
                            await self.timed_message(message.channel, message, "{0} just tipped {1} 1 retard coin, {1} now has {2} coins.".format(message.author.name.replace("_", "\_"), message.mentions[0].name.replace("_", "\_"), self.retard[userID]))
                        else:
                            reason = ' '.join(args[1:])
                            self.retard[userID] += 1
                            write_json('retard.json', self.retard)
                            await self.timed_message(message.channel, message, "{0} just tipped {1} 1 retard coin, reason: `{2}`\n{1} now has {3} coins.".format(message.author.name.replace("_", "\_"), message.mentions[0].name.replace("_", "\_"), reason, self.retard[userID]))
                except IndexError:
                    return
                except UnboundLocalError:
                    return
                except discord.HTTPException:
                    return
            elif command == 'sc':
                smallcaps_string = smallcaps(message.content[4:])
                await self.send_message(message.channel, smallcaps_string)
            elif command == 'bl':
                if message.author.id != CARL_DISCORD_ID:
                    return
                if message.mentions == []:
                    return
                if args[0] in ['+', 'add']:
                    self.blacklist[message.mentions[0].id] = message.mentions[0].name
                    write_json('blacklist.json', self.blacklist)
                    await self.send_message(discord.Object(id='249336368067510272'), "{} is now blacklisted.".format(message.mentions[0].name))
                elif args[0] in ['-', 'del']:
                    if message.mentions[0].id in self.blacklist:
                        del self.blacklist[message.mentions[0].id]
                        write_json('blacklist.json', self.blacklist)
                        await self.send_message(discord.Object(id='249336368067510272'), "{} is no longer blacklisted.".format(message.mentions[0].name))
            elif command == 'wl':
                if message.author.id != CARL_DISCORD_ID:
                    return
                if message.mentions == []:
                    return
                if args[0] in ['+', 'add']:
                    self.whitelist[message.mentions[0].id] = message.mentions[0].id
                    write_json('whitelist.json', self.whitelist)
                    await self.send_message(discord.Object(id='249336368067510272'), "{} is now whitelisted.".format(message.mentions[0].name))
                elif args[0] in ['-', 'del']:
                    if message.mentions[0] in self.whitelist:
                        del self.whitelist[message.mentions[0].id]
                        write_json('whitelist.json', self.whitelist)
                        await self.send_message(discord.Object(id='249336368067510272'), "{} is no longer whitelisted.".format(message.mentions[0].name))
            elif command == 'asdban':
                if message.author.id == CARL_DISCORD_ID or message.author.id in self.whitelist:
                    bannedusers = ''
                    i = 0
                    for mention in message.mentions:
                        await self.ban(mention)
                        bannedusers += "{}, ".format(message.mentions[i].name)
                        i += 1
                    await self.send_message(message.channel, "{} Just banned {}".format(message.author, bannedusers))
            elif command == 'r':
                score = 100 * self.retard[message.mentions[0].id]/self.postcount[message.mentions[0].id]
                #if message.author.id != CARL_DISCORD_ID:
                #    return
                if len(args) == 0:
                    await self.timed_message(message.channel, message, "You sure are.")
                elif args[0].lower() in ['leaderboard', 'leaderboards', 'top', 'highscore', 'highscores', 'hiscores']:
                    leaderboard = self.retard
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
                    post_this += "**{0}** coins in total spread across **{1}** retards.".format(sum(self.retard.values()),len(self.retard))
                    await self.timed_message(message.channel, message, post_this)
                try:
                    userID = ''.join(message.mentions[0].id)
                    userID = re.sub("[^0-9]", "", userID)
                    if userID == '':
                        return
                    elif userID not in self.retard:
                        await self.timed_message(message.channel, message, "{} has either not posted or been called a retard, please fix this.".format(message.mentions[0].name))
                    else:
                        await self.timed_message(message.channel, message, "{} has a retard score of {:.3f}, {}".format(message.mentions[0].name, score, snark(score)))
                except ValueError:
                    print("ValueError")
                    return
            elif command == 'bio':
                #if message.author.id != CARL_DISCORD_ID:
                #    return
                if "@" in msg[:10]:
                    try:
                        xdd = ''.join(args[0])
                        namedude = re.sub("[^0-9]", "", xdd)
                        print(namedude)
                        await self.timed_message(message.channel, message, "Bio for {0}:\n{1}".format(message.mentions[0], self.bio[namedude]))
                    except KeyError:
                        print("bio Keyerror triggered")
                        return
                try:
                    if args[0] == '+':
                        bioreturn = ' '.join(args)
                        #namedude = ''.join(args[0][1:-1])
                        print("message == mentions", bioreturn)
                        if len(args) == 1:
                            await self.timed_message(message.channel, message, "Empty bio <:FailFish:235926308071276555>")
                        if message.author.id in ['158370770068701184', CARL_DISCORD_ID]:
                            print(args[1:])
                            self.bio[message.author.id] = message.content[7:]
                            write_json('bio.json', self.bio)
                            await self.timed_message(message.channel, message, "bio `{0}` updated.".format(message.author))
                        elif len(message.content) < 1500:
                            self.bio[message.author.id] = message.content[7:]
                            write_json('bio.json', self.bio)
                            await self.timed_message(message.channel, message, "bio `{0}` added".format(message.author))
                        else:
                            await self.timed_message(message.channel, message, "too long <:gachiGASM:234404899511599104>")
                    elif args[0] == "+=":
                        if (len(message.content[8:]) + len(self.bio[message.author.id])) < 2000:
                            try:
                                self.bio[message.author.id] += "\n{}".format(message.content[8:])
                            except KeyError:
                                self.bio[message.author.id] = "{}".format(message.content[8:])
                            write_json('bio.json', self.bio)
                            await self.send_message(message.channel, "`{0}` was appended to {1.name}'s bio.".format(message.content[8:], message.author))
                        else:
                            await self.send_message(message.channel, "Too long")
                except IndexError:
                    bioname = message.author.id
                    print(bioname)
                    if bioname in self.bio:
                        print("hey, what the fuck")
                        await self.timed_message(message.channel, message, "Bio for {0}:\n{1}".format(message.author,self.bio[bioname]))
                    else:
                        print(bioname)
                        await self.timed_message(message.channel, message, "User has not set a bio\nTo set a bio use `!bio +`, no mention required")

            elif command == 'speak':
                if message.mentions == []:
                    victim = message.author.id
                else:
                    victim = message.mentions[0].id
                with open("logs/{}.txt".format(victim), encoding="utf-8") as f:
                    text = f.read()
                text_model = markovify.NewlineText(text)
                speech = ""
                for i in range(3):
                    try:
                        variablename = text_model.make_short_sentence(140).replace("@", "@ ")
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
                await self.send_message(message.channel, speech)
                
            elif command == 'sicklad':
                #if message.author.id != CARL_DISCORD_ID:
                #    return
                if len(args) == 0:
                    await self.timed_message(message.channel, message, "You sure are.")
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
                    await self.timed_message(message.channel, message, post_this)
                if message.mentions[0].id == message.author.id:
                    await self.timed_message(message.channel, message, "You can't call yourself a sick lad, what the h*ck")
                try:
                    userID = ''.join(message.mentions[0].id)
                    userID = re.sub("[^0-9]", "", userID)
                    if userID == '':
                        return
                    elif userID not in self.sicklad:
                        self.sicklad[userID] = 1
                        write_json('sicklad.json', self.sicklad)
                        await self.timed_message(message.channel, message, "Welcome to the sicklad club, {0}".format(args[0]))
                    else:
                        if len(args) == 1:
                            self.sicklad[userID] += 1
                            write_json('sicklad.json', self.sicklad)
                            await self.timed_message(message.channel, message, "{0} thinks {1} is a sick lad, {1} is now a lvl {2} sicklad.".format(message.author.name.replace("_", "\_"), message.mentions[0].name.replace("_", "\_"), self.sicklad[userID]))
                        else:
                            reason = ' '.join(args[1:])
                            self.sicklad[userID] += 1
                            write_json('sicklad.json', self.sicklad)
                            await self.timed_message(message.channel, message, "{0} thinks {1} is a sick lad, reason: `{2}`\n{1} is now a lvl {3} sicklad.".format(message.author.name.replace("_", "\_"), message.mentions[0].name.replace("_", "\_"), reason, self.sicklad[userID]))
                except IndexError:
                    return
                except UnboundLocalError:
                    return
                except discord.HTTPException:
                    return
            elif command == '8ball':
                await self.timed_message(message.channel, message, (responses[random.randint(0, 19)]))
            elif command == 'uptime':
                uptime = str(datetime.timedelta(seconds=((time.time() + 3600) - starttime)))
                uptime = re.sub("\.(.*)", "", uptime)
                currtime = time.strftime("%H:%M:%S", time.gmtime(time.time() + 3600))
                started_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(starttime))
                em = discord.Embed(title="Local time", description=currtime, colour=0x14e818)
                em.set_author(name=self.user.name, icon_url=self.user.avatar_url)
                em.add_field(name="Current uptime", value=uptime, inline=True)
                em.add_field(name="Starttime", value=started_time, inline=True)
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
                        await self.timed_message(message.channel, message, uglystring)
                    except ValueError:
                        print("keyerror")
                        return
            elif command == 'pickmyspec':
                await self.timed_message(message.channel, message, random.choice(WOW_SPECS))
            elif command == 'pickmyclass':
                await self.timed_message(message.channel, message, random.choice(WOW_CLASSES))
            elif command == 'aesthetics':
                #if message.author.id != CARL_DISCORD_ID:
                #    return
                hehe = aesthetics(message.content[12:])
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
            elif command == 'song':
                r = requests.get("http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=Callemang&api_key=613742fffe14cf67af284701926fa1ae&format=json")
                r = r.json()
                lastArtist = r["recenttracks"]["track"][0]["artist"]["#text"]
                lastTrack = r["recenttracks"]["track"][0]["name"]
                lastAlbum = r["recenttracks"]["track"][0]["album"]["#text"]
                #timeSince = r["recenttracks"]["track"][0]["@attr"]["nowplaying"]
                #if timeSince == 'true':
                #    timeSince = "Playing right now:"
                await self.timed_message(message.channel, message, ("{0} - {1}".format(lastArtist, lastTrack)))
            elif command in ['info', 'i']:
                if message.mentions != []:
                    user = message.mentions[0]
                    try:
                        retard = self.retard[user.id]
                    except KeyError:
                        retard = 0
                    try:
                        sicklad = self.sicklad[user.id]
                    except KeyError:
                        sicklad = 0
                    try:
                        postcount = self.postcount[user.id]
                    except KeyError:
                        postcount = "0 or bot"
                    try:
                        bio = self.bio[user.id]
                    except KeyError:
                        bio = "User has not set a bio."
                else:
                    user = message.author
                    try:
                        retard = self.retard[user.id]
                    except KeyError:
                        retard = 0
                    try:
                        sicklad = self.sicklad[user.id]
                    except KeyError:
                        sicklad = 0
                    try:
                        postcount = self.postcount[user.id]
                    except KeyError:
                        postcount = "0 or bot"
                    try:
                        bio = self.bio[user.id]
                    except KeyError:
                        bio = "User has not set a bio."
                
                usercolor = message.server.get_member(user.id).colour
                created = re.sub("\.(.*)", "", str(user.created_at))
                em = discord.Embed(title="Userinfo", description=bio, colour=usercolor)
                em.set_author(name=user.name, icon_url=user.avatar_url, url=user.avatar_url)
                em.add_field(name="Name", value="{}#{}".format(user.name, user.discriminator), inline=True)
                em.add_field(name="Nickname", value=user.display_name, inline=True)
                em.add_field(name="ID", value=user.id, inline=True)
                em.add_field(name="Postcount", value=postcount, inline=True)
                em.add_field(name="Retard coins", value=retard, inline=True)
                em.add_field(name="Sicklad", value=sicklad, inline=True)
                em.add_field(name="Created at", value="{}".format(created), inline=True)
                #em.add_field(name="Avatar", value="click me", url=user.avatar_url, inline=False)
                await self.send_message(message.channel, embed=em)
            elif command == 'postcount':
                if len(args) == 0:
                    await self.timed_message(message.channel, message, "**{0}** posts by **{1}** chatters.".format(sum(self.postcount.values()), len(self.postcount)))
                elif len(args) == 1:
                    if message.mentions != []:
                        await self.timed_message(message.channel, message, "{0} has posted {1} messages.".format(client.get_server('207943928018632705').get_member(message.mentions[0].id), self.postcount[message.mentions[0].id]))
                    elif args[0].lower() in ['leaderboard', 'leaderboards', 'top', 'highscore', 'highscores', 'hiscores']:
                        leaderboard = self.postcount
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
                    post_this += "**{0}** posts by **{1}** chatters.".format(sum(self.postcount.values()), len(self.postcount))    
                    await self.timed_message(message.channel, message, post_this)
                else:
                    return
            
            elif command == 'd':
                #if message.author.id != CARL_DISCORD_ID:
                #    return
                app_id = '3177862a'
                app_key = '7b0fd37d75535d00fb0d5fa6c90cf81d'
                language = 'en'
                try:
                    url = 'https://od-api.oxforddictionaries.com/api/v1/entries/' + language + '/' + message.content[3:].lower()
                    r = requests.get(url, headers = {'app_id': app_id, 'app_key': app_key})
                    jsonthing = r.json()
                    print(jsonthing)
                    word_type = jsonthing["results"][0]["lexicalEntries"][0]["lexicalCategory"]
                except Exception:
                    await self.send_message(message.channel, "Err, something went wrong.")
                    return

                definitions = ""
                for i in range(3):
                    try:
                        d = jsonthing["results"][0]["lexicalEntries"][i]["entries"][0]["senses"][0]["definitions"]
                        d = ''.join(d)
                        definitions += "{}.\n".format(d[:-1])
                    except IndexError:
                        pass
                await self.send_message(message.channel, "**{}**, _{}_\n{}".format(message.content[3:].capitalize(), word_type, definitions))
            elif command == 'convert':
                try:
                    if len(args) == 0:
                        await self.timed_message(message.channel, message, "**Usage:** !convert <amount> <currency> <base currency(optional)>\nbase currency is USD by default, type !convert rates for all rates.")
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
                        await self.timed_message(message.channel, message, moneystring)
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
                    await self.timed_message(message.channel, message, "**{0:,.2f} {1}** is equal to **{2:,.2f} {3}**".format(float(amount), currency, rate_return, base_currency))
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
                postthis = ''
                results = google_search(str(message.content[3:]), my_api_key, my_cse_id, num=1)
                url = results[0]['link']
                snippet = results[0]['snippet']
                await self.send_message(message.channel, "{}\n{}".format(url, snippet))
            elif command == "ping":
                await self.timed_message(message.channel, message, "pong!")
            elif command in ["date","current_year", "time"]:
                await self.timed_message(message.channel, message, "It's {0}".format(time.strftime("%Y-%m-%d\n%H:%M:%S (central carl time).")))
            else:
                tagname = re.sub("[^a-z0-9_-]", "", command)
                if tagname in self.tags:
                    await self.timed_message(message.channel, message, self.tags[tagname])
                else:
                    return
        elif re.search("(r\/[\w]+)", message.content):
            if message.content.startswith("r/") or message.content.startswith("/r/"):
                subreddit = re.search("(r\/[\w]+)", message.content)
                subreddit = subreddit.group(1)
                #subreddit = re.sub("[\/]?", "", subreddit)
                await self.send_message(message.channel, "https://www.reddit.com/{}".format(subreddit))
            else:
                return
        else:
            await self.log(message)
            return

if __name__ == '__main__':
        bot = CarlBot()
        bot.run()
