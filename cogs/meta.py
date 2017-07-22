import discord
import os, datetime
import re, asyncio
import copy
import math
import unicodedata
import inspect
import json
import aiohttp

from discord.ext import commands
from cogs.utils import checks, formats
from collections import OrderedDict, deque, Counter
from cogs.utils.formats import Plural


def load_json(filename):
    with open(filename, encoding='utf-8') as infile:
        return json.load(infile)

def write_json(filename, contents):
    with open(filename, 'w') as outfile:
        json.dump(contents, outfile, indent=4)

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

class TimeParser:
    def __init__(self, argument):
        compiled = re.compile('(\\d+)(\\D+)')
        self.original = argument
        try:
            self.seconds = int(argument)
        except ValueError as e:
            self.seconds = 0
            match = compiled.match(argument)
            if match is None or not match.group(0):
                self.time = False
                raise commands.BadArgument('Failed to parse time.') from e

            matches = re.findall(compiled, argument)

            for match1 in matches:
                try:
                    time = int(match1[0])
                except:
                    time = 0
                unit = match1[1]

                if unit in ["y", "year", "years", "yrs", "yr"]:
                    self.seconds += time * 86400 * 365
                elif unit in ["d", "day", "days"]:
                    self.seconds += time * 86400
                elif unit in ["h", "hour", "hours", "hr", "hrs"]:
                    self.seconds += time * 3600
                elif unit in ["m", "minute", "minutes"]:
                    self.seconds += time * 60
                elif unit in ["s", "sec", "seconds", "second"]:
                    self.seconds += time


        if self.seconds <= 0:
            raise commands.BadArgument("<=0")

        if self.seconds > 2.606e9: # 7 days
            raise commands.BadArgument("Please try and keep it to this century.")


        

