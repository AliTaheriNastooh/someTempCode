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
f=open('metadataFinder\output_logstash.json','a',encoding='utf-8')
f2=open('metadataFinder\output2.txt','w',encoding='utf-8')

def removeMessage(input_list):
    mongoreport = dbMongo.telegram.delete_many({'_id':{'$in':input_list}})
    if mongoreport.raw_result['n'] == len(input_list) :
        print('remove complete ',mongoreport.raw_result['n'])
    else:
        pprint.pprint('remove failed')
        pprint.pprint(mongoreport.raw_result)
        pprint.pprint(input_list)

def updateMessage(input_list):
    mongoreport = dbMongo.telegram.update({'_id':{'$in': input_list}},{'$set':{'message.read':1}},multi=True )
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
    print(data_input, file=f) 

def process_message(messages):
    useful_list=[]
    useless_list=[]
    for message in messages:
        flag=False
        message_content = message['message']['content'] 
        for name in stock_name:
            if message_content!=None and  name in message_content:
                flag=True
                break
        if flag:
            writeJsonOpjectToLogstash(message['message'])
            writeJsonOpject(message)
            useful_list.append(ObjectId(message['_id']))
        else:
            useless_list.append(ObjectId(message['_id']))
    removeMessage(useless_list)
    updateMessage(useful_list)        
def fill_namad():
    f = open(currentPath+r'\crawlerTelegram\name.txt','r',encoding='utf-8')
    namad=f.read()
    f.close()
    return namad.split('\n')



stock_name = fill_namad()
del stock_name[-1]
 
while counter_while<5:
    messages= dbMongo.telegram.find({'message.read':0}).limit(5)
    process_message(messages)
    print(' ---------- ',messages.count(True))
    counter_while+=1
