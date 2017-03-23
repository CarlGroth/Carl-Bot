# Carl Bot
## Commands
args with an asterisk(\*) are optional

/ indicates that you can use either of these args (not for the same purpose, though)

Don't actually type out <>

|Command   |Aliases   |args   |example   |usage   |perms required   |
|---|---|---|---|---|---|
|!say   |   |<message>   |!say I'm sentient!   |Causes the bot to say what you put after !say   |none   |
|!bread   |   |<@mention>   |!bread @Carlg#3516   |Sends bread to the first mentioned user   |none   |
|!weather   |temp/temperature   |<location> |!weather stockholm   |Returns weather information for the specified location. Use !weather home <location> to set a home.   |none   |
|!roll   |dice   |<sides>\* <rolls>\*   |!roll 100   |Rolls a die, defaults to 6 sides and 1 rolls if nothing else is specified   |none   |
|!affix   |m+/affixes   |none   |!affix   |Returns current and future m+ affixes, updates automatically   |none   |
|!choose   |choice/pick   |comma separated   |!choose this option, this other option   |Randomly selects one of your arguments   |none   |
|!tag   |   |+/+=/-/search <tagname> <tagcontent>   |!tag + xy http://xyproblem.info/   |Adds, appends, deletes, searches for tags. Tags are strings of text with an associated name   |none   |
|!retard   |   |<@mention>   |!retard @JayGarrick_#9390    |Lets the first mentioned user know they're retarded, use !retard top for highscores   |none   |
|!sc   |   |<text>   |!sc smallcaps only   |Returns your text as ꜱᴍᴀʟʟᴄᴀᴘꜱ    |none   |
|!spook   |   |<@mention>   |!spook @Carlg#3516   |Spooks the mentioned user!   |none   |
|!speak   |   |<repeats>\* OR <@mention>\*  |!speak 20   |Uses markov chains to generate sentences based on what you've said in the past, defaults to 3 repeats from yourself   |none   |
|!ignorechannel   |   |<#channelmentions>   |!ignorechannel #meme-archive   |Makes the bot ignore any commands in the mentioned channel (whitelisted users bypass this)   |WL   |
|!bio   |  |+/+=/<@mention>    |!bio @Kintark#0588    |Like tags but user specific and ONLY EDITABLE BY YOURSELF   |none, however WL perms are required for infinite bio length   |
|!sicklad   |   |<@mention>/top   |!sicklad @Kintark#0588   |Like !retard but good!   |none   |
|!8ball   |   |<question>\*   |!8ball Will anyone read this?   |Does the same thing as any 8ball command   |none   |
|!pickmyspec   |   |none   |!pickmyspec   |Randomly picks a wow spec   |none   |
|!pickmyclass   |   |none   |!pickmyclass   |Randomly picks a wow class   |none   |
|!pickmygold   |pickmyhero   |none   |!pickmygold   |Randomly picks an overwatch hero   |none   |
|!timer   |   |<number><time unit>\* <note>\*   |!timer 3h24m make dinner   |Reminds you about <note> after the specified time. You can mix hours and minutes   |none   |
|!d   |   |<word>   |!d agoraphobia   |Looks up the definition of the word   |none   |
|!lvl   |   |<lower level> <higher level>   |!lvl 92 99   |Returns the xp difference between two osrs levels.   |none   |
|!g   |   |<search query>   |!g manhattan project   |Searches the web   |none   |
|!date   |current_year   |none   |!date   |Returns the date   |none   |
|!uptime   |   |none   |!uptime   |Checks to see how long the bot has been running for   |none   |
|!i   |info   |<@mention>   |!i @Carlg#3516  |Returns a lot of info about the mentioned user, click their username for a link to their picture    |none   |
|!avatar   |   |file upload/<image link>   |!avatar http://i.imgur.com/3hVmkGL.png   |Changes the bot's avatar to the image specified   |Carl   |
|!ban   |   |<@mention>   |!ban @carl-bot#5002    |Fake bans the mentioned user   |none   |
|!asdban   |   |<@mentions>   |!asdban @carl-bot#5002 @Carlg#3516   |Bans all mentioned users   |WL   |
|!mute   |   |<@mentions>   |!mute @Furple#1237   |Mutes all mentioned users   |WL   |
|!unmute   |   |<@mentions>   |!unmute @Furple#1237   |Unmutes all mentioned users   |WL   |
|!ping   |   |none   |!ping   |Checks to see if the bot is alive and how long it took to process the command   |none   |
|!postcount   |   |<@mention>\*/top\*   |!postcount @Carlg#3516   |Returns the postcount for the mentioned user   |none   |
|!nicknames   |   |<@mention>\*   |!postcount   |Returns the nicknames you've had in the past   |none   |
|!forceban   |   |<ids>   |!forceban 137267770537541632   |Bans the user regardless if they're in the server or not   |Carl   |
|!cts   |   |<emoji1>\* <emoji2>\*   |!cts :thinking: :thunkang:   |Crosses the streams   |none   |
|!m   |   |<code>   |!m self.postcount["235148962103951360"]   |Runs python code   |Carl   |
|!echo   |  |<channel mention> <text>   |!echo #general I'm alive!   |Like !say but sneakier   |none   |
|!wl   |   |<@mentions>   |!wl @Kintark#0588   |Adds the mentioned users to the whitelist   |Carl   |
|!bl   |   |<@mentions>   |!bl @Antibehroz#1567   |Adds the mentioned users to the blacklist. The bot ignores all commands from blacklisted users   |Carl   |
|!poll   |   |<text>\*   |!poll Is this a worthles feature?   |Makes a poll with reactions so that you can be biased   |none   |

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
