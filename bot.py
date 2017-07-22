import discord
import asyncio
import logging
import sys
import traceback
import datetime
import re
import copy
import json
import sqlite3


from discord.ext import commands
from cogs.utils import checks
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
    'cogs.permissions'
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


discord_logger = logging.getLogger('discord')
discord_logger.setLevel(logging.CRITICAL)
log = logging.getLogger()
log.setLevel(logging.INFO)
handler = logging.FileHandler(filename="carlbot.log", encoding='utf-8', mode='w')
log.addHandler(handler)

prefix = ["§", "?", "!"]
bot = commands.Bot(command_prefix=prefix, description=description)



@bot.event
async def on_command_error(error, ctx):
    if isinstance(error, commands.NoPrivateMessage):
        await bot.send_message(ctx.message.author, 'This command cannot be used in private messages.')
    elif isinstance(error, commands.DisabledCommand):
        await bot.send_message(ctx.message.author, 'This command has been disabled and cannot be used.')
    elif isinstance(error, commands.CommandInvokeError):
        print('In {0.command.qualified_name}'.format(ctx, file=sys.stderr))
        traceback.print_tb(error.original.__traceback__)    
        print('{0.__class__.__name__}: {0}'.format(error.original), file=sys.stderr)

@bot.event
async def on_ready():
    print('Logged in as:')
    print('Username: ' + bot.user.name)
    print('ID: ' + bot.user.id)
    print('------')
    if not hasattr(bot, 'uptime'):
        bot.uptime = datetime.datetime.utcnow()
    server_invites = load_json('invites.json')
    for server in bot.servers:
        a = c.execute('SELECT * FROM servers WHERE id=?', (server.id,))
        a = a.fetchall()
        if a == []:
            c.execute('INSERT INTO servers VALUES (?, ?, ?, ?, ?)', (server.id, None, None, None, None))
            conn.commit()
        b = c.execute('SELECT * FROM logging WHERE server=?', (server.id,))
        b = b.fetchall()
        if b == []:
            c.execute('INSERT INTO logging VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', (server.id, 1, 1, 1, 1, 1, 1, 1, None))
            print(server.name)
            conn.commit()
        server_invites[server.id] = {}
        try:
            for inv in await bot.invites_from(server):
                server_invites[server.id][inv.id] = inv.uses
        except Exception as e:
            print(e)
            continue
        
    write_json('invites.json', server_invites)
    member_list = bot.get_all_members()
    for member in member_list:
        a = c.execute('SELECT * FROM users WHERE (id=? AND server=?)', (member.id, member.server.id))
        a = a.fetchall()
        if a != []:
            continue
        roles = ','.join([x.id for x in member.roles if (x.name != "@everyone" and x.id != "232206741339766784")])


        names = member.display_name
        c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (roles, member.server.id, None, member.id, names, 0, 0, 0))
        conn.commit()
    


@bot.event
async def on_resumed():
    print("resumed...")



@bot.event
async def on_message(message):
    if message.author.bot:
        return
    await bot.process_commands(message)


@bot.command(pass_context=True, hidden=True)
@checks.is_owner()
async def do(ctx, times : int, *, command):
    """repeats a command a number of times."""
    msg = copy.copy(ctx.message)
    msg.content = command
    for i in range(times):
        await bot.process_commands(msg)

def load_credentials():
    with open('cred.json') as f:
        return json.load(f)


if __name__ == '__main__':
    credentials = load_credentials()
    token = credentials["token"]
    bot.client_id = credentials['client_id']

    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))
    
    bot.run(token)
    handlers = log.handlers[:]
    for hdlr in handlers:
        hdlr.closer()
        log.removeHandler(hdlr)