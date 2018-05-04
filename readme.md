# Commands

How do I read this? 

Args are what goes after the command, in `!temp home stockholm` "stockholm" is the args, in `!tag create test Hello World` "test" is the first arg and "Hello world" is the second. If an argument is in [square brackets] it means that it's optional.

An alias is another way to call a command. For instance, `temp` and `weather` function identically. If the command is in **bold**, that means it requires "manage server" to be executed.



## Bot Prefix

|Name|Aliases   |Args   |Example   |Usage
|---|---|---|---|---|
|!prefix   |--   |--   |--   |Lists the affixes currently in use by the server   |
|**!prefix add**   |--   |prefix   |!prefix add "sudo "   |Adds a prefix to be used by the bot (limited to 10) **NOTE** if you want a two word prefix or a prefix with a space after it or an emoji you **must** use quotes, this is a discord limitation and can't be fixed   |
|**!prefix remove**   |delete   |prefix   |!prefix remove !   |Removes a prefix, same limits as !prefix add applies here, can't remove mentioning the bot.   |
|**!prefix clear**   |--   |--   |--   |Removes all prefixes except mentioning the bot. This (obviously) means you need to mention the bot to register more prefixes   |

## Logging

[Here's a screenshot showing how logging looks](https://i.imgur.com/bD5woF0.png)

|Name|Aliases   |Args   |Example   |Usage
|---|---|---|---|---|
|**!set log**  |--   |channel   |!set log #bot_logs   |Choose where the bot logs things to    |
|**!set twitch**   |--   |channel   |!set twitch #couch   |Choose which channel the bot announces twitch streams to   |
|**!set bot**   |--   | channel   |!set bot #bot-abuse   |Choose which channel restricted commands/tags go to   |
|**!config**   |--   |--   |--   |Shows what the bot logs, what channels it doesn't log from, channels it ignores commands from, disabled commands, banned users, logging channel, twitch channel and prefixes   |
|**!log avatar**  |--   |--   |--   |Sets logging avatar changes to true or false depending on what it currently is   |
|**!log edit**  |--   |--   |--   |Sets logging message edits to true or false   |
|**!log role**  |--   |--   |--   |Sets logging role updates to true or false   |
|**!log delete**  |--   |--   |--   |Sets logging message deletions to true or false   |
|**!log ban**  |--   |--   |--   |Sets logging server bans to true or false   |
|**!log join**  |--   |--   |--   |Sets logging members joining/leaving to true or false depending on what it currently is   |
|**!log name**  |--   |--   |--   |Sets logging name changes to true or false depending on what it currently is   |
|**!log ignore**   |--   |[channel]   |--   |Makes the bot ignore message edits/deletions from the channel. This is useful if you have a public log but private channels.   |
|**!log unignore**   |--   |[channel]   |--   |Unignores previously ignored channels   |

## Bot Moderation

While Carlbot doesn't provide any commands to ban/purge/mute users, it offers exceptional tools to prevent abuse and restrict commands from troublemakers.

|Name|Aliases   |Args   |Example   |Usage
|---|---|---|---|---|
|**!ignore**   |--   | [channel] [command] [subcommand]   |!ignore #general temp home   |If no channel is specified, the current channel is ignored. If no command is specified, the mentioned channel will be ignored. If only a command is supplied, the command and all of its subcommands will be ignored in the specified channel. If everything is supplied, only the subcommand will be ignored in the specified channel. Mod (manage server) will bypass all of these.   |
|**!ignore server**   | --  |--   |--   | This will ignore all channels and is future-proof.    |
|**!ignore all**   |--   |[command] [subcommand]   |!ignore all pc top   |This is equal to typing !ignore channel command subcommand in all channels the bot can see, useful if you want to ignore a command in all channels except for one. This will not work for channels created in the future. If the command is already ignored in a channel, this will unignore it.  |
|**!unignore all**   | --  | --   | --  | Unignores all channels (this does not take ignored commands into account)   |
|**!disable**   |--   | command [subcommand]  | !disable pc top  |This really disables the command globally from the server, not even manage server bypasses this.    |
|**!enable**   |--   |--   |!enable pc top   |Enables a previously disabled command.   |
|**!enable all**   |--   |--   |--   |Sets all commands to enabled.   |
|**!disable all**   |--   |--   |--   |Sets all commands to disabled.  |
|!enable list | disable list | -- | -- | Shows all enabled/disabled commands.|
|**!plonk**   |--   |member [command][subcommand]   |!plonk @Carl#0080 tag create   |This works almost exactly like !ignore but for users instead. If no command is specified, the user is banned from using the bot completely.   |
|**!unplonk**  |--   |member [command][subcommand]    |!unplonk @Carl#0080   |Unbans the user from using the bot   |
|!plonks   |--   |--   |--   |Displays all plonked users.   |
|**!restrict**   |--   |command [subcommand]   |!restrict define   |This requires a bot channel to utilize. Makes it so that if the command is used outside of the bot channel, the bot will ping the user in the botchannel and give the results there instead.   |
|**!unrestrict**   |--   |command [subcommand]   |!unrestrict d   | Unrestricts it. Like all commands where you pass in a command, aliases work just as well.   |

## Tags

Tags can be complicated, see [the full section](#tags-1) for a more thorough explanation with advanced usage.

|Name|Aliases   |Args   |Example   |Usage
|---|---|---|---|---|
|!tag   |tag get   |lookup   |!classdiscords   |This is how you get tags after they're saved.   |
|!tag create   |add, +    |tagname tagcontent   |!tag + test Hello world   |Makes a tag named test with the content Hello world.   |
|**!tag ++**   |--   |A pastebin link   |--   | Since tags can have an output shorter than their length, using !tag ++ allows you to make them  |
|!tag append   |+=   |tagname tagcontent   |!tag += test and my mom   |Adds tagcontent to an already existing tag   |
|!tag alias   | a  |alias tagname   |!tag alias testing test   | Creates a link to an already existing tag, changes made to the original tag means the aliased tag will also be changed. The name you want for the alias is the first argument, the already existing tag is the second.  |
|!tag edit   |e   |tagname tagcontent   |!tag e test bye world   |Edits the content of an already existing tag.   |
|**!tag nsfw**   |--   |tagname   |!tag nsfw test   |Restricts the tag so that it can only be used in channels marked as nsfw   |
|**!tag restrict**   |--   |tagname   |!tag restrict test   |To prevent big tags cluttering your chatty channels, this will make the bot post the content in the bot-channel and ping the author.   |
|**!tag mod**   |--   |tagname   |!tag mod test   |Makes it so that only mods can use the command (manage server)   |
|!tag stats   |--   |[member]   |!tag stats @Carl#0080   |Shows information about the servers tags (uses, top 3, total number of tags). If you mention someone, it will show their tags instead.   |
|!tag info   |--   | tagname  |!tag info test   | Shows some stats collected about the tag, uses, creation date, last update, owner.  |



## Highlights
Inspired by highlight bot, Carlbot now also does highlighting. Highlighting means you will receive a message when your keyword is said in chat. The matching is approximate and works really similarly to discord search (basically, if you search your keyword in discord search, you will find messages that would trigger the highlight, roughly speaking). It will only notify you if you haven't posted anything in chat for the past 10 minutes (prone to change). Generally doesn't seem to have too many false positives.

|Name|Aliases   |Args   |Example   |Usage
|---|---|---|---|---|
|!hl add   |+   |word   |!hl add carl    |Adds a word that will notify you. **IMPORTANT:** The bot tries to guess when you're aware of what's being typed and won't notify you if you've typed in the past 10 minutes, to see if your highlights work, please use `!hl match <sentence>`   |
|!hl match| m |Sentence | !hl match carl is cute | Tests a sentence and sees which if any words would notify you.
|!hl block   |--   |member or channel   |!hl block @Kintark#0588   |Messages sent in this channel/from this user won't notify you.   |
|!hl unblock   |--   | member or channel  | !hl unblock #general  | Unblocks the user/channel   |
|!hl show   |--   | --  | --  |  Shows your words as the bot sees them, if your words look wrong ("barri" instead of "barry" for instance) it's because of [word stemming](https://en.wikipedia.org/wiki/Stemming) |
|!hl clear   |--   | --  | --  | Removes all of your highlighted words  |
|!hl del   |--   | word  | !hl clear math  | Removes a word from your highlighted words  |

## Roles
Very typo proof.

|Name|Aliases   |Args   |Example   |Usage
|---|---|---|---|---|
|!role    |--   |role   |!role python   |This will add the role to you if the role is whitelisted. The command is typo proof so "rouge" will match with "rogue".    |
|!role whitelist   |add, +, -, del, remove, delete   |role   |!role add python   |Adds the role to the whitelist so anyone can assign it to themselves. For this command to work both the bot and the command user needs to be able to assign the role to someone.   |
|**!role unique**   |--   |--   |--   |Makes it so that any roles given will replace any other whitelisted roles. This can be useful for servers where it doesn't make any sense for someone to have multiple roles.   |
|!roles   |--   |--   |--   |Shows all whitelisted roles   |
|!role alias | -- | new_alias existing_role | !role alias shaman farseer | Aliasing roles is useful for servers with complicated role names. For instance, one wow server utilizing this command has a role called "Farseer" corresponding to the shaman class in wow. Using the command in the example allows people to get the "Farseer" role by typing "!role shaman".

### Automatic Roles

|Name|Aliases   |Args   |Example   |Usage
|---|---|---|---|---|
|!autorole | autoroles | -- | -- | Shows which roles will be added upon joining and if the bot will readd roles when someone leaves and rejoins the server
|!autoroles readd | reassign |-- |-- | Turns reassigning roles on/off
|!autorole add | -- | role | !autorole add peon | Autoroles are roles that are given to the user upon joining the server. |
|!autorole remove | -- | role | !autorole remove admin | -//-|

## Welcome and Farewell messages
|Name|Aliases   |Args   |Example   |Usage
|---|---|---|---|---|
|**!greet** | -- | text | !greet Welcome $mention, we've been expecting you| Sets up a welcome message that will be sent when a new user joins.
|**!farewell** | -- | text | !farewell Goodbye $user, maybe it wasn't meant to be... |Like !greet but for people leaving
|**!banmsg** |--|text | !banmsg **$user** just got blown the fuck out| Like !greet but for people getting banned

All these messages will be sent to the channel saved with `!set welcome`. Use a command without any text to remove the message. Supports the following variables:

`$mention` - Pings the user

`$user` - The name of the user

`$nick` - The display name of the user (not available for banmsg)

`$server` - The name of the server

`$id` - The ID of the user

`$discrim` - The last four digits (0080 for "Carl#0080") does **not** include the hash sign.

Also supports `#{random lists, separated by commas}` and `m{1 + 1} math blocks` not sure when you'd ever want a math block but random lists are pretty useful.



## Timers/reminders

|Name|Aliases   |Args   |Example   |Usage
|---|---|---|---|---|
| !rm  |reminder, remindme, timer   |time message OR message time   |!rm 1d23h pick up the next mission on your hunter. !rm set fire to the local orphanage tomorrow at noon.   | Sets up a reminder to send a message reminding you about the thing. If you use a human time like "at noon" it uses UTC.   |
|!rm mine   |--   |--   |--   |Shows your reminders.   |
|!rm clear   |del, delete, remove, purge, -   |--   |--   |Removes all of your reminders.   |
|!sub   |!rm sub   | ID   |!sub 97   |Copies a reminder someone else made. This means you own the reminder, that person deleting their reminder will have no impact.   |

## Utilities

|Name|Aliases   |Args   |Example   |Usage
|---|---|---|---|---|
|!define   |d   |word   |!define well   |Shows the oxford dictionary's definition for the word. Note: due to the length of some definitions it might be a good idea to restrict this command to prevent abuse.   |
|!wolfram   |wa   |input   |!wa e ^ (pi * i) + 1   |This is similar to going to wolframalpha and entering the text yourself. Doesn't support complicated answers.   |
|!choose   |pick, choice, select   |choices   |!choose go to sleep, play overwatch   |Picks one of your specified arguments. Use commas for multiple words.   |
|!activity| -- | [day/week/month/year] | !activity week| Defaults to month, shows the 25 most active members by postcount for the specified timespan (that the bot has seen)
|!urbandictionary   |!ud   |word   |!ud cleveland steamer   |Returns the urbandictionary definition for your word. @everyone proof. (looking at you, b1nzy)   |
|!info   |i   |[member]   |!i @Carl#0080   |Returns Name, last 5 nicknames, id, postcount (that the bot has seen), creation date, server join date  and some cool information related to these  |
|!temp   |weather   |[city]   |!weather stockholm   |EXTREMELY typo proof. If no city is specified, it will give you info for your set home. If used for the first time, that city will be set as your home.   |
|!temp home   |--   |city   |!temp home tampa   |Lets you set a city as your home for !temp to default to.  |
|!nicknames   |nicks   |--   |--   |Shows you your nicknames history, duplicates are moved to the end of the list. The names are ordered from oldest to newest.    |
|!dice   |--   |[sides] [rolls]   |!dice 6   |Rolls a [sides] sided die [rolls] times. Defaults to 6 sides and 1 roll.  |
|!roll   |--   |[[lower-]upper]   |!roll 100-1100   |Works just like in wow, defaults to 1 to 100. Changing just one number will change the upper bound.   |
|!flip | coin | -- | -- | Flips a coin|
|!google | g | query | !g umami wiki | Like googling, safesearch is set to medium.|




## Fun/silly/useless

|Name|Aliases   |Args   |Example   |Usage
|---|---|---|---|---|
|!postcount |pc| [member]| !pc @Carl#0080| Shows the amount of messages the bot has seen the member post.|
|!postcount top| -- | -- | -- | Shows the all time 10 most active members as far as the bot's concerned.|
|!ae   |aesthetics   |text   |!ae 600 iq   |Returns your text as fullwidth. The example would return "６００ｉｑ"   |
|!sc   |smallcaps   |text   |!sc neumann   |Returns your text as smallcaps. The example would return "ɴᴇᴜᴍᴀɴɴ"   |
|!8ball   |--   |--   |!8ball will anyone ever love me?   |It's like any other 8ball command on discord. Annoying, useless and unreasonably popular.   |
|!echo | -- | message | !echo #general Is this enough to pass the turing test? | Makes the bot say the message in the mentioned channel|
|!poll | -- | question | !poll should I sleep? | Creates a yes/no poll where you vote with reactions|
|!quickpoll | -- | question and answers | !quickpoll "best game?" wow overwatch "only losers play games" | Use double quotes for more than just one word. The first arg is the question, all after that are individual answers.
|!speak | -- | [member] | !speak @Yenni#2794 |Uses [Markov chains](https://github.com/jsvine/markovify) to generate sentences based on what that person has said in the past.

## Starboard

Star messages, have them posted to a channel. It's a fun way to save funny/interesting messages in a place where everyone can see them.

|Name|Aliases   |Args   |Example   |Usage
|---|---|---|---|---|
|**!starboard**   |--   |[name]   |!starboard meme-archive   |Creates the starboard.   |
|**!star limit**  |--   |number   |!star limit 3   |Sets the amount of stars required for a post to get posted to the starboard   |
|!star stats   |--   |[member]   |!star stats @Carl#0080   |Shows some information about the server's or user's star giving patterns.  |
|!star top   |--   |--   |--   |Returns the most starred posts |
|!star nsfw   |--   |--   |--   |Toggles nsfw stars. With this enabled, posts starred in channels marked as nsfw will embed |
|!star self   |--   |--   |--   |Toggles being able to star your own posts |


## Animals

|Name|Aliases   |Args   |Example   |Usage
|---|---|---|---|---|
|!cat   | --  | --  | --  | Gives you a random cat. All of these commands use a database of images collected by scraping reddit, this means you won't get the same 150 dogs that most bots offer through that one popular website. Currently I have about 15000 animals saved.   |
|!dog   | --  | --  |   --| ^  |
|!aww   | --  |--   |  -- | ^  |
|!catbomb   | --  | --  | --  | Gives you 10 links instead of just one, only use this if you LOVE animals!   |
|!dogbomb   |--   |--   | --  | ^  |
|!awwbomb   | --  |--   | --  | ^  |

## Twitch

### Adding a twitch stream

|Name|Aliases   |Args   |Example   |Usage
|---|---|---|---|---|
|**!twitch**   | --  | name [alias]  | !twitch azortharion azor | Adds the user with the alias. In the example given, the stream announcement will say "azor is now live"   |
|!twitch list   | --  | --  |   --| Shows all registered streamers and when they were last online  |
|**!twitch own**   | ownership  | --  |   --| With this enabled, users can't have the streams they themselves added removed by non-mods, this is useful if you want to allow users to add their own streams to a server  |
|**!twitch mod**   | modonly  | --  |   --| If this is disabled, any user can add a stream of their choice  |
|**!twitch limit**   | --  | number  |  !twitch limit 2  | Restricts how many streams non-mods are allowed to add  |

## Blizzard

|Name|Aliases   |Args   |Example   |Usage
|---|---|---|---|---|
|!rtb|-- |-- |--|works like the wow spell did before 7.2.5 (6 buffs maximum)
|!armory|!pug   |name realm region|!armory joshpriest tarren-mill eu| Looks up information about the character and its progress
|!pickmyspec|--|--|--|Picks a spec at random (any class)
|!pickmyclass  |--   |--   |--   |Picks a class at  random   |
|!invasion  |!invasions   |--   |--   |Shows time until the next broken isles invasion for both EU and NA   |
|!rm &lt;region&gt;  |--   |eu or na   |!rm eu   |Shortcut for creating a reminder to remind you when the invasion is up for that region next (if one is live, it picks the one after the current one)   |
|!affix  |!m+, !affixes   |--   |--   |Shows which affixes are live for EU/NA (separates when they're different) and which ones are active in the coming weeks.   |
|!w | wowhead | search | !w jeeves | This is like searching on wowhead.


## Boring bot-related commands

|Name|Aliases   |Args   |Example   |Usage
|---|---|---|---|---|
|!invite   |--   |--   |--   | Gives you the invite link for the bot.  |
|!botpermissions   |--   |--  |--   |Shows the permissions the bot currently has in the channel the command was used in   |
|!permissions  |--   |[member]   |!permissions @Carl#0080   |Shows the permissions you have in the channel the command was used in. This means even server owners won't have "connect" perms since it'll always be used in a text channel.   |
|!about   |stats   |--   |--   |Shows some stats related to the bot, mostly for bragging rights.   |
|!charinfo   |--   |character(s)   |!charinfo :thinking:   |Shows some nerdy unicode stats related to the character. Only real use I've had for this was to find out what some weird characters really are.   |
|!serverinfo   |--   |--   |--   |Displays some interesting stuff about the servers and its members.   |
|!uptime   |--   |--   |--   |How long the bot has been up for.   |
|!socketstats | -- | -- | -- | The events the bot has received from the websocket |
|!commandstats | -- | -- | -- | How many times each commands have been used since the bot was started |





# Tags

Tags are easy to use, but very powerful. With some ingenuity you can create your own, dynamic commands. To aid with this, dynamic "blocks" can be added. It is for instance entirely possible to create an 8ball command, a !hug command and many other things using just tags.

As of writing this, these blocks are:

**Random lists** `#{comma, separated,#{nested args}}`

**Math blocks** `m{1 + 1 / (3 ^ 9)}`

**React blocks** `react{:regional_indicator_f:}`

   This will react to the post with the emojis placed inside the brackets
   
   Unsure what this could be used for? `!tag create doubt react{:regional_indicator_x:} https://i.imgur.com/EacBuLR.png`

**50/50 blocks** `?{Will anyone see me?}`

**command blocks** `c{temp stockholm}`
	
Do you think that `!info` really should be called `!whois`? with command blocks you can do just that

`!tag + whois c{info $args}`

Maybe you think speak defaulting to 5 uses is an idiotic design choice, simply do

`!tag + betterspeak c{speak 20 $args}`

Important to note is that command tags are effectively not tags

**variable assignment** `!{foo=This can be anything}`

In addition to these blocks, it also comes with a few default arguments.  These are:

`$unix` - Unix time, useful for math blocks

`$uses` - The amount of times the tag has been used

`$args` - The words after the tag invocation. `!foo bar baz` means $args=bar baz

`$commandargs` - The words after the tag invocation, unlike `$args` this includes mentions in the `<@id>` format (useful for command blocks)

`$authorid` - The ID of the person using the command, useful for command blocks

`$userid` - The ID of the first mention or author if there aren't any

`$user` - Nickname of the first mentioned user or author if there aren't any mentions

`$channel` - The name of the channel mentioned or the channel the command was used in

`$server` - The name of the server

`$mention` - The nickname of the first mentioned user or NOTHING if there aren't any mentions

`$nuser` - The _name_ of $user

`$nmention` - The _name_ of $mention

`$nauthor` - The _name_ of $author

`$1 $2 $3 etc` - Like $args but only the first, second, third word etc. `!foo bar baz` means $1=bar


Still not sure how to use this? [See this link for some interesting and funny tags people have created using TagScript](https://pastebin.com/raw/fbmZ5PjR)
