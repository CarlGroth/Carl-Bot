import json
import discord
import asyncio
import inspect
import datetime
import time
import re
import sqlite3

from discord.ext import commands
from cogs.utils import checks
from discord.ext.commands.cooldowns import BucketType


class Bio:

    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('database.db')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS bio
             (owner text, content text, server text, creation real, updated real, uses real)''')

    def clean_bio_content(self, content):
        return content.replace('@everyone', '@\u200beveryone').replace('@here', '@\u200bhere')

    @commands.group(invoke_without_command=True)
    async def bio(self, ctx, *, member: discord.Member = None):
        owner = ctx.author if member is None else member
        bio = self.c.execute(
            'SELECT content FROM bio WHERE (server=? AND owner=?)', (ctx.guild.id, owner.id))
        bio = bio.fetchall()
        if bio == []:
            return await ctx.send("User has not set a bio\nTo set a bio use `!bio + <content>`, no mentions!")
        else:
            bio = bio[0][0]
            print(bio)
            self.c.execute(
                'UPDATE bio SET uses = uses + 1 WHERE (server=? AND owner=?)', (ctx.guild.id, owner.id))
            self.conn.commit()

        if len(bio) < 1250:
            if not "bot" in ctx.channel.name:
                # this is pretty dumb
                # but fuck your long ass bios
                LINK_REGEX = re.compile(r"(https?://.*)")
                bio = re.sub(LINK_REGEX, r"<\1>", str(bio))
                bio = bio.replace(" >", ">")
            await ctx.send("**Bio for {0}:**\n{1}".format(owner.name, bio))
        else:
            try:
                destination = discord.utils.find(
                    lambda m: "bot" in m.name, ctx.guild.channels)
                xd = await destination.send(ctx.message.author.mention)
            except:
                destination = ctx.message.channel
            listOfLines = bio.splitlines()
            tempmessage = "**Bio for {0}:**\n".format(owner.name)
            finalmessage = []
            if owner.id == 158370770068701184:
                # this is a kintark special
                # just to circumvent the 5 embed limit
                # probably api abuse
                linenr = 1
                for line in listOfLines:
                    if linenr < 5:
                        linenr += 1
                        tempmessage += "{}\n".format(line)
                    else:
                        finalmessage.append(tempmessage)
                        tempmessage = ""
                        linenr = 1
                        try:
                            tempmessage += "{}\n".format(line)
                        except Exception as e:
                            print(e)
            else:
                for line in listOfLines:
                    if len("{}{}".format(tempmessage, line)) < 1800:
                        tempmessage += "{}\n".format(line)
                    else:
                        finalmessage.append(tempmessage)
                        tempmessage = ""
                        linenr = 1
                        try:
                            tempmessage += "{}\n".format(line)
                        except Exception as e:
                            print(e)
            finalmessage.append(tempmessage)
            # finalmessage is a list of <2000 character long strings
            # this is pretty much here only to be annoying
            for x in finalmessage:
                if x is not None:
                    await destination.send(x)
                    await asyncio.sleep(1)

    @bio.command(name="append", aliases=["+="])
    async def _append(self, ctx, *, content: str):
        """
        Adding content to a bio without redoing it is nice when you just want to add a small accomplishment
        it is however essential if you're a bio abuser like kintark since you literally can't insert a bio this big
        otherwise
        """

        content = self.clean_bio_content(content)
        lookup = ctx.message.author.id
        a = self.c.execute(
            'SELECT content FROM bio WHERE (owner=? AND server=?)', (lookup, ctx.guild.id))
        a = a.fetchall()
        if a == []:
            return await ctx.send("Can't append to bios that don't exist.")

        bio = a[0][0] + "\n{}".format(content)
        self.c.execute('UPDATE bio SET content=?, updated=? WHERE (owner=? AND server=?)',
                       (bio, datetime.datetime.utcnow().timestamp(), lookup, ctx.guild.id))
        self.conn.commit()
        await ctx.send('Bio for {} successfully updated.'.format(ctx.message.author.name))

    @bio.command(aliases=['add', '+'])
    async def create(self, ctx, *, content: str):
        content = self.clean_bio_content(content)
        lookup = ctx.message.author.id
        a = self.c.execute(
            'SELECT * FROM bio WHERE (owner=? AND server=?)', (lookup, ctx.guild.id))
        a = a.fetchall()
        if a != []:
            await ctx.send("Bio already exists. **__r__**eplace, **__c__**ancel or **__a__**dd to? (r/c/a)")
            msg = await self.bot.wait_for('message', check=lambda x: x.author == ctx.author, timeout=30.0)
            if msg.content.lower() in ['r', 'y', 'yes', 'replace']:
                self.c.execute(
                    'UPDATE bio SET content=? WHERE (owner=? AND server=?)', (content, lookup, ctx.guild.id))
                self.conn.commit()
                return await ctx.send('Bio for {} successfully updated.'.format(ctx.message.author.name))
            elif msg.content.lower() in ['c', 'n', 'no', 'cancel']:
                return await ctx.send("Bio unchanged.")
            elif msg.content.lower() == 'a':
                bio = self.c.execute(
                    'SELECT content FROM bio WHERE (server=? AND owner=?)', (ctx.guild.id, lookup))
                bio = bio.fetchall()
                bio = bio[0][0]
                bio = bio + "\n{}".format(content)
                self.c.execute('UPDATE bio SET content=?, updated=? WHERE (owner=? AND server=?)', (
                    bio, datetime.datetime.utcnow().timestamp(), lookup, ctx.guild.id))
                self.conn.commit()
                return await ctx.send('Bio for {} successfully appended.'.format(ctx.message.author.name))
            else:
                return

        print(a)
        self.c.execute('INSERT INTO bio VALUES (?, ?, ?, ?, ?, ?)', (lookup, content, ctx.guild.id,
                                                                     datetime.datetime.utcnow().timestamp(), datetime.datetime.utcnow().timestamp(), 0))
        self.conn.commit()
        await ctx.send('Bio for {} successfully created.'.format(ctx.message.author.name))


def setup(bot):
    bot.add_cog(Bio(bot))
