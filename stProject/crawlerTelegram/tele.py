from telethon import TelegramClient, events
from telethon import utils
import configparser
from hazm import Normalizer
import psycopg2
import sys
import json
from telethon.tl.types import PeerUser, PeerChat, PeerChannel,Channel,User,Chat
from pymongo import MongoClient
import os
#mishe aval kar hame aza yek channel ro begirim ke dge har dafeh bara har payam check nakonim vali ye fekri bara aza jadid begirm v aya chanal mishe aza ro begirim
#farz shodeh har payam marbot be yek sahm ast baadan mishe avaz kard
#behbood khondan v neveshtan image
#baraye channal ha in tor hast ke id payam dahandeh ro nemideh vali author ro mideh miam id mishe esmesh va username ham esm channel
currentPath=os.path.abspath(os.getcwd())
clientMongo = MongoClient('mongodb://127.0.0.1:27017/?compressors=disabled&gssapiServiceName=mongodb')
dbMongo=clientMongo.stock
f=open('output.txt','w',encoding='utf-8')
globalVersion=1
def writeJsonOpject(jsonObject):
    json.dump(jsonObject,f,ensure_ascii=False, indent=4, sort_keys=True, default=str)
    f.flush()
def writeJsonOpjectToMongo(jsonObject):
    dbMongo.telegram.insert_one(jsonObject)
def init_database():
    mhost='localhost'
    mdatabase='telegram'
    muser='postgres'
    mpassword='aliali0321'
    conn = psycopg2.connect(host=mhost,database=mdatabase, user=muser, password=mpassword)
    cur = conn.cursor()
    return conn,cur





async def createJson(content,date,senderId,senderUserName,senderName,isGroup,channelUserName,channelName,parentId,image,version,lastMessageId,channelId):
    myJson={
        'message ':{
            'content': content,
            'date': date,
            'senderId': senderId,
            'senderUserName': senderUserName,
            'senderName': senderName,
            'isGroup': isGroup,
            'channelUserName': channelUserName,
            'channelName': channelName,
            'parentId': parentId,
            'image': image,
            'version': version,
            'lastMessageId': lastMessageId,
            'channelId': channelId,
        }
    }
    writeJsonOpject(myJson)
    writeJsonOpjectToMongo(myJson)

async def addMessage2(message,channel_group,channel,channelType):
    content=''
    date=''
    senderId=''   
    senderUserName=''		
    senderName=''
    isGroup=''
    channelUserName=''  
    channelName=''
    parentId=0    
    image=''
    version=globalVersion
    lastMessageId=0
    channelId=0
    path='none'
    print(channel)
    print(message)
    print()
    content=message.message
    date=message.date
    lastMessageId=message.id
    channelId=channel.id
    if message.photo:
        path = await message.download_media()
        actualPath=path
        f = open(actualPath,'rb')
        filedata = f.read()
        image=filedata
    if(message.reply_to_msg_id is None):
        parentId=0
    else:
        parentId=message.reply_to_msg_id

    if(channelType=='User'):
        senderId=message.from_id
        senderUserName=channel.username
        if(channel.first_name is None):
            channel.first_name=''
        if(channel.last_name is None):
            channel.last_name=''   
        senderName=channel.first_name+' '+channel.last_name
        isGroup='true'
        channelUserName=channel.username
        channelName=channel.first_name+' '+channel.last_name
    elif(channelType=='Chat'):
        senderId=message.from_id
        newUser= await client.get_entity(senderId)
        senderUserName=newUser.username
        senderId=message.from_id
        if(newUser.first_name is None):
            newUser.first_name=''
        if(newUser.last_name is None):
            newUser.last_name=''   
        senderName=newUser.first_name+' '+newUser.last_name
        isGroup='true'
        channelUserName='null'
        channelName=channel.title
    elif(channelType=='Channel'):
        if(channel_group=='false'):
            senderId=message.from_id
            newUser= await client.get_entity(senderId)
            senderUserName=newUser.username
            if(newUser.first_name is None):
                newUser.first_name=''
            if(newUser.last_name is None):
                newUser.last_name=''   
            senderName=newUser.first_name+' '+newUser.last_name
            isGroup='true'
        else:
            senderId='null'
            senderUserName='null'
            if(message.post_author is None):
                senderName='null'
            else:
                senderName=message.post_author
            isGroup='false'
        channelUserName=channel.username
        channelName=channel.title
    await createJson(content,date,senderId,senderUserName,senderName,isGroup,channelUserName,channelName,parentId,image,version,lastMessageId,channelId)



        
        



