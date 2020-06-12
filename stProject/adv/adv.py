from telethon import TelegramClient, events
from telethon import utils
import configparser
from pymongo import MongoClient
import os
from telethon.tl.types import PeerUser
import time

currentPath=os.path.abspath(os.getcwd())
clientMongo = MongoClient('mongodb://127.0.0.1:27017/?compressors=disabled&gssapiServiceName=mongodb')
db=clientMongo.stock

def getUserFromMongo(userId):
    userIdCollect = db.sendusers.find({'userId':userId})
    if userIdCollect.count() >= 1:
        return userIdCollect[0]
    else:
        return None

def addUserToMongo(userId):
    db.sendusers.insert_one({'userId':userId})

async def getUser():
    entity = await client.get_entity('@ATN508')

    # Do you have a conversation open with them? Get dialogs.
    await client.get_dialogs()

    # Are they participant of some group? Get them.
    await client.get_participants('TelethonChat')

    # Is the entity the original sender of a forwarded message? Get it.
    await client.get_messages('TelethonChat', 100)
    users = db.users.find()
    limitSendMessage = min(100,users.count())
    sendMessageNum = 0
    i=0
    while sendMessageNum <= limitSendMessage:
        tmpUserId = users[i]['userId']
        sendUser = getUserFromMongo(tmpUserId)
        print(users[i],sendUser)
        if sendUser == None:
            addUserToMongo(tmpUserId)
            if users[i]['username'] == None:
                sendMessageNum += await sendMessage(tmpUserId)
            else:
                sendMessageNum += await sendMessage(users[i]['username'])
        print('sendMessageNum',sendMessageNum)
        i+=1
def init():
    config = configparser.ConfigParser()
    path=currentPath+r'\stProject\crawlerTelegram\teleConfig.ini'
    config.read(path)
    api_id=config.getint('Telegram','api_id_adv')
    api_hash=config['Telegram']['api_hash_adv']
    api_hash = str(api_hash)
    return api_hash,api_id

async def sendMessage(userId):
    print(userId)
    try:
        lonami = await client.get_entity(userId)
    except:
        return 0
    await client.send_message(lonami, '''
سلام 
ببخشید مزاحمتون میشم
من از طریق گروه های بورسی تلگرام با شما آشنا شدم
ما جمعی از فعالان بازار سرمایه کانالی را راه‌اندازی کرده‌ که به دنبال افزایش اطلاعات بورسی سرمایه گذاران هستیم. در این زمینه در کانال خود انواع آموزش‌ها را به شیوه‌های متفاوت ارائه میکنیم. همچنین سامانه‌ایی را طراحی کردیم که اطلاعات مفید و کارایی را همچون شناسایی افراد هوشمند در بورس و بررسی پرتوی آن‌ها، پیگیری تحرکات سهامداران کلان حقیقی در نمادهای مختلف ،نمایش نمادهای عقب مانده و تشخیص شباهت سهم‌ها جمع‌آوری میکند. ما این اطلاعات را به صورت رایگان در کانال با شما به اشتراک میگذاریم. ممنون میشم نگاهی به کانال ما بندازید و در صورت تمایل عضو بشید. https://t.me/bcrows
''')
    print('sendMessage')    
    time.sleep(60)
    return 1


api_hash,api_id=init()
print(api_hash)
#getUser()
#print(db.users.find()[0])

client = TelegramClient('anon', api_id, api_hash)
with client:
    #client.loop.run_until_complete(setEventToGetMessages(channels))
    client.loop.run_until_complete(getUser())
    #client.run_until_disconnected()

