from telethon import TelegramClient, events
from telethon import utils
import configparser
from hazm import Normalizer
import sys
import json
from telethon.tl.types import PeerUser, PeerChat, PeerChannel,Channel,User,Chat
from pymongo import MongoClient
import os
import datetime
import pytz
from telethon.errors import FloodWaitError


#mishe aval kar hame aza yek channel ro begirim ke dge har dafeh bara har payam check nakonim vali ye fekri bara aza jadid begirm v aya chanal mishe aza ro begirim
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

def getLastMessageIdFromMongo(channelId):
    lastMessageIdCollect = dbMongo.lastMessageId.find({'channelId':channelId})
    if lastMessageIdCollect.count() >= 1:
        return lastMessageIdCollect[0]['lastMessageId']
    else:
        return -1
def addLastMessageIdToMongo(channelId,lastMessageId):
    dbMongo.lastMessageId.insert_one({'channelId':channelId,'lastMessageId':lastMessageId})

def updateLastMessageIdToMongo(channelId,lastMessageId):
    dbMongo.lastMessageId.update({'channelId':channelId},{'$set':{'lastMessageId':lastMessageId} })

def getUserFromMongo(userId):
    userIdCollect = dbMongo.users.find({'userId':userId})
    if userIdCollect.count() >= 1:
        return userIdCollect[0]
    else:
        return None

def addUserToMongo(userId,username,userName):
    dbMongo.users.insert_one({'userId':userId,'username':username,'userName':userName})

async def createJson(messageId,content,date,senderId,senderUserName,senderName,isGroup,channelUserName,channelName,parentId,image,version,lastMessageId,channelId):
    #date.isoformat()+'Z'
    myJson={
        'message':{
            'id':messageId,
            'content': content,
            'date': date.isoformat().replace("+00:00", "Z"),
            'senderId': senderId,
            'senderUsername': senderUserName,
            'senderName': senderName,
            'isGroup': isGroup,
            'channelUsername': channelUserName,
            'channelName': channelName,
            'parentId': parentId,
            'image': image,
            'version': version,
            'lastMessageId': lastMessageId,
            'channelId': channelId,
            'read':0,
        }
    }
    #writeJsonOpject(myJson)
    writeJsonOpjectToMongo(myJson)

async def getUser(userId):
    user = getUserFromMongo(userId)
    if user == None:
        print(userId)
        newUser= await client.get_entity(userId)
        if(newUser.first_name is None):
            newUser.first_name=''
        if(newUser.last_name is None):
            newUser.last_name=''   
        senderName=newUser.first_name+' '+newUser.last_name
        addUserToMongo(newUser.id,newUser.username,senderName)
        return {'userId':newUser.id,'username':newUser.username,'userName':senderName}
    else:
        return user
async def addMessage2(message,channel_group,channel,channelType):
    messageId=0
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
    #print(channel)
    #print(message)
    #print()
    messageId=message.id
    content=message.message
    date=message.date
    lastMessageId=message.id
    channelId=channel.id
    if message.photo:
        #path = await message.download_media()
        #actualPath=path
        #f = open(actualPath,'rb')
        #filedata = f.read()
        #image=filedata
        image='have image but lines that download the image are commented'
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
        isGroup=True
        channelUserName=channel.username
        channelName=channel.first_name+' '+channel.last_name
    elif(channelType=='Chat'):
        senderId=message.from_id
        newUser= await getUser(senderId)
        senderUserName=newUser['username'] 
        senderName=newUser['userName'] 
        isGroup=False
        channelUserName=None
        channelName=channel.title
    elif(channelType=='Channel'):
        if(channel_group==False):
            senderId=message.from_id
            newUser= await getUser(senderId)
            senderUserName=newUser['username']   
            senderName=newUser['userName'] 
            isGroup=True
        else:
            senderId=None
            senderUserName=None
            if(message.post_author is None):
                senderName=None
            else:
                senderName=message.post_author
            isGroup=False
        channelUserName=channel.username
        channelName=channel.title
    await createJson(messageId,content,date,senderId,senderUserName,senderName,isGroup,channelUserName,channelName,parentId,image,version,lastMessageId,channelId)

def get_lastMessageId(channelId):
    lastMessageId = getLastMessageIdFromMongo(channelId)
    if lastMessageId == -1:
        addLastMessageIdToMongo(channelId,-2)
    return lastMessageId

async def updateLastMessage(channel):
    lastMessage = await client.get_messages(channel)
    if len(lastMessage) > 0:
        updateLastMessageIdToMongo(channel.id, lastMessage[0].id)
    else:
        print('++++zero message+++',channel)

async def check_all_message(channel):
    try:
        channel= await client.get_entity(channel)
    except FloodWaitError as e:
        print('warning(we banned)--- Flood waited for', e.seconds)
        quit(1)
    except:
        print('all message -- channel:'+channel+' not found')
        return
    lastMessageId = get_lastMessageId(channel.id)
    await updateLastMessage(channel)
    #print(channel.title,'  : ',channel.id,' - lastMessage',lastMessageId)

    print('PeerChannel',channel)
    channelType=''
    if(type(channel) is User):
        channel_group=False
        channelType='User'
    elif(type(channel) is Channel):
        print('PeerChannel')
        channelType='Channel'
        if(channel.megagroup==True or channel.broadcast==False):
            channel_group=False
        else:
            channel_group=True
    elif(type(channel) is Chat):
        channelType='Chat'      
        channel_group=True

    async for message in client.iter_messages(channel):
        if message.date < minDate:
            break
        if message.id == lastMessageId:
            print('---lastMessageId--- ',message.id)
            break
        await addMessage2(message,channel_group,channel,channelType)

async def getAllMessages(channels):
    await client.get_dialogs()
    for channel in channels:
        await check_all_message(channel)

def init():
    config = configparser.ConfigParser()
    path=currentPath+r'\stProject\crawlerTelegram\teleConfig.ini'
    config.read(path)
    api_id=config.getint('Telegram','api_id')
    api_hash=config['Telegram']['api_hash']
    api_hash = str(api_hash)
    return api_hash,api_id

def get_channel():
    f = open(currentPath+r'\stProject\crawlerTelegram\channel_list.txt','r',encoding='utf-8')
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
    await client.get_dialogs()
    channelsEntity=[]
    for channel in channels:
        try:
            temp=await client.get_entity(channel)
            channelsEntity.append(temp.id)
        except:
            print('channel:'+channel+' not found')
        #print(temp)
        #print(temp.id)
        
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
normalizer = Normalizer()
channels = get_channel()
min_year=2020
min_month = 6
min_day = 7
minDate = datetime.datetime(min_year,min_month,min_day,tzinfo = pytz.UTC)
with client:
    #client.loop.run_until_complete(setEventToGetMessages(channels))
    client.loop.run_until_complete(getAllMessages(channels))
    #client.run_until_disconnected()
    f.close()

