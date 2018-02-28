import random
import json
import re
import discord

from discord.ext import commands

LISTOFBIRDS = ["https://i.imgur.com/18cOdIx.png"]


def load_json(filename):
    """
    Loads a json file, wow
    """
    with open(filename, encoding='utf-8') as infile:
        return json.load(infile)


def write_json(filename, contents):
    """
    Updates a json file, wow
    """
    with open(filename, 'w') as outfile:
        json.dump(contents, outfile, ensure_ascii=True, indent=4)


def clean_string(string):
    """
    Because discord is annoying
    and @everyone pings are
    even worse
    """
    string = re.sub('@', '@\u200b', string)
    string = re.sub('#', '#\u200b', string)
    return string


class RollParser(commands.Converter):
    """
    This makes parsing the roll thing into a function
    annotation
    """
    async def convert(self, ctx, argument):
        matches = re.search(r"(?:(\d*)-)?(\d*)", argument)
        minshit = matches.group(1) or 1
        maxshit = matches.group(2) or 100
        return (int(minshit), int(maxshit))


class Ping:
    """
    This used to be a ping cog
    now it has animals too
    """

    def __init__(self, bot):
        self.bot = bot
        self.dogs = load_json('dogs.json')
        self.cats = load_json('cats.json')
        self.cute = load_json('cute.json')

    @commands.command()
    async def roll(self, ctx, *, results: RollParser = None):
        """
        Works like the wow version !roll [[lower-]upper]
        """
        results = results if results is not None else (1, 100)
        roll = random.randint(results[0], results[1])
        await ctx.send(f"**{ctx.author.name}** rolls **{roll}** ({results[0]}-{results[1]})")

    @commands.command()
    async def ping(self, ctx):
        """
        used to check if the bot is alive
        """
        await ctx.send("pong! {0:.2f}ms".format(self.bot.latency * 1000))

    # @commands.command()
    # async def bread(self, ctx, member: discord.Member=None):
    #     """
    #     Sends bread to the mentioned user
    #     god I fucking hate this command
    #     """
    #     if ctx.guild.id != 207943928018632705:
    #         return

    #     user = ctx.message.author if member is None else member
    #     await user.send(random.choice(LISTOFBIRDS))

    @commands.command()
    async def echo(self, ctx, destination: discord.TextChannel=None, *, msg: str):
        """
        Makes the bot say something in the specified channel
        """
        # This wasn't always a thing lmao
        if not destination.permissions_for(ctx.author).send_messages:
            return await ctx.message.add_reaction("\N{WARNING SIGN}")
        msg = clean_string(msg)
        destination = ctx.message.channel if destination is None else destination
        await destination.send(msg)
        return await ctx.message.add_reaction("\N{WHITE HEAVY CHECK MARK}")

    async def get_cute(self):
        """
        gets us a random fluffy thing for our cat-related commands
        """
        key = random.choice(list(self.cute.keys()))
        response = random.choice(self.cute[key])
        return response

    async def get_dog(self):
        """
        gets us a random dog for our cat-related commands
        """
        key = random.choice(list(self.dogs.keys()))
        response = random.choice(self.dogs[key])
        return response

    async def get_cat(self):
        """
        gets us a random cat for our cat-related commands
        """
        key = random.choice(list(self.cats.keys()))
        response = random.choice(self.cats[key])
        return response

    @commands.command(name="aww")
    async def cmd_aww(self, ctx):
        """
        cute bot not necessarily cat or dog related
        """
        response = await self.get_cute()
        await ctx.send(response)

    @commands.command(name="awwbomb")
    async def cmd_awwbomb(self, ctx):
        """
        It's like the other bombs
        but way fluffier
        """
        response = ""
        for _ in range(10):
            try:
                response += "{}\n".format(await self.get_cute())
            except KeyError:
                pass

        await ctx.send(response)

    @commands.command(name="dog")
    async def cmd_dog(self, ctx):
        """
        Gives you a random dog picture
        """
        response = await self.get_dog()
        await ctx.send(response)

    @commands.command(name="dogbomb")
    async def cmd_dogbomb(self, ctx):
        """
        Gives you 10 random dog pictures
        """
        response = ""
        for _ in range(10):
            try:
                response += "{}\n".format(await self.get_dog())
            except KeyError:
                pass

        await ctx.send(response)

    @commands.command(name="catbomb")
    async def cmd_catbomb(self, ctx):
        """
        Gives you 10 random cat pictures
        """
        response = ""
        for _ in range(10):
            try:
                response += "{}\n".format(await self.get_cat())
            except KeyError:
                pass

        await ctx.send(response)

    @commands.command(name="cat")
    async def cmd_cat(self, ctx):
        """
        Gives you a random cat picture
        god I fucking hate bots
        """
        response = await self.get_cat()
        await ctx.send(response)


def setup(bot):
    bot.add_cog(Ping(bot))
