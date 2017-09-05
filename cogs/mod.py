import re
import json
import discord
import enum
import datetime
import asyncio
import argparse
import shlex
import logging
import sqlite3

from discord.ext import commands
from cogs.utils import config, checks
from cogs.utils.formats import human_timedelta
from collections import Counter, defaultdict
from inspect import cleandoc


class Mod:

    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('database.db')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS config
             (guild_id text, ignored_channels text, commands text, enabled boolean)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS userconfig
            (guild_id text, user_id text, command text, status boolean, plonked boolean)''')

    async def __global_check(self, ctx):
        if ctx.author.id == 106429844627169280:
            return True

        bypass = ctx.author.guild_permissions.manage_guild
        if bypass:
            return True

        a = self.c.execute(
            'SELECT * FROM userconfig WHERE (guild_id=? AND user_id=?)', (ctx.guild.id, ctx.author.id))
        a = a.fetchone()
        command_name = ctx.command.qualified_name.split()[0]

        if a[4] == 1:
            # plonked
            return False
        if a[2] is not None:
            if command_name in a[2].split(','):
                # disabled user thing
                return False
        if ctx.guild is None:
            return True
        b = self.c.execute(
            'SELECT * FROM config WHERE guild_id=?', (ctx.guild.id,))
        b = b.fetchone()

        if not b[3]:
            # plonked server
            return False
        if b[1] is not None:
            if str(ctx.channel.id) in b[1].split(','):
                # ignored channel
                return False
        if b[2] is not None:
            if command_name in b[2].split(','):
                # disabled command
                return False
        return True

    @commands.group(no_pm=True, invoke_without_command=True)
    @checks.admin_or_permissions(manage_server=True)
    async def ignore(self, ctx, channel: discord.TextChannel=None):
        if channel is None:
            channels = [str(ctx.channel.id)]
        else:
            channels = [str(x.id) for x in ctx.message.channel_mentions]
        a = self.c.execute(
            'SELECT ignored_channels FROM config WHERE guild_id=?', (ctx.guild.id,))
        a = a.fetchone()
        if a[0] is None:
            # no channels disabled, easy update
            channels_to_add = ','.join(channels)
            self.c.execute(
                'UPDATE config SET ignored_channels=? WHERE guild_id=?', (channels_to_add, ctx.guild.id))
            self.conn.commit()
            e = ', '.join([f"<#{x}>" for x in channels])
            return await ctx.send(f"Ignored **{e}**.")
        ignored_channels = a[0].split(',')
        if Counter(ignored_channels) == Counter(channels):
            # ALL mentioned channels are already in the database, remove them instead
            self.c.execute(
                'UPDATE config SET ignored_channels=? WHERE guild_id=?', (None, ctx.guild.id))
            self.conn.commit()
            e = ', '.join([f"<#{x}>" for x in channels])
            return await ctx.send(f"Unignored **{e}**.")
        else:
            # If the mentioned channels and the saved channels have nothing or some in common, extend it
            say_list = [x for x in channels if x not in ignored_channels]
            if set(channels).issubset(ignored_channels):
                # unignore
                ignored_channels = [
                    x for x in ignored_channels if x not in channels]
                say_list = [x for x in channels]
                saved_list = ','.join(list(set(ignored_channels)))
                self.c.execute(
                    'UPDATE config SET ignored_channels=? WHERE guild_id=?', (saved_list, ctx.guild.id))
                self.conn.commit()
                e = ', '.join([f"<#{x}>" for x in say_list])
                return await ctx.send(f"Unignored **{e}**.")
            ignored_channels.extend(list(channels))
            saved_list = ','.join(list(set(ignored_channels)))
            self.c.execute(
                'UPDATE config SET ignored_channels=? WHERE guild_id=?', (saved_list, ctx.guild.id))
            self.conn.commit()
            e = ', '.join([f"<#{x}>" for x in say_list])
            return await ctx.send(f"Ignored **{e}**.")

    @ignore.command(name='server')
    @checks.admin_or_permissions(manage_server=True)
    async def ignore_guild(self, ctx):
        a = self.c.execute(
            'SELECT enabled FROM config WHERE guild_id=?', (ctx.guild.id,))
        a = a.fetchone()
        if a[0]:
            # server is enabled, disable it
            self.c.execute(
                'UPDATE config SET enabled=? WHERE guild_id=?', (False, ctx.guild.id))
            self.conn.commit()
            return await ctx.send(f"Disabled **{ctx.guild.name}**.")
        self.c.execute(
            'UPDATE config SET enabled=? WHERE guild_id=?', (True, ctx.guild.id))
        self.conn.commit()
        await ctx.send(f"Enabled **{ctx.guild.name}**.")

    @ignore.command(name='all')
    @checks.admin_or_permissions(manage_server=True)
    async def ignore_all(self, ctx):
        saved_list = ','.join([str(x.id) for x in ctx.guild.text_channels])
        self.c.execute(
            'UPDATE config SET ignored_channels=? WHERE guild_id=?', (saved_list, ctx.guild.id))
        self.conn.commit()
        await ctx.send("All channels ignored.")

    @commands.group()
    async def unignore(self, ctx):
        return

    @unignore.command(name='all')
    @checks.admin_or_permissions(manage_server=True)
    async def unignore_all(self, ctx):
        self.c.execute(
            'UPDATE config SET ignored_channels=? WHERE guild_id=?', (None, ctx.guild.id))
        self.conn.commit()
        await ctx.send("All channels unignored.")

    @ignore.command(name='list', no_pm=True)
    @checks.admin_or_permissions(manage_server=True)
    async def ignore_list(self, ctx):
        a = self.c.execute(
            'SELECT ignored_channels FROM config WHERE guild_id=?', (ctx.guild.id,))
        a = a.fetchone()
        if a[0] is None:
            disabled = []
        elif a[0] == "":
            disabled = []
        else:
            disabled = a[0].split(',')
        e = discord.Embed()
        if disabled == []:
            dis = "None"
        else:
            dis = dis = '\n'.join([f'<#{x}>' for x in disabled])
        enabled = [x for x in ctx.guild.text_channels if str(
            x.id) not in disabled]
        if len(enabled) == 0:
            ena = "None"
        else:
            ena = '\n'.join([f'<#{x.id}>' for x in enabled])
        e.add_field(name='Enabled', value=ena)
        e.add_field(name='Disabled', value=dis)
        e.set_footer(text=ctx.guild.name)
        await ctx.send(embed=e)

    @commands.group(no_pm=True, invoke_without_command=True, hidden=True)
    @checks.admin_or_permissions(manage_server=True)
    async def disable(self, ctx, *, command: str):
        command = command.lower()
        if command in ('enable', 'disable'):
            return await ctx.send('Cannot disable that command.')
        cool_dict = {a.qualified_name: a.aliases for a in self.bot.commands}

        if command not in cool_dict:
            for k, v in cool_dict.items():
                if command in v:
                    command = k
            if command not in [x.name for x in self.bot.commands]:
                return await ctx.send('I do not have this command registered.')

        a = self.c.execute(
            'SELECT commands FROM config WHERE guild_id=?', (ctx.guild.id,))
        a = a.fetchone()
        if a[0] is None:
            # no commands disabled, easy update
            self.c.execute(
                'UPDATE config SET commands=? WHERE guild_id=?', (command, ctx.guild.id))
            self.conn.commit()
            return await ctx.send(f'"{command}" command disabled in this server.')
        else:
            # one or more commands disabled
            disabled_commands = a[0].split(',')
            if command in disabled_commands:
                return await ctx.send(f"**{command}** was already disabled, use `{ctx.prefix}enable` if you wish to enable it.")

            else:
                disabled_commands.append(command)
                e = ','.join(
                    list(set([x for x in disabled_commands if x != ""])))
                self.c.execute(
                    'UPDATE config SET commands=? WHERE guild_id=?', (e, ctx.guild.id))
                self.conn.commit()
                return await ctx.send(f"Disabled **{command}**.")

    @commands.group(no_pm=True, invoke_without_command=True, hidden=True)
    @checks.admin_or_permissions(manage_server=True)
    async def enable(self, ctx, *, command: str):
        command = command.lower()
        if command in ('enable', 'disable'):
            return await ctx.send('Cannot enable that command.')
        cool_dict = {a.qualified_name: a.aliases for a in self.bot.commands}

        if command not in cool_dict:
            for k, v in cool_dict.items():
                if command in v:
                    command = k
            if command not in [x.name for x in self.bot.commands]:
                return await ctx.send('I do not have this command registered.')

        a = self.c.execute(
            'SELECT commands FROM config WHERE guild_id=?', (ctx.guild.id,))
        a = a.fetchone()
        if a[0] is None:
            # all commands enabled, easy update
            return await ctx.send('All commands are already enabled on this server.')
        else:
            # one or more commands disabled
            disabled_commands = a[0].split(',')
            if command in disabled_commands:
                # remove command from ignore list
                disabled_commands.remove(command)
                e = ','.join(
                    list(set([x for x in disabled_commands if x != ""])))
                self.c.execute(
                    'UPDATE config SET commands=? WHERE guild_id=?', (e, ctx.guild.id))
                self.conn.commit()
                return await ctx.send(f"Enabled **{command}**.")

            else:
                return await ctx.send(f"**{command}** was already enabled, use `{ctx.prefix}disable` if you wish to disable it.")

    @enable.command(name='list', no_pm=True)
    async def enable_list(self, ctx):
        a = self.c.execute(
            'SELECT commands FROM config WHERE guild_id=?', (ctx.guild.id,))
        a = a.fetchone()
        if a[0] is None:
            disabled = []
        elif a[0] == "":
            disabled = []
        else:
            disabled = a[0].split(',')
        e = discord.Embed()
        enabled = [
            x.name for x in self.bot.commands if x.name not in disabled and not x.hidden]

        ena = ', '.join(enabled) if enabled != [] else "None"
        dis = ', '.join(disabled) if disabled != [] else "None"
        e.add_field(name='Enabled', value=ena)
        e.add_field(name='Disabled', value=dis)
        e.set_footer(text=ctx.guild.name)
        await ctx.send(embed=e)

    @disable.command(name='list', no_pm=True)
    async def disable_list(self, ctx):
        a = self.c.execute(
            'SELECT commands FROM config WHERE guild_id=?', (ctx.guild.id,))
        a = a.fetchone()
        if a[0] is None:
            disabled = "None"
        elif a[0] == "":
            disabled = "None"
        else:
            disabled = a[0].split(',')
        e = discord.Embed()
        enabled = [
            x.name for x in self.bot.commands if x.name not in disabled and not x.hidden]
        ena = ', '.join(enabled) or "None"
        dis = ', '.join(disabled) or "None"
        e.add_field(name='Disabled', value=dis)
        e.add_field(name='Enabled', value=ena)
        e.set_footer(text=ctx.guild.name)
        await ctx.send(embed=e)

    @disable.command(name='all', no_pm=True)
    @checks.admin_or_permissions(manage_server=True)
    async def disable_all(self, ctx):
        to_disable = [x.name for x in self.bot.commands]
        e = ','.join(to_disable)
        self.c.execute(
            'UPDATE config SET commands=? WHERE guild_id=?', (e, ctx.guild.id))
        self.conn.commit()
        return await ctx.send("Disabled ALL commands.")

    @enable.command(name='all', no_pm=True)
    @checks.admin_or_permissions(manage_server=True)
    async def enable_all(self, ctx):
        self.c.execute(
            'UPDATE config SET commands=? WHERE guild_id=?', (None, ctx.guild.id))
        self.conn.commit()
        return await ctx.send("Enabled ALL commands.")

    @commands.command()
    @checks.admin_or_permissions(manage_server=True)
    async def plonk(self, ctx, user: discord.Member=None, *, command: str=None):
        if user is None:
            return ctx.send("You need to mention a user to plonk")
        if command is None:
            #global PLONK
            a = self.c.execute(
                'SELECT plonked FROM userconfig WHERE (guild_id=? AND user_id=?)', (ctx.guild.id, user.id))
            a = a.fetchone()
            if a[0]:
                #user is plonked
                self.c.execute(
                    'UPDATE userconfig SET plonked=? WHERE (guild_id=? AND user_id=?)', (False, ctx.guild.id, user.id))
                self.conn.commit()
                return await ctx.send(f"**{user.name}** is no longer banned from using the bot in this server.")
            else:
                #not plonked
                self.c.execute(
                    'UPDATE userconfig SET plonked=? WHERE (guild_id=? AND user_id=?)', (True, ctx.guild.id, user.id))
                self.conn.commit()
                return await ctx.send(f"**{user.name}** is now banned from using the bot in this server.")
        else:
            command = command.lower()
            if command in ('enable', 'disable'):
                return await ctx.send('Cannot enable that command.')
            cool_dict = {
                a.qualified_name: a.aliases for a in self.bot.commands}

            if command not in cool_dict:
                for k, v in cool_dict.items():
                    if command in v:
                        command = k
                if command not in [x.name for x in self.bot.commands]:
                    return await ctx.send('I do not have this command registered.')

            a = self.c.execute(
                'SELECT command FROM userconfig WHERE (guild_id=? AND user_id=?)', (ctx.guild.id, user.id))
            a = a.fetchone()
            if a[0] is None:
                # all commands enabled, easy update
                self.c.execute(
                    'UPDATE userconfig SET command=? WHERE (guild_id=? AND user_id=?)', (command, ctx.guild.id, user.id))
                self.conn.commit()
                return await ctx.send(f'"{command}" disabled for {user.name}.')
            else:
                # one or more commands disabled
                disabled_commands = a[0].split(',')
                if command in disabled_commands:
                    # remove command from ignore list
                    disabled_commands.remove(command)
                    e = ','.join(
                        list(set([x for x in disabled_commands if x != ""])))
                    self.c.execute(
                        'UPDATE userconfig SET command=? WHERE (guild_id=? AND user_id=?)', (e, ctx.guild.id, user.id))
                    self.conn.commit()
                    return await ctx.send(f"Enabled **{command}** for {user.name}.")

                else:
                    disabled_commands.append(command)
                    e = ','.join(
                        list(set([x for x in disabled_commands if x != ""])))
                    self.c.execute(
                        'UPDATE userconfig SET command=? WHERE (guild_id=? AND user_id=?)', (e, ctx.guild.id, user.id))
                    self.conn.commit()
                    return await ctx.send(f"Disabled **{command}** for {user.name}.")

    @commands.command(no_pm=True)
    async def plonks(self, ctx, user: discord.Member=None):
        if user is None:
            d = self.c.execute(
                'SELECT user_id, plonked FROM userconfig WHERE guild_id=?', (ctx.guild.id,))
            d = d.fetchall()
            plonks = '\n'.join([f"<@{x[0]}>" for x in d if x[1]]) or "None"
            e = discord.Embed(
                title=f"Plonks for {ctx.guild.name}", description=plonks)
            #e.add_field(name="None", value=plonks)
            await ctx.send(embed=e)
        else:
            d = self.c.execute(
                'SELECT user_id, command FROM userconfig WHERE (guild_id=? AND user_id=?)', (ctx.guild.id, user.id))
            d = d.fetchone()
            if d[0] is None:
                plonks = "None"
            elif d[0] == "":
                plonks = "None"
            else:
                plonks = '\n'.join([x for x in d[1].split(',')])
            e = discord.Embed(
                title=f"Plonks for {user.name}#{user.discriminator}", description=plonks)
            await ctx.send(embed=e)


def setup(bot):
    bot.add_cog(Mod(bot))
