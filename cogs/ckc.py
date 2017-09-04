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
import string

from io import BytesIO
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

def pretty_weather(weather): # this is literally the dumbest thing my bot has
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


class CoolKidsClub:


    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('database.db')
        self.c = self.conn.cursor()
        

    @commands.command(aliases=["pick", "choice", "select"])
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
        await ctx.send(clean_string(random.choice(real_choices)))

    @commands.command(name='aesthetics', aliases=['ae'])
    async def _aesthetics(self, ctx, *, sentence : str):
        await ctx.send(aesthetics(sentence))

    @commands.command(name='smallcaps', aliases=['sc'])
    async def _smallcaps(self, ctx, *, sentence : str):
        await ctx.send(smallcaps(sentence))

    @commands.command(name="8ball")
    async def eightball(self, ctx):
        # I hate this command and everyone who uses it
        r = random.choice(eight_ball_responses)
        await ctx.send(":8ball: | {}, **{}**".format(r, ctx.message.author.name))


    @commands.command(no_pm=True, hidden=True)
    async def poe(self, ctx):
        a = ctx.message.author
        poe_role = discord.utils.get(ctx.guild.roles, id=345966982715277312)
        if poe_role in ctx.message.author.roles:
            await ctx.author.remove_roles(poe_role)
            await ctx.send("Removed poe role from **{}**.".format(ctx.message.author.name))
        else:
            await ctx.author.add_roles(poe_role)
            await ctx.send("Added poe role to **{}**.".format(ctx.message.author.name))



    @commands.command(no_pm=True, hidden=True)
    async def poehere(self, ctx):
        poe_role = discord.utils.get(ctx.guild.roles, id=345966982715277312)
        if poe_role not in ctx.author.roles:
            return await ctx.send("You need to have the poe role to use this command. !poe to get it.")
        offline = [x for x in ctx.guild.members if (poe_role in x.roles and str(x.status) != "online")]
        for m in offline:
            await m.remove_roles(poe_role, reason="automatic poehere")
        await poe_role.edit(mentionable=True)
        await ctx.send("<@&345966982715277312>")
        for m in offline:
            await m.add_roles(poe_role, reason="automatic poehere")
        await poe_role.edit(mentionable=False)


    @commands.group(invoke_without_command=True, hidden=True)
    async def sicklad(self, ctx, *, member: discord.Member = None):
        user = ctx.author if member is None else member
        r = self.c.execute('SELECT sicklad FROM users WHERE (server=? AND id=?)', (ctx.guild.id, user.id))
        r = r.fetchone()[0]
        leftover_args = ctx.message.content.split()
        leftover_args = leftover_args[1:]
        if user == ctx.author:
            await ctx.send("You sure are.")
            return
        if r == 0:
            self.c.execute('UPDATE users SET sicklad = sicklad + 1 WHERE (id=? AND server=?)', (user.id, ctx.guild.id))
            self.conn.commit()
            await ctx.send("Welcome to the sicklad club, **{0}**".format(user.name))
        else:
            self.c.execute('UPDATE users SET sicklad = sicklad + 1 WHERE (id=? AND server=?)', (user.id, ctx.guild.id))
            self.conn.commit()
            await ctx.send("**{0}** now has **{1}** sicklad points.".format(user.name.replace("_", "\_"), r+1))
            
        




    @sicklad.command(name="top", aliases=['leaderboard', 'leaderboards', 'highscore', 'highscores', 'hiscores'])
    async def sickladtop(self, ctx):
        a = self.c.execute('SELECT * FROM users WHERE server=? ORDER BY sicklad DESC LIMIT 10', (ctx.guild.id,))
        a = a.fetchall()
        b = self.c.execute('SELECT SUM(sicklad) AS "hello" FROM users WHERE server=?', (ctx.guild.id,))
        b = b.fetchone()[0]
        post_this = ""
        rank = 1
        for row in a:
            name = f'<@{row[3]}>'
            post_this += ("{}. {} : {}\n".format(rank, name, row[7]))
            rank += 1
        post_this += "\n**{0}** points in total spread across **{1}** sicklads.".format(b,len([x for x in ctx.guild.members]))
        em = discord.Embed(title="Current standings:", description=post_this, colour=0x3ed8ff)
        em.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=em)

    @commands.group(invoke_without_command=True, hidden=True)
    async def retard(self, ctx, member : discord.Member = None, *, reason: str=None):
        user = ctx.message.author if member is None else member
        r = self.c.execute('SELECT retard FROM users WHERE (server=? AND id=?)', (ctx.guild.id, user.id))
        r = r.fetchone()[0]
        leftover_args = ctx.message.content.split()
        leftover_args = leftover_args[1:]
        if user == ctx.message.author:
            await ctx.send("You sure are.")
            return
        if r == 0:
            self.c.execute('UPDATE users SET retard = retard + 1 WHERE (id=? AND server=?)', (user.id, ctx.guild.id))
            self.conn.commit()
            await ctx.send("Welcome to the retard club, **{0}**".format(user.name))
        else:
            if reason is None:
                self.c.execute('UPDATE users SET retard = retard + 1 WHERE (id=? AND server=?)', (user.id, ctx.guild.id))
                self.conn.commit()
                await ctx.send("**{0}** now has **{1}** coins.".format(user.name.replace("_", "\_"), r+1))
            else:
                self.c.execute('UPDATE users SET retard = retard + 1 WHERE (id=? AND server=?)', (ctx.message.author.id, ctx.guild.id))
                self.conn.commit()
                await ctx.send("**{0}** just tipped **{1} 1** retard coin, reason: `{2}`\n**{1}** now has **{3}** coins.".format(ctx.message.author.name.replace("_", "\_"), user.name.replace("_", "\_"), reason, r+1))
    

    @retard.command(name="top", aliases=['leaderboard', 'leaderboards', 'highscore', 'highscores', 'hiscores'])
    async def _top(self, ctx):
        a = self.c.execute('SELECT * FROM users WHERE server=? ORDER BY retard DESC LIMIT 10', (ctx.guild.id,))
        a = a.fetchall()
        b = self.c.execute('SELECT SUM(retard) AS "hello" FROM users WHERE server=?', (ctx.guild.id,))
        b = b.fetchone()[0]
        post_this = ""
        rank = 1
        for row in a:
            name = f'<@{row[3]}>'
            post_this += ("{}. {} : {}\n".format(rank, name, row[6]))
            rank += 1

        post_this += "\n**{0}** coins in total spread across **{1}** retards.".format(b,len([x for x in ctx.guild.members]))
        em = discord.Embed(title="Current standings:", description=post_this, colour=0xff855a)
        em.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=em)
            
    @commands.command(aliases=['ud'])
    async def urbandictionary(self, ctx, *, query: str):
        query = ''.join(ctx.message.content.split()[1:])
        url = r"http://api.urbandictionary.com/v0/define?term={}".format(query)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                definition = await r.json()
        try:
            definition = "**{}**\n{}\n\n*{}*".format(definition["list"][0]["word"].capitalize(), definition["list"][0]["definition"], definition["list"][0]["example"])
            definition = definition.replace("<b>", "**")
            definition = definition.replace("</b>", "**")
        except:
            await ctx.send('No definition found for "{}", unlucky.'.format(query))
            return
        try:
            # fuck off !ud @everyone
            await ctx.send(clean_string(definition))
        except discord.HTTPException:
            await ctx.send("Definition over 2k characters :/")

    @commands.command(name="info", aliases=['i'], no_pm=True)
    async def _i(self, ctx, *, member : discord.Member = None):
        user = ctx.message.author if member is None else member
        a = self.c.execute('SELECT * FROM users WHERE (id=? AND server=?)', (user.id, ctx.guild.id))
        _, _, _, _, names, postcount, retard, sicklad = a.fetchall()[0]
        c = self.c.execute('SELECT postcount FROM users WHERE server=?', (ctx.guild.id,))
        pc = c.fetchall()
        r = self.c.execute('SELECT retard FROM users WHERE server=?', (ctx.guild.id,))
        rc = r.fetchall()
        s = self.c.execute('SELECT sicklad FROM users WHERE server=?', (ctx.guild.id,))
        sc = s.fetchall()
        n = self.c.execute('SELECT names FROM users WHERE (server=? AND id=?)', (ctx.guild.id, user.id))
        nicks = n.fetchall()
        nicks = nicks[0][0].split(',')[-5:]
        nicks = nicks[::-1]
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
            days_after_creation = (user.joined_at - ctx.guild.created_at).days
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
        created = user.created_at.strftime("%Y-%m-%d\n%H:%M:%S")
        joined_at = user.joined_at.strftime("%Y-%m-%d\n%H:%M:%S")
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
        em.add_field(name="Created at", value="{} {}".format(created, days_since_creation), inline=True)
        em.add_field(name="Joined at", value="{} {}\nThat's {} days after the server was created".format(joined_at, days_since, days_after_creation), inline=True)
        #em.set_thumbnail(url=avatar)
        await ctx.send(embed=em)



    @commands.group(aliases=['weather'], invoke_without_command=True)
    async def temp(self, ctx, *, city : str = None):
        a = self.c.execute('SELECT location FROM users WHERE (server=? AND id=?)', (ctx.guild.id, ctx.message.author.id))        
        saved_city = a.fetchone()[0]
        # bot_channel = self.c.execute('SELECT bot_channel FROM servers WHERE id=?', (ctx.guild.id,))
        # bot_channel = bot_channel.one()
        # if bot_channel[0] is None:
        #     bot_channel = discord.utils.find(lambda m: "bot" in m.name, ctx.guild.channels)
        #     if bot_channel is None:
        #         bot_channel = ctx.channel
        # else:
        #     bot_channel = ctx.channel       
        if saved_city and city is None:
            city = saved_city
        elif saved_city is None:
            if city is None:
                return await ctx.send("No home set. To set a home, use `!weather home <location>`")
            else:
                self.c.execute('UPDATE users SET location=? WHERE id=?', (city, ctx.message.author.id))
                self.conn.commit()
                # Is this too big brother?
                await ctx.send("Your home was automatically set to **{}**, `!temp` will now default to it.".format(clean_string(city)))
            
                

        async with aiohttp.ClientSession() as session:
            async with session.get('http://api.openweathermap.org/data/2.5/weather?q=' + city  + "&appid=d7cff263f60441de43e6909ed780478e") as r:
                json_object = await r.json()
        if json_object['cod'] == '404':
            return await ctx.send("City not found")
        temp_k = float(json_object['main']['temp'])
        temp_c = temp_k - 273.15
        temp_f = temp_c * (9/5) + 32
        city, country, weather, humidity, windspeed = json_object['name'],json_object['sys']['country'], json_object['weather'][0]['description'], json_object['main']['humidity'], json_object['wind']['speed']
        user = ctx.message.author
        usercolor = user.color
        em = discord.Embed(title="Weather in {0}, {1}".format(city, country), description="", colour=usercolor)
        em.set_author(name=user.display_name, icon_url=user.avatar_url, url=user.avatar_url)
        em.add_field(name="Temperature", value="{0:.1f}°C\n{1:.1f}°F".format(temp_c, temp_f))
        em.add_field(name="Description", value=pretty_weather(weather))
        em.add_field(name="Humidity", value="{}%".format(humidity))
        em.add_field(name="Wind speed", value="{}m/s\n{}".format(windspeed, beaufort_scale(windspeed)))
        #em.set_thumbnail(url=user.avatar_url)
        await ctx.send(embed=em)

    @temp.command(name="home")
    async def _home(self, ctx, *, city : str):
        self.c.execute('UPDATE users SET location=? WHERE id=?', (city, ctx.message.author.id,))
        self.conn.commit()
        await ctx.send("Home set to **{}**".format(clean_string(city)))

    @commands.command(aliases=['nicks'])
    async def nicknames(self, ctx, *, member : discord.Member = None):          
        user = ctx.message.author if member is None else member
        n = self.c.execute('SELECT names FROM users WHERE (server=? AND id=?)', (ctx.guild.id, user.id))
        nicks = n.fetchall()
        nicks = nicks[0][0].split(',')
        #nicks = nicks[::-1] 
        nicknames = ', '.join(nicks)
        nicknames = re.sub('@', '@\u200b', nicknames.replace("_", "\_"))
        if len(nicknames) < 1900:
            await ctx.send("**Nickname history for {}#{}:**\n{}".format(user.name, user.discriminator, nicknames))
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
            # Another fantastic feature brought to you by kintark
            for x in finalmessage:
                if x != "":
                    await ctx.send(re.sub('@', '@\u200b', x))
            # url = "https://hastebin.com/documents"
            # payload = {'some': 'data'}
            # async with aiohttp.ClientSession() as session:
            #     headers = {'content-type': 'text/plain', 'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64)'}
            #     nicks = '\n'.join(nicks)
            #     data = nicks.encode('utf-8')
            #     async with session.post(url=url, data=data, headers=headers) as r:
            #         print(r.status)
            #         haste_thing = await r.json(encoding="utf-8", loads=json.loads)
            # await ctx.send("Too many nicknames to display: https://hastebin.com/{}".format(haste_thing["key"]))  
            
            
            

    @staticmethod
    def _gen(size=8, chars=string.ascii_lowercase + string.digits):
        """
        this function generates a 8 chars string that will be used as DEVICE_ID
        """
        return ''.join(random.choice(chars) for _ in range(size))



    @commands.command()
    async def faceapp(self, ctx, face_filter : str = "female", *, image_url: str =None):
        
            
        face_filter = face_filter.lower()

        if face_filter not in ['smile', 'smile_2', 'hot', 'old', 'young', 'female', 'male']:
            return await ctx.send("Unsupported filter. Try smile, smile_2, hot, old, young, male.")
        
        if image_url is not None:
            image_url = image_url
        elif ctx.message.attachments:
            image_url = ctx.message.attachments[0].url
        else:
            image_url = ctx.message.author.avatar_url.replace(".webp", ".png")
            image_url = image_url.replace(".gif", ".png")
            await ctx.send("No file upload or link provided. Using your avatar instead.")
        #image_url = image_url if image_url is not None else ctx.message.attachments[0]["url"]
        
        URL = 'https://node-01.faceapp.io'
        USER_AGENT = 'FaceApp/1.0.229 (Linux; Android 4.4)'
        DEVICE_ID = self._gen()
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as x:
                file = await x.read()
        output_buffer = BytesIO(file)
        async with aiohttp.ClientSession() as session:
            async with session.post(URL + '/api/v2.3/photos', data={'file': output_buffer}, headers={'User-Agent': USER_AGENT, 'X-FaceApp-DeviceID': DEVICE_ID}) as r:
                code = await r.json()
                if "code" in code:                
                    code = code['code']
                elif "err" in code:
                    return await ctx.send("Error: {}".format(code["err"]["code"]))
                else:
                    return await ctx.send("Is this what's causing 0 byte uploads? {}".format(code))
        async with aiohttp.ClientSession() as session:
            async with session.get(URL + '/api/v2.3/photos/{}/filters/{}?cropped=true'.format(code, face_filter),
                                headers={'User-Agent': USER_AGENT, 'X-FaceApp-DeviceID': DEVICE_ID}) as r:
                                face = await r.read()
                                print(face)
        send_me = BytesIO(face)
        await ctx.send(file=discord.File(fp=send_me, filename="hehe.png"))


    @commands.group(invoke_without_command=True)
    async def speak(self, ctx, repeats : int = 5, *, member : discord.Member = None):
        user = ctx.message.author if member is None else member
        if "bot" not in ctx.message.channel.name:
            try:
                destination = discord.utils.find(lambda m: "bot" in m.name, ctx.guild.channels)
                xd = await destination.send(ctx.message.author.mention)
            except:
                destination = ctx.message.channel
        else:
            destination = ctx.message.channel

        a = self.c.execute('SELECT content FROM messages WHERE author=?', (user.id,))
        a = a.fetchall()
        text = '\n'.join([x[0] for x in a if len(x[0]) > 20])
        text_model = markovify.NewlineText(text)
        speech = "**{}:**\n".format(user.name)
        repeats = min(repeats, 20)
        for i in range(repeats):
            try:
                variablename = text_model.make_short_sentence(140, state_size=2)
                speech += "{}\n\n".format(clean_string(variablename))
            except Exception as e:
                continue

        await destination.send(speech)

    @speak.command(name="channel")
    async def _channel(self, ctx, channel: discord.TextChannel = None):
        # For when you want a markov chain for the entire channel
        if "bot" not in ctx.message.channel.name:
            try:
                destination = discord.utils.find(lambda m: "bot" in m.name, ctx.guild.channels)
                xd = await destination.send(ctx.message.author.mention)                #await self.bot.delete_message(ctx.message)
            except:
                destination = ctx.message.channel
        else:
            destination = ctx.message.channel
        channel = channel if channel is not None else ctx.channel
        a = self.c.execute('SELECT content FROM messages WHERE channel=?', (channel.id,))
        a = a.fetchall()
        text = '\n'.join([x[0] for x in a if len(x[0]) > 20])
        text_model = markovify.NewlineText(text)
        speech = "**{}:**\n".format(channel.name)
        repeats = 20
        for i in range(repeats):
            try:
                variablename = text_model.make_short_sentence(140, state_size=2).replace("@", "@ ")
                speech += "{}\n\n".format(variablename)
            except:
                continue
        await destination.send(speech)

    @commands.command()
    async def dice(self, ctx, sides: int=6, rolls: int=1):
        results = []
        if sides > 1000000000000 or rolls > 100:
            return
        for i in range(rolls):
            diceRoll = random.randint(1, sides)
            results.append(diceRoll)
        median = statistics.median(results)
        mean = statistics.mean(results)
        if len(results) <= 30:
            results = ', '.join([str(x) for x in results])
            #results = ', '.join(results)
            await ctx.send("You rolled **{0}** **{1}-sided** dice, results: **{2}**\nMedian: **{3}**, mean: **{4:.2f}**".format(rolls, sides, results, median, mean))
        else:
            await ctx.send("You rolled **{0}** **{1}-sided** dice\nMedian: **{2}**, mean: **{3:.2f}**".format(rolls, sides, median, mean))
        
    @commands.command(aliases=['coin', 'flip'])
    async def coinflip(self, ctx):
        await ctx.send(random.choice(('Heads', 'Tails')))

      


def setup(bot):
    bot.add_cog(CoolKidsClub(bot))
    