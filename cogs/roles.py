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


class BetterRoles(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            return await commands.RoleConverter().convert(ctx, argument)
        except commands.BadArgument:
            role_to_return = discord.utils.find(lambda x: x.name.lower() == argument, ctx.guild.roles)
            return role_to_return


class Roles:
    
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('database.db')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS role_config
                         (whitelisted text, unique_roles boolean, guild_id text)''')

    @commands.group(name="role", aliases=['class'], invoke_without_command=True)
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
        # whitelisted is just a string of numbers
        # we can check if the role id is in this string
        # quite easily
        if not str(role.id) in whitelisted:
            return await ctx.send("That role is not whitelisted")

        # Does the user want the role added or removed?
        add_or_remove = role not in ctx.author.roles
        print(f"add or remove= {add_or_remove}")
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
            print(to_be_removed)
            if len(to_be_removed) == 1:                
                await ctx.author.remove_roles(to_be_removed[0])
                print("removed (1)")
            else:
                await ctx.author.remove_roles(*to_be_removed)
                print("removed (+)")
            await asyncio.sleep(0.05)
            await ctx.author.add_roles(role)
            return await ctx.send(f"Added {role.name} (replaced)")

        # Not unique means we add/remove the role without any logic

        if add_or_remove:
            await ctx.author.add_roles(role)
            await ctx.send(f"Added {role.name}")
        else:
            await ctx.author.remove_roles(role)
            await ctx.send(f"Removed {role.name}")
        



    @_role.command(aliases=['add','+', '-', 'del', 'remove', 'delete'])
    async def whitelist(self, ctx, *, role: BetterRoles=None):
        if role is None:
            return await ctx.send("You need to specify a role to be whitelisted")
        elif role.is_default():
            return await ctx.send("You can't whitelist that.")
        perms = ctx.author.guild_permissions

        if not perms.manage_roles:
            return await ctx.send('You need "manage roles" to whitelist')
        
        top_role = ctx.author.top_role
        if top_role.position < role.position:
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
            whitelisted_roles = '\n'.join([f"<@&{x}>" for x in whitelisted_roles.split(',')])

        em = discord.Embed(title="Whitelisted roles", description=whitelisted_roles)
        await ctx.send(embed=em)




def setup(bot):
    bot.add_cog(Roles(bot))