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
from twitch import TwitchClient

def load_json(filename):
    with open(filename, encoding='utf-8') as infile:
        return json.load(infile)

def write_json(filename, contents):
    with open(filename, 'w') as outfile:
        json.dump(contents, outfile, indent=4)

class Twitch:

    def __init__(self, bot):
        self.bot = bot
        #self.online = []
        self.conn = sqlite3.connect('database.db')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS twitch
             (server text, stream text, id text, alias text, last_online real)''')

        # a = self.c.execute('SELECT * FROM twitch')
        # a = a.fetchall()
        # print(a)
        # for row in a:
        #     server, _, id, _, last_online = a
        #     self.online.append(a)
        
    async def stream_checker(self):
        
        DELAY = 60
        while self == self.bot.get_cog("Twitch"):
            print("hello")
            a = self.c.execute('SELECT * FROM twitch')
            a = a.fetchall()
            for row in a:
                data = await self.twitch_online(row[2])
                if not data:
                    continue
                else: #stream is online
                    last_online = datetime.datetime.fromtimestamp(row[4])
                    now = datetime.datetime.utcnow()
                    if (now - last_online).total_seconds() < 1800:
                        self.c.execute('UPDATE twitch SET last_online=? WHERE id=?', (datetime.datetime.utcnow().timestamp(), row[2]))
                        self.conn.commit()
                        print("Twitch is online but was online for less than 30 minutes ago")
                        continue
                    stream_name = data["stream"]["channel"]["display_name"]
                    stream_title = data["stream"]["channel"]["status"]
                    streamer_icon = data["stream"]["channel"]["logo"] or "https://cdn3.iconfinder.com/data/icons/happily-colored-snlogo/512/twitch.png"
                    streamer_url = data["stream"]["channel"]["url"]
                    stream_viewers = data["stream"]["viewers"]
                    stream_game = data["stream"]["channel"]["game"]
                    stream_preview = data["stream"]["preview"]["large"]
                    em = discord.Embed(title=stream_name, description=stream_title, colour=0x6441a4)
                    em.set_author(name=stream_name, icon_url=streamer_icon, url=streamer_url)
                    print("streamer icon: ", streamer_icon)
                    em.add_field(name="Viewers", value=stream_viewers, inline=True)
                    em.add_field(name="Game", value=stream_game, inline=True)
                    em.set_image(url=stream_preview)
                    print("stream name: ", stream_name)
                    if stream_name == "SpartySmallwood":
                        await self.bot.send_message(discord.Object(id="207943928018632705"),"<@&309135201479426058>", embed=em)
                        self.c.execute('UPDATE twitch SET last_online=? WHERE id=?', (datetime.datetime.utcnow().timestamp(), row[2]))
                        self.conn.commit()
                    else:
                        log_channel = self.c.execute('SELECT twitch_channel FROM servers WHERE id=?', (row[0],))
                        log_channel = log_channel.fetchall()
                        print("log: {}".format(log_channel))
                        if log_channel == [] or log_channel[0][0] is None:
                            #await self.bot.send_message(discord.Object(id="233091778419490816"), "nice retard")
                            log_channel = discord.Object(row[0])
                            
                        else:
                            log_channel = discord.Object(id=log_channel[0][0])
                        #desti = discord.Object(id="207943928018632705")
                        self.c.execute('UPDATE twitch SET last_online=? WHERE (id=? AND server=?)', (datetime.datetime.utcnow().timestamp(), row[2], row[0]))
                        self.conn.commit()
                        await self.bot.send_message(log_channel,"{} is now online!\n<{}>".format(row[3].capitalize(), streamer_url), embed=em)
            await asyncio.sleep(DELAY)

    async def twitch_online(self, stream):
        session = aiohttp.ClientSession()
        sparty_id = "24756841"
        url = "https://api.twitch.tv/kraken/streams/" + stream
        CLIENT_ID = "br1llodxvega24ld0h70vfoa8r93q7"
        header = {
            'Client-ID': CLIENT_ID,
            'Accept': 'application/vnd.twitchtv.v5+json'
        }
        async with session.get(url, headers=header) as r:
            data = await r.json(encoding="utf-8")
        await session.close()
        if r.status == 200:
            if data["stream"] is None:
                print("twitch_online returned false")
                return False
            return data
        else:
            print(r.status)
            return

    @commands.command(pass_context=True)
    @checks.admin_or_permissions(manage_server=True)
    async def twitch(self, ctx, stream : str, *, name : str = None):
        possible_deletion = True if name is None else False
        name = stream if name is None else name        
        url = "https://api.twitch.tv/kraken/users?login=" + stream
        CLIENT_ID = "br1llodxvega24ld0h70vfoa8r93q7"
        header = {
            'Client-ID': CLIENT_ID,
            'Accept': 'application/vnd.twitchtv.v5+json'
        }
        session = aiohttp.ClientSession()
        async with session.get(url, headers=header) as r:
            data = await r.json(encoding="utf-8")
            t_id = data["users"][0]["_id"]
            a = self.c.execute('SELECT * FROM twitch WHERE (id=? AND server=?)', (t_id, ctx.message.server.id))
            a = a.fetchall()
            if a == []:
                self.c.execute("INSERT INTO twitch VALUES (?, ?, ?, ?, ?)", (ctx.message.server.id, stream, t_id, name, 1479973395.693614))
                self.conn.commit()
                return await self.bot.say('Twitch stream "{}" added with the alias "{}"'.format(stream, name))
            elif possible_deletion:
                self.c.execute('DELETE FROM twitch WHERE (id=? AND server=?)', (t_id, ctx.message.server.id))
                self.conn.commit()
                return await self.bot.say('Twitch stream "{}" deleted'.format(stream))
            else:
                self.c.execute('UPDATE twitch SET alias=? WHERE (id=? AND server=?)', (name, t_id, ctx.message.server.id))
                self.conn.commit()
                return await self.bot.say('Twitch stream "{}" had its alias changed to "{}"'.format(stream, name))
            #self.c.execute('UPDATE twitch SET stream=?, id=?, alias=? WHERE id=?', (city, ctx.message.author.id))
            # if t_id in self.streamers:
            #     del self.streamers[t_id]
            # else:
            #     self.streamers[t_id] = {
            #         "name": name,
            #         "server": ctx.message.server.id
            #     }
            # write_json('twitch.json', self.streamers)

def setup(bot):
    n = Twitch(bot)
    loop = asyncio.get_event_loop()
    loop.create_task(n.stream_checker())
    bot.add_cog(n)
    
