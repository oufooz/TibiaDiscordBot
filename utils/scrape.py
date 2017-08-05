import requests
import bs4
import json
import datetime
import re
import time
from bs4 import BeautifulSoup

"""
To Print Debug msges set DEBUG to true
"""
DEBUG = False
"""
    Base SERVER URLS
"""
BASESERVERURL = "https://secure.tibia.com/community/?subtopic="
BASEHIGHSCORE = "https://secure.tibia.com/community/?subtopic=highscores&world={0}&list={1}&profession={2}&currentpage={3}"
BASEGUILDURL = "https://secure.tibia.com/community/?subtopic=guilds&page=view&GuildName={}"
SORTURL = "&order=level_desc"
"""
    Get server data from tibia.com.
    return list of dictionaries
    'world' = worldname
    'playersOnline' = numberofplayersonline
    'location' 
    'pvpType'
    'extra' : premum blocked etc..
"""
def getServersData():
    SERVURL = "worlds"
    r = requests.get(BASESERVERURL + SERVURL)
    time = datetime.datetime.now()
    if(r.status_code != 200):
        if(DEBUG):
            print("Failed to get server data function GETSERVERDATA , Time",time)
        return
    soup = BeautifulSoup(r.text,'html.parser')

    OnlineWorldList = soup.find_all("tr",class_ =["Even","Odd"])

    servers = []
    for onlineworld in OnlineWorldList:
        serverentry = dict()
        for i,t in enumerate(onlineworld):
            for j in t:
                if(i == 0):
                    serverentry['world'] = j.getText()
                if(i == 1):
                    serverentry['playersOnline'] = int(j)
                if(i == 2):
                    serverentry['location'] = j.replace("\xa0"," ")
                if(i == 3):
                    serverentry['pvpType'] = j
                if(i == 4):
                    if(isinstance(j,bs4.element.Tag)):
                        serverentry['extra'] = ["Preview World"]
                        continue
                    j = [x.strip() for x in j.split(',')]
                    serverentry['extra'] = j
        servers.append(serverentry)
    if(DEBUG):
        print("Servers DATA \n",json.dumps(servers,indent = 4))
    return servers

def getPlayersInServer(serverName:str,sort:bool = False):
    SERVURL = "worlds&world="+serverName.title()
    if(sort):
        r = requests.get(BASESERVERURL + SERVURL + SORTURL)
    else:
        r = requests.get(BASESERVERURL + SERVURL)
    time = datetime.datetime.now()
    if(r.status_code != 200):
        if(DEBUG):
            print("Failed to get server data function GETSERVERDATA , Time",time)
        return
    soupserv = BeautifulSoup(r.text, 'html.parser')

    OnlinePlayerList = soupserv.find_all("tr" , class_ = ["Even","Odd"])
    players = []
    for playeronline in OnlinePlayerList:
        player = dict()
        i = 0
        for child in playeronline.children:
            if(i == 0):
                player['name'] = child.getText().replace("\xa0"," ")
            if(i == 1):
                player['level'] = int(child.getText())
            if(i == 2):
                player['voc'] = child.getText().replace("\xa0"," ")
            i = i+1
        players.append(player)
    return players

def parseCharInfo(table):
    temp = table.findChildren('td')
    tempinfo = dict()
    for i in range(1,len(temp),2):
        if(temp[i].getText() == "Comment:"):
            continue
        tempinfo[temp[i].getText().replace(':','').replace('\xa0',' ').strip()] = temp[i+1].getText().replace('\xa0',' ').strip()
    return tempinfo

def parseAccAchiev(table):
    temp = table.findChildren('tr')
    tempinfo = []
    for i in range(1,len(temp)):
        if(temp[i].getText() == "There are no achievements set to be displayed for this character."):
            break
        tempinfo.append(temp[i].getText())
    return tempinfo 

def parseAccInfo(table):
    temp = table.findChildren('td')
    tempinfo = dict()
    for i in range(1,len(temp),2):
        tempinfo[temp[i].getText().replace(':',' ').strip()] = temp[i+1].getText().replace('\xa0',' ')
    return tempinfo

def parseCharDeaths(table,deathlimit):
    temp = table.findChildren('td')
    tempinfo = dict()
    limit = len(temp)
    if(len(temp) > 1 + deathlimit*2):
        limit = 1 + deathlimit*2
    for i in range(1,limit,2):
        tempinfo[temp[i].getText().replace(':',' ').replace('\xa0',' ').strip()] = temp[i+1].getText().replace('\xa0',' ').strip()
    return tempinfo

def parseAltChars(table):
    temp = table.findChildren('nobr')
    tempinfo = []
    for i in range(0,len(temp),2):
        tempchar = temp[i].getText().replace('\xa0',' ')
        tempinfo.append(" ".join(tempchar.split()[1:]))
    return tempinfo

