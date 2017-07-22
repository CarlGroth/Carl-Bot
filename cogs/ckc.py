import json
import discord
import asyncio
import inspect
import datetime
import time
import re
import statistics
import aiohttp
import random
import markovify
import sqlite3

from discord.ext import commands
from cogs.utils import config, checks
from numpy.random import choice
from collections import Counter
from collections import defaultdict
from discord.ext.commands.cooldowns import BucketType




def beaufort_scale(speed):
    if speed < 0:
        return "I don't fucking know"
    elif speed <= 0.3:
        return "Calm"
    elif speed <= 1.5:
        return "Light air"
    elif speed <= 3.3:
        return "Light breeze"
    elif speed <= 5.5:
        return "Gentle breeze"
    elif speed <= 7.9:
        return "Moderate breeze"
    elif speed <= 10.7:
        return "Fresh breeze"
    elif speed <= 13.8:
        return "Strong breeze"
    elif speed <= 17.1:
        return "Moderate gale"
    elif speed <= 20.7:
        return "Gale"
    elif speed <= 24.4:
        return "Strong gale"
    elif speed <= 28.4:
        return "Storm"
    elif speed <= 32.6:
        return "Violent storm"
    else:
        return "Hurricane force"

def pretty_weather(weather):
    weather = weather.lower()
    if weather == "light rain":
        return ":cloud_rain: Light rain"
    elif weather == "snow":
        return ":cloud_snow: Snow"
    elif weather == "light intensity drizzle":
        return ":cloud_rain: Light intensity drizzle"
    elif weather == "light snow":
        return ":cloud_snow: Light snow"
    elif weather == "broken clouds":
        return ":white_sun_cloud: Broken clouds"
    elif weather == "clear sky":
        return ":large_blue_circle: Clear sky"
    elif weather == "haze":
        return ":foggy: Haze"
    elif weather == "overcast clouds":
        return ":cloud: Overcast clouds"
    elif weather == "mist":
        return ":fog: Mist"
    elif weather == "few clouds":
        return ":cloud: Few clouds"
    elif weather == "scattered clouds":
        return ":cloud: Scattered clouds"
    elif weather == "moderate rain":
        return ":cloud_rain: Moderate rain"
    elif weather == "shower rain":
        return ":cloud_rain: Shower rain"
    else:
        return weather.capitalize()




smallcaps_alphabet = "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢ1234567890"

alphabet = dict(zip("abcdefghijklmnopqrstuvwxyz1234567890", range(0,36)))
uppercase_alphabet = dict(zip("ABCDEFGHIJKLMNOPQRSTUVWXYZ", range(0, 26)))
punctuation = dict(zip("§½!\"#¤%&/()=?`´@£$€{[]}\\^¨~'*<>|,.-_:", range(0, 37)))
space = " "
aesthetic_space = '\u3000'
aesthetic_punctuation = "§½！\"＃¤％＆／（）＝？`´＠£＄€｛[]｝＼＾¨~＇＊＜＞|，．－＿："
aesthetic_lowercase = "ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ１２３４５６７８９０"
aesthetic_uppercase = "ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ"



def clean_string(string):
    string = re.sub('@', '@\u200b', string)
    string = re.sub('#', '#\u200b', string)
    return string


def aesthetics(string):
    returnthis = ""
    for word in string:
        for letter in word:
            if letter in alphabet:
                returnthis += aesthetic_lowercase[alphabet[letter]]
            elif letter in uppercase_alphabet:
                returnthis += aesthetic_uppercase[uppercase_alphabet[letter]]
            elif letter in punctuation:
                returnthis += aesthetic_punctuation[punctuation[letter]]
            elif letter == space:
                returnthis += aesthetic_space
            else:
                returnthis += letter
    return returnthis

def smallcaps(string):
    returnthis = ""
    for word in string:
        for letter in word:
            if letter in alphabet:
                returnthis += smallcaps_alphabet[alphabet[letter]]
            else:
                returnthis += letter
    return returnthis


eight_ball_responses = [
    "It is certain",
    "It is decidedly so",
    "Without a doubt",
    "Yes, definitely",
    "You may rely on it",
    "As I see it, yes",
    "Most likely",
    "Outlook good",
    "Yes",
    "Signs point to yes",
    "Reply hazy try again",
    "Ask again later",
    "Better not tell you now",
    "Cannot predict now",
    "Concentrate and ask again",
    "Don't count on it",
    "My reply is no",
    "My sources say no",
    "Outlook not so good",
    "Very doubtful"
    ]

