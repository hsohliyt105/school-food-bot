# school-food-bot
Korean school food bot for Discord

# Installation
 
## Requirements (pip)
 - discord
 - Pillow
 - PyMySQL
 - requests
 - python-dotenv
 
## Prerequisitory

Create a upper folder on the bot folder and create .env file which has 'DISCORD_TOKEN=\<your discord token\>' written.

# Usage

## !도움말

Lists out the commands

## !오늘급식 / !내일급식 / !이번주급식 / !다음주급식

Sends the school food of today/tommorrow/this week/next week in embad format.
You need to search for your school after using the command.

## !이번달급식 / !다음달급식

Sends the school food of this month/next month in image format.
You need to search for your school after using the command.

## !등록

Registers the user into the bot database so that he/she does not need to search for the school every time they use the commands.
You need to search for your school after using the command.

## !삭제

Deletes the user from the bot database. 
You need to confirm your choice. 
