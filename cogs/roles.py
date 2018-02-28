import datetime
import re
import statistics
import random
import sqlite3
import markovify
import string
import discord
import aiohttp
import asyncio

from io import BytesIO
from discord.ext import commands
from cogs.utils import checks
from fuzzywuzzy import process
from TagScriptEngine import Engine
from collections import Counter

connection = sqlite3.connect('database.db')
cursor = connection.cursor()
class GoodRoles(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            return await commands.RoleConverter().convert(ctx, argument)
        except commands.BadArgument:
            role_to_return = discord.utils.find(lambda x: x.name.lower() == argument.lower(), ctx.guild.roles)
            if role_to_return is not None:
                return role_to_return     
            # This might be a bad idea, don't care
            name, ratio = process.extractOne(argument, [x.name for x in ctx.guild.roles])
            if ratio >= 75:
                role_to_return = discord.utils.get(ctx.guild.roles, name=name)
                return role_to_return

class BetterRoles(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            return await commands.RoleConverter().convert(ctx, argument)
        except commands.BadArgument:
            role_to_return = discord.utils.find(lambda x: x.name.lower() == argument.lower(), ctx.guild.roles)
            if role_to_return is not None:
                return role_to_return
            cursor.execute('''SELECT * FROM role_alias WHERE guild_id=?''', (ctx.guild.id,))
            aliases = cursor.fetchall()
            roles_and_aliases = {}
            if aliases:
                for entry in aliases:
                    roles_and_aliases[entry[3]] = int(entry[1])
            for r in ctx.guild.roles:
                roles_and_aliases[r.name] = r.id        
            # This might be a bad idea, don't care
            name, ratio = process.extractOne(argument, [x for x in roles_and_aliases])
            if ratio >= 75:
                role_to_return = discord.utils.get(ctx.guild.roles, id=roles_and_aliases[name])
                return role_to_return

class Roles:
    
    def __init__(self, bot):
        self.bot = bot
        self.engine = Engine()
        self.conn = sqlite3.connect('database.db')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS role_config
                         (whitelisted text, unique_roles boolean, guild_id text, autoroles text)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS role_alias
                         (guild_id text, role_id text, role_name text, alias text, UNIQUE (guild_id, alias))''')

        # self.c.execute('''ALTER TABLE role_config
        #                   ADD COLUMN reassign BOOL DEFAULT 1''')
        # self.conn.commit()

    @commands.group(invoke_without_command=True)
    @checks.admin_or_permissions(manage_server=True)
    async def modrole(self, ctx, *, role: BetterRoles=None):
        if role is None:
            return await ctx.send("You need to specify a role")
        if role.is_default():
            return await ctx.send("You can't mod everyone (If you for some reason really want to do this, give it to a role and assign it to everyone)")
        self.c.execute('''SELECT mod_roles FROM config WHERE guild_id=?''', (ctx.guild.id,))
        roles_already = self.c.fetchone()[0]

        new_role = role.id


        self.c.execute('''UPDATE config SET mod_roles=? WHERE guild_id=?''', (new_role, ctx.guild.id))
        self.conn.commit()
        self.bot.modroles[str(ctx.guild.id)] = new_role
        if roles_already is None:
            return await ctx.send(f"Users with the role **{role.name}** are now seen as moderators by the bot")
        await ctx.send(f"Moderator role changed to **{role.name}**")
    
    @modrole.command(name="clear")
    @checks.admin_or_permissions(manage_server=True)
    async def _clear(self, ctx):
        self.c.execute('''UPDATE config SET mod_roles=? WHERE guild_id=?''', (None, ctx.guild.id))
        self.conn.commit()
        self.bot.modroles[str(ctx.guild.id)] = None
        await ctx.send("Mod role cleared")

    @commands.command()
    @checks.admin_or_permissions(manage_server=True)
    async def amimod(self, ctx):
        await ctx.send("Yes, you're a mod as far as I can tell.")



    @commands.group(name="role", invoke_without_command=True)
    async def _role(self, ctx, *, role: BetterRoles=None):
        """
        This tries to make adding roles as safe as possible
        for a role to be able to added from this command
        it needs to be whitelisted by a moderator. This
        moderator needs to have the required permissions
        to add the role in order for the role to be added
        """
        if role is None:
            return await ctx.send("You need to specify a role")
        # First we check if the role is whitelisted or not
        self.c.execute('''SELECT whitelisted
                          FROM role_config
                          WHERE guild_id=?''',
                        (ctx.guild.id,))
        whitelisted = self.c.fetchone()[0]
        if whitelisted is None:
            return await ctx.send("No roles are whitelisted in this server yet")
        # whitelisted is just a string of numbers
        # we can check if the role id is in this string
        # quite easily
        if not str(role.id) in whitelisted:
            return await ctx.send("That role is not whitelisted")

        # Does the user want the role added or removed?
        add_or_remove = role not in ctx.author.roles
        # Now we need to check if the server has unique roles enabled
        self.c.execute('''SELECT unique_roles
                          FROM role_config
                          WHERE guild_id=?''',
                       (ctx.guild.id,))
        unique_roles = self.c.fetchone()[0]
        if unique_roles:
            # We need to remove one role and add another
            # could technically replace roles but doing it
            # in two takes is so much easier
            whitelisted = whitelisted.split(',')
            to_be_removed = [x for x in ctx.author.roles if str(x.id) in whitelisted]
            if len(to_be_removed) == 1:
                if to_be_removed[0] == role:
                    await ctx.send(f"Removed **{role.name}** from {ctx.author.name}")
                    return await ctx.author.remove_roles(to_be_removed[0])
                await ctx.author.remove_roles(to_be_removed[0])
            else:
                await ctx.author.remove_roles(*to_be_removed)
            await asyncio.sleep(0.05)
            await ctx.author.add_roles(role)
            return await ctx.send(f"Added **{role.name}** to {ctx.author.name}")

        # Not unique means we add/remove the role without any logic

        if add_or_remove:
            await ctx.author.add_roles(role)
            await ctx.send(f"Added **{role.name}** to {ctx.author.name}")
        else:
            await ctx.author.remove_roles(role)
            await ctx.send(f"Removed **{role.name}** from {ctx.author.name}")
        



    @_role.command(aliases=['add','+', '-', 'del', 'wl', 'remove', 'delete'])
    async def whitelist(self, ctx, *, role: BetterRoles=None):
        if role is None:
            return await ctx.send("You need to specify a role to be whitelisted")
        elif role.is_default():
            return await ctx.send("You can't whitelist that.")
        perms = ctx.author.guild_permissions

        if not perms.manage_roles:
            return await ctx.send('You need "manage roles" to whitelist')
        
        top_role = ctx.author.top_role
        if top_role.position < role.position and ctx.author != ctx.guild.owner:
            return await ctx.send("You don't have the permissions required to do that.")
        elif ctx.guild.me.top_role.position < role.position:
            return await ctx.send("I don't have the permissions required to add that role")

        self.c.execute('''SELECT whitelisted FROM role_config WHERE guild_id=?''', (ctx.guild.id,))
        whitelisted_roles = self.c.fetchone()[0]
        if whitelisted_roles is None:
            # If the guild doesn't have any whitelisted roles
            # adding the first one is simple enough
            self.c.execute('''UPDATE role_config
                              SET whitelisted=? 
                              WHERE guild_id=?''',
                              (role.id, ctx.guild.id))
            self.conn.commit()
            return await ctx.send(f"Role **{role.name}** added to the whitelist")
        whitelisted_roles = whitelisted_roles.split(',')
        if not str(role.id) in whitelisted_roles:
            # Add the role
            whitelisted_roles.append(str(role.id))
            whitelisted_roles = ','.join(whitelisted_roles)
            self.c.execute('''UPDATE role_config
                              SET whitelisted=? 
                              WHERE guild_id=?''',
                              (whitelisted_roles, ctx.guild.id))
            self.conn.commit()
            return await ctx.send(f"Role **{role.name}** added to the whitelist")
        whitelisted_roles.remove(str(role.id))
        if not whitelisted_roles:
            # Inserting empty strings into sql seems to be 
            # begging for trouble, if the list of roles is
            # empty, we simply null the cell
            self.c.execute('''UPDATE role_config
                              SET whitelisted=? 
                              WHERE guild_id=?''',
                              (None, ctx.guild.id))
            self.conn.commit()
            return await ctx.send(f"Role **{role.name}** removed from the whitelist")
        whitelisted_roles = ','.join(whitelisted_roles)
        self.c.execute('''UPDATE role_config
                          SET whitelisted=? 
                          WHERE guild_id=?''',
                       (whitelisted_roles, ctx.guild.id))
        self.conn.commit()
        return await ctx.send(f"Role **{role.name}** removed from the whitelist")

        
    @_role.command(name="alias")
    async def _alias(self, ctx, alias: str=None, *, role: GoodRoles=None):
        if alias is None:
            return await ctx.send("Usage: `!role alias new_role_name existing_role`\nIf you want to create a two-word alias you need to use quotes, like `!role alias \"demon hunter\" dh`")
        perms = ctx.author.guild_permissions
        if "@everyone" in ctx.message.content or "@here" in ctx.message.content:
            return await ctx.send("Fuck off.")
        if not perms.manage_roles:
            return await ctx.send('You need "manage roles" to alias')
        if role is None:
            role = await BetterRoles().convert(ctx, alias)
            if role is None:
                return await ctx.send("That doesn't seem to be aliased, did you forget to specify a role?")
        
        top_role = ctx.author.top_role
        if top_role.position < role.position and ctx.author != ctx.guild.owner:
            return await ctx.send("You don't have the permissions required to do that.")
        elif ctx.guild.me.top_role.position < role.position:
            return await ctx.send("I don't have the permissions required to add that role")
        

        self.c.execute('''SELECT * FROM role_alias WHERE (guild_id=? AND alias=?)''', (ctx.guild.id, alias))
        maybeexists = self.c.fetchone()
        if maybeexists is None:            
            self.c.execute('''INSERT OR IGNORE INTO role_alias
                            VALUES (?, ?, ?, ?)''',
                        (ctx.guild.id, role.id, role.name, alias))
            self.conn.commit()
            return await ctx.send(f"Role alias **{alias}** pointing to **{role.name}** added.")
        self.c.execute('DELETE FROM role_alias WHERE (guild_id=? AND alias=?)',
                (ctx.guild.id, alias))
        self.conn.commit()
        await ctx.send(f'Removed role alias "{alias}"')

    @_role.command()
    @checks.admin_or_permissions(manage_server=True)
    async def unique(self, ctx):
        """
        This is for servers like r/wow that only allows one role from the
        whitelist at any given time, it probably has real uses but this is
        realistically just for that
        """
        self.c.execute('''SELECT unique_roles
                          FROM role_config
                          WHERE guild_id=?''',
                        (ctx.guild.id,))
        unique = self.c.fetchone()[0]

        if unique is None:
            # peculiar
            unique = False
        unique = not unique
        self.c.execute('''UPDATE role_config
                          SET unique_roles=? 
                          WHERE guild_id=?''',
                       (unique, ctx.guild.id))
        self.conn.commit()
        await ctx.send(f"Set unique roles to {unique}")
        
    @commands.command()
    async def roles(self, ctx):
        self.c.execute('''SELECT whitelisted FROM role_config WHERE guild_id=?''', (ctx.guild.id,))
        whitelisted_roles = self.c.fetchone()[0]
        
        if whitelisted_roles is None:
            whitelisted_roles = "This server has no whitelisted roles"
        else:
            guild_roles = [x for x in ctx.guild.roles if str(x.id) in whitelisted_roles.split(',')]
            whitelisted_roles = '\n'.join([f"**{len(x.members)}** <@&{x.id}>" for x in guild_roles])

        em = discord.Embed(title="Whitelisted roles", description=whitelisted_roles)
        await ctx.send(embed=em)

    @commands.group(aliases=['autoroles'], invoke_without_command=True)
    async def autorole(self, ctx):
        self.c.execute('''SELECT autoroles, reassign
                          FROM role_config
                          WHERE guild_id=?''',
                          (ctx.guild.id,))
        autoroles = self.c.fetchone()
        if autoroles is None or (autoroles[0] is None and autoroles[1] is None):
            return await ctx.send("This server doesn't assign any roles upon joining.")
        autoroles, reassign = autoroles
        try:
            list_of_auto = '\n'.join([f"<@&{x}>" for x in autoroles.split(',')])
        except AttributeError:
            list_of_auto = "None"

        e = discord.Embed(title="Automatically assigned roles", description=list_of_auto)
        if reassign is not None and reassign:
            reassign = "<:greentick:318044721807360010>\n"
        else:
            reassign = "<:redtick:318044813444251649>"
        e.add_field(name="Re-assigns roles?", value=reassign)
        await ctx.send(embed=e)
    
    @autorole.command(aliases=['readd', 'remember', 'persistent'])
    @checks.admin_or_permissions(manage_server=True)
    async def reassign(self, ctx):
        self.c.execute('''SELECT reassign
                          FROM role_config
                          WHERE guild_id=?''',
                          (ctx.guild.id,))
        reassigns = self.c.fetchone()[0]
        self.c.execute('''UPDATE role_config
                              SET reassign=?
                              WHERE guild_id=?''',
                              (not reassigns, ctx.guild.id))
        self.conn.commit()
        if reassigns:
            return await ctx.send("Roles will no longer be readded on joining")
        await ctx.send("Roles will now be readded on joining")
            
        
    
    @autorole.command()
    async def add(self, ctx, role: BetterRoles=None):
        if role is None: 
            return await ctx.send("You need to specify a role to be added.")
        elif role.is_default():
            return await ctx.send("You can't assign that.")
        perms = ctx.author.guild_permissions

        if not perms.manage_roles:
            return await ctx.send('You need "manage roles" for this')
        
        top_role = ctx.author.top_role
        if top_role.position < role.position and ctx.author != ctx.guild.owner:
            return await ctx.send("You don't have the permissions required to do that.")
        elif ctx.guild.me.top_role.position < role.position:
            return await ctx.send("I don't have the permissions required to add that role")
        self.c.execute('''SELECT autoroles FROM role_config WHERE guild_id=?''', (ctx.guild.id,))
        automatic_roles = self.c.fetchone()[0]
        if automatic_roles is None:
            # If the guild doesn't have any whitelisted roles
            # adding the first one is simple enough
            self.c.execute('''UPDATE role_config
                              SET autoroles=? 
                              WHERE guild_id=?''',
                              (role.id, ctx.guild.id))
            self.conn.commit()
            return await ctx.send(f'The role \"**{role.name}**\" will now be auto-assigned')
        automatic_roles = automatic_roles.split(',')
        if not str(role.id) in automatic_roles:
            # Add the role
            automatic_roles.append(str(role.id))
            automatic_roles = ','.join(automatic_roles)
            self.c.execute('''UPDATE role_config
                              SET autoroles=? 
                              WHERE guild_id=?''',
                              (automatic_roles, ctx.guild.id))
            self.conn.commit()
            return await ctx.send(f'The role \"**{role.name}**\" will now be auto-assigned')
        else:
            return await ctx.send("That role is already automatically assigned, use `!autorole remove` to remove the role.")

    @autorole.command()
    async def remove(self, ctx, role: BetterRoles=None):
        if role is None: 
            return await ctx.send("You need to specify a role to be removed.")
        elif role.is_default():
            return await ctx.send("You can't remove that.")
        perms = ctx.author.guild_permissions

        if not perms.manage_roles:
            return await ctx.send('You need "manage roles" to do that')
        
        top_role = ctx.author.top_role
        if top_role.position < role.position and ctx.author != ctx.guild.owner:
            return await ctx.send("You don't have the permissions required to do that.")
        elif ctx.guild.me.top_role.position < role.position:
            return await ctx.send("I don't have the permissions required to do that")
        self.c.execute('''SELECT autoroles FROM role_config WHERE guild_id=?''', (ctx.guild.id,))
        automatic_roles = self.c.fetchone()[0]
        automatic_roles = automatic_roles.split(',')
        try:
            automatic_roles.remove(str(role.id))
        except ValueError:
            return await ctx.send("That role isn't auto-assigned")
        if not automatic_roles:
            # Inserting empty strings into sql seems to be 
            # begging for trouble, if the list of roles is
            # empty, we simply null the cell
            self.c.execute('''UPDATE role_config
                              SET autoroles=? 
                              WHERE guild_id=?''',
                              (None, ctx.guild.id))
            self.conn.commit()
            return await ctx.send(f'The role \"**{role.name}**\" will no longer be auto-assigned')
        automatic_roles = ','.join(automatic_roles)
        self.c.execute('''UPDATE role_config
                          SET autoroles=? 
                          WHERE guild_id=?''',
                       (automatic_roles, ctx.guild.id))
        self.conn.commit()
        return await ctx.send(f'The role \"**{role.name}**\" will no longer be auto-assigned')




    async def on_member_join(self, member):
        # a = self.c.execute('SELECT autoroles FROM role_config WHERE guild_id=?', (member.guild.id,))
        # checkthis = self.c.fetchone()
        # can_edit = member.guild.me.guild_permissions.manage_roles
        # if checkthis is not None and can_edit:
        #     allRoles = member.guild.roles
        #     checkthis = checkthis[0]
        #     if checkthis is None:
        #         return
        #     checkthis = checkthis.split(',')
        #     # if even one role can't be added, none will be
        #     # because of this, I check the role hierarchy
        #     rolestobeadded = [x for x in allRoles if (
        #         str(x.id) in checkthis and x < member.guild.me.top_role)]
        #     await member.add_roles(*rolestobeadded)

        self.c.execute('''SELECT greet_channel, greet_message
                          FROM greetings
                          WHERE guild_id=?''',
                          (member.guild.id,))

        try:
            ch, msg = self.c.fetchone()
        except:
            return
        if ch is None or msg is None:
            return
        self.engine.Add_Variable("mention", f"<@{member.id}>")
        self.engine.Add_Variable("user", member.name)
        self.engine.Add_Variable("server", member.guild.name)
        self.engine.Add_Variable("id", str(member.id))
        self.engine.Add_Variable("nick", member.display_name)
        self.engine.Add_Variable("discrim", member.discriminator)
        msg = self.engine.Process(msg)
        self.engine.Clear_Variables()
        channel = self.bot.get_channel(int(ch))
        await channel.send(msg)

    async def on_member_remove(self, member):
        self.c.execute('''SELECT greet_channel, farewell_message
                          FROM greetings
                          WHERE guild_id=?''',
                          (member.guild.id,))

        try:
            ch, msg = self.c.fetchone()
        except:
            return
        if ch is None or msg is None:
            return
        self.engine.Add_Variable("mention", f"<@{member.id}>")
        self.engine.Add_Variable("user", member.name)
        self.engine.Add_Variable("server", member.guild.name)
        self.engine.Add_Variable("id", str(member.id))
        self.engine.Add_Variable("nick", member.display_name)
        self.engine.Add_Variable("discrim", member.discriminator)
        msg = self.engine.Process(msg)
        self.engine.Clear_Variables()
        channel = self.bot.get_channel(int(ch))
        await channel.send(msg)

    async def on_member_ban(self, guild, user):
        self.c.execute('''SELECT greet_channel, ban_message
                          FROM greetings
                          WHERE guild_id=?''',
                          (guild.id,))

        try:
            ch, msg = self.c.fetchone()
        except:
            return
        if ch is None or msg is None:
            return
        self.engine.Add_Variable("mention", f"<@{user.id}>")
        self.engine.Add_Variable("user", user.name)        
        self.engine.Add_Variable("server", guild.name)
        self.engine.Add_Variable("id", str(user.id))
        self.engine.Add_Variable("discrim", user.discriminator)
        msg = self.engine.Process(msg)
        self.engine.Clear_Variables()
        channel = self.bot.get_channel(int(ch))
        await channel.send(msg)
def setup(bot):
    bot.add_cog(Roles(bot))