\* = optional argument

^ = bot owner only

## Prefixes
#### Displaying all prefixes for the server
`!prefix` (defaults to mentioning the bot, ! and ?)
#### Adding a prefix
`!prefix add <prefix>`
If your prefix has a space at the end, enclose it in double quotes.

#### Removing a prefix
`!prefix remove <prefix>`
#### Clearing all prefixes
`!prefix clear`
## Logging

### Deciding what gets logged

#### !log
syntax is `!log <event>` where event can be either of:

**avatar, edit, role, delete, ban, join, name**

For example, to disable logging message edits you would type `!log edits`. It will swap to true or false depending on the current setting 
#### !log ignore/unignore
Syntax is `!log ignore <channel mention(s)>`

will ignore message edits/deletions from the mentioned channels

replace `ignore` with `unignore` to unignore a channel

### Deciding where the log is shown

`!set log #channel`

### Deciding where twitch streams are announced

`!set twitch #channel`

### Adding a twitch stream
Requires "Manage Server"
`!twitch <twitch name> *<announcement text>`

Twitch name is the name of their channel

Announcement text is what the bot will say in addition to the embed when the stream goes live, defaults to their twitch name.
(warning: this can contain @everyone by design)

### Deleting a twitch stream
Requires "Manage Server"
`!twitch <twitch name>`

## Bot moderation

### Banning a user from using the bot
These all require "manage server" to work

Ban using `!plonk <@user>`

Unban using `!plonk <@user>`

