import re
import json
import math
import discord
import datetime
import sqlite3
import random
import aiohttp

from fuzzywuzzy import fuzz
from discord.ext import commands
from cogs.utils.paginator import Pages
from cogs.utils import config, checks, formats
from TagScriptEngine import Engine


class Tags:
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('database.db')
        self.c = self.conn.cursor()
        self.variable_regex = re.compile(
            r'(?:\$(\d)=?((?:\w|%|{|.*?}|".*?")*)?)')
        self.random_regex = re.compile(r"(\{\{(.*?)\}\})")
        self.c.execute('''CREATE TABLE IF NOT EXISTS tags
             (name text, content text, server text, creation real, updated real, uses real, author text)''')

    def clean_tag_content(self, content):
        return content.replace('@everyone', '@\u200beveryone').replace('@here', '@\u200bhere')

    @commands.group(invoke_without_command=True)
    async def tag(self, ctx, name: str, *choices: str):
        choices = [x for x in choices if not re.match("<@!?\d*>", x)]
        print(f"choices = {choices}")
        lookup = name.lower()
        a = self.c.execute(
            'SELECT * FROM tags WHERE (name=? AND server=?)', (lookup, str(ctx.guild.id)))
        a = a.fetchall()
        ls = name.split()
        if a == []:
            return

        tag = a[0][1]

        var_results = re.findall(self.variable_regex, tag)
        if var_results != []:
            def cback(matchobj):
                group_one_number = int(matchobj.group(1))
                if group_one_number <= len(choices):
                    return choices[group_one_number - 1]
                else:
                    if matchobj.group(2) != "":
                        if matchobj.group(2).startswith('"') and matchobj.group(2).endswith('"'):
                            return matchobj.group(2)[1:-1]
                        return matchobj.group(2)
                    else:
                        return ""
            tag = re.sub(self.variable_regex, cback, tag)

        if r"%user" in tag:
            user = ctx.message.mentions[0] if ctx.message.mentions != [
            ] else ctx.message.author
            tag = tag.replace(r"%user", user.display_name)
        if r"%author" in tag:
            tag = tag.replace(r"%author", ctx.message.author.display_name)
        if r"%channel" in tag:
            channel = ctx.message.channel_mentions[0] if ctx.message.channel_mentions != [
            ] else ctx.message.channel
            tag = tag.replace(r"%channel", channel.name)
        if r"%server" in tag:
            tag = tag.replace(r"%server", ctx.guild.name)
        if r"%nauthor" in tag:
            tag = tag.replace(r"%nauthor", ctx.message.author.name)
        if r"%nuser" in tag:
            user = ctx.message.mentions[0] if ctx.message.mentions != [
            ] else ctx.message.author
            tag = tag.replace(r"%nuser", user.name)
        if r"%mention" in tag:
            if ctx.message.mentions:
                user = ctx.message.mentions[0] if ctx.message.mentions != [
                ] else ctx.message.author
                tag = tag.replace(r"%mention", user.name)
            else:
                tag = tag.replace(r"%mention", "")
        if r"%nmention" in tag:
            if ctx.message.mentions:
                user = ctx.message.mentions[0] if ctx.message.mentions != [
                ] else ctx.message.author
                tag = tag.replace(r"%nmention", user.name)
            else:
                tag = tag.replace(r"%nmention", "")

        results = re.findall(self.random_regex, tag)
        if results != []:
            def callback(matchobj):
                print(matchobj.group(2))
                print([s.strip('{} ') for s in matchobj.group(2).split(',')])
                # return random.choice([s.strip('{} ') for s in matchobj.group(2).split(',')])
                return random.choice(matchobj.group(2).split(',')).lstrip()
            tag = re.sub(self.random_regex, callback, tag)

        tag = self.clean_tag_content(tag)

        self.c.execute(
            'UPDATE tags SET uses = uses + 1 WHERE (name=? AND server=?)', (lookup, str(ctx.guild.id)))
        self.conn.commit()
        await ctx.send(tag)

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

    @tag.command(aliases=['++'])
    @checks.admin_or_permissions(manage_server=True)
    async def procreate(self, ctx, name: str, *, content: str):
        if ctx.message.mentions:
            return
        match = re.findall("https:\/\/pastebin.com\/(?:raw\/)?(.*)", content)
        print(match)
        if not match:
            await ctx.send("You need to pass in a pastebin link")
            return
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://pastebin.com/raw/{match[0]}') as res:
                content = await res.text()
                print(content)
        content = self.clean_tag_content(content)
        lookup = name.lower().strip()
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
            self.conn.commit()
            await ctx.send(f'Tag "{name}" successfully {word}.')

    @tag.command(aliases=['add', '+'])
    async def create(self, ctx, name: str, *, content: str):
        if ctx.message.mentions:
            return
        content = self.clean_tag_content(content)
        lookup = name.lower().strip()
        try:
            self.verify_lookup(lookup)
        except RuntimeError as e:
            return await ctx.send(e)
        a = self.c.execute(
            'SELECT * FROM tags WHERE (name=? AND server=?)', (lookup, str(ctx.guild.id)))
        a = a.fetchall()
        if a != []:
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
                print(a[0][1])
                appended_tag = a[0][1] + "\n{}".format(content)
                if len(appended_tag) >= 2000:
                    return await ctx.send("That would make the tag too long")
                self.c.execute('UPDATE tags SET content=?, updated=? WHERE (name=? AND server=?)', (
                    appended_tag, datetime.datetime.utcnow(), lookup, str(ctx.guild.id)))
                self.conn.commit()
                await ctx.send('Tag "{}" successfully appended.'.format(name))
                return
            else:
                return
        self.c.execute("INSERT INTO tags VALUES (?, ?, ?, ?, ?, ?, ?)", (lookup, content, str(
            ctx.guild.id), datetime.datetime.utcnow().timestamp(), datetime.datetime.utcnow().timestamp(), 0, ctx.message.author.id))
        self.conn.commit()
        await ctx.send('Tag "{}" successfully created.'.format(name))

    @tag.command(aliases=['update', '&'])
    async def edit(self, ctx, name: str, *, content: str):
        if ctx.message.mentions:
            return
        content = self.clean_tag_content(content)
        lookup = name.lower().strip()
        try:
            self.verify_lookup(lookup)
        except RuntimeError as e:
            return await ctx.send(e)
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
            return await ctx.send("That would make the tag too long")
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

    @tag.command()
    async def stats(self, ctx):
        server = ctx.guild
        e = discord.Embed(title=None)

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

        await ctx.send(embed=e)

    @tag.command(aliases=['delete', '-', 'del'], no_pm=True)
    async def remove(self, ctx, *, name: str):
        lookup = name.lower()
        server = ctx.guild
        tag = self.c.execute(
            'SELECT * FROM tags WHERE (name=? AND server=?)', (lookup, server.id))
        if tag.fetchall() == []:
            return await ctx.send("Tag not found")

        msg = 'Tag successfully removed.'
        self.c.execute(
            'DELETE FROM tags WHERE (name=? AND server=?)', (lookup, server.id))
        self.conn.commit()
        await ctx.send(msg)

    @tag.command(aliases=['owner'])
    async def info(self, ctx, *, name: str):
        lookup = name.lower()
        server = ctx.guild
        a = self.c.execute(
            'SELECT * FROM tags WHERE (server=? AND name=?)', (str(ctx.guild.id), lookup))
        name, _, _, created, updated, uses, author = a.fetchall()[0]
        r = self.c.execute(
            'SELECT uses FROM tags WHERE server=?', (str(ctx.guild.id),))
        rc = r.fetchall()
        rank = sorted([x[0] for x in rc], reverse=True).index(uses) + 1

        e = discord.Embed(title=name)
        e.add_field(name='Owner', value="<@{}>".format(author))
        e.add_field(name="Uses", value=int(uses))
        e.add_field(name="Rank", value=rank)
        e.add_field(name='Creation date', value=datetime.datetime.fromtimestamp(
            created).strftime("%b %d, %Y"))
        e.add_field(name='Last update', value=datetime.datetime.fromtimestamp(
            updated).strftime("%b %d, %Y"))

        await ctx.send(embed=e)

    @info.error
    async def info_error(self, error, ctx):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Missing tag name to get info of.')

    @tag.command()
    async def raw(self, ctx, *, name: str):
        lookup = name.lower()
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
    async def search(self, ctx, *, query: str):
        """Searches for a tag.
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
                    tag_to_send = self.c.execute(
                        'SELECT content FROM tags WHERE (name=? AND server=?)', (tag_name, str(ctx.guild.id)))
                    t = tag_to_send.fetchone()
                    t = t[0]
                    await ctx.send(t)

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
                    await self.bot.edit_message(initial_message, embed=em2)
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
                    tag_to_send = self.c.execute(
                        'SELECT content FROM tags WHERE (name=? AND server=?)', (tag_name, str(ctx.guild.id)))
                    t = tag_to_send.fetchone()
                    t = t[0]
                    await ctx.send(t)

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
                    await self.bot.edit_message(initial_message, embed=em2)
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