class Meta:
    def __init__(self, bot):
        self.bot = bot
        self.remindme = load_json('remindme.json')

    


    @commands.command(pass_context=True, name='define', aliases=['d'], no_pm=True)
    async def _definitions(self, ctx, *, word : str):
        language = 'en'
        user = ctx.message.author
        url = 'https://od-api.oxforddictionaries.com/api/v1/entries/en/' + word.lower()
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers = {'app_id': '3177862a', 'app_key': '5ce390244f464ed805eac645f5167322'}) as r:
                try:
                    jsonthing = await r.json()
                except Exception as e:
                    await self.bot.say('No definition found.\nError: {}: {}'.format(type(e).__name__, e))
                    return
        actual_word = word.capitalize()
        pronounciation = jsonthing["results"][0]["lexicalEntries"][0]["pronunciations"][0]["phoneticSpelling"]
        e = discord.Embed(title=actual_word, description="/{}/".format(pronounciation), color=0x738bd7)
        e.set_author(name=user.name, icon_url=user.avatar_url, url=user.avatar_url)
        try:
            x = jsonthing["results"][0]["lexicalEntries"]
        except Exception as e:
            await self.bot.say('{}: {}'.format(type(e).__name__, e))
        f = 0
        definitions = {}
        examples = {}
        for i in x:
            word_type = x[f]["lexicalCategory"]
            d = x[f]["entries"][0]["senses"][0]["definitions"]
            d = ''.join(d)
            definition = "{}\n".format( ''.join(i["entries"][0]["senses"][0]["definitions"]))
            try:
                if i["entries"][0]["senses"][0]["examples"] is not None:
                    examplestring = ""
                    for example in i["entries"][0]["senses"][0]["examples"]:
                        examplestring += "  \"*{}*\"\n".format(''.join(example["text"]))
            except KeyError:
                examplestring = ""
            try:
                definitions[word_type] += "1. {}{}\n".format(definition.capitalize(), examplestring)
                examplestring = ""
            except KeyError:
                definitions[word_type] = "1. {}{}\n".format(definition.capitalize(), examplestring)
                examplestring = ""
            try:
                if x[f]["entries"][0]["senses"][0]["subsenses"] is not None:
                    whole_thing = x[f]["entries"][0]["senses"][0]["subsenses"]
                    for n, subsense in enumerate(whole_thing):
                        subsense = "{}\n".format( ''.join(subsense["definitions"]))
                        try:
                            definitions[word_type] += "{}. {}".format(n+2, subsense.capitalize())
                        except KeyError:
                            definitions[word_type] = "{}. {}".format(n+2, subsense.capitalize())
            except KeyError:
                pass
            f += 1
        for box in definitions:
            e.add_field(name=box, value=definitions[box], inline=False)
        if ctx.message.channel.is_default:
            try:
                destination = discord.utils.find(lambda m: "bot" in m.name, ctx.message.server.channels)
                xd = await self.bot.send_message(destination, ctx.message.author.mention)
                
            except:
                destination = ctx.message.channel
            
        else:
            destination = ctx.message.channel
        await self.bot.send_message(destination, embed=e)


    @commands.command()
    async def charinfo(self, *, characters: str):
        """Shows you information about a number of characters.

        Only up to 15 characters at a time.
        """

        if len(characters) > 15:
            await self.bot.say('Too many characters ({}/15)'.format(len(characters)))
            return

        fmt = '`\\U{0:>08}`: {1} - {2} \N{EM DASH} <http://www.fileformat.info/info/unicode/char/{0}>'

        def to_string(c):
            digit = format(ord(c), 'x')
            name = unicodedata.name(c, 'Name not found.')
            return fmt.format(digit, name, c)

        await self.bot.say('\n'.join(map(to_string, characters)))

    @commands.command(pass_context=True, no_pm=True)
    async def timer(self, ctx, time : TimeParser, *, message=''):
        author = ctx.message.author
        reminder = None
        completed = None
        message = message.replace('@everyone', '@\u200beveryone').replace('@here', '@\u200bhere')
        message = message.replace('@', '@\u200b')

        if not message:
            reminder = 'Okay **{0.name}**, I\'ll remind you in {1}.'
            completed = 'Time is up {0.mention}! You asked to be reminded about something {2}.'
        else:
            reminder = 'Okay **{0.name}**, I\'ll remind you about "{2}" in {1}.'
            completed = 'Time is up {0.mention}! You asked to be reminded about "{1}" {2}.'

        human_time = datetime.datetime.utcnow() - datetime.timedelta(seconds=time.seconds)
        human_time = formats.human_timedelta(human_time)
        await self.bot.say(reminder.format(author, human_time.replace(' ago', ''), message))
        await asyncio.sleep(time.seconds)
        await self.bot.say(completed.format(author, message, human_time))

    
    @commands.group(pass_context=True, name="remindme", aliases=['rm'], invoke_without_command=True, no_pm=True)
    async def remind_me(self, ctx, time : TimeParser, *, message=''):
        author = ctx.message.author
        reminder = None
        completed = None
        message = message.replace('@everyone', '@\u200beveryone').replace('@here', '@\u200bhere')
        message = message.replace('@', '@\u200b')
        if not time:
            await self.bot.say("No time")
        if not message:
            reminder = 'Okay **{0.name}**, I\'ll remind you in {1}.'
            completed = 'Time is up {0.mention}! You asked to be reminded about something {2}.'
        else:
            reminder = 'Okay **{0.name}**, I\'ll remind you about "{2}" in {1}'
            completed = 'Time is up {0.mention}! You asked to be reminded about "{1}" {2}.'

        human_time = datetime.datetime.utcnow() - datetime.timedelta(seconds=time.seconds)
        human_time = formats.human_timedelta(human_time)
        
        try:
            if len(self.remindme) == 0:
                rm_index = 0
            else:
                rm_index = str(max(map(lambda x: int(x), self.remindme.keys())) + 1)
            self.remindme[rm_index] = {"server" : ctx.message.server.id, "author" : author.id, "created" : datetime.datetime.utcnow().timestamp(), "message" : str(message), "timestamp" : (datetime.datetime.utcnow() + datetime.timedelta(seconds=time.seconds)).timestamp()}
        except Exception as e:
            print(e)
            return
        print(message)
        write_json('remindme.json', self.remindme)
        await self.bot.say(reminder.format(author, human_time.replace(' ago', '. ID: **{}**'.format(rm_index)), message))
    

    @remind_me.command(pass_context=True, aliases=['eu', 'na'])
    async def invasion(self, ctx):
        eu = False
        if ctx.message.content.split()[1] == "eu":
            eu = True
        eu_anchor = datetime.datetime(year=2017, month=5, day=26, hour=22, minute=30, second=0, microsecond=0)
        na_anchor = datetime.datetime(year=2017, month=5, day=26, hour=12, minute=0, second=0, microsecond=0)
        eu_seconds_since = datetime.datetime.utcnow() - eu_anchor
        eu_seconds_after_start = math.floor(eu_seconds_since.total_seconds() % 66600)
        na_seconds_since = datetime.datetime.utcnow() - na_anchor
        na_seconds_after_start = math.floor(na_seconds_since.total_seconds() % 66600)
        if eu:
            time_left = 66600 - eu_seconds_after_start
        if not eu:
            time_left = 66600 - na_seconds_after_start
        time = TimeParser(time_left)
        print(time.seconds)
        author = ctx.message.author
        if eu:
            message = "EU invasion is up!"
            reminder = 'Okay **{0.name}**, I\'ll notify you about the EU invasion in {1}'
        else:
            message = "NA invasion is up!"
            reminder = 'Okay **{0.name}**, I\'ll notify you about the NA invasion in {1}'
        

        human_time = datetime.datetime.utcnow() - datetime.timedelta(seconds=time.seconds)
        human_time = formats.human_timedelta(human_time)
        
        try:
            if len(self.remindme) == 0:
                rm_index = 0
            else:
                rm_index = str(max(map(lambda x: int(x), self.remindme.keys())) + 1)
            self.remindme[rm_index] = {"server" : ctx.message.server.id, "author" : author.id, "created" : datetime.datetime.utcnow().timestamp(), "message" : str(message), "timestamp" : (datetime.datetime.utcnow() + datetime.timedelta(seconds=time.seconds)).timestamp()}
        except Exception as e:
            print(e)
            return
        print(message)
        write_json('remindme.json', self.remindme)
        await self.bot.say(reminder.format(author, human_time.replace(' ago', '. ID: **{}**'.format(rm_index))))


    @remind_me.command(pass_context=True)
    async def mine(self, ctx):
        author = ctx.message.author
        my_reminders = "```"
        for k, v in self.remindme.items():
            if v["author"] == author.id:
                date = datetime.datetime.fromtimestamp(v["timestamp"]).strftime("%Y-%m-%d %H:%M")
                my_reminders += "ID: {0:>3} Date: {2} Message: {1}\n".format(k, v["message"], date)
        if len(my_reminders) == 3:
            await self.bot.say("User has no reminders")
        else:
            await self.bot.say("{}```".format(my_reminders))
            return
    @remind_me.command(name='all', hidden=True)
    @checks.is_owner()
    async def _all(self):
        my_reminders = "```"
        for k, v in self.remindme.items():
            date = datetime.datetime.fromtimestamp(v["timestamp"]).strftime("%Y-%m-%d %H:%M")
            my_reminders += "ID: {0:>3} Date: {2} Message: {1}\n".format(k, v["message"], date)
        if len(my_reminders) == 3:
            await self.bot.say("There are no reminders")
        else:
            if len(my_reminders) < 2000:
                await self.bot.say("{}```".format(my_reminders))
                return
            else:
                url = "https://hastebin.com/documents"
                async with aiohttp.ClientSession() as session:
                    headers = {'content-type': 'text/plain', 'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64)'}
                    nicks = nicks.replace(", ", "\n")
                    data = my_reminders.encode('utf-8')
                    async with session.post(url=url, data=data, headers=headers) as r:
                        print(r.status)
                        haste_thing = await r.json(encoding="utf-8", loads=json.loads)
                await self.bot.say("Too many reminders to display: https://hastebin.com/{}".format(haste_thing["key"]))
    @remind_me.command(pass_context=True, name="clear")
    async def _clear(self, ctx, kebab : int = None):
        kebab = False if kebab is None else str(kebab)
        if not kebab:
            author = ctx.message.author
            reminders = [k for k, v in self.remindme.items() if v["author"] == author.id]
            msg = await self.bot.say('This will delete %s reminders are you sure? **This action cannot be reversed**.\n\n' \
    'React with either \N{WHITE HEAVY CHECK MARK} to confirm or \N{CROSS MARK} to deny.' % len(reminders))

            cancel = False
            author_id = ctx.message.author.id
            def check(reaction, user):
                nonlocal cancel
                if user.id != author_id:
                    return False

                if reaction.emoji == '\N{WHITE HEAVY CHECK MARK}':
                    return True
                elif reaction.emoji == '\N{CROSS MARK}':
                    cancel = True
                    return True
                return False

            for emoji in ('\N{WHITE HEAVY CHECK MARK}', '\N{CROSS MARK}'):
                await self.bot.add_reaction(msg, emoji)

            react = await self.bot.wait_for_reaction(message=msg, check=check, timeout=60.0)
            if react is None or cancel:
                await self.bot.delete_message(msg)
                return await self.bot.say('Cancelling.')

            self.remindme = { a:b for a,b in self.remindme.items() if a not in reminders }
                

            write_json('remindme.json', self.remindme)
            await self.bot.delete_message(msg)
            await self.bot.say('Successfully removed all %s reminders that belong to %s' % (len(reminders), author.name))

        else:
            try:
                if self.remindme[kebab]["author"] == ctx.message.author.id:
                    self.remindme = { a:b for a,b in self.remindme.items() if a!=kebab }
                    write_json('remindme.json', self.remindme)
                    await self.bot.say("Successfully removed reminder.")
                else:
                    await self.bot.say("That's not your reminder.")
            except KeyError:
                await self.bot.say("No reminder with that ID found.")

    @commands.command(pass_context=True, aliases=["sub"], no_pm=True)
    async def subscribe(self, ctx, rm_id : int):
        rm_id = str(rm_id)
        if rm_id not in self.remindme:
            await self.bot.say("No reminder with that id.")
            return
        elif ctx.message.server.id != self.remindme[rm_id]["server"]:
            await self.bot.say("That reminder was made in another server.")
            return
        else:
            entry = self.remindme[rm_id]

        a = datetime.datetime.fromtimestamp(float(entry["timestamp"]))
        human_time = formats.flipped_human_timedelta(a)
        rm_index = str(max(map(lambda x: int(x), self.remindme.keys())) + 1)
        self.remindme[rm_index] = {"server" : ctx.message.server.id, "author" : ctx.message.author.id, "created" : datetime.datetime.utcnow().timestamp(), "message" : entry["message"], "timestamp" : entry["timestamp"]}
        write_json('remindme.json', self.remindme)
        await self.bot.say("Okay **{}** you'll be reminded about \"{}\" in {}. ID: **{}**".format(ctx.message.author.name, entry["message"], human_time, rm_index))

    @remind_me.error
    async def rm_error(self, error, ctx):
        if isinstance(error, commands.BadArgument):
            await self.bot.say(str(error))

    async def remindme_checker(self):
        DELAY = 10
        while self == self.bot.get_cog("Meta"):
            for k, v in self.remindme.items():
                try:
                    diff = v["timestamp"] - datetime.datetime.utcnow().timestamp() < 0
                except:
                    diff = False
                if diff:
                    try:
                        rm_s = str(v["server"])
                        rm_a = str(v["author"])
                        destination = self.bot.get_server(rm_s).get_member(rm_a)
                        old_datetime = datetime.datetime.fromtimestamp(v["created"])
                        human_time = formats.human_timedelta(old_datetime)
                        await self.bot.send_message(destination, "You asked to be reminded about \"{}\"\n{} ago".format(v["message"], human_time.replace(' ago', '')))
                        self.remindme = { a:b for a,b in self.remindme.items() if a!=k }
                        write_json('remindme.json', self.remindme)
                        await asyncio.sleep(1)
                    except:
                        continue
            await asyncio.sleep(10)
    
    @timer.error
    async def timer_error(self, error, ctx):
        if isinstance(error, commands.BadArgument):
            await self.bot.say(str(error))

    
    
    
    
    @commands.command(name='quit', hidden=True)
    @checks.is_owner()
    async def _quit(self):
        """Quits the bot."""
        await self.bot.logout()



    @commands.command(name='serverinfo', pass_context=True, no_pm=True)
    async def server_info(self, ctx):
        server = ctx.message.server
        roles = [role.name.replace('@', '@\u200b') for role in server.roles]

        secret_member = copy.copy(server.me)
        secret_member.id = '0'
        secret_member.roles = [server.default_role]

        # figure out what channels are 'secret'
        secret_channels = 0
        secret_voice = 0
        text_channels = 0
        for channel in server.channels:
            perms = channel.permissions_for(secret_member)
            is_text = channel.type == discord.ChannelType.text
            text_channels += is_text
            if is_text and not perms.read_messages:
                secret_channels += 1
            elif not is_text and (not perms.connect or not perms.speak):
                secret_voice += 1

        voice_channels = len(server.channels) - text_channels
        member_by_status = Counter(str(m.status) for m in server.members)

        e = discord.Embed()
        e.title = 'Info for ' + server.name
        e.add_field(name='ID', value=server.id)
        e.add_field(name='Owner', value=server.owner)
        if server.icon:
            e.set_thumbnail(url=server.icon_url)

        if server.splash:
            e.set_image(url=server.splash_url)

        e.add_field(name='Partnered?', value='Yes' if len(server.features) >= 3 else 'No')

        fmt = 'Text %s (%s secret)\nVoice %s (%s locked)'
        e.add_field(name='Channels', value=fmt % (text_channels, secret_channels, voice_channels, secret_voice))

        fmt = 'Total: {0}\nOnline: {1[online]}' \
              ', Offline: {1[offline]}' \
              '\nDnD: {1[dnd]}' \
              ', Idle: {1[idle]}'

        e.add_field(name='Members', value=fmt.format(server.member_count, member_by_status))
        e.add_field(name='Roles', value=', '.join(roles) if len(roles) < 10 else '%s roles' % len(roles))
        e.set_footer(text='Created').timestamp = server.created_at
        await self.bot.say(embed=e)

    async def say_permissions(self, member, channel):
        permissions = channel.permissions_for(member)
        entries = [(attr.replace('_', ' ').title(), val) for attr, val in permissions]
        await formats.entry_to_code(self.bot, entries)

    @commands.command(pass_context=True, no_pm=True)
    async def permissions(self, ctx, *, member : discord.Member = None):
        """Shows a member's permissions.

        You cannot use this in private messages. If no member is given then
        the info returned will be yours.
        """
        channel = ctx.message.channel
        if member is None:
            member = ctx.message.author

        await self.say_permissions(member, channel)

    @commands.command(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def botpermissions(self, ctx):
        """Shows the bot's permissions.

        This is a good way of checking if the bot has the permissions needed
        to execute the commands it wants to execute.

        To execute this command you must have Manage Roles permissions or
        have the Bot Admin role. You cannot use this in private messages.
        """
        channel = ctx.message.channel
        member = ctx.message.server.me
        await self.say_permissions(member, channel)

    @commands.command(aliases=['invite'])
    async def join(self):
        """Joins a server."""
        perms = discord.Permissions.none()
        perms.read_messages = True
        perms.send_messages = True
        perms.manage_roles = True
        perms.ban_members = True
        perms.kick_members = True
        perms.manage_messages = True
        perms.embed_links = True
        perms.read_message_history = True
        perms.attach_files = True
        perms.add_reactions = True
        await self.bot.say(discord.utils.oauth_url(self.bot.client_id, perms))



    @commands.command(hidden=True)
    async def cud(self):
        """pls no spam"""

        for i in range(3):
            await self.bot.say(3 - i)
            await asyncio.sleep(1)

        await self.bot.say('go')
    @commands.command(pass_context=True)
    async def help(self, ctx):
        url = r"https://github.com/CarlGroth/Carl-Bot/blob/master/readme.md"
        await self.bot.send_message(ctx.message.author, 'Check out the commands on github: {}\nor PM Carl if you have any unanswered questions.'.format(url))


def setup(bot):
    n = Meta(bot)
    loop2 = asyncio.get_event_loop()
    loop2.create_task(n.remindme_checker())
    bot.add_cog(n)
