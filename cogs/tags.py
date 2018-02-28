import re
import json
import math
import discord
import datetime
import sqlite3
import random
import aiohttp
import copy
import asyncio

from fuzzywuzzy import fuzz
from discord.ext import commands
from cogs.utils.paginator import Pages
from cogs.utils import checks, formats
from TagScriptEngine import Engine



def to_keycap(c):
    return '\N{KEYCAP TEN}' if c == 10 else str(c) + '\u20e3'

class Tags:
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('database.db')
        self.c = self.conn.cursor()
        self.engine = Engine()
        self.variable_regex = re.compile(
            r'(?:\$(\d)=?((?:\w|%|{|.*?}|".*?")*)?)')
        self.random_regex = re.compile(r"(\{\{(.*?)\}\})")
        self.c.execute('''CREATE TABLE IF NOT EXISTS tags
             (name text, content text, server text, creation real, updated real, uses real, author text)''')

        self.c.execute('''CREATE TABLE IF NOT EXISTS tag_lookup
        (server text, is_alias boolean, name text, points_to text, nsfw boolean, mod boolean, restricted boolean)''')

    def clean_tag_content(self, content):
        return content.replace('@everyone', '@\u200beveryone').replace('@here', '@\u200bhere')


    # @commands.command()
    # async def populate(self, ctx):
    #     self.c.execute('''SELECT name, server
    #                       FROM tags
    #                       WHERE 1''')
    #     big_list = self.c.fetchall()
    #     for row in big_list:
    #         self.c.execute('''INSERT INTO tag_lookup
    #                           VALUES (?, ?, ?, ?, ?, ?, ?)''',
    #                           (row[1], False, row[0], row[0], False, False, False))
    #     self.conn.commit()
    #     await ctx.send("all done! :D")
            











    async def do_tag_stuff(self, ctx, name, choices=()):
        real_choices = [x for x in choices]
        choices = [x for x in choices if not re.match("<@!?\d*>", x)]
        lookup = name.lower()
        if ctx.guild is None:
            shared_servers = [x for x in self.bot.guilds if ctx.author in x.members]
            shared_servers_id = [str(x.id) for x in shared_servers]
            self.c.execute('''SELECT *
                          FROM tag_lookup
                          WHERE name=?''',
                       (lookup,))
            t = self.c.fetchall()
            if not t:
                return
            tags = [x for x in t if x[0] in shared_servers_id]
            if not tags:
                return await ctx.send("No tags found with that")
            if len(tags) == 1:
                server, is_alias, _, points_to, nsfw, mod, restricted = tags[0]
            else:
                # prompt the user
                e = discord.Embed()
                keycaps = {}
                helptext = ""
                for n,t in enumerate(tags):
                    servername = self.bot.get_guild(int(t[0])).name
                    helptext += f"{n+1}.  {servername}\n" # Jesus christ
                    keycaps[to_keycap(n+1)] = t
                e.add_field(name="Multiple servers you're in have a tag named that, react with the server you want to fetch the tag from.", value=helptext)    
                msg = await ctx.send(embed=e)
                
                
                for emoji, _ in keycaps.items():
                    await msg.add_reaction(emoji)
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', check=lambda x,y: y.id == ctx.author.id, timeout=90.0)
                except asyncio.TimeoutError:
                    return
                await msg.delete()
                server, is_alias, _, points_to, nsfw, mod, restricted = keycaps[str(reaction.emoji)]


        
        else:
            self.c.execute('''SELECT *
                            FROM tag_lookup
                            WHERE (name=? AND server=?)''',
                        (lookup, ctx.guild.id))
            t = self.c.fetchone()
            if t is None:
                return
            server, is_alias, _, points_to, nsfw, mod, restricted = t
        
        self.c.execute('''SELECT content, uses
                          FROM tags
                          WHERE (name=? AND server=?)''',
                       (points_to, str(server)))
        a = self.c.fetchone()
        destination = ctx.channel
        if a is None:
            return await ctx.send("Something that shouldn't happen just happened, tell Carl a pointed to tag doesn't exist.")
        tag, uses = a

        
        if nsfw and not ctx.channel.is_nsfw():
            return await ctx.send("<:redtick:318044813444251649> This tag can only be used in NSFW channels.")
        
        if restricted:
            is_mod = False
            bypass = ctx.author.guild_permissions.manage_guild
            if ctx.guild.id == 113103747126747136:
                mod_role = 175657731426877440
                roles = [x.id for x in ctx.author.roles]
                if mod_role in roles:
                    is_mod = True
            elif bypass:
                is_mod = True
            if not is_mod:
                self.c.execute('''SELECT bot_channel
                                FROM servers
                                WHERE id=?''',
                            (ctx.guild.id,))            
                bot_channel = self.c.fetchone()
                if bot_channel[0] is None:
                    bot_channel = discord.utils.find(lambda m: "bot" in m.name, ctx.guild.channels)
                    if bot_channel is None:
                        bot_channel = ctx.channel
                else:
                    bot_channel = self.bot.get_channel(int(bot_channel[0]))
                destination = bot_channel
                if ctx.channel != destination:
                    await destination.send(ctx.author.mention)
        
        if mod:
            is_mod = False
            bypass = ctx.author.guild_permissions.manage_guild
            if ctx.guild.id == 113103747126747136:
                mod_role = 175657731426877440
                roles = [x.id for x in ctx.author.roles]
                if mod_role in roles:
                    is_mod = True
            elif bypass:
                is_mod = True
            if not is_mod:
                return
        if choices:
            for i, item in enumerate(choices):
                self.engine.Add_Variable(str(i+1), item)
        nix = str(int(datetime.datetime.utcnow().timestamp()))
        self.engine.Add_Variable("unix", nix)
        self.engine.Add_Variable("uses", str(int(uses)))
        self.engine.Add_Variable("args", ' '.join(choices))
        self.engine.Add_Variable("commandargs", ' '.join(real_choices))
        self.engine.Add_Variable("ARGS", ' '.join(choices).upper())
        uavatar = ctx.message.mentions[0].avatar_url if ctx.message.mentions else ctx.author.avatar_url
        self.engine.Add_Variable("avatar", uavatar)
        # self.engine.Add_Variable("usercount", len(ctx.guild.members))
        self.engine.Add_Variable("authorid", str(ctx.author.id))
        uid = ctx.message.mentions[0].id if ctx.message.mentions != [] else ctx.message.author.id
        self.engine.Add_Variable("userid", str(uid))
        tag = self.engine.Process(tag)
        self.engine.Clear_Variables()
        if r"$user" in tag:
            user = ctx.message.mentions[0] if ctx.message.mentions != [
            ] else ctx.message.author
            tag = tag.replace(r"$user", user.display_name)
        if r"$author" in tag:
            tag = tag.replace(r"$author", ctx.message.author.display_name)
        if r"$channelmention" in tag:
            channel = ctx.message.channel_mentions[0] if ctx.message.channel_mentions != [
            ] else ctx.message.channel
            tag = tag.replace(r"$channelmention", channel.mention)
        if r"$channel" in tag:
            channel = ctx.message.channel_mentions[0] if ctx.message.channel_mentions != [
            ] else ctx.message.channel
            tag = tag.replace(r"$channel", channel.name)
        
        if r"$server" in tag:
            tag = tag.replace(r"$server", ctx.guild.name)
        if r"$nauthor" in tag:
            tag = tag.replace(r"$nauthor", ctx.message.author.name)
        if r"$nuser" in tag:
            user = ctx.message.mentions[0] if ctx.message.mentions != [
            ] else ctx.message.author
            tag = tag.replace(r"$nuser", user.name)
        if r"$mention" in tag:
            if ctx.message.mentions:
                user = ctx.message.mentions[0] if ctx.message.mentions != [
                ] else ctx.message.author
                tag = tag.replace(r"$mention", user.name)
            else:
                tag = tag.replace(r"$mention", "")
        if r"$nmention" in tag:
            if ctx.message.mentions:
                user = ctx.message.mentions[0] if ctx.message.mentions != [
                ] else ctx.message.author
                tag = tag.replace(r"$nmention", user.name)
            else:
                tag = tag.replace(r"$nmention", "")
        


        tag = self.clean_tag_content(tag)

        self.c.execute(
            'UPDATE tags SET uses = uses + 1 WHERE (name=? AND server=?)', (points_to, str(server)))
        self.conn.commit()
        actions = re.search(r'a{(.+?)}', tag)
        reactions = re.search(r'react{(.+?)}', tag)
        will_be_deleted = False
        to_react_with = []
        if actions is not None:
            actionstring = actions.group(1).lower()
            actions = [x.strip() for x in actionstring.split(',')]
            if ctx.guild is not None:
                if "f" in actions:
                    pay_respects = True
                if "delete" in actions:
                    will_be_deleted = True
                if "pmmention" in actions and ctx.message.mentions:
                    destination = ctx.message.mentions[0]
                elif "pm" in actions:
                    destination = ctx.author
                
            tag = re.sub(r'a{(.+?)}', '', tag)
        if reactions is not None:
            reactionstring = reactions.group(1).lower()
            reactions = [x.strip() for x in reactionstring.split(',')]
            if ctx.guild is not None:
                for emoji in reactions:
                    to_react_with.append(emoji)
            tag = re.sub(r'react{(.+?)}', '', tag)
        # Here we need to decide if it's a tag or a command
        cmd = re.search(r'c{(.+?)}', tag)
        if will_be_deleted:
            try:
                await ctx.message.delete()
            except:
                pass
        if cmd is not None:
            # It's a command
            context = copy.copy(ctx.message)
            if "tag" in cmd.group(1).lower():
                return await ctx.send("Can't have 'tag' in your command.")
            context.content = "{}{}".format(ctx.prefix, cmd.group(1))
            return await self.bot.process_commands(context)

        

        tag_msg = await destination.send(tag)
        if to_react_with:
            for emoji in to_react_with:
                if emoji.startswith("<"):
                    emoji = emoji[1:-1]
                await tag_msg.add_reaction(emoji)
        























    @commands.group(invoke_without_command=True)
    async def tag(self, ctx, name: str, *choices: str):
        # choices = [x for x in choices if not re.match("<@!?\d*>", x)]
        # lookup = name.lower()
        # destination = ctx.channel
        # self.c.execute('''SELECT *
        #                   FROM tag_lookup
        #                   WHERE (name=? AND server=?)''',
        #                (lookup, ctx.guild.id))
        # t = self.c.fetchone()
        # if t is None:
        #     return
        # _, is_alias, _, points_to, nsfw, mod, restricted = t
        
        # self.c.execute('''SELECT content, uses
        #                   FROM tags
        #                   WHERE (name=? AND server=?)''',
        #                (points_to, str(ctx.guild.id)))
        # a = self.c.fetchone()
        # if a is None:
        #     return await ctx.send("Something that shouldn't happen just happened, tell Carl a pointed to tag doesn't exist.")
        # tag, uses = a

        
        # if nsfw and not ctx.channel.is_nsfw():
        #     return await ctx.send("<:redtick:318044813444251649> This tag can only be used in NSFW channels.")
        
        # if restricted:
        #     self.c.execute('''SELECT bot_channel
        #                       FROM servers
        #                       WHERE id=?''',
        #                    (ctx.guild.id,))            
        #     bot_channel = self.c.fetchone()
        #     if bot_channel[0] is None:
        #         bot_channel = discord.utils.find(lambda m: "bot" in m.name, ctx.guild.channels)
        #         if bot_channel is None:
        #             bot_channel = ctx.channel
        #     else:
        #         bot_channel = self.bot.get_channel(int(bot_channel[0]))
        #     destination = bot_channel
        #     if ctx.channel != destination:
        #         await destination.send(ctx.author.mention)
        
        # if mod:
        #     bypass = ctx.author.guild_permissions.manage_guild
        #     if not bypass:
        #         return
        # if choices:
        #     for i, item in enumerate(choices):
        #         self.engine.Add_Variable(str(i+1), item)
        # nix = str(int(datetime.datetime.utcnow().timestamp()))
        # self.engine.Add_Variable("unix", nix)
        # self.engine.Add_Variable("uses", str(int(uses)))
        # tag = self.engine.Process(tag)
        # self.engine.Clear_Variables()
        # if r"$user" in tag:
        #     user = ctx.message.mentions[0] if ctx.message.mentions != [
        #     ] else ctx.message.author
        #     tag = tag.replace(r"$user", user.display_name)
        # if r"$author" in tag:
        #     tag = tag.replace(r"$author", ctx.message.author.display_name)
        # if r"$channel" in tag:
        #     channel = ctx.message.channel_mentions[0] if ctx.message.channel_mentions != [
        #     ] else ctx.message.channel
        #     tag = tag.replace(r"$channel", channel.name)
        # if r"$server" in tag:
        #     tag = tag.replace(r"$server", ctx.guild.name)
        # if r"$nauthor" in tag:
        #     tag = tag.replace(r"$nauthor", ctx.message.author.name)
        # if r"$nuser" in tag:
        #     user = ctx.message.mentions[0] if ctx.message.mentions != [
        #     ] else ctx.message.author
        #     tag = tag.replace(r"$nuser", user.name)
        # if r"$mention" in tag:
        #     if ctx.message.mentions:
        #         user = ctx.message.mentions[0] if ctx.message.mentions != [
        #         ] else ctx.message.author
        #         tag = tag.replace(r"$mention", user.name)
        #     else:
        #         tag = tag.replace(r"$mention", "")
        # if r"$nmention" in tag:
        #     if ctx.message.mentions:
        #         user = ctx.message.mentions[0] if ctx.message.mentions != [
        #         ] else ctx.message.author
        #         tag = tag.replace(r"$nmention", user.name)
        #     else:
        #         tag = tag.replace(r"$nmention", "")


        # tag = self.clean_tag_content(tag)

        # self.c.execute(
        #     'UPDATE tags SET uses = uses + 1 WHERE (name=? AND server=?)', (points_to, str(ctx.guild.id)))
        # self.conn.commit()
        # await destination.send(tag)
        await self.do_tag_stuff(ctx, name, choices)

    @tag.error
    async def tag_error(self, error, ctx):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('You need to pass in a tag name.')

    def verify_lookup(self, lookup):
        if '@everyone' in lookup or '@here' in lookup:
            raise RuntimeError('That tag is using blocked words.')

        if not lookup:
            raise RuntimeError('You need to actually pass in a tag name.')

        if len(lookup) > 50:
            raise RuntimeError('Tag name is a maximum of 50 characters.')


    @tag.command(name="get", hidden=True)
    async def _get(self, ctx, name: str, *choices: str):
        await self.do_tag_stuff(ctx, name, choices)

    @tag.command(aliases=['++'])
    @checks.admin_or_permissions(manage_server=True)
    async def procreate(self, ctx, name: str, *, content: str):
        """
        content is a pastebin link (or pastebin raw link) this should only
        ever be used for creating tags whose length is >2000 characters
        with output guaranteed to be below 2000
        """
        lookup = name.lower().strip().replace("@everyone", "everyone").replace("@here", "here")
        self.c.execute('''SELECT is_alias, points_to
                          FROM tag_lookup
                          WHERE (name=? AND server=?)''',
                       (lookup, ctx.guild.id))
        is_alias = self.c.fetchone()
        if is_alias is not None:
            if is_alias[0]:
                return await ctx.send(f"{lookup} is an alias pointing to {is_alias[1]} already")
        match = re.findall("https:\/\/pastebin.com\/(?:raw\/)?(.*)", content)
        if not match:
            await ctx.send("You need to pass in a pastebin link")
            return
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://pastebin.com/raw/{match[0]}') as res:
                content = await res.text()
        content = self.clean_tag_content(content)

        
        try:
            self.verify_lookup(lookup)
        except RuntimeError as e:
            return await ctx.send(e)
        a = self.c.execute(
            'SELECT * FROM tags WHERE (name=? AND server=?)', (lookup, str(ctx.guild.id)))
        a = a.fetchall()
        word = "created"
        if a != []:
            word = "updated"
            self.c.execute('UPDATE tags SET content=?, updated=? WHERE (name=? AND server=?)', (
                content, datetime.datetime.utcnow().timestamp(), lookup, str(ctx.guild.id)))
            self.conn.commit()
            await ctx.send(f'Tag "{name}" successfully {word}.')
        else:            
            self.c.execute("INSERT INTO tags VALUES (?, ?, ?, ?, ?, ?, ?)", (lookup, content, str(
                ctx.guild.id), datetime.datetime.utcnow().timestamp(), datetime.datetime.utcnow().timestamp(), 0, ctx.message.author.id))
            self.c.execute('''INSERT INTO tag_lookup VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (ctx.guild.id, False, lookup, lookup, False, False, False))
            self.conn.commit()
            await ctx.send(f'Tag "{name}" successfully {word}.')

    @tag.command()
    async def nsfw(self, ctx, name: str):
        """
        marks a tag as "nsfw", rendering it unusable (by non-mods) outside of nsfw channels
        """
        is_mod = False
        bypass = ctx.author.guild_permissions.manage_guild or ctx.author.id == 106429844627169280
        if ctx.guild.id == 113103747126747136:
            mod_role = 175657731426877440
            roles = [x.id for x in ctx.author.roles]
            if mod_role in roles:
                is_mod = True
        elif bypass:
            is_mod = True
        if not is_mod:
            return await ctx.send("You need to be a mod to restrict tags")
        lookup = name.lower()
        self.c.execute('''SELECT nsfw, points_to
                          FROM tag_lookup
                          WHERE (name=? AND server=?)''',
                          (lookup, ctx.guild.id))
        status = self.c.fetchone()
        if status is None:
            return await ctx.send("That tag doesn't seem to exist")
        
        new_status = not status[0]
        points_to = status[1]
        self.c.execute('''UPDATE tag_lookup SET nsfw=? WHERE (points_to=? AND server=?)''', (new_status, points_to, ctx.guild.id))
        self.conn.commit()
        if new_status:
            return await ctx.send(f'"{points_to}" is now marked as NSFW')
        await ctx.send(f'"{points_to}" is now marked as SFW')

    @tag.command()
    async def restrict(self, ctx, name: str):
        """
        marks a tag as restricted, when a restricted tag is used outside of the
        specified bot channel (use !set bot <#channel> for this) it will instead be
        posted in the bot channel
        """
        is_mod = False
        bypass = ctx.author.guild_permissions.manage_guild or ctx.author.id == 106429844627169280
        if ctx.guild.id == 113103747126747136:
            mod_role = 175657731426877440
            roles = [x.id for x in ctx.author.roles]
            if mod_role in roles:
                is_mod = True
        elif bypass:
            is_mod = True
        if not is_mod:
            return await ctx.send("You need to be a mod to restrict tags")
        lookup = name.lower()
        self.c.execute('''SELECT restricted, points_to
                          FROM tag_lookup
                          WHERE (name=? AND server=?)''',
                          (lookup, ctx.guild.id))
        status = self.c.fetchone()
        if status is None:
            return await ctx.send("That tag doesn't seem to exist")
        
        new_status = not status[0]
        points_to = status[1]
        self.c.execute('''UPDATE tag_lookup SET restricted=? WHERE (points_to=? AND server=?)''', (new_status, points_to, ctx.guild.id))
        self.conn.commit()
        if new_status:
            return await ctx.send(f'"{points_to}" is now restricted to the bot channel')
        await ctx.send(f'"{points_to}" is no longer restricted')

    @tag.command(name='mod')
    async def mod_only(self, ctx, name: str):
        """
        mod tags can only be used by mods
        """
        is_mod = False
        bypass = ctx.author.guild_permissions.manage_guild or ctx.author.id == 106429844627169280
        if ctx.guild.id == 113103747126747136:
            mod_role = 175657731426877440
            roles = [x.id for x in ctx.author.roles]
            if mod_role in roles:
                is_mod = True
        elif bypass:
            is_mod = True
        if not is_mod:
            return await ctx.send("You need to be a mod to restrict tags")
        lookup = name.lower()
        self.c.execute('''SELECT mod, points_to
                          FROM tag_lookup
                          WHERE (name=? AND server=?)''',
                          (lookup, ctx.guild.id))
        status = self.c.fetchone()
        if status is None:
            return await ctx.send("That tag doesn't seem to exist")
        
        new_status = not status[0]
        points_to = status[1]
        self.c.execute('''UPDATE tag_lookup SET mod=? WHERE (points_to=? AND server=?)''', (new_status, points_to, ctx.guild.id))
        self.conn.commit()
        if new_status:
            return await ctx.send(f'"{points_to}" is now accessable by mods only')
        await ctx.send(f'"{points_to}" is now free for all to use')

    @tag.command(aliases=['a'])
    async def alias(self, ctx, point: str, name: str=None):
        """
        creates a link to an already existing tag
        any changes (content, nsfw, mod etc.) will also be reflected
        to the alias
        """
        if name is None:
            return ctx.send(self.clean_tag_content(f"You need to specify a tag you want linked with {point}"))
        name = name.lower()
        try:
            self.verify_lookup(name)
            self.verify_lookup(point)
        except RuntimeError as e:
            return await ctx.send(e)
        point = point.lower()

        if name == point:
            return await ctx.send("You can't alias a tag to itself")
        # If a tag exists, a lookup will also exist
        # This means we just have to check if name is in tag_lookup
        # for an alias to be created, two things needs to be true:
        # 1. The pointed to tag exists
        # 2. There's no tag or alias with this name created already
        self.c.execute('''SELECT name
                          FROM tag_lookup
                          WHERE (points_to=? AND server=?)''',
                          (name, ctx.guild.id))
        all_rows = self.c.fetchall()
        if all_rows == []:
            return await ctx.send("That tag doesn't seem to exist")

        self.c.execute('''SELECT points_to, is_alias
                          FROM tag_lookup
                          WHERE (name=? AND server=?)''',
                          (point, ctx.guild.id))
        alias_row = self.c.fetchone()
        # We can safely assume 0 or 1 entries exist
        if alias_row is not None:
            if alias_row[1]:
                return await ctx.send(f'There already exists an alias "{point}" pointing to "{alias_row[0]}"')
            return await ctx.send(f'A tag named "{point}" already exists')

        # Our alias is ready to be created
        # FINALLY, we need the nsfw, restricted, and mod values for our tag
        self.c.execute('''SELECT nsfw, mod, restricted
                          FROM tag_lookup
                          WHERE (name=? AND server=?)''',
                          (name, ctx.guild.id))
        nsfw, mod, restricted = self.c.fetchone()
        self.c.execute('''INSERT INTO tag_lookup
                          VALUES (?, ?, ?, ?, ?, ?, ?)''',
                          (ctx.guild.id, True, point, name, nsfw, mod, restricted))
        self.conn.commit()
        await ctx.send(f'Tag alias "{point}" that points to "{name}" created')





       
            







    @tag.command(aliases=['add', '+'])
    async def create(self, ctx, name: str, *, content: str):
        """
        Creates a tag/custom command, commands can then be used with just the prefix
        For more customization, see tag nsfw/mod/restrict or the github for special variables
        """
        if ctx.message.mentions:
            return
        content = self.clean_tag_content(content)
        lookup = name.lower().strip()
        try:
            self.verify_lookup(lookup)
        except RuntimeError as e:
            return await ctx.send(e)
        self.c.execute('''SELECT is_alias, points_to
                          FROM tag_lookup
                          WHERE (name=? AND server=?)''',
                          (lookup, ctx.guild.id))
        is_alias = self.c.fetchone()
        if is_alias is not None:
            if is_alias[0]:
                return await ctx.send(f"{lookup} is an alias pointing to {is_alias[1]} already")
        
        self.c.execute('''SELECT *
                          FROM tags
                          WHERE (name=? AND server=?)''',
                       (lookup, str(ctx.guild.id)))
        a = self.c.fetchone()
        if a is not None:
            await ctx.send("Tag already exists. **__r__**eplace, **__c__**ancel or **__a__**dd to? (r/c/a)")
            msg = await self.bot.wait_for('message', check=lambda m: m.content.lower() in ['r', 'c', 'a'] and m.author == ctx.message.author)
            if msg.content.lower() == "r":
                self.c.execute('UPDATE tags SET content=?, updated=? WHERE (name=? AND server=?)', (
                    content, datetime.datetime.utcnow().timestamp(), lookup, str(ctx.guild.id)))
                self.conn.commit()
                await ctx.send('Tag "{}" updated.'.format(name))
                return
            if msg.content.lower() == "c":
                await ctx.send("Tag unchanged.")
                return
            if msg.content.lower() == "a":
                appended_tag = a[1] + "\n{}".format(content)
                if len(appended_tag) >= 2000:
                    return await ctx.send("That would make the tag too long, if you're making a tag with variables where the output would be less than 2k, use `!tag ++` and pass a pastebin instead.")
                self.c.execute('UPDATE tags SET content=?, updated=? WHERE (name=? AND server=?)', (
                    appended_tag, datetime.datetime.utcnow(), lookup, str(ctx.guild.id)))
                self.conn.commit()
                await ctx.send('Tag "{}" successfully appended.'.format(name))
                return
            else:
                return
        self.c.execute("INSERT INTO tags VALUES (?, ?, ?, ?, ?, ?, ?)", (lookup, content, str(
            ctx.guild.id), datetime.datetime.utcnow().timestamp(), datetime.datetime.utcnow().timestamp(), 0, ctx.message.author.id))
        self.c.execute('''INSERT INTO tag_lookup VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (ctx.guild.id, False, lookup, lookup, False, False, False))
        self.conn.commit()
        await ctx.send('Tag "{}" successfully created.'.format(name))

    @tag.command(aliases=['update', '&', 'e'])
    async def edit(self, ctx, name: str, *, content: str):
        """
        Skips the confirmation prompt
        """
        if ctx.message.mentions:
            return
        content = self.clean_tag_content(content)
        lookup = name.lower().strip()
        try:
            self.verify_lookup(lookup)
        except RuntimeError as e:
            return await ctx.send(e)
        self.c.execute('''SELECT points_to
                          FROM tag_lookup
                          WHERE (name=? AND server=?)''',
                          (lookup, ctx.guild.id))
        lookup = self.c.fetchone()
        if lookup is None:
            return await ctx.send("No tag or alias with that name could be found")
        lookup = lookup[0]
        a = self.c.execute(
            'SELECT * FROM tags WHERE (name=? AND server=?)', (lookup, str(ctx.guild.id)))
        a = a.fetchall()
        if a != []:
            self.c.execute('UPDATE tags SET content=?, updated=? WHERE (name=? AND server=?)', (
                content, datetime.datetime.utcnow().timestamp(), lookup, str(ctx.guild.id)))
            self.conn.commit()
            await ctx.send('Tag "{}" edited.'.format(name))
        else:
            await ctx.send("That tag doesn't seem to exist.")

    @create.error
    async def create_error(self, error, ctx):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Tag ' + str(error))

    @tag.command(name="append", aliases=['+='])
    async def _append(self, ctx, name: str, *, content: str):
        """
        Appends something to an already existing tag. Please note that a newline will be
        inserted before your text
        """
        if ctx.message.mentions:
            return
        content = self.clean_tag_content(content)
        lookup = name.lower().strip()
        a = self.c.execute(
            'SELECT * FROM tags WHERE (name=? AND server=?)', (lookup, str(ctx.guild.id)))
        a = a.fetchall()
        if a == []:
            return await ctx.send("Can't append non-existent tags")
        try:
            appended_tag = a[0][1] + "\n{}".format(content)
        except Exception as e:
            await ctx.send(e)
        if len(appended_tag) >= 2000:
            return await ctx.send("That would make the tag too long, if you're looking to create a tag with variables where the output would be less than 2k characters, use `!tag ++` and pass a pastebin link")
        self.c.execute('UPDATE tags SET content=?, updated=? WHERE (name=? AND server=?)',
                       (appended_tag, datetime.datetime.utcnow().timestamp(), lookup, str(ctx.guild.id)))
        self.conn.commit()
        await ctx.send('Tag "{}" successfully appended.'.format(name))

    def top_three_tags(self, server):
        emoji = 129351
        a = self.c.execute(
            'SELECT * FROM tags WHERE server=? ORDER BY uses DESC LIMIT 3', (server.id,))
        popular = a.fetchall()
        popular = [x for x in popular]
        for tag in popular:
            yield (chr(emoji), tag)
            emoji += 1
    def top_three_tags_user(self, user):
        emoji = 129351
        a = self.c.execute(
            'SELECT * FROM tags WHERE (author=? AND server=?) ORDER BY uses DESC LIMIT 3', (user.id, user.guild.id,))
        popular = a.fetchall()
        popular = [x for x in popular]
        for tag in popular:
            yield (chr(emoji), tag)
            emoji += 1

    @tag.command()
    async def stats(self, ctx, user: discord.Member=None):
        """
        Shows information about the tags on a server, or the tags a member owns if you mention someone
        """
        server = ctx.guild
        e = discord.Embed(title=None)
        if user is None:
            b = self.c.execute('SELECT Count(*) AS "hello" FROM tags')
            total_tags = b.fetchone()[0]
            t = self.c.execute('SELECT SUM(uses) AS "hello" FROM tags')
            total_uses = t.fetchone()[0]
            e.add_field(name='Global', value='%s tags\n%s uses' %
                        (total_tags, int(total_uses)))
            sum_of_things = self.c.execute(
                'SELECT Count(*) FROM tags WHERE server=?', (server.id,))
            a = sum_of_things.fetchone()[0]
            t = self.c.execute(
                'SELECT SUM(uses) AS "hello" FROM tags WHERE server=?', (server.id,))
            b = t.fetchone()[0]
            try:
                e.add_field(name=server.name, value='%s tags\n%s uses' %
                            (a, int(b)))
            except TypeError:
                return await ctx.send("This server doesn't seem to have any tags")
            fmt = '{} ({} uses)'
            for emoji, tag in self.top_three_tags(ctx.guild):
                e.add_field(name=emoji + ' Server Tag',
                            value=fmt.format(tag[0], int(tag[5])))

        else:
            # user-specific data, we can't guarantee that the mentioned user even has three tags created
            b = self.c.execute('SELECT Count(*) AS "hello" FROM tags WHERE (author=? AND server=?)', (user.id, ctx.guild.id))
            total_tags = b.fetchone()
            if total_tags is None:
                return await ctx.send("That user has zero tags created.")
            total_tags = total_tags[0]
            t = self.c.execute('SELECT SUM(uses) AS "hello" FROM tags WHERE (author=? AND server=?)', (user.id, ctx.guild.id))
            total_uses = t.fetchone()[0]
            e.add_field(name="Owned tags", value=total_tags)
            e.add_field(name="Owned tag usage", value=int(total_uses))
            for emoji, tag in self.top_three_tags_user(user):
                e.add_field(name=emoji + ' ' + tag[0],
                            value=f"{int(tag[5])} uses")
        await ctx.send(embed=e)



    @tag.command(aliases=['delete', '-', 'del'], no_pm=True)
    async def remove(self, ctx, *, name: str):
        '''
        When a tag is deleted, the tag and all its aliases will be deleted
        when an alias is deleted, only the alias is deleted
        '''

        lookup = name.lower()
        server = ctx.guild
        self.c.execute('''SELECT *
                          FROM tag_lookup
                          WHERE (name=? AND server=?)''',
                       (lookup, server.id))
        row = self.c.fetchone()                        
        if row is None:
            return await ctx.send("Tag not found")
        if row[1]:
            # It's an alias, just remove the reference
            self.c.execute('''DELETE FROM tag_lookup WHERE (name=? AND server=?)''', (lookup, server.id))
            self.conn.commit()
            return await ctx.send(f'Alias "{row[2]}" pointing to "{row[3]}" deleted.')
        # Since it's not an aliased tag, we know that name = points_to = lookup
        msg = 'Tag and all associated aliases successfully removed.'
        self.c.execute(
            'DELETE FROM tags WHERE (name=? AND server=?)', (lookup, server.id))
        self.conn.commit()
        # When it comes to clearing the tag_lookup, sql makes it pretty easy
        # all we need to know is which actual _tag_ we're looking for and just
        # delete all tags and aliases pointing to it
        self.c.execute('''DELETE FROM tag_lookup WHERE (points_to=? AND server=?)''', (lookup, server.id))
        self.conn.commit()
        await ctx.send(msg)

    @tag.command(aliases=['owner'])
    async def info(self, ctx, *, name: str):
        """
        Displays some nifty information about a tag
        """
        lookup = name.lower()
        server = ctx.guild
        self.c.execute('''SELECT points_to, nsfw, mod, restricted
                          FROM tag_lookup
                          WHERE (server=? AND name=?)''',
                          (ctx.guild.id, lookup))
        try:
            points_to, nsfw, mod, restricted = self.c.fetchone()
        except ValueError:
            return await ctx.send("Couldn't find a tag with that name, make sure you spelled it correctly.")
            
        self.c.execute(
            'SELECT * FROM tags WHERE (server=? AND name=?)', (str(ctx.guild.id), points_to))
        name, _, _, created, updated, uses, author = self.c.fetchone()
        self.c.execute(
            'SELECT uses FROM tags WHERE server=?', (str(ctx.guild.id),))
        rc = self.c.fetchall()
        rank = sorted([x[0] for x in rc], reverse=True).index(uses) + 1
        # Find tag aliases
        self.c.execute('''SELECT name
                          FROM tag_lookup
                          WHERE (points_to=? AND server=? AND is_alias)''',
                          (points_to, ctx.guild.id))
        list_of_aliases = self.c.fetchall()
        if not list_of_aliases:
            alias_string = "None"
        else:
            alias_string = '\n'.join(x[0] for x in list_of_aliases).replace(lookup, f"**{lookup}**")

        

        e = discord.Embed(title=name)
        e.add_field(name='Owner', value="<@{}>".format(author))
        e.add_field(name="Uses", value=int(uses))
        e.add_field(name="Rank", value=rank)
        e.add_field(name='Creation date', value=datetime.datetime.fromtimestamp(
            created).strftime("%b %d, %Y"))
        e.add_field(name='Last update', value=datetime.datetime.fromtimestamp(
            updated).strftime("%b %d, %Y"))
        prms = lambda x: ("<:redtick:318044813444251649>", "<:greentick:318044721807360010>")[x]
        e.add_field(name='Special permissions', value=f'{prms(nsfw)} nsfw\n{prms(mod)} mod\n{prms(restricted)} restricted')
        e.add_field(name='Aliases', value=alias_string)
        await ctx.send(embed=e)

    @info.error
    async def info_error(self, error, ctx):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Missing tag name to get info of.')

    @tag.command()
    async def raw(self, ctx, *, name: str):
        """
        Returns a tag without any formatting, bold text becomes **bold**
        """
        lookup = name.lower()
        self.c.execute('''SELECT points_to
                          FROM tag_lookup
                          WHERE (name=? AND server=?)''',
                       (lookup, ctx.guild.id))
        tag_name = self.c.fetchone()
        if tag_name is None:
            return await ctx.send("That tag doesn't seem to exist")
        lookup = tag_name[0]
        tag = self.c.execute(
            'SELECT * FROM tags WHERE (name=? AND server=?)', (lookup, str(ctx.guild.id)))
        tag = tag.fetchone()

        transformations = {
            re.escape(c): '\\' + c
            for c in ('*', '`', '_', '~', '\\', '<')
        }

        def replace(obj):
            return transformations.get(re.escape(obj.group(0)), '')

        pattern = re.compile('|'.join(transformations.keys()))
        await ctx.send(pattern.sub(replace, tag[1]))

    @tag.command(name='mine')
    async def _mine(self, ctx, *, member: discord.Member = None):
        """
        Shows all tags a member has created
        """
        user = ctx.message.author if member is None else member
        tags = self.c.execute(
            'SELECT name FROM tags WHERE (server=? AND author=?) ORDER BY name ASC', (str(ctx.guild.id), user.id))
        tags = tags.fetchall()
        tags = [x[0] for x in tags]
        if tags:
            try:
                if sum(len(t) for t in tags) < 1900:
                    d = ', '.join(tags)
                    await ctx.author.send(d)
                else:
                    tempmessage = []
                    finalmessage = []
                    for tag in tags:
                        if len(', '.join(tempmessage)) < 1800:
                            tempmessage.append(tag)
                        else:
                            formatted_tempmessage = ', '.join(tempmessage)
                            finalmessage.append(formatted_tempmessage)
                            tempmessage = []
                    finalmessage.append(', '.join(tempmessage))
                    for x in finalmessage:
                        if x != "":
                            await ctx.author.send(x)
            except Exception as e:
                await ctx.send(e)
        else:
            await ctx.send('This user has no tags.')

    @tag.command(name='list', no_pm=True)
    async def _list(self, ctx):
        """
        Shows you the names of all tags
        """
        tags = self.c.execute(
            'SELECT name FROM tags WHERE (server=? AND LENGTH(name) > 2) ORDER BY name ASC', (str(ctx.guild.id),))
        tags = tags.fetchall()
        tags = [x[0] for x in tags]
        if tags:
            try:
                if sum(len(t) for t in tags) < 1900:
                    d = ', '.join(tags)
                    await ctx.author.send(d)
                else:
                    tempmessage = []
                    finalmessage = []
                    for tag in tags:
                        if len(', '.join(tempmessage)) < 1800:
                            tempmessage.append(tag)
                        else:
                            formatted_tempmessage = ', '.join(tempmessage)
                            finalmessage.append(formatted_tempmessage)
                            tempmessage = []
                    finalmessage.append(', '.join(tempmessage))
                    for x in finalmessage:
                        if x != "":
                            await ctx.author.send(x)
            except Exception as e:
                await ctx.send(e)
        else:
            await ctx.send('This server has no tags.')

    @commands.command(name='taglist', aliases=['commands', 'tags'], no_pm=True)
    async def tag_list(self, ctx):
        """
        Shows you the names of all tags
        """
        tags = self.c.execute(
            'SELECT name FROM tags WHERE server=? ORDER BY name ASC', (str(ctx.guild.id),))
        tags = tags.fetchall()
        tags = [x[0] for x in tags]
        if tags:
            try:
                if sum(len(t) for t in tags) < 1900:
                    d = ', '.join(tags)
                    await ctx.author.send(d)
                else:
                    tempmessage = []
                    finalmessage = []
                    for tag in tags:
                        if len(', '.join(tempmessage)) < 1800:
                            tempmessage.append(tag)
                        else:
                            formatted_tempmessage = ', '.join(tempmessage)
                            finalmessage.append(formatted_tempmessage)
                            tempmessage = []
                    finalmessage.append(', '.join(tempmessage))
                    for x in finalmessage:
                        if x != "":
                            await ctx.author.send(x)
            except Exception as e:
                await ctx.send(e)
        else:
            await ctx.send('This server has no tags.')
    
    @tag.command()
    async def random(self, ctx):
        """
        Returns a random tag
        """
        tags = self.c.execute(
            'SELECT name, content, author, uses FROM tags WHERE server=? ORDER BY RANDOM() LIMIT 1', (ctx.guild.id,))
        tags = tags.fetchone()
        name, content, author, uses = tags
        e = discord.Embed(title="Random tag")
        e.add_field(name=f"{int(uses)} uses", value=f'<@{author}>')
        e.add_field(name=name, value=content)
        await ctx.send(embed=e)
        


    @tag.command()
    async def search(self, ctx, *, query: str):
        """
        Searches for a tag.
        The query must be at least 2 characters.
        """

        server = ctx.guild
        query = query.lower()
        if len(query) < 2:
            return await ctx.send('The query length must be at least two characters.')
        tags = self.c.execute(
            'SELECT name FROM tags WHERE (server=?  AND LENGTH(name) > 2) ORDER BY uses DESC', (server.id,))
        tags = tags.fetchall()

        results = [x[0] for x in tags]
        tagreturn = ""
        bad_var = ""
        i = 1
        if results:
            for tag in results:
                if fuzz.partial_ratio(query, tag) > 80:
                    tagreturn += "{}. {}\n".format(i, tag)
                    bad_var += "{}\n".format(tag)
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
            if len(list_of_returns) == 0:
                await ctx.send("No tags found.")
                return

            em = discord.Embed(title="Search results:",
                               description=final_list[0], colour=0x738bd7)
            em.set_author(name=ctx.message.author.name,
                          icon_url=ctx.message.author.avatar_url, url=ctx.message.author.avatar_url)
            em.set_footer(
                text="{} results. (page {}/{})".format(i - 1, 1, math.ceil((i - 1) / 15)))
            initial_message = await ctx.send(embed=em)

            def check(mesg):
                if mesg.content.isdigit():
                    return True
                elif mesg.content.startswith("p"):
                    return True
                else:
                    return False
            for p in range(5):
                msg = await self.bot.wait_for('message', check=lambda x: x.author == ctx.message.author, timeout=30.0)
                # if the message is a number, match it with the associated tag
                if msg.content.isdigit():
                    listoflines = bad_var.split('\n')
                    tag_name = listoflines[int(msg.content) - 1]
                    # tag_to_send = self.c.execute(
                    #     'SELECT content FROM tags WHERE (name=? AND server=?)', (tag_name, str(ctx.guild.id)))
                    # t = tag_to_send.fetchone()
                    # t = t[0]
                    # await ctx.send(t)
                    await self.do_tag_stuff(ctx, tag_name)

                    # await self.bot.send_message(message.channel, self.taglist[listoflines[int(msg.content)-1]])
                    # await self.bot.delete_message(initial_message)
                    return
                # this is for pages
                elif msg.content.startswith("p"):
                   # try:
                    page_number = int(msg.content[1:])
                    em2 = discord.Embed(
                        title="Search results:", description=final_list[page_number - 1], colour=0xffffff)
                    em2.set_author(name=ctx.message.author.name,
                                   icon_url=ctx.message.author.avatar_url, url=ctx.message.author.avatar_url)
                    em2.set_footer(
                        text="{} results. (page {}/{})".format(i - 1, page_number, math.ceil((i - 1) / 15)))
                    await initial_message.edit(embed=em2)
                    # except Exception as e:
                    #     print(e)
                    #     return
                else:
                    return
        else:
            await ctx.send('No tags found.')

    

    @commands.command(name="search")
    async def _search(self, ctx, *, query: str):
        """Searches for a tag.
        The query must be at least 2 characters.
        """

        server = ctx.guild
        query = query.lower()
        if len(query) < 2:
            await ctx.send('The query length must be at least two characters.')
            return

        tags = self.c.execute(
            'SELECT name FROM tags WHERE (server=?  AND LENGTH(name) > 2) ORDER BY uses DESC', (server.id,))
        tags = tags.fetchall()

        results = [x[0] for x in tags]
        tagreturn = ""
        bad_var = ""
        i = 1
        if results:
            for tag in results:
                if fuzz.partial_ratio(query, tag) > 80:
                    tagreturn += "{}. {}\n".format(i, tag)
                    bad_var += "{}\n".format(tag)
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
            if len(list_of_returns) == 0:
                return await ctx.send("No tags found.")
            em = discord.Embed(title="Search results:",
                               description=final_list[0], colour=0x738bd7)
            em.set_author(name=ctx.message.author.name,
                          icon_url=ctx.message.author.avatar_url, url=ctx.message.author.avatar_url)
            em.set_footer(
                text="{} results. (page {}/{})".format(i - 1, 1, math.ceil((i - 1) / 15)))
            initial_message = await ctx.send(embed=em)

            def check(mesg):
                if mesg.content.isdigit():
                    return True
                elif mesg.content.startswith("p"):
                    return True
                else:
                    return False
            for p in range(5):
                msg = await self.bot.wait_for('message', check=lambda x: x.author == ctx.message.author, timeout=30.0)
                # if the message is a number, match it with the associated tag
                if msg.content.isdigit():
                    listoflines = bad_var.split('\n')
                    tag_name = listoflines[int(msg.content) - 1]
                    # tag_to_send = self.c.execute(
                    #     'SELECT content FROM tags WHERE (name=? AND server=?)', (tag_name, str(ctx.guild.id)))
                    # t = tag_to_send.fetchone()
                    # t = t[0]
                    # await ctx.send(t)
                    await self.do_tag_stuff(ctx, tag_name)

                    # await self.bot.send_message(message.channel, self.taglist[listoflines[int(msg.content)-1]])
                    # await self.bot.delete_message(initial_message)
                    return
                # this is for pages
                elif msg.content.startswith("p"):
                   # try:
                    page_number = int(msg.content[1:])
                    em2 = discord.Embed(
                        title="Search results:", description=final_list[page_number - 1], colour=0xffffff)
                    em2.set_author(name=ctx.message.author.name,
                                   icon_url=ctx.message.author.avatar_url, url=ctx.message.author.avatar_url)
                    em2.set_footer(
                        text="{} results. (page {}/{})".format(i - 1, page_number, math.ceil((i - 1) / 15)))
                    await initial_message.edit(embed=em2)
                    # except Exception as e:
                    #     print(e)
                    #     return
                else:
                    return
            # msg = await self.bot.wait_for_message(author=ctx.message.author, check=lambda m: m.content.isdigit(), timeout=30.0)
            # listoflines = bad_var.split('\n')
            # if msg is not None:
            #     tag_name = listoflines[int(msg.content)-1]
            # else:
            #     return
            # server = ctx.guild
            # tag_to_send = self.c.execute('SELECT content FROM tags WHERE (name=? AND server=?)', (tag_name, server.id))
            # t = tag_to_send.fetchone()
            # t = t[0]
            # await ctx.send(t)
        else:
            await ctx.send('No tags found.')

    @search.error
    async def search_error(self, error, ctx):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Missing query to search for.')


def setup(bot):
    bot.add_cog(Tags(bot))
