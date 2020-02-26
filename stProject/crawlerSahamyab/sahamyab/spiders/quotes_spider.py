import scrapy
import json
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
from scrapy.conf import settings
import os
import pymongo
f=open('myali.json','w',encoding='utf-8')
debu=open('debug.json','w',encoding='utf-8')

# execute below command for collecting comments:
# scrapy crawl sahamyabComments -o data.jl

stock_name = "خساپا"

class SahamyabCommentsSpider(scrapy.Spider):
    name = "sahamyabComments"
    url = 'https://www.sahamyab.com/guest/twiter/list?v=0.1'
    baseUrlImage='https://www.sahamyab.com/guest/image/generic/'
    globalVersion=1
    currentPath=os.path.abspath(os.getcwd())
    last_comment_id_prev=0
    max_try=5
    count_try=0

    def createJson(self,id,content,date,senderUsername,senderName,likeCount,parentId,image,version):
        myJson={
            'message ':{
                'id': id,
                'content': content,
                'senderUsername': senderUsername,
                'senderName': senderName,
                'likeCount': likeCount,
                'parentId': parentId,
                'image': image,
                'version': version,
            }
        }
        self.writeJsonOpject(myJson)
        self.writeJsonOpjectToMongo(myJson)
    
    def writeJsonOpjectToMongo(self,jsonObject):
        self.collection.insert(jsonObject)
        #self.dbMongo.sahamyab.insert_one(jsonObject)
    
    def writeJsonOpject(self,jsonObject):
        json.dump(jsonObject,f,ensure_ascii=False, indent=4, sort_keys=True, default=str)
        f.flush()

    def __init__(self):#delay between two consecutive requests
        #self.download_delay = 1.5
        connection = pymongo.MongoClient(settings['MONGODB_SERVER'],settings['MONGODB_PORT'])
        db = connection[settings['MONGODB_DB']]
        self.collection = db[settings['MONGODB_COLLECTION']]

    def start_requests(self):#first request for collecting comments
        request = scrapy.Request(url=SahamyabCommentsSpider.url, callback=self.parse, method='POST', body=json.dumps({ "page": 0,  })) #"tag": stock_name
        request.meta['page_number'] = 0
        yield request

    def parse(self, response):
        responseSplit=response.url.split('/')
        if str(responseSplit[-3]) == 'image':
            filename = '%s.jpg' % responseSplit[-1]
            with open(filename, 'wb') as tPhoto:
                tPhoto.write(response.body)
            
            imagepathUri = self.currentPath+filename
            debu.write('write image -'+imagepathUri+'\n')
            yield response
        else:
            if response.status == 404:
                page_number = response.meta['page_number']
                last_comment_id = response.meta['last_comment_id']
                f.write('\n')
                yield '\n'
            else:
                body = json.loads(response.body)
                page_number = response.meta['page_number']
                debu.write(str(body['errorCode'])+' '+str(page_number)+'\n')
                debu.flush()
                if body['errorCode'] == '0000':
                    page_number = response.meta['page_number'] + 1
                    debu.write(str(body['errorCode'])+'\n')
                    debu.flush()
                    last_comment_id = body['items'][9]['id']
                    self.last_comment_id_prev=last_comment_id
                    for onequote in body['items']:
                        likeCount= '0'
                        parentId= '0'
                        imageUid = ''
                        flagDownloadImage = False
                        if('likeCount' in onequote):
                            likeCount=onequote['likeCount']
                        if 'parentId' in onequote:
                            parentId = onequote['parentId']
                        if 'imageUid' in onequote:
                            imageUid = onequote['imageUid']
                            flagDownloadImage=True
                        self.createJson(onequote['id'],onequote['content'],onequote['sendTime'],onequote['senderUsername'],onequote['senderName'],likeCount,parentId,imageUid,self.globalVersion)
                        if flagDownloadImage:
                            yield scrapy.Request(url=self.baseUrlImage+imageUid, callback=self.parse)
                    yield body
                else:
                    last_comment_id=self.last_comment_id_prev
                    self.count_try +=1
                    debu.write(str(response.body)+'\n'+str(response.meta)+'\n')
                    if self.count_try > self.max_try:
                        page_number+=1
                        self.count_try=0

            request = scrapy.Request(url=SahamyabCommentsSpider.url, callback=self.parse, method='POST', dont_filter=True,
                                    body=json.dumps({"page": page_number, "id": str(last_comment_id), })) #"tag": stock_name
            request.meta['page_number'] = page_number
            request.meta['last_comment_id'] = last_comment_id

            yield request


