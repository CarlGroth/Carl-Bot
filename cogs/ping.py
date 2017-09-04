import discord
import random
import json
import re

from discord.ext import commands
from cogs.utils import checks

listofbirds = ["https://i.imgur.com/18cOdIx.png"]


def load_json(filename):
    with open(filename, encoding='utf-8') as infile:
        return json.load(infile)

def write_json(filename, contents):
    with open(filename, 'w') as outfile:
        json.dump(contents, outfile, indent=2)


def clean_string(string):
    string = re.sub('@', '@\u200b', string)
    string = re.sub('#', '#\u200b', string)
    return string


class RollParser(commands.Converter):
    async def convert(self, ctx, argument):
        matches = re.search(r"(?:(\d*)-)?(\d*)", argument)
        print(f"Matches= {matches}")
        minshit = matches.group(1) or 0
        maxshit = matches.group(2) or 100
        return (int(minshit), int(maxshit))
        
        


class Ping:
    #Not sure why this got its own cog :thinking:
    def __init__(self, bot):
        self.bot = bot
        self.dogs = load_json('dogs.json')
        self.cats = load_json('cats.json')
        self.cute = load_json('cute.json')




    @commands.command()
    async def roll(self, ctx, *, results: RollParser=None):
        # works like the wow version [lower-]upper
        results = results if results is not None else (0, 100)
        roll = random.randint(results[0], results[1])
        await ctx.send(f"{ctx.author.name} rolls {roll} ({results[0]}-{results[1]})")

    @commands.command()
    async def ping(self, ctx):
        ms = self.bot.latency * 1000
        await ctx.send(f"pong! {ms:.2f}ms")

    @commands.command(pass_context=True)
    async def bread(self, ctx, member : discord.Member = None):
        user = ctx.message.author if member is None else member
        await user.send(random.choice(listofbirds))

    @commands.command(pass_context=True)
    async def echo(self, ctx, destination : discord.TextChannel = None, *, msg : str):
        # This wasn't always a thing lmao
        if not destination.permissions_for(ctx.author).send_messages:
            return
        msg = clean_string(msg)
        destination = ctx.message.channel if destination is None else destination
        await destination.send(msg)

    
    async def get_cute(self):
        key = random.choice(list(self.cute.keys()))
        response = random.choice(self.cute[key])
        return response

    async def get_dog(self):       
        key = random.choice(list(self.dogs.keys()))
        response = random.choice(self.dogs[key])
        return response

    async def get_cat(self):
        key = random.choice(list(self.cats.keys()))
        response = random.choice(self.cats[key])
        return response
    @commands.command(name="aww")
    async def cmd_aww(self, ctx):
        response = await self.get_cute()
        await ctx.send(response)
    @commands.command(name="awwbomb")
    async def cmd_awwbomb(self, ctx):
        response = ""
        for i in range(10):
            try:
                response += "{}\n".format(await self.get_cute())
            except Exception as e:
                print("{}: {}".format(type(e).__name__, e))
                
        await ctx.send(response)

    @commands.command(name="dog")
    async def cmd_dog(self, ctx):
        response = await self.get_dog()
        await ctx.send(response)
    
    @commands.command(name="dogbomb")
    async def cmd_dogbomb(self, ctx):
        response = ""
        for i in range(10):
            try:
                response += "{}\n".format(await self.get_dog())
            except Exception as e:
                print("{}: {}".format(type(e).__name__, e))
                
        await ctx.send(response)

    @commands.command(name="catbomb")
    async def cmd_catbomb(self, ctx):
        response = ""
        for i in range(10):
            try:
                response += "{}\n".format(await self.get_cat())
            except Exception as e:
                print("{}: {}".format(type(e).__name__, e))
                
        await ctx.send(response)
    
    @commands.command(name="cat")
    async def cmd_cat(self, ctx):
        response = await self.get_cat()      
        await ctx.send(response)




def setup(bot):
    bot.add_cog(Ping(bot))
