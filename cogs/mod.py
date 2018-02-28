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
import copy

from discord.ext import commands
from cogs.utils import checks
from cogs.utils.formats import human_timedelta
from collections import Counter, defaultdict
from inspect import cleandoc
from slugify import slugify


class Mod:

    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('database.db')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS config
             (guild_id text, ignored_channels text, commands text, enabled boolean)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS userconfig
            (guild_id text, user_id text, command text, status boolean, plonked boolean)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS channelconfig
        (guild_id text, channel_id text, commands text, ignored_channels text)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS blacklist
             (guild_id text, word text)''')
        self.blacklist = {}
        self.c.execute('''SELECT * FROM blacklist WHERE 1''')
        for server, word in self.c.fetchall():
            if server not in self.blacklist:
                self.blacklist[server] = [word]
            else:
                self.blacklist[server].append(word)
        self.bot.modroles = {}
        self.c.execute('''SELECT guild_id, mod_roles FROM config WHERE 1''')
        for server, modrole in self.c.fetchall():
            self.bot.modroles[server] = modrole

    async def __global_check(self, ctx):



        # -| if carl -> True
        # --| if command is disabled for the server -> False --- Without this, it's possible that commands clash with other bots
        # ----| if subcommand is disabled for the server -> False --- Not to mention the fact that mods are actually impacted negatively by the alternatives
        # ----| if manage_server -> True
        # -----| if user is plonked -> False
        # --------| if command is disabled for user -> False
        # -----------| if subcommand is disabled for user -> False
        # -----| if pms -> True (all mod actions are based on servers anyway)
        # -----| if server is disabled -> False
        # -----| if channel is ignored -> False
        # -----| if command is disabled in the channel -> False
        # -------| if subcommand is disabled in the channel -> False
        # -----| if command is restricted -> get the bot channel, send a mention in the bot channel, send command IN the bot channel
        # -| else True


        if ctx.guild is None:
            return True

        if ctx.author.id == 106429844627169280:
            return True

        self.c.execute('SELECT * FROM config WHERE guild_id=?', (ctx.guild.id,))
        b = self.c.fetchone()
        self.c.execute('''SELECT bot_channel
                              FROM servers
                              WHERE id=?''',
                              (ctx.guild.id,))
        bot_channel = self.c.fetchone()
        bot_channel = self.bot.get_channel(int(bot_channel[0])) if bot_channel[0] is not None else ctx.channel
        command_name = ctx.command.root_parent
        if command_name is None:
            command_name = ctx.command.name
        command_name = str(command_name)
        if b[2] is not None:
            if command_name in b[2].split(','):
                # disabled commands aren't overriden by
                return False
            elif ctx.invoked_subcommand is not None:
                sub_command_name = f"{command_name} {ctx.invoked_subcommand.name}"
                if sub_command_name in b[2].split(','):
                    return False
        
        bypass = ctx.author.guild_permissions.manage_guild
        if self.bot.modroles.get(str(ctx.guild.id)) in [x.id for x in ctx.author.roles]:
            return True
        if bypass:
            return True
        if not b[3]:
            # plonked server/all commands are
            return False
        if b[1] is not None:
            if str(ctx.channel.id) in b[1].split(','):
                # ignored channel
                return False
        if b[4] is not None and bot_channel != ctx.channel:
            
            if command_name in b[4].split(','):
                await bot_channel.send(ctx.author.mention)
                context = copy.copy(ctx)
                context.channel = bot_channel
                await self.bot.invoke(context)
                return False
            elif ctx.invoked_subcommand is not None:
                sub_command_name = f"{command_name} {ctx.invoked_subcommand.name}"
                if sub_command_name in b[4].split(','):
                    await bot_channel.send(ctx.author.mention)
                    context = copy.copy(ctx)
                    context.channel = bot_channel
                    await self.bot.invoke(context)
                    return False
        
        

        self.c.execute('''SELECT *
                          FROM userconfig
                          WHERE (guild_id=? AND user_id=?)''',
                       (ctx.guild.id, ctx.author.id))
        a = self.c.fetchone()
        
        
        if a is not None:
            # If the user isn't in the list, we don't have t    o check
            # This isn't really a speed up or anything, but it crashes otherwise xD
            # Unfortunately highlight ignores will put you in the userconfig
            # which isn't WEBSCALE BRO
            if a[4]:
                # user is plonked
                # no, not per command
                # just plonked
                return False
            if a[2] is not None:
                if command_name in a[2].split(','):
                    # disabled user thing
                    return False
                elif ctx.invoked_subcommand is not None:
                    # disabling subcommands per user
                    # is not fun
                    sub_command_name = f"{command_name} {ctx.invoked_subcommand.name}"
                    if sub_command_name in a[2].split(','):           
                        return False
                    
        


        self.c.execute('''SELECT commands
                          FROM channelconfig
                          WHERE (guild_id=? AND channel_id=?)''',
                       (ctx.guild.id, ctx.channel.id))
        channelconfig = self.c.fetchone()
        if channelconfig is not None:
            if channelconfig[0] is not None:
                if command_name in channelconfig[0].split(','):
                    # ignored command
                    return False
                elif ctx.invoked_subcommand is not None:
                    sub_command_name = f"{command_name} {ctx.invoked_subcommand.name}"
                    if sub_command_name in channelconfig[0].split(','):
                        return False

        # command is allowed to be used, is it restricted though?
        return True







    def do_slugify(self, string):
        string = slugify(string, separator="")
        replacements = (('4', 'a'), ('@', 'a'), ('3', 'e'), ('1', 'i'), ('0', 'o'), ('7', 't'), ('5', 's'))
        for old, new in replacements:
            string = string.replace(old, new)
        
        return string

    def clean_string(self, string):
        string = re.sub('@', '@\u200b', string)
        string = re.sub('#', '#\u200b', string)
        return string

    async def on_message_edit(self, before, after):
        if before.guild is None:
            return
        if before.author.bot:
            return
        bypass = before.author.guild_permissions.manage_guild
        if bypass:
            return
        msg = self.do_slugify(after.content)
        try:
            if str(before.guild.id) in self.blacklist:
                for blacklisted_word in self.blacklist[str(before.guild.id)]:
                    if blacklisted_word in msg:
                        try:
                            await before.delete()
                            return await before.author.send(f'''Your message "{before.content}" was removed for containing the blacklisted word "{blacklisted_word}"''')
                        except Exception as e:
                            chan = self.bot.get_channel(344986487676338187)
                            await chan.send(f"Error when trying to remove message {type(e).__name__}: {e}")
        except Exception as e:
            chan = self.bot.get_channel(344986487676338187)
            await chan.send(f"Error when trying to remove message (big) {type(e).__name__}: {e}")

    async def on_message(self, message):
        if message.guild is None:
            return
        if message.author.bot:
            return
        bypass = message.author.guild_permissions.manage_guild
        if bypass:
            return
        msg = self.do_slugify(message.content)
        try:
            if str(message.guild.id) in self.blacklist:
                for blacklisted_word in self.blacklist[str(message.guild.id)]:
                    if blacklisted_word in msg:
                        try:
                            await message.delete()
                            return await message.author.send(f'''Your message "{message.content}" was removed for containing the blacklisted word "{blacklisted_word}"''')
                        except Exception as e:
                            chan = self.bot.get_channel(344986487676338187)
                            await chan.send(f"Error when trying to remove message {type(e).__name__}: {e}")
        except Exception as e:
            chan = self.bot.get_channel(344986487676338187)
            await chan.send(f"Error when trying to remove message (big) {type(e).__name__}: {e}")
    
    @commands.group(invoke_without_command=True, name="blacklist", aliases=['bl'])
    @checks.admin_or_permissions(manage_server=True)
    async def _blacklist(self, ctx):
        await ctx.send("```Usage: !blacklist add <word>\n!blacklist remove <word>\n!blacklist show```")

    @_blacklist.command(name="add", aliases=['+'])
    @checks.admin_or_permissions(manage_server=True)
    async def add_word(self, ctx, *, to_be_blacklisted: str=None):
        if to_be_blacklisted is None:
            print(ctx)
            await ctx.channel.send("You need to specify a word to blacklist")
            return
        slugified_word = self.do_slugify(to_be_blacklisted)
        self.c.execute('''INSERT OR IGNORE INTO blacklist
                          VALUES (?, ?)''',
                          (ctx.guild.id, slugified_word))
        self.conn.commit()
        try:
            self.blacklist[str(ctx.guild.id)].append(slugified_word)
        except KeyError:
            self.blacklist[str(ctx.guild.id)] = [slugified_word]
        to_be_blacklisted = self.clean_string(to_be_blacklisted)
        await ctx.send(f'Added "{to_be_blacklisted}" to the blacklist')
    
    @_blacklist.command(name="remove", aliases=['-'])
    @checks.admin_or_permissions(manage_server=True)
    async def remove_word(self, ctx, *, word: str=None):
        if word is None:
            return await ctx.send("You need to specify a word to remove from the blacklist")
        slugified_word = self.do_slugify(word)
        if slugified_word not in self.blacklist[str(ctx.guild.id)]:
            return await ctx.send("You don't seem to be blacklisting that word")
        self.c.execute('''DELETE FROM blacklist WHERE (guild_id=? AND word=?)''',
                        (ctx.guild.id, slugified_word))
        self.conn.commit()
        self.blacklist[str(ctx.guild.id,)].remove(slugified_word)
        word = self.clean_string(word)
        await ctx.send(f'Removed "{word}" from the blacklist')

    @_blacklist.command(name="display", aliases=['show'])
    @checks.admin_or_permissions(manage_server=True)
    async def show_words(self, ctx):
        self.c.execute('SELECT word FROM blacklist WHERE guild_id=?',(ctx.guild.id,))
        words = self.c.fetchall()
        if words == []:
            return await ctx.send("No blacklisted words yet, use `!blacklist add <word>` to get started")
        e = discord.Embed(title="Blocked words", description='\n'.join(x[0] for x in words))
        await ctx.send(embed=e)

    @_blacklist.command(name="clear")
    @checks.admin_or_permissions(manage_server=True)
    async def _clear(self, ctx):
        self.c.execute('''DELETE FROM blacklist WHERE guild_id=?''',(ctx.guild.id,))
        self.conn.commit()
        self.blacklist[str(ctx.guild.id,)] = []
        await ctx.send("Removed all blacklisted words")

    

    @commands.group(no_pm=True, invoke_without_command=True)
    @checks.admin_or_permissions(manage_server=True)
    async def ignore(self, ctx, channel: discord.TextChannel=None, command: str=None, subcommand: str = None):
        if channel is None:
            channels = [str(ctx.channel.id)]
        else:
            channels = [str(x.id) for x in ctx.message.channel_mentions]
        if command is None:
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
        else:
            # This is similar to the other subcommand disables
            # But keeping all channels up to date is just unreasonable
            # Instead we're gonna have it be a bit more lenient for 
            # non-existant rows and instead have it update as it goes along
            command = command.lower()
            if command in ('enable', 'disable'):
                return await ctx.send('Cannot disable that command.')
            cool_dict = {a.qualified_name: a.aliases for a in self.bot.commands}
            # I'm pretty sure ^ qualified_name is actually wrong and I should be using .name
            # But at this point I'm too afraid to change anything

            if command not in cool_dict:
                for k, v in cool_dict.items():
                    if command in v:
                        command = k
                if command not in [x.name for x in self.bot.commands]:
                    return await ctx.send('I do not have this command registered.')
            
            # We have the command picked, now we need to check if a subcommand has to be passed too
            # Just like for the commands, we're gonna use the actual _name_ of the command and
            # not an alias, this will be what the user is after in 99.999999% of cases so I'm not
            # even gonna think twice about it

            if subcommand is not None:
                subcommand = subcommand.lower()
                # a subcommand was defined and we need to check if it's registered as a name or as an alias
                base_command = self.bot.get_command(command)
                try:
                    sub_commands = base_command.commands
                except AttributeError:
                    return await ctx.send("That command has no subcommands")
                # Now we have a generator with the group's subcommands
                # we'll do the same thing as we did in the "cool dict"
                second_cool_dict = {x.name: x.aliases for x in sub_commands}
                if subcommand not in second_cool_dict:
                    print(second_cool_dict)
                    for k, v in second_cool_dict.items():
                        print(v)
                        if subcommand in v:
                            subcommand = k
                    if subcommand not in second_cool_dict:
                        return await ctx.send("I don't have that subcommand registered (if you used a prefix, don't!)")
                command = f"{command} {subcommand}"
                print(f"subcommand is {subcommand}")
                print(f"making the disabled command '{command}'")
            self.c.execute('''SELECT commands
                              FROM channelconfig
                              WHERE (guild_id=? AND channel_id=?)''',
                           (ctx.guild.id, channel.id))
            already_disabled_commands = self.c.fetchone()
            if already_disabled_commands is None:
                self.c.execute('''INSERT INTO channelconfig
                                  VALUES (?, ?, ?, ?)''',
                               (ctx.guild.id, channel.id, command, None))
                self.conn.commit()
                return await ctx.send(f"Disabled **{command}** in #{channel.name}.")
            print(already_disabled_commands)
            if already_disabled_commands[0] is None:
                # no commands disabled, easy update
                self.c.execute('''UPDATE channelconfig
                                  SET commands=?
                                  WHERE (guild_id=? AND channel_id=?)''',
                               (command, ctx.guild.id, channel.id))
                self.conn.commit()
                return await ctx.send(f"Disabled **{command}** in #{channel.name}.")
            else:
                # one or more commands disabled
                disabled_commands = already_disabled_commands[0].split(',')
                if command in disabled_commands:
                    # If the command is already disabled, we're gonna re-enable it
                    # the syntax is inconsistent and that's unfortunate, but it's
                    # pretty neat just having one command I think
                    disabled_commands.remove(command)
                    e = ','.join(
                        list(set([x for x in disabled_commands if x != ""])))
                    if e == "":
                        e = None
                    self.c.execute('''UPDATE channelconfig
                                      SET commands=?
                                      WHERE (guild_id=? AND channel_id=?)''',
                                   (e, ctx.guild.id, channel.id))
                    self.conn.commit()
                    return await ctx.send(f"Enabled **{command}** in #{channel.name}.")

                else:
                    disabled_commands.append(command)
                    e = ','.join(
                        list(set([x for x in disabled_commands if x != ""])))
                    if e == "":
                        e = None
                    self.c.execute('''UPDATE channelconfig
                                      SET commands=?
                                      WHERE (guild_id=? AND channel_id=?)''',
                                   (e, ctx.guild.id, channel.id))
                    self.conn.commit()
                    return await ctx.send(f"Disabled **{command}** in #{channel.name}.")

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
    async def ignore_all(self, ctx, command: str=None, subcommand: str = None):
        if command is None:
            # standard command, just ignores all channels
            saved_list = ','.join([str(x.id) for x in ctx.guild.text_channels])
            self.c.execute(
                'UPDATE config SET ignored_channels=? WHERE guild_id=?', (saved_list, ctx.guild.id))
            self.conn.commit()
            return await ctx.send("All channels ignored.")
        # Here begins the fun stuff
        # Basically, the way the command works is that it will iterate over the text channels of the guild
        # And ignore the passed command (and optional subcommand) for all channels
        # will basically work the same as ignore but on a larger scale


        command = command.lower()
        if command in ('enable', 'disable'):
            return await ctx.send('Cannot disable that command.')
        cool_dict = {a.qualified_name: a.aliases for a in self.bot.commands}
        # I'm pretty sure ^ qualified_name is actually wrong and I should be using .name
        # But at this point I'm too afraid to change anything

        if command not in cool_dict:
            for k, v in cool_dict.items():
                if command in v:
                    command = k
            if command not in [x.name for x in self.bot.commands]:
                return await ctx.send('I do not have this command registered.')
        
        # We have the command picked, now we need to check if a subcommand has to be passed too
        # Just like for the commands, we're gonna use the actual _name_ of the command and
        # not an alias, this will be what the user is after in 99.999999% of cases so I'm not
        # even gonna think twice about it

        if subcommand is not None:
            subcommand = subcommand.lower()
            # a subcommand was defined and we need to check if it's registered as a name or as an alias
            base_command = self.bot.get_command(command)
            try:
                sub_commands = base_command.commands
            except AttributeError:
                return await ctx.send("That command has no subcommands")
            # Now we have a generator with the group's subcommands
            # we'll do the same thing as we did in the "cool dict"
            second_cool_dict = {x.name: x.aliases for x in sub_commands}
            if subcommand not in second_cool_dict:
                print(second_cool_dict)
                for k, v in second_cool_dict.items():
                    print(v)
                    if subcommand in v:
                        subcommand = k
                if subcommand not in second_cool_dict:
                    return await ctx.send("I don't have that subcommand registered")
            command = f"{command} {subcommand}"
            print(f"subcommand is {subcommand}")
            print(f"making the disabled command '{command}'")
        # If we reached this point, we have a command and possibly even a subcommand passed, iterating over the guild and 
        # ignoring it per channel _should_ be easy
        channels = [x for x in ctx.guild.text_channels]
        # sqlite is very VERY slow at committing but I'm too scared not to do it
        # seeing "database is locked" gives me ptsd
        disabled = []
        enabled  = []
        for channel in channels:
            self.c.execute('''SELECT commands
                                FROM channelconfig
                                WHERE (guild_id=? AND channel_id=?)''',
                            (ctx.guild.id, channel.id))
            already_disabled_commands = self.c.fetchone()
            if already_disabled_commands is None:
                self.c.execute('''INSERT INTO channelconfig
                                    VALUES (?, ?, ?, ?)''',
                                (ctx.guild.id, channel.id, command, None))
                self.conn.commit()
                disabled.append(channel.name)
                continue
            print(already_disabled_commands)
            if already_disabled_commands[0] is None:
                # no commands disabled, easy update
                self.c.execute('''UPDATE channelconfig
                                    SET commands=?
                                    WHERE (guild_id=? AND channel_id=?)''',
                                (command, ctx.guild.id, channel.id))
                self.conn.commit()
                disabled.append(channel.name)
            else:
                # one or more commands disabled
                disabled_commands = already_disabled_commands[0].split(',')
                if command in disabled_commands:
                    # If the command is already disabled, we're gonna re-enable it
                    # the syntax is inconsistent and that's unfortunate, but it's
                    # pretty neat just having one command I think
                    disabled_commands.remove(command)
                    e = ','.join(
                        list(set([x for x in disabled_commands if x != ""])))
                    if e == "":
                        e = None
                    self.c.execute('''UPDATE channelconfig
                                        SET commands=?
                                        WHERE (guild_id=? AND channel_id=?)''',
                                    (e, ctx.guild.id, channel.id))
                    self.conn.commit()
                    enabled.append(channel.name)

                else:
                    disabled_commands.append(command)
                    e = ','.join(
                        list(set([x for x in disabled_commands if x != ""])))
                    if e == "":
                        e = None
                    self.c.execute('''UPDATE channelconfig
                                        SET commands=?
                                        WHERE (guild_id=? AND channel_id=?)''',
                                    (e, ctx.guild.id, channel.id))
                    self.conn.commit()
                    disabled.append(channel.name)
        enabled = ', '.join(enabled)
        disabled = ', '.join(disabled)
        await ctx.send("**Command:** {}\n**Disabled channels:** {}\n**Enabled channels:** {}".format(command, disabled, enabled))

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
    async def disable(self, ctx, command: str, subcommand: str = None):
        command = command.lower()
        if command in ('enable', 'disable'):
            return await ctx.send('Cannot disable that command.')
        cool_dict = {a.qualified_name: a.aliases for a in self.bot.commands}
        #print(cool_dict)

        if command not in cool_dict:
            for k, v in cool_dict.items():
                if command in v:
                    command = k
            if command not in [x.name for x in self.bot.commands]:
                return await ctx.send('I do not have this command registered.')
        
        # We have the command picked, now we need to check if a subcommand has to be passed too
        # Just like for the commands, we're gonna use the actual _name_ of the command and
        # not an alias, this will be what the user is after in 99.999999% of cases so I'm not
        # even gonna think twice about it

        if subcommand is not None:
            subcommand = subcommand.lower()
            # a subcommand was defined and we need to check if it's registered as a name or as an alias
            base_command = self.bot.get_command(command)
            try:
                sub_commands = base_command.commands
            except AttributeError:
                return await ctx.send("That command has no subcommands")
            # Now we have a generator with the group's subcommands
            # we'll do the same thing as we did in the "cool dict"
            second_cool_dict = {x.name: x.aliases for x in sub_commands}
            if subcommand not in second_cool_dict:
                print(second_cool_dict)
                for k, v in second_cool_dict.items():
                    print(v)
                    if subcommand in v:
                        subcommand = k
                if subcommand not in second_cool_dict:
                    return await ctx.send("I don't have that subcommand registered")
            command = f"{command} {subcommand}"
            print(f"subcommand is {subcommand}")
            print(f"making the disabled command '{command}'")

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
                return await ctx.send(f"Disabled **{command}**.")

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
    async def enable(self, ctx, command: str, subcommand: str = None):
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

        if subcommand is not None:
            subcommand = subcommand.lower()
            # a subcommand was defined and we need to check if it's registered as a name or as an alias
            base_command = self.bot.get_command(command)
            try:
                sub_commands = base_command.commands
            except AttributeError:
                return await ctx.send("That command has no subcommands")
            # Now we have a generator with the group's subcommands
            # we'll do the same thing as we did in the "cool dict"
            second_cool_dict = {x.name: x.aliases for x in sub_commands}
            if subcommand not in second_cool_dict:
                print(second_cool_dict)
                for k, v in second_cool_dict.items():
                    print(v)
                    if subcommand in v:
                        subcommand = k
                if subcommand not in second_cool_dict:
                    return await ctx.send("I don't have that subcommand registered")
            command = f"{command} {subcommand}"
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
        to_disable = [x.name for x in self.bot.commands if str(x.name) not in ("enable", "disable")]
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
    async def plonk(self, ctx, user: discord.Member=None, command: str=None, subcommand: str = None):
        if user is None:
            return ctx.send("You need to mention a user to plonk")
        if command is None:
            #global PLONK
            a = self.c.execute(
                'SELECT plonked FROM userconfig WHERE (guild_id=? AND user_id=?)', (ctx.guild.id, user.id))
            a = a.fetchone()
            if a is not None:
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
                # if a is none, we have a clean user
                # this means they always should be plonked
                self.c.execute('''INSERT INTO userconfig
                                  VALUES (?, ?, ?, ?, ?, ?)''',(ctx.guild.id, user.id, None, None, True, None))
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

            if subcommand is not None:
                subcommand = subcommand.lower()
                # a subcommand was defined and we need to check if it's registered as a name or as an alias
                base_command = self.bot.get_command(command)
                try:
                    sub_commands = base_command.commands
                except AttributeError:
                    return await ctx.send("That command has no subcommands")
                # Now we have a generator with the group's subcommands
                # we'll do the same thing as we did in the "cool dict"
                second_cool_dict = {x.name: x.aliases for x in sub_commands}
                if subcommand not in second_cool_dict:
                    print(second_cool_dict)
                    for k, v in second_cool_dict.items():
                        print(v)
                        if subcommand in v:
                            subcommand = k
                    if subcommand not in second_cool_dict:
                        return await ctx.send("I don't have that subcommand registered")
                command = f"{command} {subcommand}"
                print(f"subcommand is {subcommand}")
                print(f"making the disabled command '{command}'")

            a = self.c.execute(
                'SELECT command FROM userconfig WHERE (guild_id=? AND user_id=?)', (ctx.guild.id, user.id))
            a = a.fetchone()
            if a is not None:
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
                        if e == "":
                            # God I fucking _hate_
                            # dealing with empty strings
                            e = None
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
            else:
                # If the row doesn't exist, we need to insert it
                # luckily this looks almost exactly like the a[0] row
                self.c.execute('''INSERT INTO userconfig
                                  VALUES (?, ?, ?, ?, ?, ?)''',
                               (ctx.guild.id, user.id, command, None, False, None))
                self.conn.commit()
                await ctx.send(f"Disabled **{command}** for {user.name}")

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
            if d is not None:
                if d[0] is None:
                    plonks = "None"
                elif d[0] == "":
                    plonks = "None"
                else:
                    if d[1] is None:
                        plonks = "None"
                    else:                    
                        plonks = '\n'.join([x for x in d[1].split(',')])
            else:
                plonks = "None"
            e = discord.Embed(
                title=f"Plonks for {user.name}#{user.discriminator}", description=plonks)
            await ctx.send(embed=e)













    @commands.group(no_pm=True, invoke_without_command=True, hidden=True)
    @checks.admin_or_permissions(manage_server=True)
    async def restrict(self, ctx, command: str, subcommand: str = None):
        command = command.lower()
        if command in ('enable', 'disable'):
            return await ctx.send('Cannot disable that command.')
        cool_dict = {a.qualified_name: a.aliases for a in self.bot.commands}
        #print(cool_dict)

        if command not in cool_dict:
            for k, v in cool_dict.items():
                if command in v:
                    command = k
            if command not in [x.name for x in self.bot.commands]:
                return await ctx.send('I do not have this command registered.')
        
        # We have the command picked, now we need to check if a subcommand has to be passed too
        # Just like for the commands, we're gonna use the actual _name_ of the command and
        # not an alias, this will be what the user is after in 99.999999% of cases so I'm not
        # even gonna think twice about it

        if subcommand is not None:
            subcommand = subcommand.lower()
            # a subcommand was defined and we need to check if it's registered as a name or as an alias
            base_command = self.bot.get_command(command)
            try:
                sub_commands = base_command.commands
            except AttributeError:
                return await ctx.send("That command has no subcommands")
            # Now we have a generator with the group's subcommands
            # we'll do the same thing as we did in the "cool dict"
            second_cool_dict = {x.name: x.aliases for x in sub_commands}
            if subcommand not in second_cool_dict:
                print(second_cool_dict)
                for k, v in second_cool_dict.items():
                    print(v)
                    if subcommand in v:
                        subcommand = k
                if subcommand not in second_cool_dict:
                    return await ctx.send("I don't have that subcommand registered")
            command = f"{command} {subcommand}"
            print(f"subcommand is {subcommand}")
            print(f"making the disabled command '{command}'")

        a = self.c.execute(
            'SELECT restricted_commands FROM config WHERE guild_id=?', (ctx.guild.id,))
        a = a.fetchone()
        if a[0] is None:
            # no commands restricted, easy update
            self.c.execute(
                'UPDATE config SET restricted_commands=? WHERE guild_id=?', (command, ctx.guild.id))
            self.conn.commit()
            return await ctx.send(f'"{command}" is now restricted to the bot channel.')
        else:
            # one or more commands disabled
            disabled_commands = a[0].split(',')
            if command in disabled_commands:
                return await ctx.send(f"Restricted **{command}**.")

            else:
                disabled_commands.append(command)
                e = ','.join(
                    list(set([x for x in disabled_commands if x != ""])))
                self.c.execute(
                    'UPDATE config SET restricted_commands=? WHERE guild_id=?', (e, ctx.guild.id))
                self.conn.commit()
                return await ctx.send(f"Restricted **{command}**.")

    @commands.group(no_pm=True, invoke_without_command=True, hidden=True)
    @checks.admin_or_permissions(manage_server=True)
    async def unrestrict(self, ctx, command: str, subcommand: str = None):
        command = command.lower()
        if command in ('enable', 'disable'):
            return await ctx.send('Cannot restrict that command.')
        cool_dict = {a.qualified_name: a.aliases for a in self.bot.commands}

        if command not in cool_dict:
            for k, v in cool_dict.items():
                if command in v:
                    command = k
            if command not in [x.name for x in self.bot.commands]:
                return await ctx.send('I do not have this command registered.')

        if subcommand is not None:
            subcommand = subcommand.lower()
            # a subcommand was defined and we need to check if it's registered as a name or as an alias
            base_command = self.bot.get_command(command)
            try:
                sub_commands = base_command.commands
            except AttributeError:
                return await ctx.send("That command has no subcommands")
            # Now we have a generator with the group's subcommands
            # we'll do the same thing as we did in the "cool dict"
            second_cool_dict = {x.name: x.aliases for x in sub_commands}
            if subcommand not in second_cool_dict:
                print(second_cool_dict)
                for k, v in second_cool_dict.items():
                    print(v)
                    if subcommand in v:
                        subcommand = k
                    if subcommand not in second_cool_dict:
                            return await ctx.send("I don't have that subcommand registered")
            command = f"{command} {subcommand}"
        a = self.c.execute(
            'SELECT restricted_commands FROM config WHERE guild_id=?', (ctx.guild.id,))
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
                    'UPDATE config SET restricted_commands=? WHERE guild_id=?', (e, ctx.guild.id))
                self.conn.commit()
                return await ctx.send(f"Set **{command}** free again.")

            else:
                return await ctx.send(f"**{command}** was already unrestricted, use `{ctx.prefix}restrict` if you wish to restrict it.")
























def setup(bot):
    bot.add_cog(Mod(bot))