async def check_all_message(channel):
    channel= await client.get_entity(channel)
    channelType=''
    if(type(channel) is User):
        channel_group='false'
        channelType='User'
    elif(type(channel) is Channel):
        print('PeerChannel')
        channelType='Channel'
        if(channel.megagroup==True or channel.broadcast==False):
            channel_group='false'
        else:
            channel_group='true'
    elif(type(channel) is Chat):
        channelType='Chat'      
        channel_group='true'

    async for message in client.iter_messages(channel):
        if(message.date.year < max_year):
            break
        await addMessage2(message,channel_group,channel,channelType)


async def getAllMessages(channels):
    for channel in channels:
        await check_all_message(channel)







def init():
    config = configparser.ConfigParser()
    path=currentPath+r'\teleConfig.ini'
    config.read(path)
    api_id=config.getint('Telegram','api_id')
    api_hash=config['Telegram']['api_hash']
    api_hash = str(api_hash)
    return api_hash,api_id


def fill_namad():
    f = open(currentPath+r'\name.txt','r',encoding='utf-8')
    namad=f.read()
    f.close()
    return namad.split('\n')

def get_channel():
    f = open(currentPath+r'\channel_list.txt','r',encoding='utf-8')
    namad=f.read()
    f.close()
    return namad.split('\n')


async def prepareMessageOnline(message,channelId):
    channel= await client.get_entity(channelId)
    channelType=''
    channel_group=''
    if(type(channel) is User):
        channel_group='false'
        channelType='User'
    elif(type(channel) is Channel):
        print('PeerChannel')
        channelType='Channel'
        if(channel.megagroup==True or channel.broadcast==False):
            channel_group='false'
        else:
            channel_group='true'
    elif(type(channel) is Chat):
        channelType='Chat'      
        channel_group='true'
    await addMessage2(message,channel_group,channel,channelType)
    
async def setEventToGetMessages(channels):
    channelsEntity=[]
    for channel in channels:
        temp=await client.get_entity(channel)
        #print(temp)
        #print(temp.id)
        channelsEntity.append(temp.id)
    @client.on(events.NewMessage(incoming=True,outgoing=False))
    async def my_event_handler(event):
        if(event.message.message == 'lotOut(;;)'):
            print('---')
            print()
            #await client.log_out()
            await client.disconnect()
        print(event)
        senderInfo=93
        #print(type(event.message.to_id))
        if(type(event.message.to_id) is PeerUser):
            senderInfo=event.message.from_id
            print(event.message.from_id)
        elif(type(event.message.to_id) is PeerChannel):
            print(event.message.to_id.channel_id)
            senderInfo=event.message.to_id.channel_id
        elif(type(event.message.to_id) is PeerChat):
            print(event.message.to_id.chat_id)
            senderInfo=event.message.to_id.chat_id
        else:            
            print('not found type message')
            return
        if(senderInfo in channelsEntity):
            print('yes in list')
            await prepareMessageOnline(event.message,senderInfo)
        else:
            print('no it isnt in list')
            print(senderInfo)

api_hash,api_id=init()
client = TelegramClient('anon', api_id, api_hash)
stocks=fill_namad()
del stocks[-1]
normalizer = Normalizer()
channels = get_channel()
max_year=2019
with client:
    client.loop.run_until_complete(setEventToGetMessages(channels))
    client.loop.run_until_complete(getAllMessages(channels))
    client.run_until_disconnected()
    f.close()

