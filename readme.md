[![Discord Bots](https://discordbots.org/api/widget/235148962103951360.svg)](https://discordbots.org/bot/235148962103951360)

[Click me to invite Carl-bot to your server](https://discordapp.com/oauth2/authorize?client_id=235148962103951360&scope=bot&permissions=470150352)

For help and questions -> [Join the bot support server](https://discord.gg/DSg744v)



# Commands

How do I read this? 

Args are what goes after the command, in `!temp home stockholm` "stockholm" is the args, in `!tag create test Hello World` "test" is the first arg and "Hello world" is the second. If an argument is in [square brackets] it means that it's optional.

An alias is another way to call a command. For instance, `temp` and `weather` function identically. If the command is in **bold**, that means it requires "manage server" to be executed.



## Bot Prefix

|Name|Aliases   |Args   |Example   |Usage
|---|---|---|---|---|
|!prefix   |--   |--   |--   |Lists the affixes currently in use by the server   |
|**!prefix add**   |--   |prefix   |!prefix add "sudo "   |Adds a prefix to be used by the bot (limited to 10) **NOTE** if you want a two word prefix or a prefix with a space after it or an emoji you **must** use quotes, this is a discord limitation and can't be fixed   |
|**!prefix set** | -- | prefix | !prefix set "haha " | Sets the specified prefix to be the ONLY prefix in the server
|**!prefix remove**   |delete   |prefix   |!prefix remove !   |Removes a prefix, same limits as !prefix add applies here, can't remove mentioning the bot.   |
|**!prefix clear**   |--   |--   |--   |Removes all prefixes except mentioning the bot. This (obviously) means you need to mention the bot to register more prefixes   |


## Reaction roles

[Carlbot finally offers reaction roles, this is how they can look](https://i.imgur.com/tPNpyYN.png)

|Name|Aliases   |Args   |Example   |Usage
|---|---|---|---|---|
|**!rr make**| setup| --|--|Starts the interactive setup to get you started with reaction roles|
|rr show| display| --| --| Shows the emoji-role pairs and their associated message id, useful for rr add|
|**!rr edit**| --| message_id title \| description |!rr edit 23094823094823490 Games \| Click on the games you want to be notified by|Edits the title and description, works like it does in the make command|
|**!rr remove**| rm del| role|!rr remove fortnite|Removes an emoji-reaction pair from the specified bot message (and more importantly, from the database)|
|**!rr add**| create| message_id emoji role|!rr add 1238901239812 :angel: pure|Adds the emoji-role pair to the message and the database. **NOTE:** This message id can belong to other people than carlbot, and the same emoji can be used for different messages for different roles (useful for regional roles)|
|**!rr color**|colour|message_id color|!rr color #00ee28|Changes the accent color of the specified  bot message|
|**!rr addmany** |-- | message_id emoji role... | !rr addmany 1238901239812 :angel: pure :poop: fortnite :grin: league of legends | **SEPARATE EACH EMOJI-ROLE PAIR WITH A NEWLINE** Works like **!rr add** except it adds more than one role at a time |
|**!rr unique** | -- | messge_id | !rr unique 123817349589 | Marks a message as 'unique' meaning a member can only claim one role from this message at a time, this works per message. Automatically removes the old reactions for you|
|**!rr link** | -- | base_message_id linked_message_id | !rr link 2389742349827 1239179273791283 | By linking two messages together, only one role from either message can be self-assigned. If you have 30 color roles for instance, linking the two messages together (since the limit is 20/message) allows a smooth, user-friendly experience when picking up roles. More than two messages can be linked together by using the same command a second time. |
|**!rr unlink** | -- | message_id | !rr unlink 2389742349827 | This breaks apart the entire group created by `!rr link` This means if you had three messages linked together, none of them will be after using this command. |
|**!rr aio** | -- | channel color "text \| description" emoji role | !rr aio #reaction eeaaee "hello there \| this is a description" :red: hello :purple: there | **SEPARATE EACH EMOJI-ROLE PAIR WITH A NEWLINE** This is meant for power users who wish to create everything with just one command. The title and description have to be enclosed in double quotes. |
|**!rr aiou** | -- | -- | -- | Works like **!rr aio** but also marks the message as unique |

 
You add roles to yourself by clicking on the reactions, you need manage server to make the reaction message and both you and the bot has to be able to assign the roles (it will warn you about this while creating it)

To remove a bot message, simply delete the message like you would delete any other message, it's handled by the bot automatically.

## Moderation
|Name|Aliases   |Args   |Example   |Usage
|---|---|---|---|---|
|**!purge**   |-- | howmany   | !purge 200  | Purges the last howmany messages.   |
|**!purge bot** | -- | prefix howmany | !purge ? 20 | Purges the bot messages (and messages with the specified prefix) from the last howmany messages.|
|**!purge contains** | -- | substring | !purge contains thanos | Purges messages containing the substring |
|**!purge user** | -- | user howmany | !purge @Carl#0001 20 | Purges messages from the user |
|**!purge all** | -- | howmany=100 | !purge all 13 | Purges the last howmany messages |
|**!purge embeds** | -- | howmany=100 | !purge embeds 12 | Purges the last howmany messages with embeds |
|**!purge emoji** | -- | howmany=100 | !purge emoji | Purges the last howmany messages containing custom emoji |
|**!purge files** | -- | howmany=100 | !purge files | Purges messages with attachments |
|**!purge images** | -- | howmany=100 | !purge images | Purges messages with attachments or embeds |
|**!purge links** | -- | howmany=100 | !purge links | Purges messages with links |
|**!purge reactions** | -- | howmany=100 | !purge reactions | Purges reactions from messages |
|**!ban** | forceban hackban | member or ID [reason] | !ban 102130103012 raiding | Bans the member from the server. This works even if the member isn't on the server. If you supply a reason, it will show up in the modlogs and in discord's built in audit log |
|**!muterole** | -- | Role | !muterole kids table | Selects a role to use for the mute command |
|**!muterole create** | -- | [name] | !muterole create shhh | Creates a new role, adds the role as a channel override with "send messages" turned off for all text channels and sets it as the server's muterole.
|**!mute** | -- | user [time [reason]] | !mute @Carl#0001 20h45m spamming | Mutes a member (using the muterole, read above) for the specified time. If no time is given, it will mute indefinitely. If a reason is given, it shows up in the mod logs.|
|**!unmute** | -- | user | !unmute @Carl#0001 | Unmutes a member |
|**!kick** | -- | user [reason] | !kick @Carl#0001 racism | Kicks a member. Reason shows up in the modlogs and in audit logs |
|**!softban**| -- | user [reason] | !softban @Carl#0001 go away | Bans and immediately unbans a member to clear 48 hours of message history. |

### Anti-raid and mentionspam
|Name|Aliases   |Args   |Example   |Usage
|---|---|---|---|---|
|**!mentionspam**   |-- | count   | !mentionspam 5  | Enables the bot to automatically punish mentionspammers. By default this action is banning, but it can be changed using the next command.  |
|**!mentionspam action** | -- | action | !mentionspam action ban | Action is one of kick, mute, ban or delete. Delete just deletes the message, which is actually sort of counterproductive. |
|**!mentionspam ignore** | -- | channels | !mentionspam ignore #announcement | Although mods are excluded from the mentionspam prevention, using this allows your members to spam mentions in certain channels, if you so desire. |
|**!mentionspam unignore** | -- | channels | !mentionspam ignore #general #announcements | Undoes what **!mentionspam ignore** does. | 
|**!raid basic** | -- | -- | -- | Basic antiraid. Sets verification level to table flip and deletes messages from members who joined less than 30 minutes ago. |
|**!raid strict** | -- | -- | -- | Strict antiraid kicks members who joined less than 30 minutes ago whenever they send a message or join a voice channel. |
|**!raid insane** | -- | -- | -- | Insane antiraid is strict but kicked members who rejoin will immediately be kicked. |

### Mod logs
[Useful for transparency and organizing](https://i.imgur.com/QXEG0Cr.png)


|Name|Aliases   |Args   |Example   |Usage
|---|---|---|---|---|
|**!modlog create** | -- | name | !modlog create auditlog | Creates a modlog where moderation actions will be logged.|
|**!modlog set** | -- | #channel | !modlog set #modlog | Sets an already existing channel to send action to (make sure the bot has the permissions requried to post in the channel)|
|**!modlog clear** | -- | -- | -- | Makes the bot stop logging actions to the channel|
|**!modlog from** | -- | user | !modlog from @Carl#0001 | Retrieves all infractions for a member with the responsible moderator. |
|**!reason** | -- | id reason | !reason 17 Spamming nazi imagery | Sets a reason for a modlog entry, useful for cases where you either banned manually or forgot to specify a reason |

## Logging

[Here's a screenshot showing how logging looks](https://i.imgur.com/bD5woF0.png)

|Name|Aliases   |Args   |Example   |Usage
|---|---|---|---|---|
|**!set log**  |--   |channel   |!set log #bot_logs   |Choose where the bot logs things to    |
|**!set twitch**   |--   |channel   |!set twitch #couch   |Choose which channel the bot announces twitch streams to   |
|**!set bot**   |--   | channel   |!set bot #bot-abuse   |Choose which channel restricted commands/tags go to   |
|**!config**   |--   |--   |--   |Shows what the bot logs, what channels it doesn't log from, channels it ignores commands from, disabled commands, banned users, logging channel, twitch channel and prefixes   |
|**!log embed** | -- | -- | -- | Toggles between the standard logs with embeds and the old text-based logging|
|**!log discord**| -- | -- | -- | Toggles logging discord invites posted |
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

Carlbot offers exceptional tools to prevent abuse and restrict commands from troublemakers.

|Name|Aliases   |Args   |Example   |Usage
|---|---|---|---|---|
|**!ignore**   |--   | [channel] [command] [subcommand]   |!ignore #general temp home   |If no channel is specified, the current channel is ignored. If only a command is supplied, the command and all of its subcommands will be ignored in the specified channel. If everything is supplied, only the subcommand will be ignored in the specified channel. Mod (manage server) will bypass all of these.   |
|**!ignore server**   | --  |--   |--   | This will ignore all channels and is future-proof.    |
|**!ignore all**   |--   |[command] [subcommand]   |!ignore all pc top   |This is equal to typing !ignore channel command subcommand in all channels the bot can see, useful if you want to ignore a command in all channels except for one. This will not work for channels created in the future. If the command is already ignored in a channel, this will unignore it.  |
|**!unignore** | -- | [channel] [command] | !unignore #general temp | Reverses what !ignore does |
|**!unignore all**   | --  | --   | --  | Unignores all channels (this does not take ignored commands into account)   |
|**!disable**   |--   | command [subcommand]  | !disable pc top  |This really disables the command globally from the server, not even manage server bypasses this.    |
|**!enable**   |--   |--   |!enable pc top   |Enables a previously disabled command.   |
|**!enable all**   |--   |--   |--   |Sets all commands to enabled.   |
|**!disable all**   |--   |--   |--   |Sets all commands to disabled.  |
|**!enable mod** | -- | -- | -- | Enables all moderation commands |
|**!disable mod** | -- | -- | -- | Disables all moderation commands |
|!enable list | disable list | -- | -- | Shows all enabled/disabled commands.|
|**!plonk**   |--   |member [command][subcommand]   |!plonk @Carl#0080 tag create   |This works almost exactly like !ignore but for users instead. If no command is specified, the user is banned from using the bot completely.   |
|**!unplonk**  |--   |member [command][subcommand]    |!unplonk @Carl#0080   |Unbans the user from using the bot   |
|!plonks   |--   |--   |--   |Displays all plonked users.   |
|**!restrict**   |--   |command [subcommand]   |!restrict define   |This requires a bot channel to utilize. Makes it so that if the command is used outside of the bot channel, the bot will ping the user in the botchannel and give the results there instead.   |
|**!unrestrict**   |--   |command [subcommand]   |!unrestrict d   | Unrestricts it. Like all commands where you pass in a command, aliases work just as well.   |
|**!modonly** | -- | command | !modonly echo | Makes a command usable by mods only |
|**!unmodonly** | -- | command | !unmodonly dog | Removes a command from the modonly list |
|**!modrole** | -- | role | !modrole bot commander | Makes it so that any member with the specified role is seen as a moderator by the bot, this means being able to invoke any command in bold on this page. Only exception to this is the **!ban** command which still requires the member to be able to ban the target normally.

## Tags

Tags can be complicated, see [the full section](#tags-1) for a more thorough explanation with advanced usage.

|Name|Aliases   |Args   |Example   |Usage
|---|---|---|---|---|
|!tag   |tag get   |lookup   |!classdiscords   |This is how you get tags after they're saved.   |
|!tag create   |add, +    |tagname tagcontent   |!tag + test Hello world   |Makes a tag named test with the content Hello world.   |
|!tag ++   |--   |A pastebin link   |--   | Since tags can have an output shorter than their length, using !tag ++ allows you to make them  |
|!tag append   |+=   |tagname tagcontent   |!tag += test and my mom   |Adds tagcontent to an already existing tag   |
|!tag alias   | a  |alias tagname   |!tag alias testing test   | Creates a link to an already existing tag, changes made to the original tag means the aliased tag will also be changed. The name you want for the alias is the first argument, the already existing tag is the second.  |
|!tag edit   |e   |tagname tagcontent   |!tag e test bye world   |Edits the content of an already existing tag.   |
|**!tag nsfw**   |--   |tagname   |!tag nsfw test   |Restricts the tag so that it can only be used in channels marked as nsfw   |
|**!tag restrict**   |--   |tagname   |!tag restrict test   |To prevent big tags cluttering your chatty channels, this will make the bot post the content in the bot-channel and ping the author.   |
|**!tag mod**   |--   |tagname   |!tag mod test   |Makes it so that only mods can use the command (manage server)   |
|!tag stats   |--   |[member]   |!tag stats @Carl#0080   |Shows information about the servers tags (uses, top 3, total number of tags). If you mention someone, it will show their tags instead.   |
|!tag info   |--   | tagname  |!tag info test   | Shows some stats collected about the tag, uses, creation date, last update, owner.  |
|**!tag ownership** | own | -- | -- | With this enabled (disabled by default) tags are 'owned' meaning that unless you're a mod, you can't edit, append or delete other people's tags (You can still create aliases to people's tags) |
| **!tag modonly** | -- | -- | -- | With this enabled, only mods can manage tags, non-mods can still use them.|
| **!tag prompt** | -- | -- | -- | Know how trying to create a tag that already exists asks you if you want to edit, or append? With this disabled (enabled by default) it will default to editing the tag |
| **!tag claim** | -- | tagname | !tag claim realms | Claims a tag from a member who has left the server, only relevant if ownership is enabled |
|**!tag sub** | replace s | tagname from_string to_string | !tag sub invite discord.gg/abc123 discord.gg/xyz999 | Replaces every occurance of from_string with to_string in an already existing tag. This can be extremely useful for expired invite links, slightly outdated information, or anything else that allows you to systematically correct your mistakes. |




## Highlights
Inspired by highlight bot, Carlbot now also does highlighting. Highlighting means you will receive a message when your keyword is said in chat. The matching is approximate and works really similarly to discord search (basically, if you search your keyword in discord search, you will find messages that would trigger the highlight, roughly speaking). It will only notify you if you haven't posted anything in chat for the past 10 minutes (prone to change). Generally doesn't seem to have too many false positives.

|Name|Aliases   |Args   |Example   |Usage
|---|---|---|---|---|
|!hl add   |+   |word(s)   |!hl add carl    |Adds a word that will notify you. **IMPORTANT:** The bot tries to guess when you're aware of what's being typed and won't notify you if you've typed in the past 5 minutes, to see if your highlights work, please use `!hl match <sentence>`. Additionally, when adding a multi-word highlight, it will check for a sequence of words, not a substring.   |
|!hl match| m |Sentence | !hl match carl is cute | Tests a sentence and sees which if any words would notify you.
|!hl block   |--   |member or channel   |!hl block @Kintark#0588   |Messages sent in this channel/from this user won't notify you.   |
|!hl unblock   |--   | member or channel  | !hl unblock #general  | Unblocks the user/channel   |
|!hl show   |--   | --  | --  |  Shows your words as the bot sees them, if your words look wrong ("barri" instead of "barry" for instance) it's because of [word stemming](https://en.wikipedia.org/wiki/Stemming) |
|!hl clear   |--   | --  | --  | Removes all of your highlighted words  |
|!hl del   |--   | word  | !hl clear math  | Removes a word from your highlighted words  |

## Roles
Very typo proof. **Note** these are completely separate from the reaction roles and literally not a single setting carries over.

|Name|Aliases   |Args   |Example   |Usage
|---|---|---|---|---|
|!role    |--   |role   |!role python   |This will add the role to you if the role is whitelisted. The command is typo proof so "rouge" will match with "rogue".    |
|!role whitelist   |add, +, -, del, remove, delete   |role   |!role add python   |Adds the role to the whitelist so anyone can assign it to themselves. For this command to work both the bot and the command user needs to be able to assign the role to someone.   |
|**!role unique**   |--   |--   |--   |Makes it so that any roles given will replace any other whitelisted roles. This can be useful for servers where it doesn't make any sense for someone to have multiple roles.   |
|!roles   |--   |--   |--   |Shows all whitelisted roles   |


### Automatic Roles

|Name|Aliases   |Args   |Example   |Usage
|---|---|---|---|---|
|**!autorole** | autoroles | -- | -- | Shows which roles will be added upon joining and if the bot will readd roles when someone leaves and rejoins the server
|**!autoroles readd** | reassign |-- |-- | Turns reassigning roles on/off
|**!autorole add** | -- | role | !autorole add peon | Autoroles are roles that are given to the user upon joining the server. |
|**!autorole remove** | -- | role | !autorole remove admin | -//-|

## Welcome and Farewell messages
|Name|Aliases   |Args   |Example   |Usage
|---|---|---|---|---|
|**!greet** | -- | text | !greet Welcome $mention, we've been expecting you| Sets up a welcome message that will be sent when a new user joins.
|**!farewell** | -- | text | !farewell Goodbye $user, maybe it wasn't meant to be... |Like !greet but for people leaving
|**!banmsg** |--|text | !banmsg **$user** just got blown the fuck out| Like !greet but for people getting banned
|**!set dm** | pm/joindm/joinpm | text | !set dm Hello and welcome to $server, before chatting you need to assign roles in #get-roles | Like !greet except it dms the message to the user upon joining

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
|!rm del   | delete, remove, purge, -   | id   |--   |Removes the reminder with that id.   |
|!sub   |!rm sub   | ID   |!sub 97   |Copies a reminder someone else made. This means you own the reminder, that person deleting their reminder will have no impact.   |
|!rm clear | -- | -- | -- | Removes all your reminders from the server (or ALL if used in DMs) |
|!rm repeat | -- | interval | !rm repeat 247 20d | Sets a timer to be repeated. |
|!rm when | -- | id | !rm when 247 | Shows some information about a timer created in the server (or from you, if used in DMs)|

## Feeds and timed/automatic feeds

What are feeds? Feeds are a way for you to make announcements and ping a specific role without having to deal with the annoyances and potential abuse from either having a pingable role or manually toggling inbetween pingable and not. 

Automatic feeds on the other hand can be seen as group reminders, and they share a lot of functionality with reminders.

|Name|Aliases   |Args   |Example   |Usage
|---|---|---|---|---|
|**!feed**   | !feeds  |--   |--   |Lists all the feeds that have been set up in the server.   |
|**!feed create**| --|name role |!feed create ffxiv final fantasy xiv|Creates a feed in the channel the command is used with with a specific name and a specific role that will be mentioned.|
|**!feed announce**| !announce| name content... | !feed announce ffxiv Hey guys, patch 1.0.12 has been released |Makes an announcement to the specified feed. |
|**!feed delete** | - del remove |name | !feed delete ffxiv | Deletes a feed. Note: This does not delete the associated role, so if you created one specifically for a feed, you need to delete it. |
|**!feed clear** | -- |-- | -- | Deletes ALL feeds from the server. |
|**!autofeed** | !autofeeds | -- | -- | Lists all autofeeds set up in the server. |
|**!autofeed create**| -- | name role time message... | !autofeed create reset "final fantasy xiv" 18h The servers have been reset, get out there! | Normal autofeeds (the ones created by this command) will ping the role  specified when setting them up. |
|**!autofeed silent** | -- | name time message... | !autofeed silent vote 2 hours Vote for carlbot on discord bots! | Like a normal autofeed except it does not have a role associated with it and thus, does not ping anything. |
|**!autofeed silence** | -- | name | !autofeed silence reset | Silences an already existing normal feed. |
|**!autofeed repeat** | -- | name duration | !autofeed repeat vote 24h | Marks an autofeed to be repeated. This keeps going until you delete the autofeed. |
|**!autofeed remove** | -- | name | !autofeed remove vote | Removes an autofeed |
|**!autofeed clear** | -- | -- | -- | Removes ALL autofeeds. |


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
|!quickpoll | -- | question and answers | !quickpoll best game?\| wow \| overwatch \| only losers play games | Use pipes `|` or commas to separate the questions and answers. The first arg is the question, all after that are individual answers. You can't mix pipes and commas, pipes are intended for polls where you want commas in the question or answer.
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

**Unique random list variables** `#variablename{comma, separated, values}`

Unlike random lists assigned to a variable through variable blocks, unique random lists randomly pick an element each time. This allows for some very nice commands, see the link at the bottom.

**Math blocks** `m{1 + 1 / (3 ^ 9)}`

Supports relatively advanced math.

`+ - * / ^ % sin cos tan exp abs trunc round sgn log ln log2`

**React blocks** `react{:regional_indicator_f:}`
`reactu{:regional_indicator_x:}`

   This will react to the tag(react) or original message (reactu) with the emojis placed inside the brackets
   
   Unsure what this could be used for? `!tag create doubt react{:regional_indicator_x:} https://i.imgur.com/EacBuLR.png`

**50/50 blocks** `?{Will anyone see me?}`

**Command blocks** `c{temp stockholm}`
	
Do you think that `!info` really should be called `!whois`? with command blocks you can do just that

`!tag + whois c{info $args}`

Maybe you think speak defaulting to 5 uses is an idiotic design choice, simply do

`!tag + betterspeak c{speak 20 $args}`

Important to note is that command tags are effectively not tags in the sense that whatever else you put in a tag won't be sent

**Action blocks** a{_action_} where _action_ is `pm` or `delete` (or both, comma separated)

`pm` pms the content of the tag to the user who triggered the tag

`delete` deletes the message that triggered the tag


**Formatted time blocks** strf{_strftime_}

Returns the current time formatted according to python's strftime, see http://strftime.org/ for more information.

**Example:** `The current year is strf{%Y} hehe`

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

`$authorid` - The ID of the author

`$userid` - The ID of the mentioned user if mentioned or the author if there aren't any mentions

`$serverid` - The ID of the server

`$randommember` - A random member's nickname

`$randomonline` - A random online member's nickname (online in this case means not-offline i.e. away and busy count as online)

`$randomoffline` - A random offline member's nickname

`$1 $2 $3 etc` - Like $args but only the first, second, third word etc. `!foo bar baz` means $1=bar


Still not sure how to use this? [See this link for some interesting and funny tags people have created using TagScript](https://pastebin.com/hXmtSpkF)
