import logging
import discord
import datetime
import random
import traceback
import psutil
import os
import json
import sqlite3
import re


from cogs.utils import checks, config
from discord.ext import commands
from collections import Counter
from io import BytesIO


# conn = sqlite3.connect('database.db')
# c = conn.cursor()
dt_format = '%Y-%m-%d %H:%M:%S'

# c.execute('''CREATE TABLE messages
#              (unix real, timestamp timestamp, content text, id text, author text, channel text, server text)''')


#c.execute("INSERT INTO messages VALUES ({}, {}, {}, {}, {}, {}".format(message.timestamp, message.clean_content, message.id, message.author.id, message.channel.id, message.server.id))

def log(message):
    file_path = "logs/{}/".format(message.server.id)
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open("logs/{}/{}.txt".format(message.server.id, message.author.id), "a", encoding="utf-8") as f:
        f.write("{}\n".format(message.clean_content))




legendaries = [
    "[Acherus Drapes]",
    "[Shackles of Bryndaor]",
    "[Rattlegore Bone Legplates]",
    "[Service of Gorefiend]",
    "[Lana'thel's Lament]",
    "[Skullflower's Haemostasis]",
    "[Seal of Necrofantasia]",
    "[Koltira's Newfound Will]",
    "[Toravon's Whiteout Bindings]",
    "[Perseverance of the Ebon Martyr]",
    "[Consort's Cold Core]",
    "[Tak'theritrix's Shoulderpads]",
    "[Draugr, Girdle of the Everlasting King]",
    "[Uvanimor, the Unbeautiful]",
    "[The Instructor's Fourth Lesson]",
    "[Death March]",
    "[Mo'arg Bionic Stabilizers]",
    "[Raddon's Cascading Eyes]",
    "[Achor, the Eternal Hunger]",
    "[Loramus Thalipedes' Sacrifice]",
    "[Anger of the Half-Giants]",
    "[Delusions of Grandeur]",
    "[Cloak of Fel Flames]",
    "[Kirel Narak]",
    "[Runemaster's Pauldrons]",
    "[The Defiler's Lost Vambraces]",
    "[Fragment of the Betrayer's Prison]",
    "[Spirit of the Darkness Flame]",
    "[Ekowraith, Creator of Worlds]",
    "[Impeccable Fel Essence]",
    "[Promise of Elune, the Moon Goddess]",
    "[The Emerald Dreamcatcher]",
    "[Oneth's Intuition]",
    "[Lady and the Child]",
    "[Chatoyant Signet]",
    "[Ailuro Pouncers]",
    "[The Wildshaper's Clutch]",
    "[Fiery Red Maimers]",
    "[Luffa Wrappings]",
    "[Skysec's Hold]",
    "[Elize's Everlasting Encasement]",
    "[Dual Determination]",
    "[Oakheart's Puny Quods]",
    "[Tearstone of Elune]",
    "[Essence of Infusion]",
    "[Edraith, Bonds of Aglaya]",
    "[Aman'Thul's Wisdom]",
    "[The Dark Titan's Advice]",
    "[X'oni's Caress]",
    "[The Shadow Hunter's Voodoo Mask]",
    "[Roar of the Seven Lions]",
    "[Qa'pla, Eredun War Order]",
    "[The Apex Predator's Claw]",
    "[The Mantle of Command]",
    "[Call of the Wild]",
    "[Magnetized Blasting Cap Launcher]",
    "[Ullr's Feather Snowshoes]",
    "[Zevrim's Hunger]",
    "[War Belt of the Sentinel Army]",
    "[MKII Gyroscopic Stabilizer]",
    "[Nesingwary's Trapping Treads]",
    "[Frizzo's Fingertrap]",
    "[Helbrine, Rope of the Mist Marauder]",
    "[Butcher's Bone Apron]",
    "[Tearstone of Elune]",
    "[Essence of Infusion]",
    "[Edraith, Bonds of Aglaya]",
    "[Aman'Thul's Wisdom]",
    "[The Dark Titan's Advice]",
    "[X'oni's Caress]",
    "[Shard of the Exodar]",
    "[Belo'vir's Final Stand]",
    "[Rhonin's Assaulting Armwraps]",
    "[Cord of Infinity]",
    "[Mystic Kilt of the Rune Master]",
    "[Gravity Spiral]",
    "[Koralon's Burning Touch]",
    "[Darckli's Dragonfire Diadem]",
    "[Marquee Bindings of the Sun King]",
    "[Pyrotex Ignition Cloth]",
    "[Lady Vashj's Grasp]",
    "[Magtheridon's Banished Bracers]",
    "[Zann'esu Journey]",
    "[Ice Time]",
    "[Firestone Walkers]",
    "[Sal'salabim's Lost Tunic]",
    "[Fundamental Observation]",
    "[Gai Plin's Soothing Sash]",
    "[Jewel of the Lost Abbey]",
    "[Anvil-Hardened Wristwraps]",
    "[Eye of Collidus the Warp-Watcher]",
    "[Petrichor Lagniappe]",
    "[Leggings of The Black Flame]",
    "[Unison Spaulders]",
    "[Ei'thas, Lunar Glides of Eramas]",
    "[Ovyd's Winter Wrap]",
    "[Shelter of Rin]",
    "[Cenedril, Reflector of Hatred]",
    "[Drinking Horn Cover]",
    "[March of the Legion]",
    "[Hidden Master's Forbidden Touch]",
    "[Katsuo's Eclipse]",
    "[The Emperor's Capacitor]",
    "[Chain of Thrayn]",
    "[Ilterendi, Crown Jewel of Silvermoon]",
    "[Obsidian Stone Spaulders]",
    "[Tyr's Hand of Faith]",
    "[Maraad's Dying Breath]",
    "[Uther's Guard]",
    "[Heathcliff's Immortality]",
    "[Tyelca, Ferren Marcus's Stature]",
    "[Breastplate of the Golden Val'kyr]",
    "[Saruan's Resolve]",
    "[Liadrin's Fury Unleashed]",
    "[Aegisjalmur, the Armguards of Awe]",
    "[Whisper of the Nathrezim]",
    "[Justice Gaze]",
    "[Ashes to Dust]",
    "[Cord of Maiev, Priestess of the Moon]",
    "[Estel, Dejahna's Inspiration]",
    "[N'ero, Band of Promises]",
    "[Skjoldr, Sanctuary of Ivagont]",
    "[Xalan the Feared's Clench]",
    "[Kam Xi'raff]",
    "[X'anshi, Shroud of Archbishop Benedictus]",
    "[Muze's Unwavering Will]",
    "[Phyrix's Embrace]",
    "[Entrancing Trousers of An'juna]",
    "[Al'maiesh, the Cord of Hope]",
    "[Rammal's Ulterior Motive]",
    "[Anund's Seared Shackles]",
    "[Zenk'aram, Iridi's Anadem]",
    "[The Twins' Painful Touch]",
    "[Mangaza's Madness]",
    "[Mother Shahraz's Seduction]",
    "[Zeks Exterminatus]",
    "[Insignia of Ravenholdt]",
    "[Will of Valeera]",
    "[Mantle of the Master Assassin]",
    "[Duskwalker's Footpads]",
    "[Zoldyck Family Training Shackles]",
    "[The Dreadlord's Deceit]",
    "[Thraxi's Tricksy Treads]",
    "[Greenskin's Waterlogged Wristcuffs]",
    "[Shivarran Symmetry]",
    "[Shadow Satyr's Walk]",
    "[Denial of the Half-Giants]",
    "[Uncertain Reminder]",
    "[Eye of the Twisting Nether]",
    "[The Deceiver's Blood Pact]",
    "[Echoes of the Great Sundering]",
    "[Pristine Proto-Scale Girdle]",
    "[Al'Akir's Acrimony]",
    "[Storm Tempests]",
    "[Akainu's Absolute Justice]",
    "[Emalon's Charged Core]",
    "[Spiritual Journey]",
    "[Focuser of Jonat, the Elder]",
    "[Intact Nazjatar Molting]",
    "[Elemental Rebalancers]",
    "[Praetorian's Tidecallers]",
    "[Nobundo's Redemption]",
    "[Pillars of the Dark Portal]",
    "[Sacrolash's Dark Strike]",
    "[Power Cord of Lethtendris]",
    "[Streten's Sleepless Shackles]",
    "[Hood of Eternal Disdain]",
    "[Reap and Sow]",
    "[Kazzak's Final Curse]",
    "[Wilfred's Sigil of Superior Summoning]",
    "[Recurrent Ritual]",
    "[Sin'dorei Spite]",
    "[Wakener's Loyalty]",
    "[Alythess's Pyrogenics]",
    "[Odr, Shawl of the Ymirjar]",
    "[Feretory of Souls]",
    "[Magistrike Restraints]",
    "[Lessons of Space-Time]",
    "[Mannoroth's Bloodletting Manacles]",
    "[Timeless Stratagem]",
    "[Weight of the Earth]",
    "[Archavon's Heavy Hand]",
    "[Ayala's Stone Heart]",
    "[Naj'entus's Vertebrae]",
    "[Ceann-Ar Charger]",
    "[Kazzalax, Fujieda's Fury]",
    "[Thundergod's Vigor]",
    "[The Walls Fell]",
    "[Kakushan's Stormscale Gauntlets]",
    "[Destiny Driver]",
    "[Kargath's Sacrificed Hands]",
    "[Norgannon's Foresight]",
    "[Cinidaria, the Symbiote]",
    "[Roots of Shaladrassil]",
    "[Aggramar's Stride]",
    "[Archimonde's Hatred Reborn]",
    "[Kil'jaeden's Burning Wish]",
    "[Velen's Future Sight]",
    "[Sephuz's Secret]",
    "[Prydaz, Xavaric's Magnum Opus]"
]



