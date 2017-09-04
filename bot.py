import logging
import sys
import traceback
import datetime
import copy
import json
import sqlite3
import aiohttp

import discord

from discord.ext import commands
from cogs.utils import checks, context
from collections import Counter


description = "Like the previous one but good."


initial_extensions = [
    'cogs.admin',
    'cogs.poll',
    'cogs.ping',
    'cogs.tags',
    'cogs.automod',
    'cogs.bio',
    'cogs.stats',
    'cogs.stattrak',
    'cogs.meta',
    'cogs.blizzard',
    'cogs.ckc',
    'cogs.convert',
    'cogs.mod',
    'cogs.twitch',
    'cogs.highlight',
    'cogs.nsfw',
    'cogs.reminders'
]





def load_json(filename):
    with open(filename, encoding='utf-8') as infile:
        return json.load(infile)
def write_json(filename, contents):
    with open(filename, 'w') as outfile:
        json.dump(contents, outfile, ensure_ascii=True, indent=4)

conn = sqlite3.connect('database.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users
        (roles text, server text, location text, id text, names text, postcount int, retard int, sicklad int)''')


# discord_logger = logging.getLogger('discord')
# discord_logger.setLevel(logging.CRITICAL)
# log = logging.getLogger()
# log.setLevel(logging.INFO)
# handler = logging.FileHandler(filename="carlbot.log", encoding='utf-8', mode='w')
# log.addHandler(handler)
log = logging.getLogger(__name__)

def _prefix_callable(bot, msg):
    user_id = bot.user.id
    base = ['<@!{}> '.format(user_id), '<@{}> '.format(user_id)]
    if msg.guild is None:
        base.append('!')
        base.append('?')
    else:
        base.extend(bot.prefixes.get(msg.guild.id, ['?', '!']))
    return base




def load_credentials():
    with open('cred.json') as f:
        return json.load(f)



credentials = load_credentials()
    


class CarlBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=_prefix_callable, description="Better than the last one", help_attrs=dict(hidden=True))
        self.client_id = 235148962103951360
        self.owner_id = 106429844627169280
        a = c.execute('SELECT * FROM servers WHERE 1')
        a = a.fetchall()
        pre = {k[0]:k[5] or '!,?' for k in a}
        self.prefixes = {int(k):v.split(',') for (k, v) in pre.items()}
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.token = credentials["token"]
        self.remove_command('help')

        for extension in initial_extensions:
            try:
                self.load_extension(extension)
            except Exception as e:
                print('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.author.send('This command cannot be used in private messages.')
        elif isinstance(error, commands.DisabledCommand):
            await ctx.author.send('Sorry. This command is disabled and cannot be used.')
        elif isinstance(error, commands.CommandInvokeError):
            print(f'In {ctx.command.qualified_name}:', file=sys.stderr)
            traceback.print_tb(error.original.__traceback__)
            print(f'{error.original.__class__.__name__}: {error.original}', file=sys.stderr)

    async def on_ready(self):
        print('Logged in as:')
        print('Username: ' + self.user.name)
        print('ID: ' + str(self.user.id))
        print('------')
        if not hasattr(self, 'uptime'):
            self.uptime = datetime.datetime.utcnow()
        for server in self.guilds:
            a = c.execute('SELECT * FROM servers WHERE id=?', (str(server.id),))
            a = a.fetchall()
            if a == []:
                c.execute('INSERT INTO servers VALUES (?, ?, ?, ?, ?, ?)', (str(server.id), None, None, None, None, '?,!'))
                conn.commit()
            b = c.execute('SELECT * FROM logging WHERE server=?', (str(server.id),))
            b = b.fetchall()
            if b == []:
                c.execute('INSERT INTO logging VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', (str(server.id), 1, 1, 1, 1, 1, 1, 1, None))
                print(server.name)
                conn.commit()
            xc = c.execute('SELECT * FROM config WHERE guild_id=?', (server.id,))
            xc = xc.fetchall()
            if xc == []:
                c.execute('INSERT INTO config VALUES (?, ?, ?, ?)', (server.id, None, None, True))
                conn.commit()


        member_list = self.get_all_members()
        for member in member_list:
            a = c.execute('SELECT * FROM users WHERE (id=? AND server=?)', (str(member.id), member.guild.id))
            a = a.fetchall()
            if a == []:
                roles = ','.join([str(x.id) for x in member.roles if x.name != "@everyone" and x.id != 232206741339766784])
                names = member.display_name
                c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (roles, str(member.guild.id), None, str(member.id), names, 0, 0, 0))
                conn.commit()
            xd = c.execute('SELECT * FROM userconfig WHERE (guild_id=? AND user_id=?)', (member.guild.id, member.id))
            xd = xd.fetchall()
            if xd == []:
                c.execute('INSERT INTO userconfig VALUES (?, ?, ?, ?, ?, ?)', (member.guild.id, member.id, None, None, False, None))
                conn.commit()

    def get_guild_prefixes(self, guild, *, local_inject=_prefix_callable):
        proxy_msg = discord.Object(id=None)
        proxy_msg.guild = guild
        return local_inject(self, proxy_msg)

    def get_raw_guild_prefixes(self, guild_id):
        return self.prefixes.get(guild_id, ['?', '!'])

    async def set_guild_prefixes(self, guild, prefixes):
        if not prefixes:
            c.execute('UPDATE servers SET prefix=? WHERE id=?', (None, str(guild.id)))
            conn.commit()
            self.prefixes[guild.id] = prefixes
        elif len(prefixes) > 10:
            raise RuntimeError('Cannot have more than 10 custom prefixes.')
        else:
            c.execute('UPDATE servers SET prefix=? WHERE id=?', (','.join(sorted(set(prefixes))), str(guild.id)))
            conn.commit()
            self.prefixes[guild.id] = sorted(set(prefixes))
            print(self.prefixes[guild.id])

    async def on_resumed(self):
        print("resumed...")




    async def on_message(self, message):
        if message.author.bot:
            return
        await self.process_commands(message)
        ctx = await self.get_context(message)
        if ctx.invoked_with not in self.commands and ctx.command is None:      
            msg = copy.copy(message)
            if ctx.prefix:
                new_content = msg.content[len(ctx.prefix):]
                print("new content: {}".format(new_content))
                print(f"old content: '{ctx.invoked_with}'")
                if ctx.invoked_with in [
                        "add",
                        "+",
                        "remove",
                        "procreate",
                        "create",
                        "&",
                        "append",
                        "owner",
                        "raw",
                        "mine",
                        "+=",
                        "++",
                        "edit",
                        "update",
                        "list"
                    ]:
                    return
                msg.content = "{}tag {}".format(ctx.prefix, new_content)
                await self.process_commands(msg)

    async def close(self):
        await super().close()
        await self.session.close()

    def run(self):
        super().run(self.token, reconnect=True)







if __name__ == '__main__':
    bot = CarlBot()
    bot.run()