no_flight_list = ["https://pbs.twimg.com/media/C-70Iq5XcAAwmgY.jpg",
                  "https://pbs.twimg.com/media/C_EyLx_W0AEPkJ0.jpg:orig",
                  "https://pbs.twimg.com/media/C-_gxHbVoAAiSrV.jpg:orig",
                  "https://pbs.twimg.com/media/C-6a-oeXgAEmEvp.jpg:orig",
                  "https://pbs.twimg.com/media/C-2s0XiWsAAKbSt.jpg:orig",
                  "https://pbs.twimg.com/media/C-0-qYzUAAA0a9I.jpg:orig",
                  "https://pbs.twimg.com/media/C-ycXPNU0AEKrQj.jpg:orig",
                  "https://pbs.twimg.com/media/C-v5iyXXsAA1pRL.jpg:orig",
                  "https://pbs.twimg.com/media/C-tOAc5UQAAS26K.jpg:orig",
                  "https://pbs.twimg.com/media/C-q2Qx5U0AAhJ47.jpg",
                  "https://pbs.twimg.com/media/C-nwdDUVYAAx3vp.jpg:orig",
                  "https://pbs.twimg.com/media/C-l8aprVoAAwEvA.jpg:orig",
                  "https://pbs.twimg.com/media/C-jIDqsU0AAbeQb.jpg:orig",
                  "https://pbs.twimg.com/media/C-gkSfFUAAAjm6o.jpg",
                  "https://pbs.twimg.com/media/C-dn9knUIAAuRm8.jpg:orig",
                  "https://pbs.twimg.com/media/C-cgIqTUMAA79dg.jpg:orig",
                  "https://pbs.twimg.com/media/C-YksDSVYAErfpb.jpg:orig",
                  "https://pbs.twimg.com/media/C-WHBmTVYAEmfsw.jpg:orig",
                  "https://pbs.twimg.com/media/C-SyQiHUMAADE9p.jpg",
                  "https://pbs.twimg.com/media/C-Q2vdmUAAACjk8.jpg:orig",
                  "https://pbs.twimg.com/media/C-M8I8NVwAASSQo.jpg:orig",
                  "https://pbs.twimg.com/media/C-JoIGcU0AAy4YM.jpg:orig",
                  "https://pbs.twimg.com/media/C-G7oyIUwAEt-Jg.jpg:orig",
                  "https://pbs.twimg.com/media/C-C56TXVwAA3Y3P.jpg:orig",
                  "https://pbs.twimg.com/media/C-BloX-UAAELn7C.jpg:orig",
                  "https://pbs.twimg.com/media/C9-bY5WW0AA2vPI.jpg:orig",
                  "https://pbs.twimg.com/media/C98hYw4VwAI0c3U.jpg:orig",
                  "https://pbs.twimg.com/media/C94X3RtVYAENsRE.jpg:orig",
                  "https://pbs.twimg.com/media/C93B21UUAAQvUhC.jpg:orig",
                  "https://pbs.twimg.com/media/C9zWWMJVYAAE7DB.jpg:orig",
                  "https://pbs.twimg.com/media/C9yTS-pVoAElheD.jpg:orig",
                  "https://pbs.twimg.com/media/C9u_iLmWAAEz-rw.jpg:orig",
                  "https://pbs.twimg.com/media/C9tQ9FzUMAckkLI.jpg:orig",
                  "https://pbs.twimg.com/media/C9pTdm6VwAAS51Y.jpg:orig",
                  "https://pbs.twimg.com/media/C9nOkGfV0AA4fcZ.jpg:orig",
                  "https://pbs.twimg.com/media/C9kb4ZdXkAE1w6G.jpg:orig",
                  "https://pbs.twimg.com/media/C9iaJa_XgAAFFb7.jpg:orig",
                  "https://pbs.twimg.com/media/C9e59vVUQAAEqPl.jpg",
                  "https://pbs.twimg.com/media/C9dyfzuUwAU2ShL.jpg",
                  "https://pbs.twimg.com/media/C9ajB2lWAAAB7ns.jpg",
                  "https://pbs.twimg.com/media/C9YxhTTUQAAhuNH.jpg:orig",
                  "https://pbs.twimg.com/media/C9VQOPRUMAASNxF.jpg:orig",
                  "https://pbs.twimg.com/media/C9O9T_dUQAQxcL1.jpg:orig",
                  "https://pbs.twimg.com/media/C9JH1kAUwAAQmcc.jpg:orig",
                  "https://pbs.twimg.com/media/C9D6hozVwAAElCp.jpg:orig",
                  "https://pbs.twimg.com/media/C9AwPXDVYAAEG8I.jpg",
                  "https://pbs.twimg.com/media/C86dw25U0AA3VTY.jpg:orig",
                  "https://pbs.twimg.com/media/C83aXszVoAAly1f.jpg:orig",
                  "https://pbs.twimg.com/media/C80g5DCVYAIN89t.jpg",
                  "https://pbs.twimg.com/media/C8xX0I3UwAA3Rzt.jpg:orig",
                  "https://pbs.twimg.com/media/C8vp1xBVYAAba5e.jpg:orig",
                  "https://pbs.twimg.com/media/C8qX8hnVwAIb2PK.jpg:orig",
                  "https://pbs.twimg.com/media/C8l6moYXoAAV6Rc.jpg:orig",
                  "https://pbs.twimg.com/media/C8iHOUrW0AExFlV.jpg:orig",
                  "https://pbs.twimg.com/media/C8f7eJbVwAA-rxe.jpg:orig",
                  "https://pbs.twimg.com/media/C8dfhggVoAEhqnE.jpg:orig",
                  "https://pbs.twimg.com/media/C8b2wdLV0AAltSB.jpg:orig",
                  "https://pbs.twimg.com/media/C8bK1irV0AAKwaP.jpg",
                  "https://pbs.twimg.com/media/C8a0bRcUQAAU9OG.jpg:orig",
                  "https://pbs.twimg.com/media/C8X-kZVVYAA81EI.jpg:orig",
                  "https://pbs.twimg.com/media/C8XP53zUMAErf3K.jpg:orig",
                  "https://pbs.twimg.com/media/C8WevXRUwAA0NSp.jpg:orig",
                  "https://pbs.twimg.com/media/C8WEuosVYAAyHln.jpg",
                  "https://pbs.twimg.com/media/C8TE9g-VYAAmGyZ.jpg:orig",
                  "https://pbs.twimg.com/media/C8S-7YlUAAAuJ5R.jpg",
                  "https://pbs.twimg.com/media/C8S2IuJUwAEcHZG.jpg:orig",
                  "https://pbs.twimg.com/media/C8Sp1EXUIAAVzKc.jpg:orig",
                  "https://pbs.twimg.com/media/C8Snoh_UIAEa22V.jpg:orig",
                  "https://pbs.twimg.com/media/DA2eJbqWAAI7Rvv.jpg:orig",
                  "https://pbs.twimg.com/media/DAwu22FW0AIfktm.jpg:orig",
                  "https://pbs.twimg.com/media/DArRs7cXoAIN5Hr.jpg:orig",
                  "https://pbs.twimg.com/media/DAmvE08XUAAXqB2.jpg:orig",
                  "https://pbs.twimg.com/media/DAcwAQsXgAE-0qx.jpg:orig",
                  "https://pbs.twimg.com/media/DAXp6U-XsAELxJx.jpg:orig",
                  "https://pbs.twimg.com/media/DASCXiNXoAAWQZQ.jpg:orig",
                  "https://pbs.twimg.com/media/DANQaeeVoAA-aRn.jpg:orig",
                  "https://pbs.twimg.com/media/DAIlTlJWsAEG1ns.jpg:orig",
                  "https://pbs.twimg.com/media/DACxxQXXYAQTIZy.jpg:orig",
                  "https://pbs.twimg.com/media/C_97NVsVYAA45cX.jpg:orig",
                  "https://pbs.twimg.com/media/C_zOECLXkAAEf65.jpg:orig",
                  "https://pbs.twimg.com/media/C_uFAC0XkAEBb8X.jpg:orig",
                  "https://pbs.twimg.com/media/C_pCwwIXoAEhRX_.jpg:orig",
                  "https://pbs.twimg.com/media/C_ZXCLbXYAAWbMp.jpg:orig",
                  "https://pbs.twimg.com/media/C_T-Rm4UMAA88Fc.jpg:orig",
                  "https://pbs.twimg.com/media/C_O7jSnW0AAbkST.jpg:orig",
                  "https://pbs.twimg.com/media/C_KJ_tPWAAEPvbg.jpg:orig",
                  "https://pbs.twimg.com/media/C_EyLx_W0AEPkJ0.jpg:orig",
                  "https://pbs.twimg.com/media/C-_gxHbVoAAiSrV.jpg:orig",
                  "https://pbs.twimg.com/media/DAhyZY1XUAAjG19.jpg:large",
                  "https://pbs.twimg.com/media/C_f2oXcW0AkbZK8.jpg:large"
]


class CoolKidsClub:


    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('database.db')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS spoilers
             (episode real, name text)''')
        


    @commands.command()
    async def memri(self):
        await self.bot.say(random.choice(no_flight_list))

    @commands.command(pass_context=True, aliases=["pick", "choice", "select"])
    async def choose(self, ctx, *choices):
        if ctx.message.mentions:
            return
        if "," in ctx.message.content:
            real_choices = ctx.message.content.split()
            real_choices = real_choices[1:]
            real_choices = ' '.join(real_choices)
            real_choices = real_choices.split(",")
        else:
            real_choices = choices
        await self.bot.say(clean_string(random.choice(real_choices)))

    @commands.command(pass_context=True, name='aesthetics', aliases=['ae'])
    async def _aesthetics(self, ctx, *, sentence : str):
        await self.bot.say(aesthetics(sentence))

    @commands.command(pass_context=True, name='smallcaps', aliases=['sc'])
    async def _smallcaps(self, ctx, *, sentence : str):
        await self.bot.say(smallcaps(sentence))

    @commands.command(name="8ball", pass_context=True)
    @commands.cooldown(2, 60, BucketType.channel)
    async def eightball(self, ctx):
        r = random.choice(eight_ball_responses)
        await self.bot.say(":8ball: | {}, **{}**".format(r, ctx.message.author.name))

    @commands.command(pass_context=True)
    async def sparty(self, ctx):
        if ctx.message.server.id != "207943928018632705":
            return
        sparty_role = discord.utils.get(ctx.message.server.roles, name='Sparty Fan Club')
        if sparty_role in ctx.message.author.roles:
            await self.bot.remove_roles(ctx.message.author, sparty_role)
            await self.bot.send_message(ctx.message.channel, "You will no longer receive a notification when sparty goes live.")
        else:
            await self.bot.add_roles(ctx.message.author, sparty_role)
            await self.bot.send_message(ctx.message.channel, "You will now receive a notification when sparty goes live.")

    @commands.group(pass_context=True, invoke_without_command=True)
    @commands.cooldown(2, 3600, BucketType.user)
    async def sicklad(self, ctx, *, member: discord.Member = None):
        user = ctx.message.author if member is None else member
        r = self.c.execute('SELECT sicklad FROM users WHERE (server=? AND id=?)', (user.server.id, user.id))
        r = r.fetchone()[0]
        leftover_args = ctx.message.content.split()
        leftover_args = leftover_args[1:]
        if user == ctx.message.author:
            await self.bot.say("You sure are.")
            return
        if r == 0:
            self.c.execute('UPDATE users SET sicklad = sicklad + 1 WHERE (id=? AND server=?)', (user.id, ctx.message.server.id))
            self.conn.commit()
            await self.bot.say("Welcome to the sicklad club, **{0}**".format(user.name))
        else:
            self.c.execute('UPDATE users SET sicklad = sicklad + 1 WHERE (id=? AND server=?)', (user.id, ctx.message.server.id))
            self.conn.commit()
            await self.bot.say("**{0}** now has **{1}** sicklad points.".format(user.name.replace("_", "\_"), r+1))
            
        




    @sicklad.command(pass_context=True, name="top", aliases=['leaderboard', 'leaderboards', 'highscore', 'highscores', 'hiscores'])
    async def sickladtop(self, ctx):
        a = self.c.execute('SELECT * FROM users WHERE server=? ORDER BY sicklad DESC LIMIT 10', (ctx.message.server.id,))
        a = a.fetchall()
        b = self.c.execute('SELECT SUM(sicklad) AS "hello" FROM users WHERE server=?', (ctx.message.server.id,))
        b = b.fetchone()[0]
        print(b)
        post_this = ""
        server = ctx.message.server.id
        rank = 1
        for row in a:
            name = row[4].split(',')
            name = name[-1]
            post_this += ("{}. **{}:** {}\n".format(rank, name, row[7]))
            rank += 1
        post_this += "\n**{0}** points in total spread across **{1}** sicklads.".format(b,len([x for x in ctx.message.server.members]))
        post_this = clean_string(post_this)
        em = discord.Embed(title="Current standings:", description=post_this, colour=0x14e818)
        em.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        await self.bot.say(embed=em)
    @commands.group(pass_context=True, invoke_without_command=True)
    async def retard(self, ctx, *, member : discord.Member = None):
        user = ctx.message.author if member is None else member
        r = self.c.execute('SELECT retard FROM users WHERE (server=? AND id=?)', (user.server.id, user.id))
        r = r.fetchone()[0]
        leftover_args = ctx.message.content.split()
        leftover_args = leftover_args[1:]
        if user == ctx.message.author:
            await self.bot.say("You sure are.")
            return
        if r == 0:
            self.c.execute('UPDATE users SET retard = retard + 1 WHERE (id=? AND server=?)', (user.id, ctx.message.server.id))
            self.conn.commit()
            await self.bot.say("Welcome to the retard club, **{0}**".format(user.name))
        else:
            if len(leftover_args) == 1:
                self.c.execute('UPDATE users SET retard = retard + 1 WHERE (id=? AND server=?)', (user.id, ctx.message.server.id))
                self.conn.commit()
                await self.bot.say("**{0}** now has **{1}** coins.".format(user.name.replace("_", "\_"), r+1))
            else:
                reason = ' '.join(leftover_args[1:])
                self.c.execute('UPDATE users SET retard = retard + 1 WHERE (id=? AND server=?)', (ctx.message.author.id, ctx.message.server.id))
                self.conn.commit()
                await self.bot.say("**{0}** just tipped **{1} 1** retard coin, reason: `{2}`\n**{1}** now has **{3}** coins.".format(ctx.message.author.name.replace("_", "\_"), user.name.replace("_", "\_"), reason, r+1))
    

    @retard.command(pass_context=True, name="top", aliases=['leaderboard', 'leaderboards', 'highscore', 'highscores', 'hiscores'])
    async def _top(self, ctx):
        a = self.c.execute('SELECT * FROM users WHERE server=? ORDER BY retard DESC LIMIT 10', (ctx.message.server.id,))
        a = a.fetchall()
        b = self.c.execute('SELECT SUM(retard) AS "hello" FROM users WHERE server=?', (ctx.message.server.id,))
        b = b.fetchone()[0]
        print(b)
        post_this = ""
        server = ctx.message.server.id
        rank = 1
        for row in a:
            name = row[4].split(',')
            name = name[-1]
            post_this += ("{}. **{}:** {}\n".format(rank, name, row[6]))
            rank += 1
            
        # rank = 1
        # for w in sorted(retardcoins[server], key=retardcoins[server].get, reverse=True):
        #     if rank < 11:
        #         try:
        #             post_this += ("{0}. **{1}:** {2}\n".format(rank, ctx.message.server.get_member(w).name, retardcoins[server][w]))
        #             rank += 1
        #         except Exception as e:
        #             await self.bot.send_message(discord.Object(id="213720502219440128"), e)
        #             continue
        #     else:
        #         continue
        post_this += "\n**{0}** coins in total spread across **{1}** retards.".format(b,len([x for x in ctx.message.server.members]))
        post_this = clean_string(post_this)
        em = discord.Embed(title="Current standings:", description=post_this, colour=0x14e818)
        em.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        await self.bot.say(embed=em)
            
    @commands.command(pass_context=True, aliases=['ud'])
    async def urbandictionary(self, ctx, *, query: str):
        query = ''.join(ctx.message.content.split()[1:])
        url = r"http://api.urbandictionary.com/v0/define?term={}".format(query)
        async with aiohttp.get(url) as r:
            definition = await r.json()
        try:
            definition = "**{}**\n{}\n\n*{}*".format(definition["list"][0]["word"].capitalize(), definition["list"][0]["definition"], definition["list"][0]["example"])
            definition = definition.replace("<b>", "**")
            definition = definition.replace("</b>", "**")
        except:
            await self.bot.say('No definition found for "{}", unlucky.'.format(query))
            return
        try:
            await self.bot.say(definition)
        except discord.HTTPException:
            await self.bot.say("Definition over 2k characters :/")

    @commands.command(pass_context=True, name="i", aliases=['info'], no_pm=True)
    async def _i(self, ctx, *, member : discord.Member = None):
        user = ctx.message.author if member is None else member
        a = self.c.execute('SELECT * FROM users WHERE (id=? AND server=?)', (user.id, user.server.id))
        _, _, _, _, names, postcount, retard, sicklad = a.fetchall()[0]
        c = self.c.execute('SELECT postcount FROM users WHERE server=?', (user.server.id,))
        pc = c.fetchall()
        r = self.c.execute('SELECT retard FROM users WHERE server=?', (user.server.id,))
        rc = r.fetchall()
        s = self.c.execute('SELECT sicklad FROM users WHERE server=?', (user.server.id,))
        sc = s.fetchall()
        n = self.c.execute('SELECT names FROM users WHERE (server=? AND id=?)', (user.server.id, user.id))
        nicks = n.fetchall()
        nicks = nicks[0][0].split(',')[-5:]
        nicks = nicks[::-1]        
        print(pc)
        print(sorted([x[0] for x in pc], reverse=True))
        retard_rank = "{}\nrank {}".format(retard, (sorted([x[0] for x in rc], reverse=True).index(retard)+1))
        postcount_rank = "{}\nrank {}".format(postcount, (sorted([x[0] for x in pc], reverse=True).index(postcount)+1))
        sicklad_rank = "{}\nrank {}".format(sicklad, (sorted([x[0] for x in sc], reverse=True).index(sicklad)+1))
        try:
            avatar = user.avatar_url
        except:
            avatar = user.default_avatar_url
        try:
            joined_at = user.joined_at
            days_since = "({} days ago)".format((datetime.datetime.today() - user.joined_at).days)
            days_after_creation = (user.joined_at - ctx.message.server.created_at).days
        except:
            joined_at = "User somehow doesn't have a join date.'"
            days_since = ""
        try:
            days_since_creation = "({} days ago)".format((datetime.datetime.today() - user.created_at).days)
        except Exception as e:
            print(e)
            days_since_creation = ""

        if len(nicks) > 1:
            hmm = "Nicknames"
        else:
            hmm = "Nickname"

        nicks = '\n'.join(nicks)
        usercolor = user.color
        created = re.sub("\.(.*)", "", str(user.created_at))
        joined_at = re.sub("\.(.*)", "", str(user.joined_at))
        em = discord.Embed(title=None, description=None, colour=usercolor)
        em.set_author(name=user.name, icon_url=user.avatar_url, url=user.avatar_url.replace(".webp", ".png"))
        em.add_field(name="Name", value="{}#{}".format(user.name, user.discriminator), inline=True)
        em.add_field(name=hmm, value=nicks, inline=True)
        em.add_field(name="ID", value=user.id, inline=True)
        em.add_field(name="Postcount", value=postcount_rank, inline=True)
        if retard > 0:
            em.add_field(name="Retard coins", value=retard_rank, inline=True)
        if sicklad > 0:
            em.add_field(name="Sicklad points", value=sicklad_rank, inline=True)
        em.add_field(name="Created at", value="{} {}".format(created.replace(" ", "\n"), days_since_creation), inline=True)
        em.add_field(name="Joined at", value="{} {}\nThat's {} days after the server was created".format(joined_at.replace(" ", "\n"), days_since, days_after_creation), inline=True)
        #em.set_thumbnail(url=avatar)
        await self.bot.say(embed=em)



    @commands.group(pass_context=True, aliases=['weather'], invoke_without_command=True)
    async def temp(self, ctx, *, city : str = None):
        a = self.c.execute('SELECT location FROM users WHERE (server=? AND id=?)', (ctx.message.server.id, ctx.message.author.id))        
        saved_city = a.fetchone()[0]
        bot_channel = self.c.execute('SELECT bot_channel FROM servers WHERE id=?', (ctx.message.server.id,))
        bot_channel = bot_channel.fetchall()
        if bot_channel == [] or bot_channel[0][0] is None:
            bot_channel = discord.utils.find(lambda m: "bot" in m.name, ctx.message.server.channels)
            if bot_channel is None:
                bot_channel = ctx.message.channel
        else:
            bot_channel = discord.Object(id=bot_channel[0][0])
        if ctx.message.channel.is_default:             
            xd = await self.bot.send_message(bot_channel, ctx.message.author.mention)  
            await self.bot.delete_message(ctx.message)
        else:
            bot_channel = ctx.message.channel
        
        if saved_city and city is None:
            city = saved_city
        elif saved_city is None:
            if city is None:
                return await self.bot.say("No home set. To set a home, use `!weather home <location>`")
            else:
                self.c.execute('UPDATE users SET location=? WHERE id=?', (city, ctx.message.author.id))
                self.conn.commit()
                await self.bot.say("Your home was automatically set to **{}**.".format(clean_string(city)))
            
                

        
        async with aiohttp.get('http://api.openweathermap.org/data/2.5/weather?q=' + city  + "&appid=d7cff263f60441de43e6909ed780478e") as r:
            json_object = await r.json()
        print(json_object)
        if json_object['cod'] == '404':
            return await self.bot.say("City not found")
        temp_k = float(json_object['main']['temp'])
        temp_c = temp_k - 273.15
        temp_f = temp_c * (9/5) + 32
        city, country, weather, humidity, windspeed = json_object['name'],json_object['sys']['country'], json_object['weather'][0]['description'], json_object['main']['humidity'], json_object['wind']['speed']
        user = ctx.message.author
        usercolor = user.color
        em = discord.Embed(title="Weather in {0}, {1}".format(city, country), description="", colour=usercolor)
        em.set_author(name=user.display_name, icon_url=user.avatar_url, url=user.avatar_url)
        em.add_field(name="Temperature", value="{0:.1f}°C\n{1:.1f}°F".format(temp_c, temp_f), inline=True)
        em.add_field(name="Description", value=pretty_weather(weather), inline=True)
        em.add_field(name="Humidity", value="{}%".format(humidity), inline=True)
        em.add_field(name="Wind speed", value="{}m/s\n{}".format(windspeed, beaufort_scale(windspeed)), inline=True)
        em.set_thumbnail(url=user.avatar_url)
        await self.bot.send_message(bot_channel, embed=em)

    @temp.command(pass_context=True, name="home")
    async def _home(self, ctx, *, city : str):
        self.c.execute('UPDATE users SET location=? WHERE id=?', (city, ctx.message.author.id,))
        self.conn.commit()
        await self.bot.say("Home set to **{}**".format(clean_string(city)))

    @commands.command(pass_context=True, aliases=['nicks'])
    async def nicknames(self, ctx, *, member : discord.Member = None):          
        user = ctx.message.author if member is None else member
        n = self.c.execute('SELECT names FROM users WHERE (server=? AND id=?)', (user.server.id, user.id))
        nicks = n.fetchall()
        nicks = nicks[0][0].split(',')
        #nicks = nicks[::-1] 
        nicknames = ', '.join(nicks)
        nicknames = re.sub('@', '@\u200b', nicknames.replace("_", "\_"))
        if len(nicknames) < 1900:
            await self.bot.say("**Nickname history for {}#{}:**\n{}".format(user.name, user.discriminator, nicknames))
        else:
            tempmessage = []
            finalmessage = []
            for tag in nicks:
                if len(', '.join(tempmessage)) < 1800:
                    tempmessage.append(tag)
                else:
                    formatted_tempmessage = ', '.join(tempmessage)
                    finalmessage.append(formatted_tempmessage)
                    tempmessage = []
            finalmessage.append(', '.join(tempmessage))
            for x in finalmessage:
                if x != "":
                    await self.bot.say(re.sub('@', '@\u200b', x))
            # url = "https://hastebin.com/documents"
            # payload = {'some': 'data'}
            # async with aiohttp.ClientSession() as session:
            #     headers = {'content-type': 'text/plain', 'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64)'}
            #     nicks = '\n'.join(nicks)
            #     data = nicks.encode('utf-8')
            #     async with session.post(url=url, data=data, headers=headers) as r:
            #         print(r.status)
            #         haste_thing = await r.json(encoding="utf-8", loads=json.loads)
            # await self.bot.say("Too many nicknames to display: https://hastebin.com/{}".format(haste_thing["key"]))  
            
            
            



    @commands.command(pass_context=True)
    async def speak(self, ctx, repeats : int = 5, *, member : discord.Member = None):
        user = ctx.message.author if member is None else member
        if "bot" not in ctx.message.channel.name:
            try:
                destination = discord.utils.find(lambda m: "bot" in m.name, ctx.message.server.channels)
                xd = await self.bot.send_message(destination, ctx.message.author.mention)
                #await self.bot.delete_message(ctx.message)
            except:
                destination = ctx.message.channel
        else:
            destination = ctx.message.channel
        try:
            with open("logs/{}/{}.txt".format(user.server.id, user.id), encoding="utf-8") as f:
                text = f.read()
            text_model = markovify.NewlineText(text)
            speech = "**{}:**\n".format(user.name)
        except:
            await self.bot.send_message(destination, "No file matching {}".format(repeats))
        repeats = min(repeats, 20)
        for i in range(repeats):
            try:
                variablename = text_model.make_short_sentence(140, state_size=2).replace("@", "@ ")
                try:
                    id_mention = re.search("<@ [!]?(.*)>", variablename)
                    id_mention = id_mention.group(1)
                    id_name = self.get_server("207943928018632705").get_member(str(id_mention)).name
                    add_this = re.sub("<@ [!]?.*>", id_name, variablename)
                    speech += "{}\n\n".format(add_this)
                except AttributeError:
                    speech += "{}\n\n".format(variablename)
            except KeyError:
                return
            except AttributeError:
                pass
        await self.bot.send_message(destination, speech)

    @commands.command(pass_context=True)
    async def roll(self, ctx):
        args = ctx.message.content.split()
        if len(args) == 1:
            sides = 6
            rolls = 1
        elif len(args) == 2:
            sides = int(args[1])
            rolls = 1
        elif len(args) == 3:
            sides = int(args[1])
            rolls = int(args[2])
        else:
            return
        results = []
        if sides > 1000000000000 or rolls > 100:
            return
        for i in range(rolls):
            diceRoll = random.randint(1, sides)
            results.append(diceRoll)
        median = statistics.median(results)
        mean = statistics.mean(results)
        if len(results) <= 10:
            results = ', '.join([str(x) for x in results])
            #results = ', '.join(results)
            await self.bot.say("You rolled **{0}** **{1}-sided** dice, results: **{2}**\nMedian: **{3}**, mean: **{4:.2f}**".format(rolls, sides, results, median, mean))
        else:
            await self.bot.say("You rolled **{0}** **{1}-sided** dice\nMedian: **{2}**, mean: **{3:.2f}**".format(rolls, sides, median, mean))

    async def got_checker(self):
        DELAY = 60
        await asyncio.sleep(5)
        first_episode = datetime.datetime(2017, 7, 17, 0, 50, 0)
        while self == self.bot.get_cog("CoolKidsClub"):
            a = self.c.execute('SELECT * FROM spoilers')
            a = a.fetchall()
            now = datetime.datetime.utcnow()
            difference = (now - first_episode).total_seconds()
            episode, remainder = divmod(difference, 604800)
            episode += 1
            if 0 < remainder <= 3600:
                for row in a:
                    db_episode = int(row[0])
                    if db_episode == episode:                      
                        db_name = row[1]
                        self.c.execute('DELETE FROM spoilers WHERE episode=?', (episode,))
                        self.conn.commit()
                        try:
                            server = self.bot.get_server(id="207943928018632705")
                            got_role = discord.utils.get(server.roles, id='288186937804587008')
                            mention = got_role.mentionable
                            if not mention:
                                await self.bot.edit_role(server, got_role, mentionable=True)
                            await self.bot.send_message(discord.Object(id="335477719431249932"), '<@&288186937804587008>\nGame of Thrones is live in 10 minutes with the episode "{}"'.format(db_name))
                            await self.bot.edit_role(server, got_role, mentionable=False)
                        except Exception as e:
                            print(e)
            else:
                print("no")
                print(remainder)
            await asyncio.sleep(10)

    @commands.command(pass_context=True)
    async def got(self, ctx):
        if ctx.message.server.id != "207943928018632705":
            return
        got_role = discord.utils.get(ctx.message.server.roles, id='288186937804587008')
        if got_role in ctx.message.author.roles:
            await self.bot.remove_roles(ctx.message.author, got_role)
            await self.bot.send_message(ctx.message.channel, "You will no longer be notified when Game of Thrones is live.")
        else:
            await self.bot.add_roles(ctx.message.author, got_role)
            await self.bot.send_message(ctx.message.channel, "You will be notified when Game of Thrones is live.")
                    
                
                


def setup(bot):
    f = CoolKidsClub(bot)
    loop = asyncio.get_event_loop()
    loop.create_task(f.got_checker())
    bot.add_cog(f)
    