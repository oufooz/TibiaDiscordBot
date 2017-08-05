import discord
import traceback
import asyncio
from discord.ext import commands
import random
from utils import scrape
import json
import operator

description = '''An example bot to showcase the discord.ext.commands extension
module.
There are a number of utility commands being showcased here.'''
bot = commands.Bot(command_prefix='?', description=description)

ALLOCATED_LISTS = ''
CACHED_SERVER = ''
KEYS = ''
INGAME_SERVER = 'hydera'
DISPLAY_LISTS = dict()
DISPLAY_LISTS_HISTORY = dict()
CHANNEL_LISTS = dict()
SERVER_NAME = 'TestingDiscordBot'

def comparelist(listX,listY):
    returnList = []
    for j in listX:
        for i in listY:
            if j['name'] == i:
                returnList.append(j)
                    
    return(returnList)
    
def SameDictionary(DictX,DictY):
    print(DictX,'\n\n\n',DictY)
    if(len(DictX) != len(DictY)):
        return False
    for j in DictX:
        if j in DictY:
            t = sameList(DictX[j],DictY[j])
            print(j)
            print(t)
            if t:
                continue
            return False
    return True
    
def sameList(ListX,ListY):
    if(len(ListX) != len(ListY)):
        return False
    for j in ListY:
        if j in ListX:
            continue
        return False
    return True
    
def deepCopyList(ListX):
    temp = []
    for j in ListX:
        temp.append(j)
    return temp

def deepCopyDict(DictX):
    temp = dict()
    for j in DictX:
        temp[j] = deepCopyList(DictX[j])
    return temp




@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    
    server = discord.utils.get(bot.servers,name = SERVER_NAME)

    readAllocatedList()
    await checkForChannelsAndCreate()
    bot.loop.create_task(my_background_task())
    
def readAllocatedList():
    global ALLOCATED_LISTS
    try:
        with open('lists.txt',"r") as file_object:
            content = file_object.read()
            ALLOCATED_LISTS = json.loads(content)
            #print(ALLOCATED_LISTS)
    except FileNotFoundError:
        msg = 'couldnt find the file' + 'lists.txt'
        print(msg)
        
def saveAllocatedList():
    global ALLOCATED_LISTS
    try:
        with open('lists.txt',"w") as file_object:
            print(json.dumps(ALLOCATED_LISTS,sort_keys = True,indent=4),file = file_object)
            #print(ALLOCATED_LISTS)
    except FileNotFoundError:
        msg = 'couldnt find the file' + 'lists.txt'
        print(msg)

    
async def checkForChannelsAndCreate():
    global KEYS
    global CACHED_SERVER
    global CHANNEL_LISTS
    KEYS = [{x : False} for x in ALLOCATED_LISTS]

    for server in bot.servers:
        if(server.name == 'TestingDiscordBot'):
            CACHED_SERVER = server
            
    if not CACHED_SERVER:
        return
    
    for channel in CACHED_SERVER.channels:
        for key in KEYS:
            for j in key:
                if(j == channel.name): 
                    CHANNEL_LISTS[j] = channel
                    key[j] = True
                    continue
             
    for key in KEYS:
        for j in key:
            if(key[j] == True):
                continue
            await createChannel(j)


async def createChannel(strtemp):
    global CACHED_SERVER
    global CHANNEL_LISTS
    everyone = discord.PermissionOverwrite(read_messages=False)
    mine = discord.PermissionOverwrite(read_messages=True)
    try:
        t = await bot.create_channel(CACHED_SERVER, strtemp, (CACHED_SERVER.default_role, everyone), (CACHED_SERVER.me, mine))
        CHANNEL_LISTS[strtemp] = t
    except Exception as e:
        traceback.print_exc()
        print('\n\n\n Failed to create channel ')
        raise e

async def deleteChannel(strtemp):
    global CACHED_SERVER
    global CHANNEL_LISTS
    try:
        await bot.delete_channel(CHANNEL_LISTS[strtemp])
        del CHANNEL_LISTS[strtemp]
    except Exception as e:
        traceback.print_exc()
        print('\n\n\n Failed to create channel ')
        raise e
    
async def my_background_task():
    await bot.wait_until_ready()
    global DISPLAY_LISTS
    global ALLOCATED_LISTS
    DISPLAY_LISTS_HISTORY = {}
    while not bot.is_closed:
        OnlineList = scrape.getPlayersInServer(INGAME_SERVER,True)
        for j in ALLOCATED_LISTS:
            DISPLAY_LISTS[j] = comparelist(OnlineList,ALLOCATED_LISTS[j])
            DISPLAY_LISTS[j] = sorted(DISPLAY_LISTS[j],key= operator.itemgetter('voc'))
        for j in DISPLAY_LISTS:
            if(not len(DISPLAY_LISTS_HISTORY) or not j in DISPLAY_LISTS_HISTORY):
                await displayListToChannel(CHANNEL_LISTS[j],DISPLAY_LISTS[j],j)   
                continue
                
            if(not sameList(DISPLAY_LISTS[j],DISPLAY_LISTS_HISTORY[j])):
                    await displayListToChannel(CHANNEL_LISTS[j],DISPLAY_LISTS[j],j)   
        DISPLAY_LISTS_HISTORY = deepCopyDict(DISPLAY_LISTS)
        await asyncio.sleep(10) 
            
