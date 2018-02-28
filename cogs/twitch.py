import discord
import json
import os
import re
import aiohttp
import asyncio
import sqlite3
import datetime

from cogs.utils import checks
from discord.ext import commands
from collections import defaultdict
from string import ascii_letters
from random import choice
from cogs.utils.formats import human_timedelta


def load_json(filename):
    with open(filename, encoding='utf-8') as infile:
        return json.load(infile)


def write_json(filename, contents):
    with open(filename, 'w') as outfile:
        json.dump(contents, outfile, indent=4)


class Twitch:

    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('database.db')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS twitch
             (server text, stream text, id text, alias text, last_online real, added_by text)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS twitch_config
             (guild_id text UNIQUE, ownership boolean, mod_only boolean, max_ownership integer, mention_everyone boolean)''')
        self._task = bot.loop.create_task(self.stream_checker())
        self.regex = re.compile(r"(?:https?://)?(?:www\.)?(?:go\.)?(?:twitch\.tv/)?(.+)")

    def clean_string(self, string):
        string = re.sub('@', '@\u200b', string)
        string = re.sub('#', '#\u200b', string)
        return string

    def __unload(self):
        self._task.cancel()

    async def stream_checker(self):
        await self.bot.wait_until_ready()

        DELAY = 60
        while not self.bot.is_closed():
            try:
                difference = datetime.datetime.utcnow().timestamp() - 600
                self.c.execute('SELECT * FROM twitch WHERE last_online < ?', (difference,))
                a = self.c.fetchall()
                big_data = {}
                for row in a:
                    server, _, stream_id, alias, last_online, added_by = row
                    if stream_id not in big_data:
                        big_data[str(stream_id)] = {
                            "display_name": "",
                            "servers": [(server, alias)],
                            "last_online": last_online,
                            "url": "twitch.tv",
                            "game": "None",
                            "icon": "None",
                            "title": "None"
                            }
                    else:
                        big_data[str(stream_id)]["servers"].append((server, alias))
                list_me = list(big_data)
                data = await self.get_twitch_list(list_me)
                
                if not data or "streams" not in data[0]:
                    await asyncio.sleep(DELAY)
                    continue
                for i in data:

                    data = i["streams"]
                    for stream in data:
                        streamer_id = str(stream["channel"]['_id'])
                        big_data[streamer_id]["display_name"] = stream["channel"]["display_name"]
                        big_data[streamer_id]["title"] = stream["channel"]["status"]
                        big_data[streamer_id]["url"] = stream["channel"]["url"]
                        big_data[streamer_id]["game"] = stream["channel"]["game"]
                        big_data[streamer_id]["icon"] = stream["channel"]["logo"] or "https://cdn3.iconfinder.com/data/icons/happily-colored-snlogo/512/twitch.png"
                for _id, stream in big_data.items():  
                    if stream["display_name"] == "":                       
                        continue
                    last_online = datetime.datetime.fromtimestamp(stream["last_online"])
                    now = datetime.datetime.utcnow()
                    
                    if (now - last_online).total_seconds() < 1800:
                        self.c.execute('UPDATE twitch SET last_online=? WHERE id=?',
                                        (datetime.datetime.utcnow().timestamp(), _id))
                        self.conn.commit()
                        continue
                    stream_name = stream["display_name"]
                    stream_title = stream["title"]
                    streamer_icon = stream["icon"]
                    stream_game = stream.get("game", "None, peculiar")
                    streamer_url = stream["url"]

                    for server,alias in stream["servers"]:
                        em = discord.Embed(title="Title", description=stream_title, colour=0x6441a4)
                        em.set_author(name=stream_name, icon_url=streamer_icon, url=streamer_url)
                        em.add_field(name="Game", value=stream_game, inline=True)
                        em.set_thumbnail(url=streamer_icon)
                        self.c.execute(
                            'SELECT id, twitch_channel FROM servers WHERE id=?', (server,))
                        log_channel = self.c.fetchone()
                        if log_channel[1] is None:
                            continue
                        else:
                            desti = self.bot.get_channel(int(log_channel[1]))
                        self.c.execute('UPDATE twitch SET last_online=? WHERE (id=? AND server=?)', (
                            datetime.datetime.utcnow().timestamp(), _id, server))
                        self.conn.commit()
                        if desti is not None:
                            try:
                                await desti.send("{} is now online!\n<{}>".format(alias.capitalize(), streamer_url), embed=em)
                            except Exception as e:
                                chan = self.bot.get_channel(344986487676338187)
                                await chan.send(f"Tried to send a message to {desti.name} in the server {desti.guild.name} but couldn't.\nError: {e}")




            except asyncio.CancelledError:
                chan = self.bot.get_channel(344986487676338187)
                await chan.send("cancellederror (twitch)...")
            except Exception as e:
                chan = self.bot.get_channel(344986487676338187)
                await chan.send("twitch restarted restarted...\nError: {0}: {1}".format(type(e).__name__, e))
                self._task.cancel()
                self._task = self.bot.loop.create_task(self.stream_checker())

            await asyncio.sleep(DELAY)

    async def twitch_online(self, stream):
        url = "https://api.twitch.tv/kraken/streams/" + stream
        CLIENT_ID = "TOKEN HERE"
        header = {
            'Client-ID': CLIENT_ID,
            'Accept': 'application/vnd.twitchtv.v5+json'
        }
        async with self.bot.session.get(url, headers=header) as r:
                data = await r.json(encoding="utf-8")
                print(data)
        if r.status == 200:
            if data["stream"] is None:
                return False
            return data
        else:
            return

    async def twitch_community_online(self, community):
        url = "https://api.twitch.tv/kraken/communities?name=" + community
        CLIENT_ID = "TOKEN HERE"
        header = {
            'Client-ID': CLIENT_ID,
            'Accept': 'application/vnd.twitchtv.v5+json'
        }
        async with self.bot.session.get(url, headers=header) as r:
            data = await r.json(encoding="utf-8")
        if r.status == 200:
           # print(data)
            if data["_id"] is None:
                return
            return data
        else:
            return

    async def get_twitch_list(self, streams: list):
        url = "https://api.twitch.tv/kraken/streams?channel="
        # The way twitch deals with this is by
        # returning a list of all the online users
        # this seems to be limited to 100 streams but I'll 
        # worry about that when I get there
        CLIENT_ID = "TOKEN HERE"
        header = {
            'Client-ID': CLIENT_ID,
            'Accept': 'application/vnd.twitchtv.v5+json'
        }
        nr_of_chunks = (len(streams) // 100) + 1 # Twitch doesn't like it when you give it more than 100 streams
                      # This number is the amount of requests that have to be sent
        payload = []
        for i in range(nr_of_chunks):
            streams = ','.join(streams[i*100:i*100+100]) # nice chunks of 100 streams each :feelsgoodman:
            async with self.bot.session.get(f"{url}{streams}", headers=header) as re:
                data = await re.json(encoding="utf-8")
            payload.append(data)        #print(payload)
        return payload


    @commands.group(invoke_without_command=True)
    async def twitch(self, ctx, stream: str, *, name: str = None):
        if ctx.guild is None:
            return await ctx.send("Can't announce to pms")
        stream = self.regex.search(stream).group(1)
        if name is not None:
            bypass = ctx.author.guild_permissions.manage_guild
            if not bypass:
                name = self.clean_string(name)
        self.c.execute('''INSERT OR IGNORE INTO twitch_config VALUES (?, ?, ?, ?, ?)''', (ctx.guild.id, 0, 1, 0, 0))
        self.conn.commit()
        self.c.execute('''SELECT ownership, mod_only, max_ownership FROM twitch_config WHERE guild_id=?''', (ctx.guild.id,))
        ownership, mod_only, max_ownership = self.c.fetchone()
        bypass = ctx.author.guild_permissions.manage_guild
        if mod_only and not bypass:
            return await ctx.send("Only mods can add channels to be announced.")
        if max_ownership != 0:
            self.c.execute('''SELECT * FROM twitch WHERE added_by=?''', (ctx.author.id,))
            howmany = len(self.c.fetchall())
            if howmany >= max_ownership and not bypass:
                return await ctx.send("You can't add any more channels than that")

        ax = self.c.execute(
            'SELECT * FROM servers WHERE id=?', (ctx.guild.id,))
        ax = ax.fetchone()
        if ax[2] is None:
            await ctx.send("No twitch channel has been set and no streams will be announced, use `!set twitch #channel` to set one.")
        possible_deletion = True if name is None else False
        name = stream if name is None else name
        url = "https://api.twitch.tv/kraken/users?login=" + stream
        CLIENT_ID = "TOKEN HERE"
        header = {
            'Client-ID': CLIENT_ID,
            'Accept': 'application/vnd.twitchtv.v5+json'
        }
        async with self.bot.session.get(url, headers=header) as r:
            data = await r.json(encoding="utf-8")
            try:
                t_id = data["users"][0]["_id"]
            except:
                return await ctx.send("Couldn't find that streamer, make sure you spelled it correctly.")
        a = self.c.execute(
            'SELECT * FROM twitch WHERE (id=? AND server=?)', (t_id, ctx.guild.id))
        a = a.fetchall()
        if a == []:
            self.c.execute("INSERT OR IGNORE INTO twitch VALUES (?, ?, ?, ?, ?, ?)",
                            (ctx.guild.id, stream, t_id, name, 1479973395.693614, ctx.author.id))
            self.conn.commit()
            return await ctx.send('Twitch stream "{}" added with the alias "{}"'.format(stream, name))
        self.c.execute('''SELECT added_by FROM twitch WHERE (server=? AND id=?)''', (ctx.guild.id, t_id))
        whoadded = self.c.fetchone()[0]
        if ownership and whoadded != str(ctx.author.id):
            return await ctx.send("This server has ownership enabled and you didn't add that streamer")
        if possible_deletion:            
            self.c.execute(
                'DELETE FROM twitch WHERE (id=? AND server=?)', (t_id, ctx.guild.id))
            self.conn.commit()
            return await ctx.send('Twitch stream "{}" deleted'.format(stream))
        else:
            self.c.execute(
                'UPDATE twitch SET alias=? WHERE (id=? AND server=?)', (name, t_id, ctx.guild.id))
            self.conn.commit()
            return await ctx.send('Twitch stream "{}" had its alias changed to "{}"'.format(stream, name))


    @twitch.command(name="own", aliases=['ownership'])
    @checks.admin_or_permissions(manage_server=True)
    async def twitch_ownership(self, ctx):
        self.c.execute('''INSERT OR IGNORE INTO twitch_config VALUES (?, ?, ?, ?, ?)''', (ctx.guild.id, 0, 1, 0, 0))
        self.c.execute('''UPDATE twitch_config SET ownership = NOT ownership WHERE guild_id=?''', (ctx.guild.id,))
        self.conn.commit()
        self.c.execute('''SELECT ownership FROM twitch_config WHERE guild_id=?''', (ctx.guild.id,))
        maybeown = self.c.fetchone()[0]
        if maybeown:
            return await ctx.send("Twitch channels are now 'owned', only mods and the person who added the stream can edit channels")
        await ctx.send("Twitch channels are no longer owned")

    @twitch.command(name="mod", aliases=['modonly'])
    @checks.admin_or_permissions(manage_server=True)
    async def twitch_modonly(self, ctx):
        self.c.execute('''INSERT OR IGNORE INTO twitch_config VALUES (?, ?, ?, ?, ?)''', (ctx.guild.id, 0, 1, 0, 0))
        self.c.execute('''UPDATE twitch_config SET mod_only = NOT mod_only WHERE guild_id=?''', (ctx.guild.id,))
        self.conn.commit()
        self.c.execute('''SELECT mod_only, max_ownership FROM twitch_config WHERE guild_id=?''', (ctx.guild.id,))
        maybeown, limit = self.c.fetchone()
        if limit == 0:
            limit = "no limit"
        if maybeown:
            return await ctx.send("Only mods can add streams now")
        await ctx.send(f"Anyone can add streams now, limit: {limit}")

    @twitch.command(name="everyone", aliases=['ateveryone'])
    @checks.admin_or_permissions(manage_server=True)
    async def twitch_everyone(self, ctx):
        self.c.execute('''INSERT OR IGNORE INTO twitch_config VALUES (?, ?, ?, ?, ?)''', (ctx.guild.id, 0, 1, 0, 0))
        self.c.execute('''UPDATE twitch_config SET mention_everyone = NOT mention_everyone WHERE guild_id=?''', (ctx.guild.id,))
        self.conn.commit()
        self.c.execute('''SELECT mention_everyone FROM twitch_config WHERE guild_id=?''', (ctx.guild.id,))
        everyone = self.c.fetchone()[0]
        if everyone:
            return await ctx.send("Twitch streams will now ping everyone when they go live")
        await ctx.send("Twitch streams will no longer ping everyone when they go live")


    @twitch.command(name="limit")
    @checks.admin_or_permissions(manage_server=True)
    async def twitch_limit(self, ctx, limit: int=0):
        self.c.execute('''INSERT OR IGNORE INTO twitch_config VALUES (?, ?, ?, ?, ?)''', (ctx.guild.id, 0, 1, 0, 0))
        self.c.execute('''UPDATE twitch_config SET max_ownership = ? WHERE guild_id=?''', (limit, ctx.guild.id))
        self.conn.commit()
        self.c.execute('''SELECT max_ownership FROM twitch_config WHERE guild_id=?''', (ctx.guild.id,))
        howmany = self.c.fetchone()[0]
        if howmany != 0:
            return await ctx.send(f"Users (non-mods) are now limited to {howmany} streams added")
        await ctx.send("Users can now add as many twitch streamers as they want")


    @twitch.command(name="config")
    async def twitch_cfg(self, ctx):
        self.c.execute('''INSERT OR IGNORE INTO twitch_config VALUES (?, ?, ?, ?, ?)''', (ctx.guild.id, 0, 1, 0, 0))
        self.conn.commit()
        self.c.execute('''SELECT ownership, mod_only, max_ownership, mention_everyone FROM twitch_config WHERE guild_id=?''', (ctx.guild.id,))
        ownership, mod_only, max_ownership, mention_everyone = self.c.fetchone()
        if ownership:
            ownership = "<:greentick:318044721807360010> Ownership"
        else:
            ownership = "<:redtick:318044813444251649> Ownership"
        if mod_only:
            mod_only = "<:greentick:318044721807360010> Mod only"
        else:
            mod_only = "<:redtick:318044813444251649> Mod only"
        if mention_everyone:
            mention_everyone = "<:greentick:318044721807360010> Mentions everyone"
        else:
            mention_everyone = "<:redtick:318044813444251649> Mentions everyone"
        if max_ownership != 0:
            max_ownership = f"Maximum number of streams owned: {max_ownership}"
        else:
            max_ownership = "No limit to streams owned"
        e = discord.Embed(title=f"Twitch config for {ctx.guild.name}", description=f"{ownership}\n{mod_only}\n{mention_everyone}\n{max_ownership}")
        await ctx.send(embed=e)


    @commands.command(name='twitchlist')
    async def twitch_all(self, ctx):
        a = self.c.execute(
            'SELECT * FROM twitch WHERE server=?', (ctx.guild.id,))
        a = a.fetchall()
        if a != []:
            e = discord.Embed()
            name = '\n'.join([x[1] for x in a])
            alias = '\n'.join([x[3] for x in a])
            last_online = '\n'.join(
                [human_timedelta(datetime.datetime.fromtimestamp(x[4])) for x in a])
            e.add_field(name='Name', value=name)
            e.add_field(name='Alias', value=alias)
            e.add_field(name="Last online", value=last_online)
            e.set_footer(text=ctx.guild.name)
            await ctx.send(embed=e)


def setup(bot):
    bot.add_cog(Twitch(bot))
