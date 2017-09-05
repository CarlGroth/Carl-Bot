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

Ban a user from using a specific subcommand `!plonk <@user> <command> <subcommand>`

This ONLY disables the subcommand, disabling `!temp home` means `!temp` still works etc. If you specify a command alias it will automatically convert it to the actual command name.

Display all plonked users by typing `!plonks`

Display disabled commands per user by typing `!plonks <@user>`

### Disabling commands per command

`!disable <command>`
For example: `!disable remindme` 

Will disable the remindme command for all users unless they have manage server

`!disable <command> <subcommand>`

For example: `!disable role whitelist`

Will disable `!role whitelist` while still allowing users to use `!role`. Works for aliases.


### Disabling all commands

Either use `!disable all`
Which will add all commands to the blacklist (this means that any future commands won't be blacklisted)
or use `!disable server`
Which will actually disable the server from having any command registered (manage server bypasses this)
### Disabling a channel

`!ignore #channel` or `!ignore all`

Disables ALL commands from being used in the mentioned channel (unless you have manage roles)
`!unignore #channel` or `!unignore all`

Enables ALL commands from being used in the mentioned channel (unless you have manage roles).

### Disabling commands and sub commands per channel

`!ignore #channel <command> [<subcommand>]`

Works the same as the other disablers, subcommands will only block the specified subcommand (and all aliases) while blocking the command will block the command and all subcommands.

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

You can also add variables/custom args with `$1, $2, $3` etc. These variables will be replaced with your words after `!command <tagname>`.

You can set a default value to these variables by typing `$1="your thing here"`

By using double quotes you can add multiple words at once. It also supports things like random lists, %author and pretty much everything you can think of. Emojis need to be enclosed in quotes and you can't set a variable default to equal another variable.

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

## Roles

CarlBot supports fairly basic role assignments.

### Getting a role

`!role <role>` where `<role>` can be an id, a role mention or just the name (case insensitive, but special characters appear broken)

### Whitelisting a role

For users to be able to give themselves roles, you first need to whitelist the role.
In order to whitelist a role, three things must be true:

1. You have the manage roles permission

2. You're high enough in the role hierarchy that you can assign the role

3. The bot can assign the role

`!role whitelist <role>`

### Making roles unique

Some servers will want you to only have one assignable role, Carlbot can handle this.

`!role unique` - requires manage server. This makes it so that any role Carlbot assigns will replace all other whitelisted roles.


## Highlights

Inspired by highlight bot, Carlbot now also does highlighting.
Highlighting means you will receive a message when your keyword is said in chat. The matching is approximate and works really similarly to discord search (basically, if you search your keyword in discord search, you will find messages that would trigger the highlight, roughly speaking). It will only notify you if you haven't posted anything in chat for the past 10 minutes (prone to change). Generally doesn't seem to have too many false positives.

### Adding words to be highlighted
`!hl add <word>` - adds a word that will notify you

### (un)Blocking a user or channel from highlighting you
`!hl block <@/#mention>` - messages sent in this channel/from this user won't notify you

`!hl unblock <@/#mention>` - unblock the user/channel
### Listing your highlighted words
`!hl show` - Shows your words as the bot sees them, if your words look wrong ("barri" instead of "barry" for instance) it's because of [word stemming](https://en.wikipedia.org/wiki/Stemming)

### Removing a highlighted word
`!hl del <word>`
### Removing all highlighted words
`!hl clear`

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

