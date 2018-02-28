import discord
import json
import shlex

from discord.ext import commands


def to_keycap(c):
    return '\N{KEYCAP TEN}' if c == 10 else str(c) + '\u20e3'


class Polls:
    """Poll voting system."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(no_pm=True)
    async def quickpoll(self, ctx, *, questions_and_choices: str):
        """
        delimit questions and answers by either | or , 
        supports up to 10 choices
        """
        if "|" in questions_and_choices:
            delimiter = "|"
        elif "," in questions_and_choices:
            delimiter = ","
        else:
            delimiter = None
        if delimiter is not None:
            questions_and_choices = questions_and_choices.split(delimiter)
        else:
            questions_and_choices = shlex.split(questions_and_choices)

        if len(questions_and_choices) < 3:
            return await ctx.send('Need at least 1 question with 2 choices.')
        elif len(questions_and_choices) > 11:
            return await ctx.send('You can only have up to 10 choices.')

        perms = ctx.channel.permissions_for(ctx.guild.me)
        if not (perms.read_message_history or perms.add_reactions):
            return await ctx.send('Need Read Message History and Add Reactions permissions.')

        question = questions_and_choices[0]
        choices = [(to_keycap(e), v)
                   for e, v in enumerate(questions_and_choices[1:], 1)]

        try:
            await ctx.message.delete()
        except:
            pass

        fmt = '{0} asks: {1}\n\n{2}'
        answer = '\n'.join('%s: %s' % t for t in choices)
        poll = await ctx.send(fmt.format(ctx.message.author, question.replace("@", "@\u200b"), answer.replace("@", "@\u200b")))
        for emoji, _ in choices:
            await poll.add_reaction(emoji)

    @commands.command(no_pm=True)
    async def poll(self, ctx, *, question: str):
        """
        Quick and easy yes/no poll, for multiple answers, see !quickpoll
        """
        msg = await ctx.send("**{}** asks: {}".format(ctx.message.author, question.replace("@", "@\u200b")))
        try:
            await ctx.message.delete()
        except:
            pass
        if ctx.guild.id == 207943928018632705:
            # Essential :sexthumb:
            yes_thumb = discord.utils.get(
                ctx.guild.emojis, id=287711899943043072)
            no_thumb = discord.utils.get(
                ctx.guild.emojis, id=291798048009486336)
        else:
            yes_thumb = "👍"
            no_thumb = "👎"
        await msg.add_reaction(yes_thumb)
        await msg.add_reaction(no_thumb)

    @commands.command()
    async def strawpoll(self, ctx, *, question_and_choices: str=None):
        """
        Usage: !strawpoll my question | answer a | answer b | answer c\nAt least two answers required.
        """
        if question_and_choices is None:
            return await ctx.send("Usage: !strawpoll my question | answer a | answer b | answer c\nAt least two answers required.")
        if "|" in question_and_choices:
            delimiter = "|"
        else:
            delimiter = ","
        question_and_choices = question_and_choices.split(delimiter)
        if len(question_and_choices) == 1:
            return await ctx.send("Not enough choices supplied")
        elif len(question_and_choices) >= 31:
            return await ctx.send("Too many choices")
        question, *choices = question_and_choices
        choices = [x.lstrip() for x in choices]
        print(choices)
        header = {"Content-Type": "application/json"}
        payload = {
            "title": question,
            "options": choices,
            "multi": False
        }
        print(payload)
        async with self.bot.session.post("https://www.strawpoll.me/api/v2/polls", headers=header, json=payload) as r:
            data = await r.json()
        print(data)
        id = data["id"]
        await ctx.send(f"http://www.strawpoll.me/{id}")


def setup(bot):
    bot.add_cog(Polls(bot))