Ban a user from using a specific command `!plonk <@user> <command>`
Banning a user from a specific command bans them from using any subcommand for that as well (`!temp` means you can't use `!temp home` etc.)

Display all plonked users by typing `!plonks`



### Disabling commands per command

`!disable <command>`
For example: `!disable remindme` 

Will disable the remindme command for all users unless they have manage roles
### Disabling all commands

Either use `!disable all`
Which will add all commands to the blacklist (this means that any future commands won't be blacklisted)
or use `!disable server`
Which will actually disable the server from having any command registered (manage server bypasses this)
### Disabling commands per channel

`!ignore #channel` or `!ignore all`

Disables ALL commands from being used in the mentioned channel (unless you have manage roles)
`!unignore #channel` or `!unignore all`

Enables ALL commands from being used in the mentioned channel (unless you have manage roles).

## Tags
Tags are server-specific and case insensitive

#### Accessing a tag
Just use `!<tagname>` multiple words are supported.
#### Creating tags
`!tag +/create/add <tagname> <tag content>`

Tag names can be two words, use double quotes for this

**Examples:**

`!tag + 3ball :8ball::8ball::8ball:`

`!tag + "hey there" I'm a two-word tag!`

### Advanced tag usage
`%user` - Nickname of the mentioned user or the author if nobody is mentioned.

`%channel` - Name of the mentioned channel or the channel the command was invoked in if there are no mentions.

`%server` - Name of the server.

`%author` - Nickname of the person who used the command (not the one who created it).

`%mention` - Nickname of the first mentioned user or NOTHING if there's no mention.

In addition to these you can use `%nuser, %nauthor and %mention` which will return the discord name instead of their nickname.

`{{arg1, arg2, arg3}}` Enclosing comma separated words with double curly brackets will choose one at random. Supports having more than one list per tag and can contain the variables listed above.

#### Appending tags
`!tag += <tagname> <tag content>`
Appends <tag content> on a new line to the tag.

**Example:**

`!tag += tankchat http://i.imgur.com/ONtLdiu.png`

#### Removing tags
`!tag - <tagname>`
Removes the tag and all aliases.
**Example:**

`!tag - tankchat`

#### Showing information about a tag
`!tag info <tagname>`

Shows uses and its ranking on the server compared to other tags
**Example:**
`!tag info tankchat`
#### Showing stats for all tags on a server
`!tag stats`
Shows some global and server-specific tag stats

#### Returning all tags someone has created
`!tag mine *<mention>`

Defaults to yourself, displays all tags you or the user mentioned has created.

#### Returning all tags
`!taglist/commands/tags`

PMs you all tagnames

#### Retrieving the raw tag content
`!tag raw <tagname>`

Uses backslash escaping to display **text** as \*\*text\**

#### ^ Removing a user's tags
`!tag purge *<mention>`

Removes all tags associated with that user

#### Searching for tags (using fuzzy string matching)

`!tag search/!tagsearch/commands <search query>`

Searches for matches, reply with numbers to print the tag

## Bio

#### Accessing a bio
`!bio *<mention>`

Defaults to yourself
#### Creating a bio
`!bio + <biocontent>`
#### Appending to a bio
`!bio += <biocontent>`

## Blizzard related commands
First of all there's a 1/10000 chance per message sent to receive a legendary.

#### RTB
`!rtb`

Works exactly like the spell in wow did pre-7.2.5
#### Wow armory
`!armory/pug <name> <realm> <zone>`

Shows legendaries, ilvl, enchants, gems, traits, progression and m+ stats
#### Invasion timer
`!invasion`
Returns invasion timers for EU and NA

**Tip:**
use `!rm eu/na` to be reminded when the invasion is up
#### M+ affixes
`!m+/affix/affixes`
Returns current and future m+ affixes and information about them
#### Pick my x
`!pickmygold`
Random ow hero

`!pickmyclass`
Random wow class

`!pickmyspec`
Random wow spec
## General utilities
### Reminders

#### Remindme
`!rm <time> <message>`

Time syntax looks something like `4d23h123m` it's one word, supports years, days, hours, minutes and seconds. You can repeat time units and you can go above 60 minutes for instance. Limited to this century. For the reminder to work you need to be in the same server as you were in when you created the reminder.
#### Display reminders
`!rm mine`
#### Remove reminder
`!rm clear *<id>`

If no id is supplied, it will ask you if you wish to remove _all_ reminders
#### Copy someone else's reminder
`!sub <id>`

Will make a copy of the specified reminder with you as the author
#### Timer (don't use this please)
`!timer <time> <message>`

Same syntax as `!rm` but won't work across bot crashes, also won't allow you to delete or list reminders, use for things < 5 minutes.

### Definitions
`!d <word>`

Gives you all definitions for the mentioned word.

### Unit conversion
`!c/convert <query>`

Uses google to convert pretty much anything, supports currency, distance, temperature, time, anything.
### Weather
`!temp/weather *<location>`

Returns weather information about a location, defaults to your home
#### Setting a home
Using `!weather` for the first time will save your information. If you wish to change it, you can do so by typing

`!temp home <location>`
#### Random numbers
`!roll *<range> *<rolls>`

defaults to 6 and 1
#### Aesthetics/smallcaps
`!ae/aesthetics <text>`

`!sc/smallcaps <text>`

Returns the text as Ｆｕｌｌｗｉｄｔｈ or ꜱᴍᴀʟʟᴄᴀᴘꜱ

#### Charinfo
`!charinfo <characters>`

Returns information about the characters

#### 8Ball
`!8ball`

Your basic shitty 8ball function, rate limited to two uses/channel/minute

## Fun/stupid
### Echo
`!echo #channel <text>`

Will make the bot say what you put as `<text>` in the mentioned #channel
### Retard

#### Tipping a retard coin
`!retard <@mention>`
#### Biggest retards
`!retard top`

### Sicklad

#### Tipping a sicklad point
`!sicklad <@mention>`
#### Sickest lads
`!sicklad top`

#### Urban dictionary
`!ud <word>`
Returns the top definition and example

## Meta
Commands relating to discord and members in general

#### Nickname history
`!nicks/nicknames *<@user>`

Returns nickname history for the mentioned user, defaults to yourself.

Since discord doesn't track this, the bot  can only show nicknames since it joined. Duplicates are deleted and only the most recent nickname is shown.

#### Userinfo
`!i *<@user>`
Will show your name, discriminator, ID, last five nicknames, postcount (since the bot has been in the server), creation date, join date and avatar (click the name). Defaults to yourself, hides fields with 0.
#### Serverinfo
`!serverinfo`
Shows ID, owner, if it's partnered, text and voice channels, members by status, and roles.

#### Bot info
`!about`
Shows Members, channels, servers, commands, uptime and resource usage.

#### Uptime
`!uptime` Shows how long the bot has been online for

## Search commands

### Googling
`!g <query>`
Works just like googling, supports google cards like definitions and calculators

### Wowhead search
`!w <query>`
Returns the most relevant wowhead page
Alternatively you can wrap words in [[double brackets]] to do the same
**Example:**
Hey guys, check out my new [[prydaz]] :kms:

