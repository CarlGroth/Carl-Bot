import re
import json
import math
import discord
import datetime
import sqlite3

from fuzzywuzzy import fuzz
from discord.ext import commands
from cogs.utils.paginator import Pages
from cogs.utils import config, checks, formats
from cogs.mod import *



class Tags:
    def __init__(self, bot):
        self.bot = bot
        self.modconfig = config.Config('mod.json', loop=bot.loop, object_hook=object_hook, encoder=RaidModeEncoder)
        self.conn = sqlite3.connect('database.db')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS tags
             (name text, content text, server text, creation real, updated real, uses real, author text)''')


    def clean_tag_content(self, content):
        return content.replace('@everyone', '@\u200beveryone').replace('@here', '@\u200bhere')
    

    def is_plonked(self, server, member):
        db = self.modconfig.get('plonks', {}).get(server.id, [])
        bypass_ignore = member.server_permissions.manage_server
        if not bypass_ignore and member.id in db:
            return True
        return False

    async def on_message(self, message):
        if message.author.id == self.bot.client_id:
            return
        if message.channel.is_private:
            return
        if message.author.id == "290321689286279168":
            return
        if message.attachments:
            return
        if message.content == "":
            return
        if self.is_plonked(message.server, message.author):
            return False

        command = message.content.split()
        command = command[0]
        if command[:1] not in ["§", "?", "!", "computer, "]:
            return
        command = command[1:]
        command = command.lower()
        if message.content[1:4] == "tag":
            return
        if command in self.bot.commands:
            return
        name = message.content[1:]
        lookup = name.lower()
        server = message.server
        
        tag = self.c.execute('SELECT content FROM tags WHERE (name=? AND server=?)', (lookup, server.id))
        tag = tag.fetchall()
        if tag == []:
            return
        await self.bot.send_message(message.channel, tag[0][0])
        self.c.execute('UPDATE tags SET uses = uses + 1 WHERE (name=? AND server=?)', (lookup, server.id))
        self.conn.commit()

       


    @commands.group(pass_context=True, invoke_without_command=True)
    async def tag(self, ctx, *, name : str):        
        lookup = name.lower()
        a = self.c.execute('SELECT * FROM tags WHERE (name=? AND server=?)', (lookup, ctx.message.server.id))
        a = a.fetchall()
        if a == []:
            await self.bot.say("No tag named {} could be found.".format(lookup.replace("@", "@\u200b")))
            return

        tag = a[0][1]


        self.c.execute('UPDATE tags SET uses = uses + 1 WHERE (name=? AND server=?)', (lookup, ctx.message.server.id))
        self.conn.commit()
        await self.bot.say(tag)
    @tag.error
    async def tag_error(self, error, ctx):
        if isinstance(error, commands.MissingRequiredArgument):
            await self.bot.say('You need to pass in a tag name.')
    
    def verify_lookup(self, lookup):
        if '@everyone' in lookup or '@here' in lookup:
            raise RuntimeError('That tag is using blocked words.')
    
        if not lookup:
            raise RuntimeError('You need to actually pass in a tag name.')
        
        if len(lookup) > 50:
            raise RuntimeError('Tag name is a maximum of 50 characters.')
    @tag.command(pass_context=True, aliases=['add', '+'])
    async def create(self, ctx, name : str, *, content : str):
        if ctx.message.mentions:
            return
        content = self.clean_tag_content(content)
        lookup = name.lower().strip()
        try:
            self.verify_lookup(lookup)
        except RuntimeError as e:
            return await self.bot.say(e)
        location = self.get_database_location(ctx.message)
        db = self.config.get(location, {})
        a = self.c.execute('SELECT * FROM tags WHERE (name=? AND server=?)', (lookup, ctx.message.server.id))
        a = a.fetchall()
        if a != []:
            await self.bot.say("Tag already exists. **__r__**eplace, **__c__**ancel or **__a__**dd to? (r/c/a)")
            msg = await self.bot.wait_for_message(author=ctx.message.author, check=lambda m: m.content.lower() in ['r', 'c', 'a'])
            if msg.content.lower() == "r":
                self.c.execute('UPDATE tags SET content=? WHERE (name=? AND server=?)', (content, lookup, ctx.message.server.id))
                self.conn.commit()
                await self.bot.say('Tag "{}" successfully updated.'.format(name))
                return
            if msg.content.lower() == "c":
                await self.bot.say("Tag unchanged.")
                return
            if msg.content.lower() == "a":
                print(a[0][1])
                appended_tag = a[0][1] + "\n{}".format(content)
                if len(appended_tag) >= 2000:
                    return await self.bot.say("That would make the tag too long")
                self.c.execute('UPDATE tags SET content=? WHERE (name=? AND server=?)', (appended_tag, lookup, ctx.message.server.id))
                self.c.execute('UPDATE tags SET updated=? WHERE (name=? AND server=?)', (datetime.datetime.utcnow().timestamp(), lookup, ctx.message.server.id))
                self.conn.commit()
                await self.bot.say('Tag "{}" successfully appended.'.format(name))
                return
            else:
                return
        self.c.execute("INSERT INTO tags VALUES (?, ?, ?, ?, ?, ?, ?)", (lookup, content, ctx.message.server.id, datetime.datetime.utcnow().timestamp(), datetime.datetime.utcnow().timestamp(), 0, ctx.message.author.id))
        self.conn.commit()
        await self.bot.say('Tag "{}" successfully created.'.format(name))

    @create.error
    async def create_error(self, error, ctx):
        if isinstance(error, commands.MissingRequiredArgument):
            await self.bot.say('Tag ' + str(error))

    @tag.command(pass_context=True, name="append", aliases=['+='])
    async def _append(self, ctx, name : str, *, content : str):
        content = self.clean_tag_content(content)
        lookup = name.lower().strip()
        a = self.c.execute('SELECT * FROM tags WHERE (name=? AND server=?)', (lookup, ctx.message.server.id))
        a = a.fetchall()
        if a == []:
            return await self.bot.say("Can't append non-existent tags")
        try:
            appended_tag = a[0][1] + "\n{}".format(content)
        except Exception as e:
            await self.bot.say(e)
        if len(appended_tag) >= 2000:
            return await self.bot.say("That would make the tag too long")
        self.c.execute('UPDATE tags SET content=?, updated=? WHERE (name=? AND server=?)', (appended_tag, datetime.datetime.utcnow().timestamp(), lookup, ctx.message.server.id))
        self.conn.commit()
        await self.bot.say('Tag "{}" successfully appended.'.format(name))
        





    def top_three_tags(self, server):
        emoji = 129351
        a = self.c.execute('SELECT * FROM tags WHERE server=? ORDER BY uses DESC LIMIT 3', (server.id,))
        popular = a.fetchall()
        popular = [x for x in popular]
        for tag in popular:
            yield (chr(emoji), tag)
            emoji += 1


    @tag.command(pass_context=True)
    async def stats(self, ctx):
        server = ctx.message.server
        e = discord.Embed(title=None)
        
        
        b = self.c.execute('SELECT Count(*) AS "hello" FROM tags')
        total_tags = b.fetchone()[0]
        t = self.c.execute('SELECT SUM(uses) AS "hello" FROM tags')
        total_uses = t.fetchone()[0]
        e.add_field(name='Global', value='%s tags\n%s uses' % (total_tags, int(total_uses)))
        sum_of_things = self.c.execute('SELECT Count(*) FROM tags WHERE server=?', (server.id,))
        a = sum_of_things.fetchone()[0]
        t = self.c.execute('SELECT SUM(uses) AS "hello" FROM tags WHERE server=?', (server.id,))
        b = t.fetchone()[0]
        try:            
            e.add_field(name=server.name, value='%s tags\n%s uses' % (a, int(b)))
        except TypeError:
            return await self.bot.say("This server doesn't seem to have any tags")
        fmt = '{} ({} uses)'
        for emoji, tag in self.top_three_tags(ctx.message.server):
            e.add_field(name=emoji + ' Server Tag', value=fmt.format(tag[0], int(tag[5])))
        
        await self.bot.say(embed=e)



    @tag.command(pass_context=True, aliases=['delete', '-', 'del'], no_pm=True)
    async def remove(self, ctx, *, name : str):
        lookup = name.lower()
        server = ctx.message.server
        tag = self.c.execute('SELECT * FROM tags WHERE (name=? AND server=?)', (lookup, server.id))
        if tag.fetchall() == []:
            return await self.bot.say("Tag not found")
        

        msg = 'Tag successfully removed.'
        self.c.execute('DELETE FROM tags WHERE (name=? AND server=?)', (lookup, server.id))
        self.conn.commit()
        await self.bot.say(msg)

    @tag.command(pass_context=True, aliases=['owner'])
    async def info(self, ctx, *, name : str):
        lookup = name.lower()
        server = ctx.message.server
        a = self.c.execute('SELECT * FROM tags WHERE (server=? AND name=?)', (ctx.message.server.id, lookup))
        name, _, _, created, updated, uses, author = a.fetchall()[0]
        r = self.c.execute('SELECT uses FROM tags WHERE server=?', (ctx.message.server.id,))
        rc = r.fetchall()
        rank = sorted([x[0] for x in rc], reverse=True).index(uses)+1

        e = discord.Embed(title=name)
        e.add_field(name='Owner', value="<@{}>".format(author))
        e.add_field(name="Uses", value=int(uses))
        e.add_field(name="Rank", value=rank)
        e.add_field(name='Creation date', value=datetime.datetime.fromtimestamp(created).strftime("%b %d, %Y"))
        e.add_field(name='Last update', value=datetime.datetime.fromtimestamp(updated).strftime("%b %d, %Y"))

        await self.bot.say(embed=e)


    @info.error
    async def info_error(self, error, ctx):
        if isinstance(error, commands.MissingRequiredArgument):
            await self.bot.say('Missing tag name to get info of.')
        
    @tag.command(pass_context=True)
    async def raw(self, ctx, *, name : str):
        lookup = name.lower()
        server = ctx.message.server
        tag = self.c.execute('SELECT * FROM tags WHERE (name=? AND server=?)', (lookup, server.id))
        tag = tag.fetchone()


        transformations = {
            re.escape(c): '\\' + c
            for c in ('*', '`', '_', '~', '\\', '<')
        }
        def replace(obj):
            return transformations.get(re.escape(obj.group(0)), '')

        pattern = re.compile('|'.join(transformations.keys()))
        await self.bot.say(pattern.sub(replace, tag[1]))

    @tag.command(name='mine', pass_context=True)
    async def _mine(self, ctx, *, member : discord.Member = None):
        user = ctx.message.author if member is None else member
        tags = self.c.execute('SELECT name FROM tags WHERE (server=? AND author=?) ORDER BY name ASC', (ctx.message.server.id, user.id))
        tags = tags.fetchall()
        tags = [x[0] for x in tags]
        if tags:
            try:
                if sum(len(t) for t in tags) < 1900:
                    d = ', '.join(tags)
                    await self.bot.send_message(ctx.message.author, d)
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
                            await self.bot.send_message(ctx.message.author, x)
            except Exception as e:
                await self.bot.say(e)
        else:
            await self.bot.say('This user has no tags.')


    @tag.command(name='list', pass_context=True, no_pm=True)
    async def _list(self, ctx):
        tags = self.c.execute('SELECT name FROM tags WHERE (server=?) ORDER BY name ASC', (ctx.message.server.id,))
        tags = tags.fetchall()
        tags = [x[0] for x in tags]
        if tags:
            try:
                if sum(len(t) for t in tags) < 1900:
                    d = ', '.join(tags)
                    await self.bot.send_message(ctx.message.author, d)
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
                            await self.bot.send_message(ctx.message.author, x)
            except Exception as e:
                await self.bot.say(e)
        else:
            await self.bot.say('This server has no tags.')
    
    @commands.command(name='taglist', aliases=['commands', 'tags'], pass_context=True, no_pm=True)
    async def tag_list(self, ctx):
        tags = self.c.execute('SELECT name FROM tags WHERE (server=?) ORDER BY name ASC', (ctx.message.server.id,))
        tags = tags.fetchall()
        tags = [x[0] for x in tags]
        if tags:
            try:
                if sum(len(t) for t in tags) < 1900:
                    d = ', '.join(tags)
                    await self.bot.send_message(ctx.message.author, d)
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
                            await self.bot.send_message(ctx.message.author, x)
            except Exception as e:
                await self.bot.say(e)
        else:
            await self.bot.say('This server has no tags.')


    
    @tag.command(pass_context=True, no_pm=True)
    @checks.is_owner()
    async def purge(self, ctx, member : discord.Member):
        tags = self.c.execute('SELECT * FROM tags WHERE author=?', (member.id,))
        tags = tags.fetchall()
        
        if not ctx.message.channel.permissions_for(ctx.message.server.me).add_reactions:
            return await self.bot.say('Bot cannot add reactions.')

        if not tags:
            return await self.bot.say('This user has no tags.')

        msg = await self.bot.say('This will delete %s tags are you sure? **This action cannot be reversed**.\n\n' \
'React with either \N{WHITE HEAVY CHECK MARK} to confirm or \N{CROSS MARK} to deny.' % len(tags))
        
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

        self.c.execute('DELETE FROM tags WHERE (author=? AND server=?)', (author_id, ctx.message.server.id))
        self.conn.commit()
        await self.bot.delete_message(msg)
        await self.bot.say('Successfully removed all %s tags that belong to %s' % (len(tags), member.display_name))





    @tag.command(pass_context=True)
    async def search(self, ctx, *, query : str):
        """Searches for a tag.
        The query must be at least 2 characters.
        """

        server = ctx.message.server
        query = query.lower()
        if len(query) < 2:
            return await self.bot.say('The query length must be at least two characters.')
        tags = self.c.execute('SELECT name FROM tags WHERE server=? ORDER BY uses DESC', (server.id,))
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

            em = discord.Embed(title="Search results:", description=final_list[0], colour=0x738bd7)
            em.set_author(name=ctx.message.author.name, icon_url=ctx.message.author.avatar_url, url=ctx.message.author.avatar_url)
            em.set_footer(text="{} results. (page {}/{})".format(i-1, 1, math.ceil((i-1)/15)))
            initial_message = await self.bot.say(embed=em)
            msg = await self.bot.wait_for_message(author=ctx.message.author, check=lambda m: m.content.isdigit(), timeout=30.0)
            listoflines = bad_var.split('\n')
            if msg is not None:
                tag_name = listoflines[int(msg.content)-1]
            else:
                return
            server = ctx.message.server
            tag_to_send = self.c.execute('SELECT content FROM tags WHERE (name=? AND server=?)', (tag_name, server.id))
            t = tag_to_send.fetchone()
            t = t[0]
            await self.bot.say(t)
        else:
            await self.bot.say('No tags found.')


    @commands.command(pass_context=True, name="search")
    async def _search(self, ctx, *, query : str):
        """Searches for a tag.
        The query must be at least 2 characters.
        """

        server = ctx.message.server
        query = query.lower()
        if len(query) < 2:
            return await self.bot.say('The query length must be at least two characters.')

        tags = self.c.execute('SELECT name FROM tags WHERE server=? ORDER BY uses DESC', (server.id,))
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

            em = discord.Embed(title="Search results:", description=final_list[0], colour=0x738bd7)
            em.set_author(name=ctx.message.author.name, icon_url=ctx.message.author.avatar_url, url=ctx.message.author.avatar_url)
            em.set_footer(text="{} results. (page {}/{})".format(i-1, 1, math.ceil((i-1)/15)))
            initial_message = await self.bot.say(embed=em)
            msg = await self.bot.wait_for_message(author=ctx.message.author, check=lambda m: m.content.isdigit(), timeout=30.0)
            listoflines = bad_var.split('\n')
            if msg is not None:
                tag_name = listoflines[int(msg.content)-1]
            else:
                return
            server = ctx.message.server
            tag_to_send = self.c.execute('SELECT content FROM tags WHERE (name=? AND server=?)', (tag_name, server.id))
            t = tag_to_send.fetchone()
            t = t[0]
            await self.bot.say(t)
        else:
            await self.bot.say('No tags found.')

    @search.error
    async def search_error(self, error, ctx):
        if isinstance(error, commands.MissingRequiredArgument):
            await self.bot.say('Missing query to search for.')




def setup(bot):
    bot.add_cog(Tags(bot))
    