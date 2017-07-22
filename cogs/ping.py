import discord
import random
import re

from discord.ext import commands
from cogs.utils import checks

listofbirds = ["https://i.imgur.com/18cOdIx.png"]

def clean_string(string):
    string = re.sub('@', '@\u200b', string)
    string = re.sub('#', '#\u200b', string)
    return string

class Ping:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping", hidden=True, pass_context=True)
    async def ping(self, ctx):
        msg = await self.bot.say("pong!")
        q_time = ctx.message.timestamp
        m_time = msg.timestamp
        diff_time = m_time - q_time
        d_time = diff_time.microseconds / 1000
        await self.bot.edit_message(msg, "pong! {}ms".format(int(d_time)))

    @commands.command(pass_context=True)
    async def bread(self, ctx, member : discord.Member = None):
        user = ctx.message.author if member is None else member
        await self.bot.send_message(user, random.choice(listofbirds))

    @commands.command(pass_context=True)
    async def echo(self, ctx, destination : discord.Channel = None, *, msg : str):
        msg = clean_string(msg)
        destination = ctx.message.channel if destination is None else destination
        await self.bot.send_message(destination, msg)



def setup(bot):
    bot.add_cog(Ping(bot))
