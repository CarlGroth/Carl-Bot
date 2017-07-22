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
    
    @commands.group(pass_context=True, invoke_without_command=True)
    @commands.cooldown(2, 60, BucketType.user)
    async def bio(self, ctx, *, member : discord.Member = None):
        owner = ctx.message.author if member is None else member
        server = ctx.message.server
        bio = self.c.execute('SELECT content FROM bio WHERE (server=? AND owner=?)', (server.id, owner.id))
        bio = bio.fetchall()
        if bio == []:
            return await self.bot.say("User has not set a bio\nTo set a bio use `!bio + <content>`, no mentions!")
        else:
            bio = bio[0][0]
            print(bio)
            self.c.execute('UPDATE bio SET uses = uses + 1 WHERE (server=? AND owner=?)', (server.id, owner.id))
            self.conn.commit()

        if len(bio) < 1250:
            if ctx.message.channel.is_default:
                LINK_REGEX = re.compile(r"(https?://.*)")
                bio = re.sub(LINK_REGEX, r"<\1>", str(bio))
                bio = bio.replace(" >", ">")
            await self.bot.send_message(ctx.message.channel, "**Bio for {0}:**\n{1}".format(owner.name, bio))
        else:
            if ctx.message.channel.is_default:
                try:
                    destination = discord.utils.find(lambda m: "bot" in m.name, ctx.message.server.channels)
                    xd = await self.bot.send_message(destination, ctx.message.author.mention)
                except:
                    destination = ctx.message.channel
                
            else:
                destination = ctx.message.channel
            listOfLines = bio.splitlines()
            tempmessage = "**Bio for {0}:**\n".format(owner.name)
            finalmessage = []
            if owner.id == "158370770068701184":
                linenr = 1
                for line in listOfLines:
                    if linenr < 5:#len("{}{}".format(tempmessage, line)) < 1800:
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
            for x in finalmessage:
                if x is not None:
                    await self.bot.send_message(destination, x)
                    await asyncio.sleep(1)


    @bio.command(pass_context=True, name="append", aliases=["+="])
    async def _append(self, ctx, *, content : str):
        content = self.clean_bio_content(content)
        lookup = ctx.message.author.id
        a = self.c.execute('SELECT content FROM bio WHERE (owner=? AND server=?)', (lookup, ctx.message.server.id))
        a = a.fetchall()
        if a == []:
            return await self.bot.say("Can't append to bios that don't exist.")

        bio = a[0][0] + "\n{}".format(content)
        self.c.execute('UPDATE bio SET content=?, updated=? WHERE (owner=? AND server=?)', (bio, datetime.datetime.utcnow().timestamp(), lookup, ctx.message.server.id))
        self.conn.commit()
        await self.bot.say('Bio for {} successfully updated.'.format(ctx.message.author.name))


    @bio.command(pass_context=True, aliases=['add', '+'])
    async def create(self, ctx, *, content : str):
        content = self.clean_bio_content(content)
        lookup = ctx.message.author.id
        a = self.c.execute('SELECT * FROM bio WHERE (owner=? AND server=?)', (lookup, ctx.message.server.id))
        a = a.fetchall()
        if a != []:
            await self.bot.send_message(ctx.message.channel, "Bio already exists. **__r__**eplace, **__c__**ancel or **__a__**dd to? (r/c/a)")
            msg = await self.bot.wait_for_message(author=ctx.message.author)
            if msg.content.lower() in ['r', 'y', 'yes', 'replace']:
                self.c.execute('UPDATE bio SET content=? WHERE (owner=? AND server=?)', (content, lookup, ctx.message.server.id))
                self.conn.commit()
                return await self.bot.say('Bio for {} successfully updated.'.format(ctx.message.author.name))
            elif msg.content.lower() in ['c', 'n', 'no', 'cancel']:
                return await self.bot.send_message(ctx.message.channel, "Bio unchanged.")
            elif msg.content.lower() == 'a':
                bio = self.c.execute('SELECT content FROM bio WHERE (server=? AND owner=?)', (ctx.message.server.id, lookup))
                bio = bio.fetchall()
                bio = bio[0][0]
                bio = bio + "\n{}".format(content)
                self.c.execute('UPDATE bio SET content=?, updated=? WHERE (owner=? AND server=?)', (bio, datetime.datetime.utcnow().timestamp(), lookup, ctx.message.server.id))
                self.conn.commit()
                return await self.bot.say('Bio for {} successfully appended.'.format(ctx.message.author.name))

        
        self.c.execute('INSERT INTO bio VALUES (?, ?, ?, ?, ?, ?)', (lookup, a[0][0], ctx.message.server.id, datetime.datetime.utcnow().timestamp(), datetime.datetime.utcnow().timestamp(), 0))
        self.conn.commit()
        await self.bot.say('Bio for {} successfully created.'.format(ctx.message.author.name))

def setup(bot):
    bot.add_cog(Bio(bot))