def getPlayerInfo(name:str,deathlimit : int = 5):
    tries = 0
    requestString = "https://secure.tibia.com/community/?subtopic=characters&name=" + name.title().replace(' ','%20')
    print(requestString)
    rchar = requests.get(requestString)
    soupchar = BeautifulSoup(rchar.text,'html.parser')
    content = soupchar.find_all("table")
    while(int(rchar.status_code) != 200 and tries < 10):
        time.sleep(10)
        tries = tries + 1
        rchar = requests.get(requestString)
    playerinfo = dict()
    for table in content:
        if(table.tr.getText() == "Could not find character"):
            print("Couldnt find character with name {} ".format(name))
            return dict()
        tempcat = table.tr.getText()
        if(tempcat == 'Character Information'):
            playerinfo['Character Information'] = parseCharInfo(table)
            continue
        if(tempcat == 'Account Achievements'):
            playerinfo['Account Achievements'] = parseAccAchiev(table)
            continue
        if(tempcat == 'Account Information'):
            playerinfo['Account Information'] = parseAccInfo(table)
            continue
        if(tempcat == 'Character Deaths'):
            playerinfo['Character Deaths'] = parseCharDeaths(table,deathlimit)
            continue
        if(tempcat == 'Characters'):
            playerinfo['Characters'] = parseAltChars(table)
            continue
        break
    return playerinfo
    


"""
    Profession:
        0 : All ( no specific one )
        1 : No Vocation ( rookgaurd and dawnport )
        2 : Druids
        3 : Knights
        4 : Paladins
        5 : Sorcerers
        
    list == Cateogry:
        Experience Points : "experience"
        Magic Level : "magic"
        Club Fighting : "club"
        Axe Fighting : "axe"
        Sword Fighting : "sword"
        Fishing : "fishing"
        Shielding : "shielding"
        Fisting : "fist"
        Loyalty Points : "Loyalty"
        Achievements : "Achievements"
        
    PageNumber start at 1 goes up to 12 ( 25 entries per page ). However if Highscore results < 300 results. ( might end before that)
"""

def getHighscores(world,category,voc,pgnum : int = 1):
    tries = 0
    temp  = BASEHIGHSCORE.format(world.title(),category,voc,pgnum)
    print(temp)
    page = requests.get(temp)
    while(int(page.status_code) != 200 and tries < 10):
        time.sleep(1)
        page = requests.get(temp)
        tries = tries + 1
    soup = BeautifulSoup(page.text, 'html.parser')
    content = soup.find_all("table" , class_ = "TableContent")
    temp = content[0].findChildren('tr')
    length = len(temp)
    highscore = []
    rank = 0
    for i in range(2,length):
        obj = []
        for k,j in enumerate(temp[i].children):
            if(i == length-1):
                t = j.findNext('b').findNext('b').text
                t = int(re.search(r'\d+', t).group())
                if(int(rank) == t):
                    t = True
                else:
                    t = False
                return highscore,t 
            if( k == 0):
                rank = j.text
            obj.append(j.text)
        highscore.append(obj)
        
def getAllHighscores(world,category,voc):
    pgnum = 1
    temp2= False
    highscorefull = []
    temp = []
    while(not temp2 and pgnum < 20):
        temp1,temp2 = getHighscores(world,category,voc,pgnum)
        pgnum = pgnum +1
        highscorefull = highscorefull + temp1
        time.sleep(1)
    return highscorefull
    


def getGuildData(guild_name,sort:bool = False):
    tries = 0
    URL = BASEGUILDURL.format(guild_name.title())
    if(sort):
        URL = URL +  SORTURL
    page = requests.get(URL)
    while(int(page.status_code) != 200 and tries < 10):
        time.sleep(1)
        page = requests.get(temp)
        tries = tries + 1
    soup = BeautifulSoup(page.text,'lxml')
    content = soup.find_all("table", class_ = "TableContent")
    
    pattern = '\(.+\)'

    if(content[1].getText() == "An internal error has occurred. Please try again later! "):
        print("Guild doesnt exist")
        return

    tr = content[0].findChildren('tr')
    listdata = []
    
    for i in range(1,len(tr)):
        td  = tr[i].findChildren('td')
        obj = []
        for u,j in enumerate(td):
            #print(u , j)
            if(u == 0):
                continue

            temp = j.getText().replace('\xa0',' ')
            temp = re.sub(pattern,'',temp).strip()
            obj.append(temp)
        listdata.append(obj)
        
    return listdata
    
def testServer():
    t = getServersData()
    print(t,"\n\n\n\n")
    return t

def testServerData(name:str = 'hydera'):
    t = getPlayersInServer(name,True)
    print(t,"\n\n\n\n\n")
    return t
    
def testPlayerInfo(name:str = 'kern cyma',deathlimit = 5):
    t = getPlayerInfo(name,deathlimit)
    print(t,"\n\n\n\n\n")
    return t
    
def testGetHighscores(world : str = 'hydera',category : str = 'experience', voc : int = 0, pageNum : int  = 1):
    t = getAllHighscores(world,category,voc)
    print(t,"\n\n\n\n\n")
    return t

def testGetGuildData(name:str = 'oic'):
    t = getGuildData(name)
    print(t,"\n\n\n\n\n")
    return t
    

def main():
    """
    testServer()
    time.sleep(1)
    testServerData()
    time.sleep(1)
    testPlayerInfo()
    time.sleep(1)
    testGetHighscores()
    time.sleep(1)
    testGetGuildData()
    """
    testPlayerInfo(deathlimit = 100)

    


if __name__ == "__main__":
    main()