async def clearNotCommand(ctx, number = 99):
    mgs = [] #Empty list to put all the messages in the log
    number = int(number) #Converting the amount of messages to delete to an integer
    async for x in bot.logs_from(ctx, limit = number):
            mgs.append(x)
    if len(mgs) == 0:
        return
    if len(mgs) == 1:
        await bot.delete_message(mgs[0])
    else:
        await bot.delete_messages(mgs)
        

    
def swap_voc_short(vocation):
    if( vocation == "Paladin"):
       return " P"
    if( vocation == "Sorcerer"):
       return " S"
    if( vocation == "Druid"):
       return " D"
    if( vocation == "Knight"):
       return " K"
    if( vocation == "Royal Paladin"):
       return "RP"
    if( vocation == "Elite Knight"):
       return "EK"
    if( vocation == "Master Sorcerer"):
       return "MS"
    if( vocation == "Elder Druid"):
       return "ED"
    # No Voc chosen
    return " N"
    



async def displayListToChannel(channel,displayList,name):
    print('Display List Name : ',name)
    temp = "List of "+ name + " players\n"
    startend = "```"
    tempVoc = None
    await clearNotCommand(channel,99)
    for i in displayList:
        tName = i['name']
        tVoc = swap_voc_short(i['voc'])
        if(tVoc != tempVoc):
            temp += '\n'
        tempVoc = tVoc                
        tLevel = str(i['level'])
        t= "| " + '{0: <3}'.format(tVoc) + "| " + '{0: <60}'.format(tName) + "| " +  '{0: <4}'.format(tLevel)+ "|\n"
        temp += t
        if(len(temp) >= 1942):
            await bot.send_message(channel,startend+temp+startend)
            temp = ""

                

    if(len(temp) < 1942):
            await bot.send_message(channel,startend+temp+startend)
            


@bot.command()
async def add(str1,*,str2):
    str2 = str2.title()
    if str1 is None or str2 is None:
        bot.say( "Command invalid \nUsage !add ListName PlayerName")
        return
        
    print(str1, "\n",str2)
    global ALLOCATED_LISTS

    if not str1 in ALLOCATED_LISTS:
        x = [str(y) for y in ALLOCATED_LISTS]
        await bot.say("List name invalid \nAvailable ListNames  :" + str(x))
        return
    
    if str2 in ALLOCATED_LISTS[str1]:
        await bot.say("Character is already in list ")
        return
    ALLOCATED_LISTS[str1].append(str2)
    saveAllocatedList()
    await bot.say("Addition of " + str2 + " to " + str1 + " was Successful")
    
@bot.command()
async def remove(str1,*,str2):

    if str1 is None or str2 is None:
        bot.say( "Command invalid \nUsage !add ListName PlayerName")
        return
     
    str2 = str2.title().strip()
    print(str1, "\n",str2)
    global ALLOCATED_LISTS

    if not str1 in ALLOCATED_LISTS:
        x = [str(y) for y in ALLOCATED_LISTS]
        await bot.say("List name invalid \nAvailable ListNames  :" + str(x))
        return
    
    if not str2 in ALLOCATED_LISTS[str1]:
        await bot.say("character does not exist in this list")
        return
    
    ALLOCATED_LISTS[str1].remove(str2)
    saveAllocatedList()
    await bot.say("Removal of " + str2 + " from " + str1 + " was Successful")
    
@bot.command()
async def create(str1):
    if str1 is None:
        bot.say( "Command invalid \nUsage !create ListName")
        return
        
    print(str1)
    global ALLOCATED_LISTS

    if str1 in ALLOCATED_LISTS:
        x = [str(y) for y in ALLOCATED_LISTS]
        await bot.say("ListName In Use \n Currently Used ListNames  :")
        await bot.say(x)
        return
    
    ALLOCATED_LISTS[str1] = []
    await createChannel(str1)
    saveAllocatedList()
    await bot.say("Creation of " + str1 + " Successful")
    
@bot.command()
async def delete(str1):
    if not str1 in ALLOCATED_LISTS:
        x = [str(y) for y in ALLOCATED_LISTS]
        await bot.say("List name invalid \nAvailable ListNames  :" + str(x))
        return
    del ALLOCATED_LISTS[str1]
    saveAllocatedList()
    await deleteChannel(str1)
    await bot.say("Deletion of " + str1 + " Successful")
    

    
@bot.command()
async def display(str1):

    if str1 is None:
        bot.say( "Command invalid \nUsage !display ListName")
        return
        
    print(str1)
    global ALLOCATED_LISTS

    if not str1 in ALLOCATED_LISTS:
        x = [str(y) for y in ALLOCATED_LISTS]
        await bot.say("List name invalid \nAvailable ListNames  :")
        await bot.say(x)
        return
    
    await bot.say("Tracked Characters in list " + str1 + " : \n")
    if(not len(ALLOCATED_LISTS[str1])):
        await bot.say("No Characters in List")
        return
    temp = ''
    for i in ALLOCATED_LISTS[str1]:
        if(len(temp) > 1900 and len(temp) < 2000):
            await bot.say(temp)
            temp = ''
        temp = temp + "\t" + i
    if(len(temp) <= 1900):
        await bot.say(temp)
    
    

    

try:
    bot.run(Token)
except Exception as e:
     traceback.print_exc()
     raise e