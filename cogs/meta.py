import discord
import os
import datetime
import re
import asyncio
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


ctx_tick = ("<:redtick:318044813444251649>", "<:greentick:318044721807360010>")


class Prefix(commands.Converter):
    async def convert(self, ctx, argument):
        user_id = ctx.bot.user.id
        if argument.startswith((f'<@{user_id}>', f'<@!{user_id}>')):
            raise commands.BadArgument(
                'That is a reserved prefix already in use.')
        return argument


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


class Meta:
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='prefix', invoke_without_command=True)
    async def _prefix(self, ctx):
        """Manages the server's custom prefixes.

        If called without a subcommand, this will list the currently set
        prefixes.
        """

        prefixes = self.bot.get_guild_prefixes(ctx.guild)

        # we want to remove prefix #2, because it's the 2nd form of the mention
        # and to the end user, this would end up making them confused why the
        # mention is there twice
        del prefixes[1]

        e = discord.Embed(title='Prefixes', colour=discord.Colour.blurple())
        e.set_footer(text=f'{len(prefixes)} prefixes')
        e.description = '\n'.join(
            f'{index}. {elem}' for index, elem in enumerate(prefixes, 1))
        await ctx.send(embed=e)

    @_prefix.command(name='add', ignore_extra=False)
    @checks.admin_or_permissions(manage_server=True)
    async def prefix_add(self, ctx, prefix: Prefix):
        if "@everyone" in prefix:
            return ctx.send("Fuck off.")
        if "@here" in prefix:
            return ctx.send("Fuck off.")
        if "," in prefix:
            return ctx.send("No commas, I'm lazy.")

        current_prefixes = self.bot.get_raw_guild_prefixes(ctx.guild.id)
        current_prefixes.append(prefix)
        try:
            await self.bot.set_guild_prefixes(ctx.guild, current_prefixes)
        except Exception as e:
            await ctx.send(e)
        else:
            await ctx.send("{} added".format(prefix))

    @prefix_add.error
    async def prefix_add_error(self, ctx, error):
        if isinstance(error, commands.TooManyArguments):
            await ctx.send("You've given too many prefixes. Either quote it or only do it one by one.")

    @_prefix.command(name='remove', aliases=['delete'], ignore_extra=False)
    @checks.admin_or_permissions(manage_server=True)
    async def prefix_remove(self, ctx, prefix: Prefix):

        current_prefixes = self.bot.get_raw_guild_prefixes(ctx.guild.id)

        try:
            current_prefixes.remove(prefix)
        except ValueError:
            return await ctx.send('I do not have this prefix registered.')

        try:
            await self.bot.set_guild_prefixes(ctx.guild, current_prefixes)
        except Exception as e:
            await ctx.send('{}'.format(e))
        else:
            await ctx.send("{} removed".format(prefix))

    @_prefix.command(name='clear')
    @checks.admin_or_permissions(manage_server=True)
    async def prefix_clear(self, ctx):

        await self.bot.set_guild_prefixes(ctx.guild, [])
        await ctx.send('ALL prefixes removed, you need to mention me to set a new one.')

    @commands.command(name='define', aliases=['d'], no_pm=True)
    async def _definitions(self, ctx, *, word: str):
        language = 'en'
        user = ctx.author
        url = 'https://od-api.oxforddictionaries.com/api/v1/entries/en/' + word.lower()
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers={'app_id': '3177862a', 'app_key': '5ce390244f464ed805eac645f5167322'}) as r:
                try:
                    jsonthing = await r.json()
                except Exception as e:
                    await ctx.send('No definition found.')
                    return
        actual_word = word.capitalize()
        pronounciation = jsonthing["results"][0]["lexicalEntries"][0]["pronunciations"][0]["phoneticSpelling"]
        e = discord.Embed(
            title=actual_word, description="/{}/".format(pronounciation), color=0x738bd7)
        e.set_author(name=user.name, icon_url=user.avatar_url,
                     url=user.avatar_url)
        try:
            x = jsonthing["results"][0]["lexicalEntries"]
        except Exception as e:
            await ctx.send('{}: {}'.format(type(e).__name__, e))
        f = 0
        definitions = {}
        examples = {}
        for i in x:
            word_type = x[f]["lexicalCategory"]
            try:
                d = x[f]["entries"][0]["senses"][0]["definitions"]
            except:
                continue
            d = ''.join(d)
            definition = "{}\n".format(
                ''.join(i["entries"][0]["senses"][0]["definitions"]))
            try:
                if i["entries"][0]["senses"][0]["examples"] is not None:
                    examplestring = ""
                    for example in i["entries"][0]["senses"][0]["examples"]:
                        examplestring += "  \"*{}*\"\n".format(
                            ''.join(example["text"]))
            except KeyError:
                examplestring = ""
            try:
                definitions[word_type] += "1. {}{}\n".format(
                    definition.capitalize(), examplestring)
                examplestring = ""
            except KeyError:
                definitions[word_type] = "1. {}{}\n".format(
                    definition.capitalize(), examplestring)
                examplestring = ""
            try:
                if x[f]["entries"][0]["senses"][0]["subsenses"] is not None:
                    whole_thing = x[f]["entries"][0]["senses"][0]["subsenses"]
                    for n, subsense in enumerate(whole_thing):
                        subsense = "{}\n".format(
                            ''.join(subsense["definitions"]))
                        try:
                            definitions[word_type] += "{}. {}".format(
                                n + 2, subsense.capitalize())
                        except KeyError:
                            definitions[word_type] = "{}. {}".format(
                                n + 2, subsense.capitalize())
            except KeyError:
                pass
            f += 1
        for box in definitions:
            e.add_field(name=box, value=definitions[box], inline=False)
        try:
            destination = discord.utils.find(
                lambda m: "bot" in m.name, ctx.guild.channels)
            #xd = await destination.send(ctx.author.mention)

        except:
            destination = ctx.message.channel
        await ctx.send(embed=e)

    @commands.command()
    async def charinfo(self, ctx, *, characters: str):
        """Shows you information about a number of characters.

        Only up to 15 characters at a time.
        """

        if len(characters) > 15:
            await ctx.send('Too many characters ({}/15)'.format(len(characters)))
            return

        fmt = '`\\U{0:>08}`: {1} - {2} \N{EM DASH} <http://www.fileformat.info/info/unicode/char/{0}>'

        def to_string(c):
            digit = format(ord(c), 'x')
            name = unicodedata.name(c, 'Name not found.')
            return fmt.format(digit, name, c)

        await ctx.send('\n'.join(map(to_string, characters)))

    @commands.command(name='serverinfo', pass_context=True, no_pm=True)
    async def server_info(self, ctx):
        guild = ctx.guild
        roles = [role.name.replace('@', '@\u200b') for role in guild.roles]

        class Secret:
            pass

        secret_member = Secret()
        secret_member.id = 0
        secret_member.roles = [guild.default_role]

        # figure out what channels are 'secret'
        secret_channels = 0
        secret_voice = 0
        text_channels = 0
        for channel in guild.channels:
            perms = channel.permissions_for(secret_member)
            is_text = isinstance(channel, discord.TextChannel)
            text_channels += is_text
            if is_text and not perms.read_messages:
                secret_channels += 1
            elif not is_text and (not perms.connect or not perms.speak):
                secret_voice += 1

        voice_channels = len(guild.channels) - text_channels
        member_by_status = Counter(str(m.status) for m in guild.members)

        e = discord.Embed()
        e.title = 'Info for ' + guild.name
        e.add_field(name='ID', value=guild.id)
        e.add_field(name='Owner', value=guild.owner)
        if guild.icon:
            e.set_thumbnail(url=guild.icon_url)

        if guild.splash:
            e.set_image(url=guild.splash_url)

        info = []
        info.append(ctx_tick[len(guild.features) >= 3] + " Partnered")

        sfw = guild.explicit_content_filter is not discord.ContentFilter.disabled
        info.append(ctx_tick[sfw] + " Scanning Images")
        info.append(ctx_tick[guild.member_count > 100] + " Large")

        e.add_field(name='Info', value='\n'.join(map(str, info)))

        fmt = f'Text {text_channels} ({secret_channels} secret)\nVoice {voice_channels} ({secret_voice} locked)'
        e.add_field(name='Channels', value=fmt)

        fmt = '<:online:346921745279746048> {} ' \
              '<:away:346921747330891780> {} ' \
              '<:dnd:346921781786836992> {} ' \
              '<:offline:346921814435430400> {}\n' \
              'Total: {}'.format(member_by_status["online"], member_by_status["idle"],
                                 member_by_status["dnd"], member_by_status["offline"], guild.member_count)

        e.add_field(name='Members', value=fmt)
        e.add_field(name='Roles', value=', '.join(roles)
                    if len(roles) < 10 else f'{len(roles)} roles')
        e.set_footer(text='Created').timestamp = guild.created_at
        await ctx.send(embed=e)

    async def say_permissions(self, ctx, member, channel):
        permissions = channel.permissions_for(member)
        e = discord.Embed()
        allowed, denied = [], []
        for name, value in permissions:
            name = name.replace('_', ' ').title()
            if value:
                allowed.append(name)
            else:
                denied.append(name)

        e.add_field(name='Allowed', value='\n'.join(allowed))
        e.add_field(name='Denied', value='\n'.join(denied))
        await ctx.send(embed=e)

    @commands.command(pass_context=True, no_pm=True)
    async def permissions(self, ctx, *, member: discord.Member = None):
        """Shows a member's permissions.

        You cannot use this in private messages. If no member is given then
        the info returned will be yours.
        """
        channel = ctx.message.channel
        if member is None:
            member = ctx.author

        await self.say_permissions(ctx, member, channel)

    @commands.command(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def botpermissions(self, ctx):
        """Shows the bot's permissions.

        This is a good way of checking if the bot has the permissions needed
        to execute the commands it wants to execute.

        To execute this command you must have Manage Roles permissions or
        have the Bot Admin role. You cannot use this in private messages.
        """
        channel = ctx.channel
        member = ctx.message.guild.me
        await self.say_permissions(ctx, member, channel)

    @commands.command(name='invite')
    async def cmd_invite(self, ctx):
        e = discord.Embed(title="Invite links", description=f"[Invite link (recommended)](https://discordapp.com/oauth2/authorize?client_id=235148962103951360&scope=bot&permissions=470150352)\n[Invite link (admin)](https://discordapp.com/oauth2/authorize?client_id=235148962103951360&scope=bot&permissions=66321471)")
        
        await ctx.send(embed=e)


    @commands.command(hidden=True)
    async def cud(self, ctx):
        """pls no spam"""

        for i in range(3):
            await ctx.send(3 - i)
            await asyncio.sleep(1)

        await ctx.send('go')


    @commands.command()
    async def discrim(self, ctx, number: str=None):
        members = self.bot.get_all_members()
        if number is None or len(number) != 4:
            number = ctx.author.discriminator
        good_boys = list(set([x.name for x in members if x.discriminator == number]))
        if not good_boys:
            return await ctx.send("Couldn't find any users with that discriminator, invite me to more servers to improve the functionality of this command ;)")
        good_boys = '\n'.join(good_boys)
        await ctx.send(f"Found the following users with the discriminator {number}\n```\n{good_boys}\n```")


    # @commands.command(pass_context=True)
    # async def help(self, ctx):
    #     url = r"https://github.com/CarlGroth/Carl-Bot/blob/master/readme.md"
    #     e = discord.Embed(title="Helpful links", description=f"[Invite link (recommended)](https://discordapp.com/oauth2/authorize?client_id=235148962103951360&scope=bot&permissions=470150352)\n[Invite link (admin)](https://discordapp.com/oauth2/authorize?client_id=235148962103951360&scope=bot&permissions=66321471)\n[Bot support server](https://discord.gg/DSg744v)")
        
    #     await ctx.author.send('Check out the commands on github: {}\nPM Carl#0001 or join the support server if you have any unanswered questions.'.format(url), embed=e)


def setup(bot):
    # n = Meta(bot)
    # loop2 = asyncio.get_event_loop()
    # loop2.create_task(n.remindme_checker())
    bot.add_cog(Meta(bot))
