from pymongo import MongoClient
from bson.objectid import ObjectId
import pprint
import os
import json
import logging
import logstash

clientMongo = MongoClient('mongodb://127.0.0.1:27017/?compressors=disabled&gssapiServiceName=mongodb')
dbMongo=clientMongo.stock
dbMongo.telegram
host = 'localhost'
test_logger = logging.getLogger('python-logstash-logger')
test_logger.setLevel(logging.INFO)
test_logger.addHandler(logstash.TCPLogstashHandler(host, 5959, version=1))
counter_while=0
currentPath=os.path.abspath(os.getcwd())
print('path: '+currentPath)
#f=open(currentPath+'\stProject\metadataFinder\output_logstash.json','a',encoding='utf-8')
#f2=open(currentPath+'\stProject\metadataFinder\output2.txt','w',encoding='utf-8')

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
    f2.flush()

def writeJsonOpjectToLogstash(data_input):
    test_logger.info('some temp message',extra=data_input)
    #print(data_input, file=f) 
    #json.dump(data_input, f,ensure_ascii=False,default=str)
    #f.write('\n')
    #f.flush()

    

def getSentimentMessage(message):
    return 'nothing'
#'message':{
def preparing_telegram_message_for_logstash(message,stockName):
    messageSentiment = getSentimentMessage(message)
    prepareJson={  
        'messageId':message['message']['id']  ,
        'content': message['message']['content'] ,
        'messageDate': message['message']['date'] ,
        'senderId': message['message']['senderId'] ,
        'senderUsername': message['message']['senderUsername'],
        'senderName': message['message']['senderName'],
        'isGroup': message['message']['isGroup'],
        'channelUsername': message['message']['channelUsername'],
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
    writeJsonOpjectToLogstash(prepareJson)
    #writeJsonOpject(message)

def preparing_sahamyab_message_for_logstash(message,stockName):
    messageSentiment = getSentimentMessage(message)
    prepareJson={
        'messageId':message['message']['id']  ,
        'content': message['message']['content'] ,
        'messageDate': message['message']['date'] ,
        'senderId': None ,
        'senderUsername': message['message']['senderUsername'],
        'senderName': message['message']['senderName'],
        'isGroup': False,
        'channelUsername': 'sahamyab',
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
    writeJsonOpjectToLogstash(prepareJson)
    #writeJsonOpject(message)

def process_message(messages,source):
    useful_list=[]
    useless_list=[]
    for message in messages:
        messageStock='none'
        message_content = message['message']['content'] 
        if message_content==None:
                continue
        for name in stock_name:
            index = message_content.find(name)
            if index!= -1 and (index==0  or (message_content[index-1]=='#' or message_content[index-1].isspace())) and (index+len(name) >= len(message_content)  or (index+len(name) <len(message_content) and message_content[index+len(name)].isspace())):
                messageStock = name
                break
        if messageStock != 'none':
            if source == 'sahamyab':
                preparing_sahamyab_message_for_logstash(message,messageStock)
            elif source == 'telegram':
                preparing_telegram_message_for_logstash(message,messageStock)
            else:
                print('error in source -- process_messge function')
                continue
            useful_list.append(ObjectId(message['_id']))
        else:
            useless_list.append(ObjectId(message['_id']))
    removeMessage(useless_list,source)
    updateMessage(useful_list,source)
    
def fill_namad():
    #currentPath+
    f = open(r'E:\job\bourse\gitBourse\stProject\crawlerTelegram\name.txt','r',encoding='utf-8')
    namad=f.read()
    f.close()
    return namad.split('\n')


stock_name = fill_namad()
countMessage = -1 
while countMessage != 0:
    messages= dbMongo.telegram.find({'message.read':0}).limit(100)
    process_message(messages,'telegram')
    countMessage = messages.count(True)
countMessage = -1
while countMessage != 0:
    messages= dbMongo.sahamyab.find({'message.read':0}).limit(100)
    process_message(messages,'sahamyab')
    print(' ---------- ',messages.count(True))
    countMessage =messages.count(True)
