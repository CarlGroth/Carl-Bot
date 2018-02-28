import asyncio
import datetime
import time
import re
import sqlite3
import aiohttp
import discord

from discord.ext import commands
from cogs.utils import checks
from collections import OrderedDict



def clean_string(string):
    string = re.sub('@', '@\u200b', string)
    string = re.sub('#', '#\u200b', string)
    return string


CARL_DISCORD_ID = 106429844627169280
dt_format = '%Y-%m-%d %H:%M:%S (UTC+0)'

DEGENERATE_CHANNELS = [
    327671109551915018,
    218148472262492161,
    218148510527127552,
    218169083600961547,
    218546616561434634
]


class Automod:
    def __init__(self, bot):
        self.bot = bot
        
        self.conn = sqlite3.connect('database.db')
        self.c = self.conn.cursor()
        self.website_regex = re.compile("https?:\/\/[^\s]*")
        self.c.execute('''CREATE TABLE IF NOT EXISTS servers
                         (id text, log_channel text, twitch_channel text,
                          welcome_message text, bot_channel text, prefix text)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS logging
             (server text, message_edit boolean, message_deletion boolean,
             role_changes boolean, name_update boolean, member_movement boolean,
             avatar_changes boolean, bans boolean, ignored_channels text)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS greetings
                       (guild_id text UNIQUE NOT NULL, greet_channel text, greet_message text, farewell_message text, ban_message text)
                        ''')

    @commands.group(name='set', invoke_without_command=True)
    @checks.admin_or_permissions(manage_server=True)
    async def _set(self, ctx):
        await ctx.send("You need to use a subcommand")

    @_set.command()
    @checks.admin_or_permissions(manage_server=True)
    async def twitch(self, ctx, *, channel: discord.TextChannel=None):
        if channel is None:
            return await ctx.send("You need to mention a channel")
        self.c.execute('''UPDATE servers
                          SET twitch_channel=?
                          WHERE id=?''',
                       (channel.id, ctx.message.guild.id))
        self.conn.commit()
        await ctx.send("Twitch channel set to <#{}>".format(channel.id))

    @_set.command(aliases=['logs', 'logchannel'])
    @checks.admin_or_permissions(manage_server=True)
    async def log(self, ctx, *, channel: discord.TextChannel=None):
        if channel is None:
            return await ctx.send("You need to mention a channel")
        self.c.execute('''UPDATE servers
                          SET log_channel=?
                          WHERE id=?''',
                       (channel.id, ctx.message.guild.id))
        self.conn.commit()
        await ctx.send("Logging channel set to <#{}>".format(channel.id))

    @_set.command(name='bot', aliases=['botchannel'])
    @checks.admin_or_permissions(manage_server=True)
    async def _bot(self, ctx, channel: discord.TextChannel=None):
        if channel is None:
            return await ctx.send("You need to mention a channel")
        self.c.execute('''UPDATE servers
                          SET bot_channel=?
                          WHERE id=?''',
                       (channel.id, ctx.message.guild.id))
        self.conn.commit()
        await ctx.send("Bot channel changed to <#{}>".format(channel.id))

    @_set.command(aliases=['welcomechannel'])
    @checks.admin_or_permissions(manage_server=True)
    async def welcome(self, ctx, *, channel: discord.TextChannel = None):
        self.c.execute('''INSERT OR IGNORE INTO greetings (guild_id, greet_channel, greet_message, farewell_message, ban_message)
                          VALUES (?, ?, ?, ?, ?)''',
                       (str(ctx.guild.id), None, None, None, None))
        self.conn.commit()
        if channel is None:
            self.c.execute('''UPDATE greetings
                              SET greet_channel=?
                              WHERE guild_id=?''',
                           (None, ctx.guild.id))
            self.conn.commit()
            return await ctx.send("Welcome channel removed.")

        self.c.execute('''UPDATE greetings
                          SET greet_channel=?
                          WHERE guild_id=?''',  
                       (channel.id, ctx.guild.id))
        self.conn.commit()
        await ctx.send(f"Welcome channel set to **#{channel.name}**.")



    @commands.command()
    @checks.admin_or_permissions(manage_server=True)
    async def greet(self, ctx, *, msg: str = None):
        self.c.execute('''INSERT OR IGNORE INTO greetings (guild_id, greet_channel, greet_message, farewell_message, ban_message)
                          VALUES (?, ?, ?, ?, ?)''',
                       (ctx.guild.id, None, None, None, None))
        self.conn.commit()
        if msg is None:
            self.c.execute('''UPDATE greetings
                              SET greet_message=?
                              WHERE guild_id=?''',
                           (None, ctx.message.guild.id))
            self.conn.commit()
            return await ctx.send("Greeting message removed.")
        msg = clean_string(msg)
        self.c.execute('''UPDATE greetings
                          SET greet_message=?
                          WHERE guild_id=?''',
                       (msg, ctx.guild.id))
        self.conn.commit()
        await ctx.send(f"Greet message updated.")


    @commands.command()
    @checks.admin_or_permissions(manage_server=True)
    async def farewell(self, ctx, *, msg: str = None):
        self.c.execute('''INSERT OR IGNORE INTO greetings (guild_id, greet_channel, greet_message, farewell_message, ban_message)
                          VALUES (?, ?, ?, ?, ?)''',
                       (ctx.guild.id, None, None, None, None))
        self.conn.commit()
        if msg is None:
            self.c.execute('''UPDATE greetings
                              SET farewell_message=?
                              WHERE guild_id=?''',
                           (None, ctx.message.guild.id))
            self.conn.commit()
            return await ctx.send("Farewell message removed.")
        msg = clean_string(msg)
        self.c.execute('''UPDATE greetings
                          SET farewell_message=?
                          WHERE guild_id=?''',
                       (msg, ctx.message.guild.id))
        self.conn.commit()
        await ctx.send(f"Farewell message updated.")

    @commands.command(aliases=['banmsg'])
    @checks.admin_or_permissions(manage_server=True)
    async def banmessage(self, ctx, *, msg: str = None):
        self.c.execute('''INSERT OR IGNORE INTO greetings (guild_id, greet_channel, greet_message, farewell_message, ban_message)
                          VALUES (?, ?, ?, ?, ?)''',
                       (str(ctx.guild.id), None, None, None, None))
        self.conn.commit()
        if msg is None:
            self.c.execute('''UPDATE greetings
                              SET ban_message=?
                              WHERE guild_id=?''',
                           (None, ctx.message.guild.id))
            self.conn.commit()
            return await ctx.send("Ban message removed.")
        msg = clean_string(msg)
        self.c.execute('''UPDATE greetings
                          SET ban_message=?
                          WHERE guild_id=?''',
                       (msg, ctx.message.guild.id))
        self.conn.commit()
        await ctx.send(f"Ban message updated.")


    @commands.command(name='config')
    @checks.admin_or_permissions(manage_server=True)
    async def _cfg(self, ctx):
        enu = {
            "Message edits": 1,
            "Message deletions": 2,
            "Role updates": 3,
            "Name changes": 4,
            "Join/Leave": 5,
            "Avatar updates": 6,
            "Bans/Unbans": 7
        }
        self.c.execute('SELECT * FROM logging WHERE server=?', (ctx.guild.id,))
        logging_table = self.c.fetchone()
        self.c.execute('SELECT * FROM config WHERE guild_id=?',
                       (ctx.guild.id,))
        config = self.c.fetchone()
        self.c.execute(
            'SELECT user_id, plonked FROM userconfig WHERE guild_id=?', (ctx.guild.id,))
        id_and_plonk = self.c.fetchall()
        print(id_and_plonk)
        self.c.execute('''SELECT log_channel, twitch_channel, prefix
                          FROM servers WHERE id=?''',
                       (ctx.guild.id,))
        cfg = self.c.fetchone()

        e = discord.Embed(title=f"{ctx.guild.name}",
                          description=f"Bot config for {ctx.guild.name}")
        enabled, disabled = [], []
        for k, v in enu.items():
            if logging_table[v]:
                enabled.append(k.capitalize())
            else:
                disabled.append(k.capitalize())
        ena = '\n'.join(enabled) or "None"
        dis = '\n'.join(disabled) or "None"
        cmd_ignore = config[1]
        if cmd_ignore is None:
            cmd_ignore = "None"
        elif cmd_ignore == "":
            cmd_ignore = "None"
        else:
            cmd_ignore = '\n'.join("<#{}>".format(x)
                                   for x in config[1].split(',') if x != "")
        ignore = logging_table[8] or "None"
        if ignore != "None":
            ignore = '\n'.join("<#{}>".format(x)
                               for x in ignore.split(',') if x != "")
        if config[2] is None:
            cmd_disabled = "None"
        elif config[2] == "":
            cmd_disabled = "None"
        else:
            cmd_disabled = config[2].split(',')
            cmd_disabled = ', '.join(cmd_disabled) or None
        log_chan = f'<#{cfg[0]}>' if cfg[0] is not None else "None"
        twtch_chan = f'<#{cfg[1]}>' if cfg[1] is not None else "None"
        self.c.execute('''SELECT *
                          FROM greetings
                          WHERE guild_id=?''',
                          (ctx.guild.id,))
        greet = self.c.fetchone()
        try:
            _, greet_chn, gre_msg, far_msg, ban_msg = greet
        except:
            greet_chn = "None"
        else:
            greet_chn = f"<#{greet_chn}>"
            

        if greet_chn == "None":
            gre_msg = far_msg = ban_msg = "<:redtick:318044813444251649>"
        else:
            gre_msg = "<:greentick:318044721807360010>" if gre_msg is not None else "<:redtick:318044813444251649>"
            far_msg = "<:greentick:318044721807360010>" if gre_msg is not None else "<:redtick:318044813444251649>"
            ban_msg = "<:greentick:318044721807360010>" if gre_msg is not None else "<:redtick:318044813444251649>"

        plonks = '\n'.join(
            [f"<@{x[0]}>" for x in id_and_plonk if x[1]]) or "None"
        server_prefixes = cfg[2].split(',')
        server_prefixes = '\n'.join(server_prefixes)
        e.add_field(name='Enabled (log)', value=ena)
        e.add_field(name='Disabled (log)', value=dis)
        e.add_field(name='Ignored Channels (log)', value=ignore)
        e.add_field(name="Ignored Channels", value=cmd_ignore)
        e.add_field(name="Disabled Commands", value=cmd_disabled)
        e.add_field(name="Plonks", value=plonks)
        e.add_field(name="Logging Channel", value=log_chan)
        e.add_field(name="Twitch Channel", value=twtch_chan)
        e.add_field(name="Greet Channel", value=greet_chn)
        e.add_field(name="Greets?", value=f"{gre_msg} Greet msg\n{far_msg} Farewell msg\n{ban_msg} Ban msg")
        e.add_field(name="Prefixes", value=server_prefixes)
        await ctx.send(embed=e)

    @commands.group(name='log', invoke_without_command=True)
    @checks.admin_or_permissions(manage_server=True)
    async def _log(self, ctx, logging: str = None):
        # This is mostly to keep myself sane
        enumeration = {
            "edit": 1,
            "delete": 2,
            "role": 3,
            "name": 4,
            "join": 5,
            "avatar": 6,
            "ban": 7
        }
        # this allows the user to be pretty
        # vague in their logging options
        # and still get the right option
        # also makes it less 1337h4xx0r
        translation = {
            "avatar": "avatar_changes",
            "edit": "message_edit",
            "role": "role_changes",
            "delete": "message_deletion",
            "ban": "bans",
            "join": "member_movement",
            "name": "name_update"
        }
        if logging is None or logging.lower() == "help":
            return await ctx.send(f"Usage `!log <action>` where action is one of the following: avatar, edit, role, delete, ban, join, name, ignore or unignore")
        logging = logging.lower()
        update = None
        self.c.execute('''SELECT *
                          FROM logging
                          WHERE server=?''',
                       (ctx.message.guild.id,))
        logging_config = self.c.fetchone()
        if logging_config is None:
            # This only happens if the bot somehow missed adding the guild
            self.c.execute('''INSERT INTO logging
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                           (ctx.message.guild.id, 1, 1, 1, 1, 1, 1, 1))
            self.conn.commit()
            # We still want the command to work, and by default everything will be set to true
            self.c.execute('''SELECT *
                              FROM logging
                              WHERE server=?''',
                           (ctx.message.guild.id,))
            logging_config = self.c.fetchone()
        # This looks very ugly but I'm not
        # entirely sure how I'd meaningfully
        # change it
        if "avatar" in logging:
            string = "avatar"
        elif "edit" in logging:
            string = "edit"
        elif "delete" in logging:
            string = "delete"
        elif "role" in logging:
            string = "role"
        elif "ban" in logging:
            string = "ban"
        elif "join" in logging:
            string = "join"
        elif "leave" in logging:
            string = "join"
        elif "name" in logging:
            string = "name"

        else:
            return await ctx.send(f"That isn't a valid subcommand, try: avatar, edit, role, delete, ban, join, name, ignore or unignore")

        update = translation[string]
        index = enumeration[string]
        value = not logging_config[index]
        # This only looks unsafe
        # for some reason sqlite3 doesn't
        # like me using bindings to select which
        # column that will be updated so I use
        # string interpolation instead ¯\_(ツ)_/¯
        self.c.execute(f'''UPDATE logging
                           SET {translation[string]}=?
                           WHERE server=?''',
                       (value, ctx.message.guild.id))
        self.conn.commit()

        await ctx.send("Set {} to {}".format(logging, value))

    @_log.command()
    @checks.admin_or_permissions(manage_server=True)
    async def ignore(self, ctx, channel: discord.TextChannel=None):
        mentioned_chans = [
            channel.id] if channel is not None else [ctx.channel.id]
        if len(ctx.message.channel_mentions) >= 2:
            mentioned_chans = [x.id for x in ctx.message.channel_mentions]
        mentioned_chans = ','.join([str(x)
                                    for x in mentioned_chans if x is not None])

        self.c.execute('''SELECT ignored_channels
                          FROM logging
                          WHERE server=?''',
                       (ctx.message.guild.id,))
        ignored_channels = self.c.fetchone()[0]

        # our already ignored channels
        saved_channels = ignored_channels.split(
            ',') if ignored_channels is not None else []

        # Since I have an ignore and an unignore command, I can use set.union()
        # To make calculating the new ignored channels easy
        new_channels = list(
            set(mentioned_chans.split(',')).union(saved_channels))
        new_channels = [x for x in new_channels if x != ""]
        new_channels = ','.join(new_channels)

        self.c.execute('''UPDATE logging
                          SET ignored_channels=?
                          WHERE server=?''',
                       (new_channels, ctx.message.guild.id))
        self.conn.commit()

        if channel is None:
            # If no channels were mentioned, assume they wanted the
            # channel the message was sent in to be ignored
            mentioned_chans = ','.join(
                [x for x in mentioned_chans.split(',') if x is not None])
            names = ', '.join(["<#{}>".format(x)
                               for x in mentioned_chans.split(',')])
        else:
            channel_mentions = ctx.message.channel_mentions
            new_channels = ','.join([str(x.id)
                                     for x in channel_mentions if x is not None])
            names = ', '.join(["<#{}>".format(x)
                               for x in new_channels.split(',')])
        await ctx.send("Ignored {}".format(names))
        # This is of course wrong when mentioning more channels
        # Than will be added, hopefully people know not to

    @_log.command()
    @checks.admin_or_permissions(manage_server=True)
    async def unignore(self, ctx, channel: discord.TextChannel=None):
        mentioned_chans = [
            channel.id] if channel is not None else [ctx.channel.id]
        if len(ctx.message.channel_mentions) >= 2:
            mentioned_chans = [x.id for x in ctx.message.channel_mentions]
        mentioned_chans = ','.join([str(x)
                                    for x in mentioned_chans if x is not None])

        self.c.execute('''SELECT ignored_channels
                          FROM logging
                          WHERE server=?''',
                       (str(ctx.message.guild.id),))
        unignored_channels = self.c.fetchone()[0]

        saved_channels = unignored_channels.split(
            ',') if unignored_channels is not None else []
        new_channels = list(
            filter(lambda x: x not in mentioned_chans, saved_channels))
        new_channels = ','.join(new_channels)

        self.c.execute('''UPDATE logging
                          SET ignored_channels=?
                          WHERE server=?''',
                       (new_channels, str(ctx.message.guild.id)))
        self.conn.commit()

        if new_channels == "":
            mentioned_chans = ','.join(
                [x for x in mentioned_chans.split(',') if x is not None])
            names = ', '.join(["<#{}>".format(x)
                               for x in mentioned_chans.split(',')])
        else:
            new_channels = ','.join([x for x in new_channels if x is not None])
            names = ', '.join(["<#{}>".format(x)
                               for x in new_channels.split(',')])
        await ctx.send("Unignored {}".format(names))

    async def on_member_ban(self, guild, user):
        # first we get the channel
        self.c.execute(
            'SELECT log_channel FROM servers WHERE id=?', (str(guild.id),))
        log_channel = self.c.fetchone()
        if log_channel is None or log_channel[0] is None:
            return
        else:
            log_channel = guild.get_channel(int(log_channel[0]))
        self.c.execute('SELECT * FROM logging WHERE server=?',
                       (str(guild.id),))
        predicate = self.c.fetchone()
        # This is pretty lazy programming, selecting wildcards. But the gist of it is
        # that we want to see if ban logging is enabled or not
        if predicate[7]:
            ban_emoji = "<:FeelsBanMan:335145180833251330>"
            pretty_date = datetime.datetime.utcnow().strftime(dt_format)
            fmt = "{2} **{0}** *({0.id})* was banned from the server at `{1}`"
            await log_channel.send(fmt.format(user, pretty_date, ban_emoji))

    async def on_member_unban(self, guild, user):
        log_channel = self.c.execute(
            'SELECT log_channel FROM servers WHERE id=?', (str(guild.id),))
        log_channel = log_channel.fetchone()
        if log_channel is None or log_channel[0] is None:
            return
        else:
            log_channel = guild.get_channel(int(log_channel[0]))
        predicate = self.c.execute(
            'SELECT * FROM logging WHERE server=?', (str(guild.id),))
        predicate = self.c.fetchone()
        if predicate[7]:
            fmt = "**{0}** *({0.id})* was unbanned from the server at `{1}`"
            await log_channel.send(fmt.format(user, datetime.datetime.utcnow().strftime(dt_format)))

    async def on_member_update(self, before, after):
        if before is None:
            return
        self.c.execute('''SELECT log_channel
                          FROM servers
                          WHERE id=?''',
                       (str(before.guild.id),))
        log_channel = self.c.fetchone()
        if log_channel is None or log_channel[0] is None:
            log_channel = None
        else:
            log_channel = self.bot.get_channel(id=int(log_channel[0]))
        if before.display_name != after.display_name:
            self.c.execute('''SELECT names
                              FROM users
                              WHERE (server=? AND id=?)''',
                           (before.guild.id, before.id))
            name_list = self.c.fetchone()[0]
            name_list = name_list.split(',')
            name_list = list(OrderedDict.fromkeys(name_list))
            print(name_list)
            if after.display_name not in name_list:
                name_list.append(after.display_name)
            else:
                # To prevent duplicate nicknames for the !nicks command
                # bringing the name to the tail of the list is a decent solution
                old_index = name_list.index(after.display_name)
                name_list.pop(old_index)
                name_list.append(after.display_name)
            new_names = ','.join(name_list)
            self.c.execute('''UPDATE users
                              SET names=?
                              WHERE (id=? AND server=?)''',
                           (new_names, before.id, before.guild.id))
            self.conn.commit()
            fmt = ":spy: **{0}** changed their nickname:\n**Before:** {1}\n**+After:** {2}"
            fmt_edit = ":spy: **{0}** had their nickname changed by **{3}**:\n**Before:** {1}\n**+After:** {2}"
            fmt_edit_self = ":spy: **{0}** changed their own nickname:\n**Before:** {1}\n**+After:** {2}"
            fmt = fmt.format(before, before.display_name, after.display_name)
            fmt = clean_string(fmt)
            # No @everyones
            # No codeblocks
            fmt = re.sub("([`])", r"\\\1", fmt)
            predicate = self.c.execute(
                'SELECT * FROM logging WHERE server=?', (before.guild.id,))
            predicate = self.c.fetchone()
            if predicate[4] and log_channel is not None:
                msg = await log_channel.send(fmt)
                perms = before.guild.me.guild_permissions
                if not perms.view_audit_log:
                    return
                action = discord.AuditLogAction.member_update
                async for entry in before.guild.audit_logs(limit=100, action=action):
                    # Unlike some other audit log actions, name changes seem _very_ responsive
                    # and even spamming it seems to have no effect on its accuracy
                    # It's one ugly conditional but it sure works
                    if entry.target == after:
                        if (before.display_name == entry.before.nick and (after.display_name == entry.after.nick or entry.after.nick is None)) or (entry.before.nick is None and after.display_name == entry.after.nick):
                            if entry.target != entry.user:
                                await msg.edit(content=fmt_edit.format(before, before.display_name, after.display_name, entry.user))
                                return
                            else:
                                await msg.edit(content=fmt_edit_self.format(before, before.display_name, after.display_name))
                                return

        elif before.roles != after.roles:
            roles = ','.join([str(x.id)
                              for x in after.roles if x.name != "@everyone"])
            self.c.execute('UPDATE users SET roles=? WHERE (id=? AND server=?)',
                           (roles, before.id, before.guild.id))
            self.conn.commit()
            if len(before.roles) < len(after.roles):
                # role added
                s = set(before.roles)
                # Check for what actually happened
                newrole = [x for x in after.roles if x not in s]
                if len(newrole) == 1:
                    fmt = ":warning: **{}#{}** had the role **{}** added.".format(
                        before.name, before.discriminator, newrole[0].name)
                elif not newrole:
                    return
                else:
                    # This happens when the bot autoassigns your roles
                    # after rejoining the server
                    new_roles = [x.name for x in newrole]
                    fmt = ":warning: **{}#{}** had the roles **{}** added.".format(
                        before.name, before.discriminator, ', '.join(new_roles))
                predicate = self.c.execute(
                    'SELECT * FROM logging WHERE server=?', (before.guild.id,))
                predicate = self.c.fetchone()
                if predicate[3] and log_channel is not None:
                    msg = await log_channel.send(clean_string(fmt))
                    perms = before.guild.me.guild_permissions
                    if not perms.view_audit_log:
                        return
                    # Like for nicknames, it's very reliable
                    # It seems to work well for updates where more than one role was added
                    async for entry in before.guild.audit_logs(limit=100, action=discord.AuditLogAction.member_role_update):
                        if entry.target == after:
                            if entry.target != entry.user:
                                await msg.edit(content=msg.content[:-1] + " to them by **{}**.".format(entry.user))
                                return
                            await msg.edit(content=":warning: **{}#{}** added the role **{}** to themselves.".format(before.name, before.discriminator, newrole[0].name))
                            return
            else:
                s = set(after.roles)
                newrole = [x for x in before.roles if x not in s]
                if len(newrole) == 1:
                    fmt = ":warning: **{}#{}** had the role **{}** removed.".format(
                        before.name, before.discriminator, newrole[0].name)
                elif len(newrole) == 0:
                    return
                else:
                    new_roles = [x.name for x in newrole]
                    fmt = ":warning: **{}#{}** had the roles **{}** removed.".format(
                        before.name, before.discriminator, ', '.join(new_roles))
                predicate = self.c.execute(
                    'SELECT * FROM logging WHERE server=?', (before.guild.id,))
                predicate = self.c.fetchone()
                if predicate[3] and log_channel is not None:
                    msg = await log_channel.send(clean_string(fmt))
                    perms = before.guild.me.guild_permissions
                    if not perms.view_audit_log:
                        return
                    async for entry in before.guild.audit_logs(limit=100, action=discord.AuditLogAction.member_role_update):
                        if entry.target == after:
                            if entry.target != entry.user:
                                await msg.edit(content=msg.content[:-1] + " from them by **{}**.".format(entry.user))
                                return
                            await msg.edit(content=":warning: **{}#{}** removed the role **{}** from themselves.".format(before.name, before.discriminator, newrole[0].name))
                            return

        elif (before.avatar != after.avatar) and after.avatar is not None:
            # rewrite currently fucks this real good
            # in the future it will be fixed
            # as of right now it will send this update to a random
            # server the member is in
            fmt = ":spy: **{0}#{1}** changed their avatar:\n**After:** {2}"
            predicate = self.c.execute(
                'SELECT * FROM logging WHERE server=?', (after.guild.id,))
            predicate = self.c.fetchone()
            if predicate[6] and log_channel is not None:
                await log_channel.send(fmt.format(after.name, after.discriminator, after.avatar_url.replace(".webp", ".png")))

    async def on_member_join(self, member):
        log_channel = self.c.execute(
            'SELECT log_channel FROM servers WHERE id=?', (member.guild.id,))
        log_channel = log_channel.fetchone()
        if log_channel is not None and log_channel[0] is not None:
            log_channel = member.guild.get_channel(int(log_channel[0]))
        try:
            if member.guild.id == 207943928018632705:
                # Need to know when I'm being powerplayed
                fmt = ":white_check_mark: **{0.name}#{0.discriminator}** *({0.id})* Joined the server at `{1}` :white_check_mark: <@137267770537541632> <@106429844627169280> <@158370770068701184> :white_check_mark:"
            else:
                fmt = ":white_check_mark: **{0.name}#{0.discriminator}** *({0.id})* Joined the server at `{1}` :white_check_mark:"
            predicate = self.c.execute(
                'SELECT * FROM logging WHERE server=?', (member.guild.id,))
            predicate = self.c.fetchone()
            if predicate[5]:
                await log_channel.send(fmt.format(member, datetime.datetime.utcnow().strftime(dt_format)))

        except Exception as e:
            print(f"on_member_join={e}")
        a = self.c.execute(
            'SELECT names FROM users WHERE (server=? AND id=?)', (member.guild.id, member.id))
        add_this_name = a.fetchone()
        # This is so fucking stupid
        if add_this_name is not None:
            add_this_name = add_this_name[0]
        if add_this_name is not None:
            add_this_name = add_this_name.split(',')[-1]
            can_edit_names = member.guild.me.guild_permissions.manage_nicknames
            if can_edit_names:
                try:
                    await member.edit(nick=add_this_name)
                except Exception as e:
                    ch = self.bot.get_channel(344986487676338187)
                    await ch.send(f"{e} in {member.guild.name} when {member} tried to join.")
            # Sleeping seems required for both the role and nickname change to go through
            await asyncio.sleep(1)
        allRoles = member.guild.roles
        self.c.execute('SELECT roles FROM users WHERE (server=? AND id=?)', (member.guild.id, member.id))
        checkthis = self.c.fetchone()
        self.c.execute('SELECT autoroles, reassign FROM role_config WHERE guild_id=?', (member.guild.id,))
        autoroles, reassign = self.c.fetchone()
        can_edit = member.guild.me.guild_permissions.manage_roles
        if not can_edit:
            return

        rolestobeadded = []
        if checkthis is not None:
            checkthis = checkthis[0]
            if checkthis is not None and reassign:
                checkthis = checkthis.split(',')
                # if even one role can't be added, none will be
                # because of this, I check the role hierarchy
                rolestobeadded = [x for x in allRoles if (
                    str(x.id) in checkthis and x < member.guild.me.top_role)]
        if autoroles is not None:
            if autoroles is not None:
                autoroles = autoroles.split(',')
                autoroles = [x for x in allRoles if (str(x.id) in autoroles and x < member.guild.me.top_role)]
                rolestobeadded.extend(autoroles)
                rolestobeadded = list(set(rolestobeadded))
        if rolestobeadded:
            try:
                await member.edit(roles=rolestobeadded)
            except:
                chn = self.bot.get_channel(344986487676338187)
                await chn.send("Failed to give roles: {} to {} in {}".format(', '.join(rolestobeadded), member, member.guild.name))

    async def on_member_remove(self, member):
        destination = self.c.execute(
            'SELECT log_channel FROM servers WHERE id=?', (member.guild.id,))
        log_channel = destination.fetchone()
        if log_channel is None or log_channel[0] is None:
            return
        else:
            log_channel = member.guild.get_channel(int(log_channel[0]))
        if member.guild.id == 207943928018632705:
            fmt = ":wave: **{0.name}#{0.discriminator}** *({0.id})* Left the server at `{1}`<@137267770537541632> <@106429844627169280> <@158370770068701184> :wave:"
            fmt_log = ":wave: **{0.name}#{0.discriminator}** *({0.id})* Left the server at `{1}` after being kicked by **{2}** <@137267770537541632> <@106429844627169280> <@158370770068701184>"
            fmt_banlog = ":wave: **{0.name}#{0.discriminator}** *({0.id})* Left the server at `{1}` after being banned by **{2}** <@137267770537541632> <@106429844627169280> <@158370770068701184>"

        else:
            fmt = ":wave: **{0.name}#{0.discriminator}** *({0.id})* Left the server at `{1}` :wave:"
            fmt_log = ":wave: **{0.name}#{0.discriminator}** *({0.id})* Left the server at `{1}` after being kicked by **{2}**"
            fmt_banlog = ":wave: **{0.name}#{0.discriminator}** *({0.id})* Left the server at `{1}` after being banned by **{2}**"

        predicate = self.c.execute(
            'SELECT * FROM logging WHERE server=?', (member.guild.id,))
        predicate = self.c.fetchone()
        if predicate[5]:
            msg = await log_channel.send(fmt.format(member, datetime.datetime.utcnow().strftime(dt_format)))
            perms = member.guild.me.guild_permissions
            if not perms.view_audit_log:
                return
            async for entry in member.guild.audit_logs(limit=100):
                # Checks to see if a reason was given for kicking/banning the user
                # Limited to the last 10 seconds
                # if you ban someone enough times for the audit logs
                # to group them together, it won't find a reason
                # probably timer based, unlucky
                if entry.target == member and (entry.action == discord.AuditLogAction.kick or entry.action == discord.AuditLogAction.ban):
                    if entry.action == discord.AuditLogAction.ban:
                        postme = fmt_banlog.format(
                            member, datetime.datetime.utcnow().strftime(dt_format), entry.user)
                    else:
                        postme = fmt_log.format(
                            member, datetime.datetime.utcnow().strftime(dt_format), entry.user)
                    if -10 < (entry.created_at - datetime.datetime.utcnow()).total_seconds() < 10:
                        if entry.reason is not None:
                            postme = "{} with the reason: {}:wave:".format(
                                postme, entry.reason)

                        else:
                            postme = "{} without a reason :wave:".format(
                                postme)
                        await msg.edit(content=postme)
                        return


    async def on_message(self, message):
        if message.guild is None:
            return
        if message.author.bot:
            return
        if message.guild.id != 218148381954932736:
            return
        if message.channel.id in DEGENERATE_CHANNELS:
            links = re.findall(self.website_regex, message.content)
            if links or message.attachments:
                return
            await message.delete()
            





    # async def on_message(self, message):
    #     if message is None:
    #         return
    #     if message.guild is None:
    #         return
    #     if message.author.id == self.bot.user.id:
    #         return
    #     if message.attachments:
    #         s_url = message.attachments[0].url
    #         filename = message.attachments[0].filename
    #         if re.match(r"^(?:.*\.(mp4|webm|mkv|mov)$)$", filename):
    #             s = await message.channel.send("Discord doesn't embed direct uploads, would you like me to upload it to streamable? (y/n)")
    #             msg = await self.bot.wait_for('message', check=lambda m: m.content.lower() == 'y' and m.author == message.author, timeout=30.0)
    #             if msg:
    #                 await msg.delete()
    #                 stream_msg = await message.channel.send('\U0001f44c sending file to streamable...')
    #                 await s.delete()
    #                 USER_AGENT = 'Carl-bot/2.1.9 (Linux; Ubuntu 16.8)'
                    
    #                 async with self.bot.session.get(url="https://api.streamable.com/import?url={}".format(s_url), headers={'User-Agent': USER_AGENT}, auth=aiohttp.BasicAuth(login="carl.groth@protonmail.com", password="google123")) as r:
    #                     print(await r.text())
    #                     reply = await r.json()
    #                 await stream_msg.edit(content="<https://streamable.com/{}> processing video...".format(reply['shortcode']))
    #                 embed = False
    #                 tries = 0
    #                 while not embed:
    #                     # gotta edit the message for the embed to show
    #                     # the first link doesn't actually point to a video
    #                     # and streamable takes a few seconds to process the video
    #                     if (tries % 5) == 0:
    #                         async with self.bot.session.get("https://api.streamable.com/videos/{}".format(reply['shortcode'])) as r:
    #                             ree = await r.json()
    #                         if ree['status'] == 2:
    #                             embed = True
    #                         elif tries == 100:
    #                             break
    #                     my_dots = (tries % 4) * "."
    #                     # This would probably be enough for b1nzy
    #                     # to personally ban my account, no snitch
    #                     await stream_msg.edit(content="<https://streamable.com/{}> processing video{}".format(reply['shortcode'], my_dots))

    #                     tries += 1
    #                     await asyncio.sleep(1)
    #                 await stream_msg.edit(content="https://streamable.com/{}".format(reply['shortcode']))

    async def on_message_delete(self, message):
        if message is None:
            return
        if message.guild is None:
            return
        if message.author.bot:
            if not "embed" in message.content:
                return
        if message.content == "":
            return

        poststring = clean_string(":x: `{1}` **{0}** deleted their message:  ```{2}``` in `{3}`".format(message.author, time.strftime("%H:%M:%S"), message.clean_content, message.channel))
        logstring = ":x: `{1}` **{0}** had their message deleted by **{4}**:  ```{2}``` in `{3}`"

        if message.attachments:
            poststring += "\n{}".format(message.attachments[0].url)

        log_channel = self.c.execute(
            'SELECT log_channel FROM servers WHERE id=?', (message.guild.id,))
        log_channel = log_channel.fetchone()
        if log_channel is None or log_channel[0] is None:
            return
        else:
            log_channel = message.guild.get_channel(int(log_channel[0]))
        predicate = self.c.execute(
            'SELECT * FROM logging WHERE server=?', (message.guild.id,))
        predicate = self.c.fetchone()
        ignore_predicate = predicate[8].split(
            ',') if predicate[8] is not None else []
        if str(message.channel.id) in ignore_predicate:
            return
        if predicate[2]:
            msg = await log_channel.send(poststring)
            perms = message.guild.me.guild_permissions
            if not perms.view_audit_log:
                return
            async for entry in message.guild.audit_logs(limit=100, action=discord.AuditLogAction.message_delete):
                if entry.target == message.author:
                    if -10 < (entry.created_at - datetime.datetime.utcnow()).total_seconds() < 10:
                        await msg.edit(content=clean_string(logstring.format(message.author, time.strftime("%H:%M:%S"), message.clean_content, message.channel, entry.user)))
                        return

    async def on_message_edit(self, before, after):
        if before.guild is None:
            return
        if before.clean_content == after.clean_content:
            return
        if before.author.id == self.bot.user.id:
            return

        log_channel = self.c.execute(
            'SELECT log_channel FROM servers WHERE id=?', (before.guild.id,))
        log_channel = log_channel.fetchone()
        if log_channel is None or log_channel[0] is None:
            return
        else:
            log_channel = before.guild.get_channel(int(log_channel[0]))
        fmt = ":pencil2: `{}` **{}** edited their message:\n**Before:** {}\n**+After:** {}"
        predicate = self.c.execute(
            'SELECT * FROM logging WHERE server=?', (before.guild.id,))
        predicate = self.c.fetchone()
        ignore_predicate = predicate[8].split(
            ',') if predicate[8] is not None else []
        if str(before.channel.id) in ignore_predicate:
            return
        if predicate is None:
            predicate = False
        if predicate[1]:
            await log_channel.send(fmt.format(time.strftime("%H:%M:%S"), before.author, before.clean_content, after.clean_content))


def setup(bot):
    bot.add_cog(Automod(bot))
