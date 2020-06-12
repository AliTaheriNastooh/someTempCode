from telethon import TelegramClient, events
from telethon import utils
from telethon.tl.types import PeerUser, PeerChat, PeerChannel,Channel,User,Chat
import configparser
import os
from datetime import datetime
from elasticsearch import Elasticsearch

def init():
    config = configparser.ConfigParser()
    path=currentPath+r'\stProject\crawlerTelegram\teleConfig.ini'
    config.read(path)
    api_id=config.getint('Telegram','api_id_adv')
    api_hash=config['Telegram']['api_hash_adv']
    api_hash = str(api_hash)
    return api_hash,api_id

async def sendMessage(message):
    addHeader = '----گزارش سامانه-----'+'\n'+message
    await client.send_message(lonami_group, addHeader)

async def sendElasticsearchQuery1(type,key_query,value_query,value_field,p_field):
    requestBody = {}
    if type == 'uniqueCount':
        requestBody={  
                    "query": {
                        "match": {
                        key_query: value_query
                        }
                    }, 
                    "size": 0,
                    "aggs": {
                        "my_count": {
                            "terms": {
                                "field": value_field,
                                "size":1000
                            }
                        }
                    }
                }
    print('elastic query')
    print(requestBody)
    aa = es.search(index="socialnetwork",body=requestBody)
    messageSendTelegram = ''
    if p_field == 'نماد':
        detective='#'
    else:
        detective = '@'
    if(len(aa['aggregations']['my_count']['buckets'])==0):
        messageSendTelegram ='موردی یافت نشد'
    else:
        for item in aa['aggregations']['my_count']['buckets']:
            messageSendTelegram+= (p_field+ ' : ' + detective+item['key'] + '  -----  ' + 'تعداد تکرار'+str(item['doc_count']) + '\n')
    print(messageSendTelegram)
    await sendMessage(messageSendTelegram)
    
async def sendElasticsearchQuery2(type,fromDate,toDate):
    requestBody = {}
    sizeRequest = 20
    if type == 'uniqueCount':
        requestBody={
                "query": {
                    "match_all": {}
                }, 
                "size": 0,
                "aggs": {
                    "my_count": {
                    "terms": {
                        "field": "stock",
                        "size": sizeRequest
                    },    
                    "aggs":{
                    "range":{
                        "date_range": {
                        "field": "messageDate",
                        "ranges": [
                            { "from": fromDate
                            }
                        ]
                        }
                    }
                    }
                    }

                }
            }
    print('elastic query')
    print(requestBody)
    aa = es.search(index="socialnetwork",body=requestBody)
    messageSendTelegram = ''
    if(len(aa['aggregations']['my_count']['buckets'])==0):
        messageSendTelegram ='موردی یافت نشد'
    else:
        mylist = []
        for item in aa['aggregations']['my_count']['buckets']:
            mylist.append((item['key'],item['range']['buckets'][0]['doc_count']))
        print(mylist)
        sortedList = sorted(mylist,key=lambda x: x[1],reverse=True)
        print(sortedList)
        for i in range(min(sizeRequest,len(sortedList))):
            messageSendTelegram+= ('نماد'+ ' : ' + '#' + sortedList[i][0]  + '\n')#+ '   ------   ' + 'تعداد تکرار'+str(sortedList[i][1] )
    print(messageSendTelegram)
    await sendMessage(messageSendTelegram)

    
async def processMessage(messageWords):
    query_type = ' '
    p_field='نماد'
    if messageWords[1] == 'تحلیل_بازار':
        if messageWords[2] == 'سهام':
            await sendElasticsearchQuery2('uniqueCount',messageWords[3],messageWords[4])
    else:
        query_type = 'uniqueCount'
        if messageWords[1] == 'تحلیل_سهام':
            
            if messageWords[2] == 'فرد':
                p_field='فرد'
                key_query = 'stock'
                value_query = messageWords[3]
                value_field = "senderUsername"
            elif messageWords[2] == 'گروه':
                p_field='گروه'
                key_query = 'stock'
                value_query = messageWords[3]
                value_field = "channelUsername"
        if messageWords[1] == 'تحلیل_گروه':
                p_field='نماد'
                key_query = 'channelUsername'
                value_query = messageWords[2]
                value_field = "stock"
        if messageWords[1] == 'تحلیل_فرد':
                p_field='نماد'
                key_query = 'senderUsername'
                value_query = messageWords[2]
                value_field = "stock"
        
        print('processMessage')
        await sendElasticsearchQuery1(query_type,key_query,value_query,value_field,p_field)
    


async def preProcessMessage(message):
    content = message.message
    words = content.split()
    print('words split')
    print(words)
    print(words[0])
    if len(words)== 0:
        return
    if words[0] == 'گزارش':
        await processMessage(words)
    else:
        print('noooo')



async def setEventToGetMessages():
    await client.get_dialogs()
    temp=await client.get_entity(groupUsername)
    groupId = temp.id    
    @client.on(events.NewMessage(incoming=True,outgoing=True))
    async def my_event_handler(event):
        if(event.message.message == 'lotOut(;;)'):
            print('---')
            print()
            #await client.log_out()
            await client.disconnect()
        
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
        if(senderInfo == groupId):
            
            message = event.message
            print(event)
            await preProcessMessage(message)
            print('yes in list')
        else:
            print('no it isnt in list')

es = Elasticsearch()
lonami_group = 493888855
groupUsername = 'https://t.me/joinchat/Bn-A6B1wJVewog2VvkyHow'
currentPath=os.path.abspath(os.getcwd())
api_hash,api_id=init()
client = TelegramClient('anon', api_id, api_hash)
with client:
    #client.loop.run_until_complete(sendMessage('yesss'))
    client.loop.run_until_complete(setEventToGetMessages())
    client.run_until_disconnected()