class StatTrak:
    
    def __init__(self, bot):
        self.bot           = bot
        self.conn = sqlite3.connect('database.db')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS messages
             (unix real, timestamp timestamp, content text, id text, author text, channel text, server text)''')

    def get_global_stats(self, dic):
        return [x[1] for x in sorted(dic["global"]["bigGlobal"].items(), key=lambda x: int(x[0]))]

    def get_server_stats(self, dic, s):
        return [x[1] for x in sorted(dic[s.id]["serverglobal"].items(), key=lambda x: int(x[0]))]

    def get_channel_stats(self, dic, c):
        return [x[1] for x in sorted(dic[c.server.id][c.id].items(), key=lambda x: int(x[0]))]

    def get_global_user_stats(self, dic, u):
        return [x[1] for x in sorted(dic["global"][u.id].items(), key=lambda x: int(x[0]))]

    def get_channel_user_stats(self, dic, c, u):
        return [x[1] for x in sorted(dic[u.server.id][u.id][c.id].items(), key=lambda x: int(x[0]))]

    def get_server_user_stats(self, dic, u):
        return [x[1] for x in sorted(dic[u.server.id][u.id]["server"].items(), key=lambda x: int(x[0]))]



    def fix_postcount(self, message):
        if message.channel.is_private:
            return
        self.c.execute('UPDATE users SET postcount = postcount + 1 WHERE (id=? AND server=?)', (message.author.id, message.server.id))
        self.conn.commit()


    # @commands.group(pass_context=True, invoke_without_command=True)
    # async def activity(self, ctx, member : discord.Member = None):
    #     user = ctx.message.author if member is None else member
    #     y_axis = self.get_global_stats(self.globaldata)
    #     plt.figure()
    #     plt.hist(y_axis, self.x_axis)
    #     plt.xlabel('Hour (UTC+0)')
    #     plt.ylabel('messages posted')
    #     plt.title("Global activity")
    #     buf = BytesIO()
    #     plt.savefig(buf, format='png', dpi=500)
    #     buf.seek(0)
    #     await self.bot.send_file(ctx.message.channel, fp=buf, filename="suckmydick.png")

    # @activity.command(name="server", pass_context=True)
    # async def _server(self, ctx, *, normalized: str = []):
    #     print("norm:_",normalized)
    #     if "norm" in normalized:
    #         normalized = True
    #     else:
    #         normalized = False
    #     print("norm2", normalized)
    #     mentions = ctx.message.mentions
    #     if not mentions:
    #         mentions = [x for x in ctx.message.server.members]
    #     mentions = [x.id for x in mentions]
    #     plt.figure()

    #     server_shit = self.globaldata[ctx.message.server.id]
    #     names = []
    #     for user, value in server_shit.items():
    #         if user == "serverglobal" or user in [x.id for x in ctx.message.server.channels]:
    #             continue
    #         elif user not in mentions:
    #             print(user)
    #             continue
    #         userlist = []
    #         for k, v in value.items():
    #             if k == "server":
    #                 shit = v.items()
    #                 for pair in shit:
    #                     userlist.append(pair)
    #         userlist = [x[1] for x in sorted(userlist, key=lambda x: int(x[0]))]            
    #         normalizer = sum(userlist) or 1
    #         normalized_userlist = [x/normalizer for x in userlist]
    #         print(userlist)
    #         print(normalized_userlist)
    #         print("normalized = ", normalized)
    #         y_axis = [userlist, normalized_userlist][normalized]
    #         print(y_axis)
    #         plt.plot(self.x_axis, y_axis)
    #         name = ctx.message.server.get_member(user).name
    #         print(name)
    #         names.append(name)
    #     if len(names) <= 5:
    #         plt.legend(names)
    #     plt.xlabel('Hour (UTC+0)')
    #     if normalized:
    #         plt.ylabel('activity %')
    #     else:
    #         plt.ylabel('messages posted')
    #     plt.title("Server activity")
    #     buf = BytesIO()
    #     plt.savefig(buf, format='png', dpi=500)
    #     buf.seek(0)
    #     await self.bot.send_file(ctx.message.channel, fp=buf, filename="suckmydick.png")


    # @activity.command(name="channel", pass_context=True)
    # async def _channel(self, ctx, *, normalized: str = []):
    #     #print("norm:_",normalized)
    #     if "norm" in normalized:
    #         normalized = True
    #     else:
    #         normalized = False
    #     #print("norm2", normalized)
    #     mentions = ctx.message.channel_mentions
    #     if not mentions:
    #         mentions = [x for x in ctx.message.server.channels]
    #     mentions = [x.id for x in mentions]
    #     fig, ax = plt.subplots()
    #     server_shit = self.globaldata[ctx.message.server.id]
    #     names = []
    #     for user, value in server_shit.items():
            
    #         if user not in mentions:
    #             continue
    #         print("user: {}, value: {}".format(user, value))
    #         userlist = []
    #         for pair in value.items():
    #             #if k == "server":
    #             #for pair in v:
    #             userlist.append(pair)
    #         userlist = [x[1] for x in sorted(userlist, key=lambda x: int(x[0]))]            
    #         normalizer = sum(userlist) or 1
    #         normalized_userlist = [x/(normalizer/100) for x in userlist]
    #         # print(userlist)
    #         # print(normalized_userlist)
    #         # print("normalized = ", normalized)
    #         y_axis = [userlist, normalized_userlist][normalized]
    #         #print(y_axis)
    #         plt.stackplot(self.x_axis, y_axis)
    #         name = ctx.message.server.get_channel(user).name
    #         #print(name)
    #         names.append(name)
    #     if len(names) <= 17:
    #         plt.legend(names)
    #     plt.xlabel('Hour (UTC+0)')
    #     if normalized:
    #         plt.ylabel('activity %')
    #     else:
    #         plt.ylabel('messages posted')
    #     #ax.set_xticks(np.arange(0, 24, 2))
    #     #plt.grid()
        
    #     plt.title(r'$\mathrm{Channel\ activity}$')
    #     buf = BytesIO()
    #     plt.savefig(buf, format='png')
    #     buf.seek(0)
    #     await self.bot.send_file(ctx.message.channel, fp=buf, filename="suckmydick.png")

            



    @commands.group(pass_context=True, name="postcount", aliases=['pc'], invoke_without_command=True)
    async def pc(self, ctx, member : discord.Member = None):        
        user = ctx.message.author if member is None else member
        a = self.c.execute('SELECT * FROM users WHERE (server=? AND id=?)', (ctx.message.server.id, user.id))
        a = a.fetchall()[0]
        await self.bot.say("**{}** has posted **{}** messages.".format(user.name, a[5]))

    @pc.command(name="top", pass_context=True)
    async def postcounttop(self, ctx):
        a = self.c.execute('SELECT * FROM users WHERE server=? ORDER BY postcount DESC LIMIT 20', (ctx.message.server.id,))
        a = a.fetchall()
        b = self.c.execute('SELECT SUM(postcount) AS "hello" FROM users WHERE server=?', (ctx.message.server.id,))
        b = b.fetchone()[0]
        print(b)
        post_this = ""
        server = ctx.message.server.id
        rank = 1
        for row in a:
            name = row[4].split(',')
            name = name[-1]
            post_this += ("{}. **{}:** {}\n".format(rank, name, row[5]))
            rank += 1
        post_this += "\n**{0}** posts by **{1}** chatters.".format(b,len([x for x in ctx.message.server.members]))
        em = discord.Embed(title="Current standings:", description=post_this, colour=0x14e818)
        em.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        await self.bot.say(embed=em)



    async def on_member_join(self, member):
        a = self.c.execute('SELECT * FROM users WHERE (id=? AND server=?)', (member.id, member.server.id))
        a = a.fetchall()
        if a != []:
            return
        roles = ','.join([x.id for x in member.roles if (x.name != "@everyone" and x.id != "232206741339766784")])
        self.c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (roles, member.server.id, None, member.id, member.display_name, 0, 0, 0))
        self.conn.commit()

    async def on_server_join(self, server):
        a = self.c.execute('SELECT * FROM servers WHERE id=?', (server.id,))
        a = a.fetchall()
        
        print(a)
        if a == []:
            self.c.execute('INSERT INTO servers VALUES (?, ?, ?, ?, ?)', (server.id, None, None, None, None))
            self.conn.commit()
        b = self.c.execute('SELECT * FROM logging WHERE server=?', (server.id,))
        b = b.fetchall()
        if b == []:
            self.c.execute('INSERT INTO logging VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', (server.id, 1, 1, 1, 1, 1, 1, 1, None))
            self.conn.commit()
        for member in server.members:
            a = self.c.execute('SELECT * FROM users WHERE (id=? AND server=?)', (member.id, member.server.id))
            a = a.fetchall()
            if a != []:
                continue
            roles = ','.join([x.id for x in member.roles if (x.name != "@everyone" and x.id != "232206741339766784")])
            self.c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (roles, member.server.id, None, member.id, member.display_name, 0, 0, 0))
            self.conn.commit()



    async def on_message(self, message):
        if (random.randint(1, 10000) == 1 and message.server.id == "207943928018632705"):
            legendaryRole = discord.utils.get(message.server.roles, name='Legendary')
            await self.bot.add_roles(message.author, legendaryRole)
            await self.bot.send_message(message.channel, "{} just received a legendary item: **{}**".format(message.author.mention, random.choice(legendaries)))
        self.fix_postcount(message)
        if message.content[:1] in ["?", "!", "§"]:
            return
        if message.author.id == "235148962103951360":
            return
        if message.channel.is_private:
            return
        if message.content == "":
            return
        log(message)
            
        self.c.execute("INSERT INTO messages VALUES (?, ?, ?, ?, ?, ?, ?)", (message.timestamp.timestamp(), message.timestamp.strftime(dt_format), message.clean_content, message.id, message.author.id, message.channel.id, message.server.id))
        self.conn.commit()
        if "carl" in message.content.lower():
            insensitive_carl = re.compile(re.escape('carl'), re.IGNORECASE)
            postme = insensitive_carl.sub('**__Carl__**', message.clean_content)
            await self.bot.send_message(discord.Object(id="213720502219440128"), "**{}** in **<#{}>**:\n{}".format(message.author.display_name, message.channel.id, postme))

def setup(bot):
    bot.add_cog(StatTrak(bot))