import json
import discord
import asyncio
import inspect
import datetime
import time
import re
import aiohttp
import sqlite3

from collections import Counter
from discord.ext import commands
from cogs.utils import config, checks

def clean_string(string):
    string = re.sub('@', '@\u200b', string)
    string = re.sub('#', '#\u200b', string)
    return string

def load_json(filename):
    with open(filename, encoding='utf-8') as infile:
        return json.load(infile)

def write_json(filename, contents):
    with open(filename, 'w') as outfile:
        json.dump(contents, outfile, indent=4)

CARL_DISCORD_ID = "106429844627169280"

class Automod:
    def __init__(self, bot):
        self.bot = bot
        self.invites = load_json('invites.json')
        self.conn = sqlite3.connect('database.db')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS servers
             (id text, log_channel text, twitch_channel text, welcome_message text, bot_channel text)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS logging
             (server text, message_edit boolean, message_deletion boolean, role_changes boolean, name_update boolean, member_movement boolean, avatar_changes boolean, bans boolean, ignored_channels text)''')


    @commands.group(name='set', pass_context=True, invoke_without_command=True)
    @checks.admin_or_permissions(manage_server=True)
    async def _set(self, ctx):
        await self.bot.say("You need to use a subcommand")


    @_set.command(pass_context=True)
    @checks.admin_or_permissions(manage_server=True)
    async def twitch(self, ctx, *, channel: discord.Channel = None):
        if channel is None:
            return await self.bot.say("You need to mention a channel")
        self.c.execute('UPDATE servers SET twitch_channel=? WHERE id=?', (channel.id, ctx.message.server.id))
        self.conn.commit()
        await self.bot.say("Twitch channel changed to <#{}>".format(channel.id))

    @_set.command(pass_context=True, aliases=['logs', 'logchannel'])
    @checks.admin_or_permissions(manage_server=True)
    async def log(self, ctx, *, channel: discord.Channel = None):
        if channel is None:
            return await self.bot.say("You need to mention a channel")
        self.c.execute('UPDATE servers SET log_channel=? WHERE id=?', (channel.id, ctx.message.server.id))
        self.conn.commit()
        await self.bot.say("Logging channel changed to <#{}>".format(channel.id))
    
    @_set.command(pass_context=True, name='bot', aliases=['botchannel'])
    @checks.admin_or_permissions(manage_server=True)
    async def _bot(self, ctx, channel: discord.Channel = None):
        if channel is None:
            return await self.bot.say("You need to mention a channel")
        self.c.execute('UPDATE servers SET bot_channel=? WHERE id=?', (channel.id, ctx.message.server.id))
        self.conn.commit()
        await self.bot.say("Bot channel changed to <#{}>".format(channel.id))


    @_set.command(pass_context=True, aliases=['welcomemessage'])
    @checks.admin_or_permissions(manage_server=True)
    async def welcome(self, ctx, *, message: str = None):
        if message is None:
            self.c.execute('UPDATE servers SET welcome_message=? WHERE id=?', (None, ctx.message.server.id))
            self.conn.commit()
            return await self.bot.say("Welcome message removed")
        self.c.execute('UPDATE servers SET welcome_message=? WHERE id=?', (message, ctx.message.server.id))
        self.conn.commit()
        await self.bot.say("Welcome message successfully updated.")









    @commands.group(name='log', pass_context=True, invoke_without_command=True)
    @checks.admin_or_permissions(manage_server=True)
    async def _log(self, ctx, logging: str = None):
        if logging is None:
            return await self.bot.say("You need to use a subcommand")
        translation = {
            "avatar": "avatar_changes",
            "edit"  : "message_edit",
            "role"  : "role_changes",
            "delete": "message_deletion",
            "ban"   : "bans",
            "join"  : "member_movement",
            "name"  : "name_update"
        }
        enumeration = {
            "edit"  : 1,
            "delete": 2,
            "role"  : 3,
            "name"  : 4,
            "join"  : 5,
            "avatar": 6,
            "ban"   : 7
        }
        logging = logging.lower()
        update = None
        a = self.c.execute('SELECT * FROM logging WHERE server=?', (ctx.message.server.id,))
        a = a.fetchone()
        if a is None:
            self.c.execute('INSERT INTO logging VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (ctx.message.server.id, 1, 1, 1, 1, 1, 1, 1))
            self.conn.commit()
            a = self.c.execute('SELECT * FROM logging WHERE server=?', (ctx.message.server.id,))
            a = a.fetchone()
        if "avatar" in logging:
            update = translation["avatar"]
            index = enumeration["avatar"]
            value = not a[index]
            self.c.execute('UPDATE logging SET avatar_changes=? WHERE server=?', (value, ctx.message.server.id))
            self.conn.commit()
        elif "edit" in logging:
            update = translation["edit"]
            index = enumeration["edit"]
            value = not a[index]
            self.c.execute('UPDATE logging SET message_edit=? WHERE server=?', (value, ctx.message.server.id))
            self.conn.commit()
        elif "delete" in logging:
            update = translation["delete"]
            index = enumeration["delete"]
            value = not a[index]
            self.c.execute('UPDATE logging SET message_deletion=? WHERE server=?', (value, ctx.message.server.id))
            self.conn.commit()
        elif "role" in logging:
            update = translation["role"]
            index = enumeration["role"]
            value = not a[index]
            self.c.execute('UPDATE logging SET role_changes=? WHERE server=?', (value, ctx.message.server.id))
            self.conn.commit()
        elif "ban" in logging:
            update = translation["bans"]
            index = enumeration["bans"]
            value = not a[index]
            self.c.execute('UPDATE logging SET bans=? WHERE server=?', (value, ctx.message.server.id))
            self.conn.commit()
        elif "join" in logging:
            update = translation["join"]
            index = enumeration["join"]
            value = not a[index]
            self.c.execute('UPDATE logging SET member_movement=? WHERE server=?', (value, ctx.message.server.id))
            self.conn.commit()
        elif "leave" in logging:
            update = translation["join"]
            index = enumeration["join"]
            value = not a[index]
            self.c.execute('UPDATE logging SET member_movement=? WHERE server=?', (value, ctx.message.server.id))
            self.conn.commit()
        elif "name" in logging:
            update = translation["name"]
            index = enumeration["name"]
            value = not a[index]
            self.c.execute('UPDATE logging SET name_update=? WHERE server=?', (value, ctx.message.server.id))
            self.conn.commit()
        else:
            return await self.bot.say("Invalid subcommand passed, accepted subcommands: avatar, edit, role, delete, ban, join, name")
        
        
        await self.bot.say("Set {} to {}".format(logging, value))


        

    @_log.command(pass_context=True)
    @checks.admin_or_permissions(manage_server=True)
    async def ignore(self, ctx, channel: discord.Channel = None):
        mentioned_channels = [channel.id] if channel is not None else ([x.id for x in ctx.message.server.channels if str(x.type) == "text"])
        if len(ctx.message.channel_mentions) >= 2:
            mentioned_channels = [x.id for x in ctx.message.channel_mentions]
        mentioned_channels = ','.join([x for x in mentioned_channels if x is not None])
        a = self.c.execute('SELECT ignored_channels FROM logging WHERE server=?', (ctx.message.server.id,))
        self.conn.commit()
        a = a.fetchone()[0]
        saved_channels = a.split(',') if a is not None else []
        print(saved_channels, mentioned_channels)
        new_channels = list(set(mentioned_channels.split(',')).union(saved_channels))
        new_channels = [x for x in new_channels if x != ""]
        new_channels = ','.join(new_channels)
        print(channel)
        self.c.execute('UPDATE logging SET ignored_channels=? WHERE server=?', (new_channels, ctx.message.server.id))
        self.conn.commit()
        print("New channels: x{}x".format(new_channels))
        if channel is None:            
            mentioned_channels = ','.join([x for x in mentioned_channels.split(',') if x is not None])
            print(mentioned_channels)
            names = ', '.join(["<#{}>".format(x) for x in mentioned_channels.split(',')])
        else:
            new_channels = ','.join([x.id for x in ctx.message.channel_mentions if x is not None])
            names = ', '.join(["<#{}>".format(x) for x in new_channels.split(',')])
        await self.bot.say("Ignored {}".format(names))

    @_log.command(pass_context=True)
    @checks.admin_or_permissions(manage_server=True)
    async def unignore(self, ctx, channel: discord.Channel = None):
        mentioned_channels = [channel.id] if channel is not None else ([x.id for x in ctx.message.server.channels if str(x.type) == "text"])
        if len(ctx.message.channel_mentions) >= 2:
            mentioned_channels = [x.id for x in ctx.message.channel_mentions]
        mentioned_channels = ','.join([x for x in mentioned_channels if x is not None])
        a = self.c.execute('SELECT ignored_channels FROM logging WHERE server=?', (ctx.message.server.id,))
        self.conn.commit()
        a = a.fetchone()[0]
        saved_channels = a.split(',') if a is not None else []
        new_channels = list(filter(lambda x: x not in mentioned_channels, saved_channels))
        new_channels = ','.join(new_channels)
        print(mentioned_channels)
        self.c.execute('UPDATE logging SET ignored_channels=? WHERE server=?', (new_channels, ctx.message.server.id))
        self.conn.commit()
        print("New channels: x{}x".format(new_channels))
        if new_channels == "":            
            mentioned_channels = ','.join([x for x in mentioned_channels.split(',') if x is not None])
            print(mentioned_channels)
            names = ', '.join(["<#{}>".format(x) for x in mentioned_channels.split(',')])
        else:
            new_channels = ','.join([x for x in new_channels if x is not None])
            names = ', '.join(["<#{}>".format(x) for x in new_channels.split(',')])
        await self.bot.say("Unignored {}".format(names))








    async def serverfix(self, server):
        if server.id not in self.invites:
            self.invites[server.id] = {}
        write_json('invites.json', self.invites)

    async def on_member_ban(self, member):
        log_channel = self.c.execute('SELECT log_channel FROM servers WHERE id=?', (member.server.id,))
        log_channel = log_channel.fetchall()
        if log_channel == [] or log_channel[0][0] is None:
            log_channel = discord.utils.get(member.server.channels, name='log')
            if log_channel is None:
                return
        else:
            log_channel = discord.Object(id=log_channel[0][0])
        predicate = self.c.execute('SELECT * FROM logging WHERE server=?', (member.server.id,))
        predicate = self.c.fetchone()
        if predicate[7]:
            print("Banning is enabled so I announce it")
            await self.bot.send_message(log_channel, "<:FeelsBanMan:335145180833251330> **{0}#{1}** was just banned from the server.".format(member.name, member.discriminator))
        else:
            print("Banning isn't enabled, not broadcasting")
    async def on_member_unban(self, server, user):
        log_channel = self.c.execute('SELECT log_channel FROM servers WHERE id=?', (server.id,))
        log_channel = log_channel.fetchall()
        if log_channel == [] or log_channel[0][0] is None:
            log_channel = discord.utils.get(server.channels, name='log')
            if log_channel is None:
                return
        else:
            log_channel = discord.Object(id=log_channel[0][0])
        predicate = self.c.execute('SELECT * FROM logging WHERE server=?', (server.id,))
        predicate = self.c.fetchone()
        if predicate[7]:
            print("bans is enabled so I announce it")
            await self.bot.send_message(log_channel, "**{0}#{1}** was just unbanned from the server.".format(user.name, user.discriminator))
        else:
            print("bans isn't enabled, not broadcasting")
        



    async def on_member_update(self, before, after,):
        if before is None:
            return
        log_channel = self.c.execute('SELECT log_channel FROM servers WHERE id=?', (before.server.id,))
        log_channel = log_channel.fetchall()
        if log_channel == [] or log_channel[0][0] is None:
            log_channel = discord.utils.get(before.server.channels, name='log')
            if log_channel is None:
                return
        else:
            log_channel = discord.Object(id=log_channel[0][0])
        if before.display_name != after.display_name:
            a = self.c.execute('SELECT names FROM users WHERE (server=? AND id=?)', (before.server.id, before.id))
            name_list = a.fetchall()
            name_list = [''.join(x) for x in name_list]
            fmt = ":spy: **{0}#{1}** changed their nickname:\n**Before:** {2}\n**+After:** {3}"
            fmt = fmt.format(before.name, before.discriminator, before.display_name, after.display_name)
            fmt = clean_string(fmt)
            predicate = self.c.execute('SELECT * FROM logging WHERE server=?', (before.server.id,))
            predicate = self.c.fetchone()
            if predicate[4]:
                print("name is enabled so I announce it")
                await self.bot.send_message(log_channel, fmt)
            else:
                print("name isn't enabled, not broadcasting")
            
            #await self.userfix(before)            
            if after.display_name not in name_list:
                name_list.append(after.display_name)
            else:
                #duplicate nicknames are lame
                old_index = name_list.index(after.display_name)
                name_list.pop(old_index)
                name_list.append(after.display_name)
            new_names = ','.join(name_list)
            self.c.execute('UPDATE users SET names=? WHERE (id=? AND server=?)', (new_names, before.id, before.server.id))
            self.conn.commit()
        elif before.roles != after.roles:
            roles = ','.join([x.id for x in after.roles if x.name != "@everyone"])
            self.c.execute('UPDATE users SET roles=? WHERE (id=? AND server=?)', (roles, before.id, before.server.id))
            self.conn.commit()
            if len(before.roles) < len(after.roles):
                #role added
                s = set(before.roles)
                newrole = [x for x in after.roles if x not in s]
                if len(newrole) == 1:
                    fmt = ":warning: **{}** had the role **{}** added.".format(before.display_name, newrole[0].name)
                elif len(newrole) == 0:
                    return
                else:
                    new_roles = [x.name for x in newrole]
                    fmt = ":warning: **{}** had the roles **{}** added.".format(before.display_name, ', '.join(new_roles))
                predicate = self.c.execute('SELECT * FROM logging WHERE server=?', (before.server.id,))
                predicate = self.c.fetchone()
                if predicate[3]:
                    print("role is enabled so I announce it")
                    await self.bot.send_message(log_channel, clean_string(fmt))
                else:
                    print("role isn't enabled, not broadcasting")
            else:
                s = set(after.roles)
                newrole = [x for x in before.roles if x not in s]
                if len(newrole) == 1:
                    fmt = ":warning: **{}** had the role **{}** removed.".format(before.display_name, newrole[0].name)
                elif len(newrole) == 0:
                    return
                else:
                    new_roles = [x.name for x in newrole]
                    fmt = ":warning: **{}** had the roles **{}** removed.".format(before.display_name, ', '.join(new_roles))
                predicate = self.c.execute('SELECT * FROM logging WHERE server=?', (before.server.id,))
                predicate = self.c.fetchone()
                if predicate[3]:
                    print("role is enabled so I announce it")
                    await self.bot.send_message(log_channel, clean_string(fmt))
                else:
                    print("role isn't enabled, not broadcasting")
                
    
        elif (before.avatar != after.avatar) and after.avatar is not None:
            fmt = ":spy: **{0}#{1}** changed their avatar:\n**After:** {2}"
            predicate = self.c.execute('SELECT * FROM logging WHERE server=?', (before.server.id,))
            predicate = self.c.fetchone()
            if predicate[6]:
                print("avatar is enabled so I announce it")
                await self.bot.send_message(log_channel, fmt.format(after.name, after.discriminator, after.avatar_url))
            else:
                print("avatar isn't enabled, not broadcasting")
            

    async def on_server_join(self, server):
        server_blacklist = []
        if server.id in server_blacklist:
            await self.bot.send_message(server.default_channel, "You've been blacklisted. :wave:")
            await self.bot.leave_server(server)
        await self.serverfix(server)
    async def on_member_join(self, member):
        log_channel = self.c.execute('SELECT log_channel FROM servers WHERE id=?', (member.server.id,))
        log_channel = log_channel.fetchall()
        if log_channel == [] or log_channel[0][0] is None:
            log_channel = discord.utils.get(member.server.channels, name='log')
            if log_channel is None:
                return
        else:
            log_channel = discord.Object(id=log_channel[0][0])
        has_perms = True
        server = member.server
        permissions = server.me.server_permissions
        if not permissions.manage_server:
            has_perms = False
            invite = None
        else:
            list_of_invites = await self.bot.invites_from(member.server)
            list_of_invites = sorted(list_of_invites, key=lambda x: x.id)
            ugly_var = self.invites[member.server.id]
            new_ting = [x for x in list_of_invites if x.id in ugly_var]
            list_of_saved_invites = sorted(ugly_var.items())
            dict_of_invites = dict(zip(new_ting, list_of_saved_invites))
            invite = "xd"
            for k, v in dict_of_invites.items():
                if k.id == v[0] and k.uses != v[1]:
                    try:
                        self.invites[member.server.id][k.id] += 1
                        invite = "**{}#{}'s** invite: {}".format(k.inviter.name, k.inviter.discriminator, k.id)
                    except KeyError:
                        self.invites[member.server.id][k.id] = 1
                        invite = "**{}#{}'s** invite: {}".format(k.inviter.name, k.inviter.discriminator, k.id)
            possible_invite = [x for x in list_of_invites if x.id not in ugly_var.keys()]
            if invite == "xd":
                if len(possible_invite) != 0:
                    try:
                        invite = "unknown invite, my guess: {0.id} from **{0.inviter.name}#{0.inviter.discriminator}**".format(possible_invite[-1])
                    except:
                        invite = "unknown invite."
                else:
                    invite = "unknown invite (really!)"
            for inv in await self.bot.invites_from(member.server):
                self.invites[member.server.id][inv.id] = inv.uses
            write_json('invites.json', self.invites)
        
        try:
            if member.server.id == "207943928018632705":
                fmt = ":white_check_mark: **{0.name}#{0.discriminator}** *({0.id})* Joined the server at `{1}` using {2} <@137267770537541632> <@106429844627169280> <@158370770068701184> :white_check_mark:"
            elif not has_perms:
                fmt = ":white_check_mark: **{0.name}#{0.discriminator}** *({0.id})* Joined the server at `{1}`"
            else:
                fmt = ":white_check_mark: **{0.name}#{0.discriminator}** *({0.id})* Joined the server at `{1}` using {2}"
            predicate = self.c.execute('SELECT * FROM logging WHERE server=?', (member.server.id,))
            predicate = self.c.fetchone()
            if predicate[5]:
                print("member movement is enabled so I announce it")
                await self.bot.send_message(log_channel, fmt.format(member, time.strftime("%Y-%m-%d %H:%M:%S (UTC+0)."), invite))
            else:
                print("member movement isn't enabled, not broadcasting")
            
        except Exception as e:
            print(e)
        a = self.c.execute('SELECT names FROM users WHERE (server=? AND id=?)', (member.server.id, member.id))
        add_this_name = a.fetchone()
        if add_this_name is not None:
            add_this_name = add_this_name[0]
        if add_this_name is not None:
            add_this_name = add_this_name.split(',')[-1]
            await self.bot.change_nickname(member, add_this_name)
            await asyncio.sleep(1)
        allRoles = member.server.roles
        a = self.c.execute('SELECT roles FROM users WHERE (server=? AND id=?)', (member.server.id, member.id))            
        checkthis = a.fetchone()
        print("checkthis: {}".format(checkthis))
        if checkthis is not None:
            checkthis = checkthis[0]
            if checkthis is None:
                print("checkthis is none")
                return
            checkthis = checkthis.split(',')
            rolestobeadded = [x for x in allRoles if (x.id in checkthis and x < member.server.me.top_role)]
            cant_add_these_roles = [x for x in allRoles if (x.id in checkthis and x >= member.server.me.top_role)]
            #rolestobeadded = [x for x in rolestobeadded if x < member.server.me.top_role]
            print(cant_add_these_roles)
            await self.bot.add_roles(member, *rolestobeadded)
        
        

    async def on_member_remove(self, member):
        destination = self.c.execute('SELECT log_channel FROM servers WHERE id=?', (member.server.id,))
        log_channel = destination.fetchall()
        if log_channel == [] or log_channel[0][0] is None:
            log_channel = discord.utils.get(member.server.channels, name='log')
            if log_channel is None:
                return
        else:
            log_channel = discord.Object(id=log_channel[0][0])
        if member.server.id == "207943928018632705":
            fmt = ":wave: **{0.name}#{0.discriminator}** *({0.id})* Left the server at `{1}`<@137267770537541632> <@106429844627169280> <@158370770068701184> :white_check_mark:"
        else:
            fmt = ":wave: **{0.name}#{0.discriminator}** *({0.id})* Left the server at `{1}` :wave:"

        predicate = self.c.execute('SELECT * FROM logging WHERE server=?', (member.server.id,))
        predicate = self.c.fetchone()
        if predicate[5]:
            print("member movement is enabled so I announce it")
            await self.bot.send_message(log_channel, fmt.format(member, datetime.datetime.utcnow(), CARL_DISCORD_ID, "158370770068701184"))
        else:
            print("member movement isn't enabled, not broadcasting")
        

    async def on_message(self, message):
        if message is None:
            return
        if message.channel.id == "267085455047000065":
            return
        if message.channel.is_private:
            return
        if message.author.id == self.bot.user.id:
            return
        if message.content != "":
            if message.clean_content[0] in ["!", "§", "++", "?"]:
                return
        if message.attachments:
            s_url = message.attachments[0]["url"]
            print(message.attachments[0])
            filename = message.attachments[0]['filename']
            if re.match(r"^(?:.*\.(mp4|webm|mkv|mov)$)$", filename):
                s = await self.bot.send_message(message.channel, "Discord doesn't embed direct uploads, would you like me to upload it to streamable? (y/n)")
                msg = await self.bot.wait_for_message(author=message.author, check=lambda m: m.content.lower() == 'y', timeout=30.0)
                if msg:
                    async with aiohttp.get("https://api.streamable.com/import?url={}".format(s_url)) as r:
                        reply = await r.json()
                    print(reply)
                    d = await self.bot.send_message(message.channel, "<https://streamable.com/{}>".format(reply['shortcode']))
                    embed = False
                    tries = 0
                    while not embed:
                        async with aiohttp.get("https://api.streamable.com/videos/{}".format(reply['shortcode'])) as r:
                            ree = await r.json()
                        if ree['status'] == 2:
                            embed = True
                        elif tries == 10:
                            break
                        tries += 1
                        await asyncio.sleep(5)
                    #await self.bot.delete_message(msg)
                    await self.bot.edit_message(d, "https://streamable.com/{}".format(reply['shortcode']))

    async def on_message_delete(self, message):
        if message is None:
            return
        if message.channel.is_private:
            return
        if message.author.bot:
            await self.bot.send_message(discord.Object(id="213720502219440128"), ":x: <@106429844627169280> My message: ```{0}``` in <#{1}> was deleted".format(message.clean_content, message.channel.id))
            return
        if message.content == "":
            return
        if message.clean_content[0] in ["!", "§", "++", "?"]:
            return
        
        poststring = ":x: `{1}` **{0}** Deleted their message:  ```{2}``` in `{3}`".format(clean_string(message.author.display_name), time.strftime("%H:%M:%S"), message.clean_content, message.channel)
        if message.attachments:
            poststring += "\n{}".format(message.attachments[0]['url'])

        log_channel = self.c.execute('SELECT log_channel FROM servers WHERE id=?', (message.server.id,))
        log_channel = log_channel.fetchall()
        if log_channel == [] or log_channel[0][0] is None:
            log_channel = discord.utils.get(message.server.channels, name='log')
            if log_channel is None:
                return
        else:
            log_channel = discord.Object(id=log_channel[0][0])
        predicate = self.c.execute('SELECT * FROM logging WHERE server=?', (message.server.id,))
        predicate = self.c.fetchone()
        ignore_predicate = predicate[8].split(',') if predicate[8] is not None else []
        if message.channel.id in ignore_predicate:
            print("Ignored channel message delete")
            return
        if predicate[2]:
            print("message deletion is enabled so I announce it")
            await self.bot.send_message(log_channel, poststring)
        else:
            print("message deletion isn't enabled, not broadcasting")
        

        
    async def on_message_edit(self, before, after):
        if before.channel.is_private:
            return
        if before.clean_content == after.clean_content:
            return
        if before.author.id == self.bot.user.id:
            return

        log_channel = self.c.execute('SELECT log_channel FROM servers WHERE id=?', (before.server.id,))
        log_channel = log_channel.fetchall()
        if log_channel == [] or log_channel[0][0] is None:
            log_channel = discord.utils.get(before.server.channels, name='log')
            if log_channel is None:
                return
        else:
            log_channel = discord.Object(id=log_channel[0][0])
        fmt = ":pencil2: `{}` **{}** edited their message:\n**Before:** {}\n**+After:** {}"
        predicate = self.c.execute('SELECT * FROM logging WHERE server=?', (before.server.id,))
        predicate = self.c.fetchone()
        ignore_predicate = predicate[8].split(',') if predicate[8] is not None else []
        if before.channel.id in ignore_predicate:
            print("Ignored channel")
            return
        if predicate is None:
            predicate = False
        if predicate[1]:
            print("message edits is enabled so I announce it")
            await self.bot.send_message(log_channel, fmt.format(time.strftime("%H:%M:%S"), before.author.name, before.clean_content, after.clean_content))
        else:
            print("message edits isn't enabled, not broadcasting")
        


def setup(bot):
    bot.add_cog(Automod(bot))
