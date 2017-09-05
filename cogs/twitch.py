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
             (server text, stream text, id text, alias text, last_online real)''')

    async def stream_checker(self):
        await self.bot.wait_until_ready()

        DELAY = 60
        while self == self.bot.get_cog("Twitch"):
            try:
                a = self.c.execute('SELECT * FROM twitch')
                a = a.fetchall()
                for row in a:
                    data = await self.twitch_online(row[2])
                    if not data:
                        continue
                    else:  # stream is online
                        last_online = datetime.datetime.fromtimestamp(row[4])
                        now = datetime.datetime.utcnow()
                        if (now - last_online).total_seconds() < 1800:
                            self.c.execute('UPDATE twitch SET last_online=? WHERE id=?',
                                           (datetime.datetime.utcnow().timestamp(), row[2]))
                            self.conn.commit()
                            continue
                        stream_name = data["stream"]["channel"]["display_name"]
                        stream_title = data["stream"]["channel"]["status"]
                        streamer_icon = data["stream"]["channel"]["logo"] or "https://cdn3.iconfinder.com/data/icons/happily-colored-snlogo/512/twitch.png"
                        streamer_url = data["stream"]["channel"]["url"]
                        stream_viewers = data["stream"]["viewers"]
                        stream_game = data["stream"]["channel"]["game"]
                        stream_preview = data["stream"]["preview"]["large"]
                        em = discord.Embed(
                            title=stream_name, description=stream_title, colour=0x6441a4)
                        em.set_author(name=stream_name,
                                      icon_url=streamer_icon, url=streamer_url)
                        em.add_field(name="Viewers",
                                     value=stream_viewers, inline=True)
                        em.add_field(
                            name="Game", value=stream_game, inline=True)
                        em.set_image(url=stream_preview)
                        log_channel = self.c.execute(
                            'SELECT id, twitch_channel FROM servers WHERE id=?', (row[0],))
                        log_channel = log_channel.fetchone()
                        if log_channel[1] is None:
                            continue
                        else:
                            desti = self.bot.get_channel(int(log_channel[1]))

                        self.c.execute('UPDATE twitch SET last_online=? WHERE (id=? AND server=?)', (
                            datetime.datetime.utcnow().timestamp(), row[2], row[0]))
                        self.conn.commit()
                        await desti.send("{} is now online!\n<{}>".format(row[3].capitalize(), streamer_url), embed=em)
            except Exception as e:
                print(f"twitch={e}")

            await asyncio.sleep(DELAY)

    async def twitch_online(self, stream):
        sparty_id = "24756841"
        url = "https://api.twitch.tv/kraken/streams/" + stream
        CLIENT_ID = "token"
        header = {
            'Client-ID': CLIENT_ID,
            'Accept': 'application/vnd.twitchtv.v5+json'
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=header) as r:
                data = await r.json(encoding="utf-8")
        if r.status == 200:
            if data["stream"] is None:
                return False
            return data
        else:
            return

    @commands.group(invoke_without_subcommand=True)
    @checks.admin_or_permissions(manage_server=True)
    async def twitch(self, ctx, stream: str, *, name: str = None):
        ax = self.c.execute(
            'SELECT * FROM servers WHERE id=?', (ctx.guild.id,))
        ax = ax.fetchone()
        if ax[2] is None:
            await ctx.send("No twitch channel has been set and no streams will be announced, use `!set twitch #channel` to set one.")
        possible_deletion = True if name is None else False
        name = stream if name is None else name
        url = "https://api.twitch.tv/kraken/users?login=" + stream
        CLIENT_ID = "token"
        header = {
            'Client-ID': CLIENT_ID,
            'Accept': 'application/vnd.twitchtv.v5+json'
        }
        session = aiohttp.ClientSession()
        async with session.get(url, headers=header) as r:
            data = await r.json(encoding="utf-8")
            t_id = data["users"][0]["_id"]
            a = self.c.execute(
                'SELECT * FROM twitch WHERE (id=? AND server=?)', (t_id, ctx.guild.id))
            a = a.fetchall()
            if a == []:
                self.c.execute("INSERT INTO twitch VALUES (?, ?, ?, ?, ?)",
                               (ctx.guild.id, stream, t_id, name, 1479973395.693614))
                self.conn.commit()
                return await ctx.send('Twitch stream "{}" added with the alias "{}"'.format(stream, name))
            elif possible_deletion:
                self.c.execute(
                    'DELETE FROM twitch WHERE (id=? AND server=?)', (t_id, ctx.guild.id))
                self.conn.commit()
                return await ctx.send('Twitch stream "{}" deleted'.format(stream))
            else:
                self.c.execute(
                    'UPDATE twitch SET alias=? WHERE (id=? AND server=?)', (name, t_id, ctx.guild.id))
                self.conn.commit()
                return await ctx.send('Twitch stream "{}" had its alias changed to "{}"'.format(stream, name))

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
    n = Twitch(bot)
    loop = asyncio.get_event_loop()
    loop.create_task(n.stream_checker())
    bot.add_cog(n)
