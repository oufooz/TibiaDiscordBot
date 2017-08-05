# TibiaDiscordBot
A Discord Bot that tracks online lists of enemies/friends in Tibia MMORPG.
The Bot uses the Scraping Utility to acquire the data from Tibia's website.
The Discordbot interface allows the user to modify the display lists by creating/deleting lists , adding/removing characters

Example of a List:

Where Listname = 'huntedlist' and each entry is composed of 'vocation' : 'ed','ek','ms','rp' | 'charactername' | 'level'

![ListDisplay](https://i.gyazo.com/23c0582a3250fb41bfd7334b65a13d67.png)

## Scraping Utility.

Uses Requests And Beautiful Soup to extract/scrape useful data from Tibia's website.

Such as:
- Character stats ( name,level,vocation,deathlist,alt characters etc..)
- Server information ( onlinenumber, pvpType,location.. )
- Guild Data
- Highscores
        
##### TODO:
- Manage Permissions of Server Members
- ADD Guilds as a whole to a list
- Allow users to retrieve specific high scores through discord
