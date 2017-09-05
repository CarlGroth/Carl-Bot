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
from stemming.porter2 import stem


class ChannelOrMember(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            return await commands.TextChannelConverter().convert(ctx, argument)
        except commands.BadArgument:
            return await commands.MemberConverter().convert(ctx, argument)


class Highlight:
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('database.db')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS highlight
             (author text, highlights text, guild_id text)''')
        self.last_seen = {}
        self.regex_pattern = re.compile('([^\s\w]|_)+')
        self.website_regex = re.compile("https?:\/\/[^\s]*")

    @commands.group(invoke_without_command=False, aliases=['hl'], no_pm=True)
    async def highlight(self, ctx):
        pass

    @highlight.command(name="block", aliases=['ignore'], no_pm=True)
    async def highlight_block(self, ctx, *blocks: ChannelOrMember):
        if ctx.guild is None:
            return
        print(blocks)
        a = self.c.execute(
            '''SELECT highlight_ignores FROM userconfig WHERE (guild_id=? AND user_id=?)''', (ctx.guild.id, ctx.author.id))
        a = a.fetchone()[0]
        print(a)
        if a is None:
            # no ignored channels, just chuck them in there
            if len(blocks) == 0:
                # no mention = block current channel
                self.c.execute('UPDATE userconfig SET highlight_ignores=? WHERE (guild_id=? AND user_id=?)', (
                    ctx.channel.id, ctx.guild.id, ctx.author.id))
                self.conn.commit()
                await ctx.send('👌')
            else:
                new_blocks = ','.join([str(x.id)
                                       for x in blocks if x is not None])

                self.c.execute('UPDATE userconfig SET highlight_ignores=? WHERE (guild_id=? AND user_id=?)', (
                    new_blocks, ctx.guild.id, ctx.author.id))
                self.conn.commit()
                await ctx.send("👌")
        else:
            a = str(a)
            already_blocked = a.split(',')
            if len(blocks) == 0:
                blocks = [ctx.channel]
            new_blocks = [str(x.id) for x in blocks if (
                str(x.id) not in already_blocked and x is not None)]
            new_blocks.extend(already_blocked)
            new_blocks = ','.join(new_blocks)
            self.c.execute('UPDATE userconfig SET highlight_ignores=? WHERE (guild_id=? AND user_id=?)',
                           (new_blocks, ctx.guild.id, ctx.author.id))
            self.conn.commit()
            await ctx.send("👌")

    # @highlight.command(name="unblock", aliases=['unignore'])
    # async def highlight_block(self, ctx, *blocks: ChannelOrMember):

    @highlight.command(name="add", aliases=['+'], no_pm=True)
    async def highlight_add(self, ctx, *, word: str=None):
        word = word.lower()
        word = stem(word)
        if ctx.guild is None:
            return
        if ctx.message.mentions:
            return await ctx.send("Can't have any mentions")
        if "@everyone" in ctx.message.content:
            return await ctx.send("Fuck off")
        if "@here" in ctx.message.content:
            return await ctx.send("Fuck off")
        if word is None:
            return await ctx.send("You need to specify a word to add")
        if len(word) < 2:
            return await ctx.send("Word needs to be at least 2 characters long")
        if len(word) > 50:
            return await ctx.send("50 characters or less please")
        a = self.c.execute(
            'SELECT highlights FROM highlight WHERE (author=? AND guild_id=?)', (ctx.author.id, ctx.guild.id))
        a = a.fetchall()
        print(a)
        if len(a) == 0:
            self.c.execute('''INSERT INTO highlight VALUES(?, ?, ?)''',
                           (ctx.author.id, word, ctx.guild.id))
            self.conn.commit()
            await ctx.send(f"Added {word} to your highlights")
        else:
            already_registered = [x[0] for x in a]
            if word in already_registered:
                return await ctx.send(f"'{word}' is already highlighted for you")
            else:
                self.c.execute('''INSERT INTO highlight VALUES(?, ?, ?)''',
                               (ctx.author.id, word, ctx.guild.id))
                self.conn.commit()
                await ctx.send(f"{word} added to highlights")

    @highlight.command(name="clear", aliases=['purge'], no_pm=True)
    async def highlight_clear(self, ctx):
        if ctx.guild is None:
            return
        self.c.execute('DELETE FROM highlight WHERE (author=? AND guild_id=?)',
                       (ctx.author.id, ctx.guild.id))
        self.conn.commit()
        await ctx.send("Removed all your highlighted words 👌")

    @highlight.command(name="remove", aliases=['-'], no_pm=True)
    async def highlight_remove(self, ctx, *, word: str):
        if ctx.guild is None:
            return
        self.c.execute('DELETE FROM highlight WHERE (author=? AND guild_id=? AND highlights=?)',
                       (ctx.author.id, ctx.guild.id, word))
        self.conn.commit()
        await ctx.send(f"Removed {word} from your highlighted words 👌")

    @highlight.command(name="show", aliases=['display'], no_pm=True)
    async def highlight_show(self, ctx):
        if ctx.guild is None:
            return
        a = self.c.execute(
            'SELECT highlights FROM highlight WHERE (guild_id=? AND author=?)', (ctx.guild.id, ctx.author.id))
        a = a.fetchall()
        if len(a) != 0:
            return await ctx.send("You're currently tracking the following words:\n{}".format('\n'.join([x[0] for x in a])))
        await ctx.send(f"You're not tracking any words yet, use `{ctx.prefix}highlight add <word>` to start tracking")

    @highlight.command(name="unblock", aliases=['unignore'], no_pm=True)
    async def highlight_unblock(self, ctx, *blocks: ChannelOrMember):
        if ctx.guild is None:
            return
        a = self.c.execute(
            '''SELECT highlight_ignores FROM userconfig WHERE (guild_id=? AND user_id=?)''', (ctx.guild.id, ctx.author.id))
        a = a.fetchone()[0]
        print(f"a = {a}")
        if a == "":
            a = None
        if a is None:
            return await ctx.send("You're not ignoring anything yet (on this server at least)")
        else:
            a = str(a)
            print(a)
            # We can't remove more channels than we already have
            # the final block list will consist of previous bans
            # with the newly mentioned ones removed. Because of
            # this, we use the previously blocked channels as a
            # "base" for our operations
            # [a, b] - [a, c] = [b]
            #   a         b      c
            # c = [x for x in a if x not in b]
            already_blocked = a.split(',')
            if len(blocks) == 0:
                blocks = [ctx.channel]
            unblocks = [str(x.id) for x in blocks if x is not None]
            new_blocks = [x for x in already_blocked if (
                x not in unblocks and x is not None)]
            print(f"new blocks={new_blocks}")
            if len(new_blocks) == 0 or new_blocks is None:
                # Makes things easier, avoids empty splits too
                self.c.execute('UPDATE userconfig SET highlight_ignores=? WHERE (guild_id=? AND user_id=?)', (
                    None, ctx.guild.id, ctx.author.id))
                self.conn.commit()
                return await ctx.send("👌")
            new_blocks = ','.join(new_blocks)
            self.c.execute('UPDATE userconfig SET highlight_ignores=? WHERE (guild_id=? AND user_id=?)',
                           (new_blocks, ctx.guild.id, ctx.author.id))
            self.conn.commit()
            await ctx.send("👌")

    async def generate_context(self, msg, hl):
        fmt = []
        async for m in msg.channel.history(limit=5):
            time = m.created_at.strftime("%H:%M:%S")
            fmt.append(f"**[{time}] {m.author.name}:** {m.content[:200]}")
        e = discord.Embed(title=f"**{hl}**", description='\n'.join(fmt[::-1]))
        return e

    async def on_message(self, message):
        self.last_seen[message.author.id] = datetime.datetime.utcnow()
        if message.guild is None:
            return
        if message.author.bot:
            return

        a = self.c.execute(
            'SELECT highlights,author FROM highlight WHERE guild_id=?', (message.guild.id,))
        a = a.fetchall()
        final_message = self.website_regex.sub('', message.content.lower())
        final_message = self.regex_pattern.sub('', final_message)
        final_message = [stem(x) for x in final_message.split()]
        print(final_message)
        for k, v in a:
            local_last_seen = self.last_seen.get(
                int(v), datetime.datetime.fromtimestamp(1503612000))
            if (datetime.datetime.utcnow() - local_last_seen).total_seconds() < 600:
                print("not sending")
                continue
            if stem(k.lower()) in final_message and message.author.id != int(v):
                b = self.c.execute(
                    'SELECT highlight_ignores FROM userconfig WHERE (guild_id=? AND user_id=?)', (message.guild.id, v))
                b = b.fetchone()[0]
                print(f"Should I block? {b}")
                if b is not None:
                    all_ignored_stuff = b.split(',')
                    all_ignored_stuff = [int(x) for x in all_ignored_stuff]
                    if message.channel.id in all_ignored_stuff:
                        continue
                    if message.author.id in all_ignored_stuff:
                        continue
                e = await self.generate_context(message, k)
                usr = message.guild.get_member(int(v))
                if message.channel.permissions_for(usr).read_messages:
                    ctx = await self.bot.get_context(message)
                    if ctx.prefix is not None:
                        continue
                    await usr.send(f'In <#{message.channel.id}>, you were mentioned with highlight word "{k}"', embed=e)


def setup(bot):
    bot.add_cog(Highlight(bot))
