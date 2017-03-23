# Carl Bot
## Commands
args with an asterisk(\*) are optional

/ indicates that you can use either of these args (not for the same purpose, though)

Don't actually type out &lt;&gt;

|Command   |Aliases   |args   |example   |usage   |perms required   |
|---|---|---|---|---|---|
|!say   |   |&lt;message&gt;   |!say I'm sentient!   |Causes the bot to say what you put after !say   |none   |
|!bread   |   |&lt;@mention&gt;   |!bread @Carlg#3516   |Sends bread to the first mentioned user   |none   |
|!weather   |temp   |&lt;location&gt; |!weather stockholm   |Returns weather information for the specified location. Use !weather home &lt;location&gt; to set a home.   |none   |
|!roll   |dice   |&lt;sides&gt;\* &lt;rolls&gt;\*   |!roll 100   |Rolls a die, defaults to 6 sides and 1 rolls if nothing else is specified   |none   |
|!affix   |m+/affixes   |none   |!affix   |Returns current and future m+ affixes, updates automatically   |none   |
|!choose   |choice/pick   |comma separated   |!choose a b, c d   |Randomly selects one of your arguments   |none   |
|!tag   |   |+/+=/-/search &lt;tagname&gt; &lt;tagcontent&gt;   |!tag + xy xd   |See below   |none   |
|!retard   |   |&lt;@mention&gt;   |!retard @JayGarrick_#9390    |Lets the first mentioned user know they're retarded, use !retard top for highscores   |none   |
|!sc   |   |&lt;text&gt;   |!sc smallcaps only   |Returns your text as ꜱᴍᴀʟʟᴄᴀᴘꜱ    |none   |
|!spook   |   |&lt;@mention&gt;   |!spook @Carlg#3516   |Spooks the mentioned user!   |none   |
|!speak   |   |&lt;repeats&gt;\* OR &lt;@mention&gt;\*  |!speak 20   |Uses markov chains to generate sentences based on what you've said in the past, defaults to 3 repeats from yourself   |none   |
|!ignorechannel   |   |&lt;#channelmentions&gt;   |!ignorechannel #log   |Makes the bot ignore any commands in the mentioned channel (whitelisted users bypass this)   |WL   |
|!bio   |  |+/+=/&lt;@mention&gt;    |!bio @Kintark#0588    |Like tags but user specific and ONLY EDITABLE BY YOURSELF   |none, however WL perms are required for infinite bio length   |
|!sicklad   |   |&lt;@mention&gt;/top   |!sicklad @Kintark#0588   |Like !retard but good!   |none   |
|!8ball   |   |&lt;question&gt;\*   |!8ball Will anyone read this?   |Does the same thing as any 8ball command   |none   |
|!pickmyspec   |   |none   |!pickmyspec   |Randomly picks a wow spec   |none   |
|!pickmyclass   |   |none   |!pickmyclass   |Randomly picks a wow class   |none   |
|!pickmygold   |pickmyhero   |none   |!pickmygold   |Randomly picks an overwatch hero   |none   |
|!timer   |   |&lt;number&gt; &lt;time unit&gt;\* &lt;note&gt;\*   |!timer 3h24m make dinner   |Reminds you about &lt;note&gt; after the specified time. You can mix hours and minutes   |none   |
|!d   |   |&lt;word&gt;   |!d agoraphobia   |Looks up the definition of the word   |none   |
|!lvl   |   |&lt;lower level&gt; &lt;higher level&gt;   |!lvl 92 99   |Returns the xp difference between two osrs levels.   |none   |
|!g   |   |&lt;search query&gt;   |!g manhattan project   |Searches the web   |none   |
|!date   |current_year   |none   |!date   |Returns the date   |none   |
|!uptime   |   |none   |!uptime   |Checks to see how long the bot has been running for   |none   |
|!i   |info   |&lt;@mention&gt;   |!i @Carlg#3516  |Returns a lot of info about the mentioned user, click their username for a link to their picture    |none   |
|!avatar   |   |file upload/&lt;image link&gt;   |!avatar   |Changes the bot's avatar to the image specified   |Carl   |
|!ban   |   |&lt;@mention&gt;   |!ban @carl-bot#5002    |Fake bans the mentioned user   |none   |
|!asdban   |   |&lt;@mentions&gt;   |!asdban @carl-bot#5002   |Bans all mentioned users   |WL   |
|!mute   |   |&lt;@mentions&gt;   |!mute @Furple#1237   |Mutes all mentioned users   |WL   |
|!unmute   |   |&lt;@mentions&gt;   |!unmute @Furple#1237   |Unmutes all mentioned users   |WL   |
|!ping   |   |none   |!ping   |Checks to see if the bot is alive and how long it took to process the command   |none   |
|!postcount   |   |&lt;@mention&gt;\*/top\*   |!postcount @Carlg#3516   |Returns the postcount for the mentioned user   |none   |
|!nicknames   |   |&lt;@mention&gt;\*   |!postcount   |Returns the nicknames you've had in the past   |none   |
|!forceban   |   |&lt;ids&gt;   |!forceban 137267770537541632   |Bans the user regardless if they're in the server or not   |Carl   |
|!cts   |   |&lt;emoji1&gt;\* &lt;emoji2&gt;\*   |!cts :thinking: :thunkang:   |Crosses the streams   |none   |
|!m   |   |&lt;code&gt;   |   |Runs python code   |Carl   |
|!echo   |  |&lt;channel mention&gt; &lt;text&gt;   |!echo #general I'm alive!   |Like !say but sneakier   |none   |
|!wl   |   |&lt;@mentions&gt;   |!wl @Kintark#0588   |Adds the mentioned users to the whitelist   |Carl   |
|!bl   |   |&lt;@mentions&gt;   |!bl @Antibehroz#1567   |Adds the mentioned users to the blacklist. The bot ignores all commands from blacklisted users   |Carl   |
|!poll   |   |&lt;text&gt;\*   |!poll Is this a worthles feature?   |Makes a poll with reactions so that you can be biased   |none   |

## Tags
The tag command can be used for a number of things. Creating tags, adding to tags, removing tags, searching for tags, returning a list of all tags.

#### Creating tags
If no tag exists, you can use `!tag + tagname tagcontent`
#### Replacing tags
You replace tags the same way you create them. The bot will ask if you want to replace or append the contents, reply with r.
#### Appending tags
If you have a tag that you wish to append something to, use `!tag += tagname tagcontent`. There's no confirmation for this so make sure you've spelled everything right. (this will add a newline before the content)
#### Deleting tags
Use `!tag - tagname`
#### Searching for tags
Using `!tag search <query>` allows you to search for tags closely resembling your query. (`!tag search face` will return all tags with the word face)
#### Tag list
Use `!tag list` for a list of all tags
#### Using tags
Simply use `!<tagname>`
