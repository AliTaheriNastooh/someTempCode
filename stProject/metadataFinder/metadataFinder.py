from pymongo import MongoClient
from bson.objectid import ObjectId
import pprint
import os
import json

clientMongo = MongoClient('mongodb://127.0.0.1:27017/?compressors=disabled&gssapiServiceName=mongodb')
dbMongo=clientMongo.stock
dbMongo.telegram
counter_while=0
currentPath=os.path.abspath(os.getcwd())
print('path: '+currentPath)
f=open(currentPath+'\stProject\metadataFinder\output_logstash.json','a',encoding='utf-8')
f2=open(currentPath+'\stProject\metadataFinder\output2.txt','w',encoding='utf-8')

def removeMessage(input_list,source):
    if source == 'sahamyab':
        mongoreport = dbMongo.sahamyab.delete_many({'_id':{'$in':input_list}})
    elif source == 'telegram':
        mongoreport = dbMongo.telegram.delete_many({'_id':{'$in':input_list}})
    else:
        print('error in source -- removeMessage function')
    if mongoreport.raw_result['n'] == len(input_list) :
        print('remove complete ',mongoreport.raw_result['n'])
    else:
        pprint.pprint('remove failed')
        pprint.pprint(mongoreport.raw_result)
        pprint.pprint(input_list)

def updateMessage(input_list,source):
    if source == 'sahamyab':
        mongoreport = dbMongo.sahamyab.update({'_id':{'$in': input_list}},{'$set':{'message.read':1}},multi=True )
    elif source == 'telegram':
        mongoreport = dbMongo.telegram.update({'_id':{'$in': input_list}},{'$set':{'message.read':1}},multi=True )
    else:
        print('error in source -- removeMessage function')
    if mongoreport['n'] == len(input_list):
        print('upadate complete ', mongoreport['n'])
    else:
        pprint.pprint('update failed')
        pprint.pprint(mongoreport.raw_result)
        pprint.pprint(input_list)

def writeJsonOpject(jsonObject):
    json.dump(jsonObject,f2,ensure_ascii=False,default=str, indent=4, sort_keys=True, )#
    f.flush()

def writeJsonOpjectToLogstash(data_input):
    #print(data_input, file=f) 
    json.dump(data_input, f)
    

def getSentimentMessage(message):
    return 'nothing'

def preparing_telegram_message_for_logstash(message,stockName):
    messageSentiment = getSentimentMessage(message)
    prepareJson={
        'message':{
            'id':message['message']['id']  ,
            'content': message['message']['content'] ,
            'date': message['message']['date'] ,
            'senderId': message['message']['senderId'] ,
            'senderUserName': message['message']['senderUsername'],
            'senderName': message['message']['senderName'],
            'isGroup': message['message']['isGroup'],
            'channelUserName': message['message']['channelUsername'],
            'channelName': message['message']['channelName'],
            'channelId': message['message']['channelId'],
            'parentId': message['message']['parentId'],
            'likeCount': 0,
            'source':'telegram',
            'stock':stockName,
            'sentiment':messageSentiment,
            'image': message['message']['image'],
            'version': message['message']['version'],
        }
    }
    writeJsonOpjectToLogstash(prepareJson)
    writeJsonOpject(message)

def preparing_sahamyab_message_for_logstash(message,stockName):
    messageSentiment = getSentimentMessage(message)
    prepareJson={
        'message':{
            'id':message['message']['id']  ,
            'content': message['message']['content'] ,
            'date': message['message']['date'] ,
            'senderId': None ,
            'senderUserName': message['message']['senderUsername'],
            'senderName': message['message']['senderName'],
            'isGroup': False,
            'channelUserName': 'sahamyab',
            'channelName': 'sahamyab',
            'channelId': None,
            'parentId': message['message']['parentId'],
            'likeCount': message['message']['likeCount'],
            'source':'sahamyab',
            'stock':stockName,
            'sentiment':messageSentiment,
            'image': message['message']['image'],
            'version': message['message']['version'],
        }
    }
    writeJsonOpjectToLogstash(prepareJson)
    writeJsonOpject(message)

def process_message(messages,source):
    useful_list=[]
    useless_list=[]
    for message in messages:
        messageStock='none'
        message_content = message['message']['content'] 
        for name in stock_name:
            if message_content!=None and  name in message_content:
                messageStock = name
                break
        if messageStock != 'none':
            if source == 'sahamyab':
                preparing_sahamyab_message_for_logstash(message,messageStock)
            elif source == 'telegram':
                preparing_telegram_message_for_logstash(message,messageStock)
            else:
                print('error in source -- process_messge function')
            useful_list.append(ObjectId(message['_id']))
        else:
            useless_list.append(ObjectId(message['_id']))
    removeMessage(useless_list,source)
    updateMessage(useful_list,source)
    
def fill_namad():
    f = open(currentPath+r'\stProject\crawlerTelegram\name.txt','r',encoding='utf-8')
    namad=f.read()
    f.close()
    return namad.split('\n')


stock_name = fill_namad()
del stock_name[-1]
while counter_while<5:
    messages= dbMongo.telegram.find({'message.read':0}).limit(5)
    process_message(messages,'telegram')
    messages= dbMongo.sahamyab.find({'message.read':0}).limit(5)
    process_message(messages,'sahamyab')
    print(' ---------- ',messages.count(True))
    counter_while+=1
