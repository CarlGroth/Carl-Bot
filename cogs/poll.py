import discord

from discord.ext import commands

def to_keycap(c):
    return '\N{KEYCAP TEN}' if c == 10 else str(c) + '\u20e3'

class Polls:
    """Poll voting system."""

    def __init__(self, bot):
        self.bot = bot


    @commands.command(no_pm=True)
    async def quickpoll(self, ctx, *questions_and_choices: str):

        if len(questions_and_choices) < 3:
            return await ctx.send('Need at least 1 question with 2 choices.')
        elif len(questions_and_choices) > 11:
            return await ctx.send('You can only have up to 10 choices.')

        perms = ctx.channel.permissions_for(ctx.guild.me)
        if not (perms.read_message_history or perms.add_reactions):
            return await ctx.send('Need Read Message History and Add Reactions permissions.')

        question = questions_and_choices[0]
        choices = [(to_keycap(e), v) for e, v in enumerate(questions_and_choices[1:], 1)]

        try:
            await ctx.message.delete()
        except:
            pass

        fmt = '{0} asks: {1}\n\n{2}'
        answer = '\n'.join('%s: %s' % t for t in choices)
        poll = await ctx.send(fmt.format(ctx.message.author, question.replace("@", "@\u200b"), answer))
        for emoji, _ in choices:
            await poll.add_reaction(emoji)

    @commands.command(pass_context=True, no_pm=True)
    async def poll(self, ctx, *questions_and_choices : str):
        msg = await ctx.send("**{}#{}** asks: {}".format(ctx.message.author.name, ctx.message.author.discriminator, ctx.message.clean_content[5:]))
        await ctx.message.delete()
        if ctx.guild.id == 207943928018632705:
            # Essential :sexthumb:
            yes_thumb = discord.utils.get(ctx.guild.emojis, id=287711899943043072)
            no_thumb = discord.utils.get(ctx.guild.emojis, id=291798048009486336)
        else:
            yes_thumb = "👍"
            no_thumb = "👎"
        await msg.add_reaction(yes_thumb)
        await msg.add_reaction(no_thumb)

def setup(bot):
    bot.add_cog(Polls(bot))
    
