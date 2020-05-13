import scrapy
import json
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
from scrapy.conf import settings
import time
import os
import pymongo
import configparser
import sys
f=open('myali.json','w',encoding='utf-8')
debu=open('debug.json','w',encoding='utf-8')

# execute below command for collecting comments:
# scrapy crawl sahamyabComments -o data.jl

stock_name = "خساپا"

class SahamyabCommentsSpider(scrapy.Spider):
    name = "sahamyabComments"
    urlTwit = 'https://www.sahamyab.com/app/twiter/list?v=0.1'
    urlLogin = 'https://www.sahamyab.com/api/login'
    urlChangeToken = 'https://www.sahamyab.com/auth/realms/sahamyab/protocol/openid-connect/token'
    baseUrlImage='https://www.sahamyab.com/guest/image/generic/'
    globalVersion=1
    sahamyabTwitChannelIdInMongo = -1000
    sahamyabChartChannelIdInMongo = -2000
    currentPath=os.path.abspath(os.getcwd())
    lastMessageId=-1
    max_try=5
    count_try=0
    accessToken=''
    refreshToken=''
    username = ''
    password = ''
    state = 'twit'

    def createJson(self,id,content,date,senderUsername,senderName,likeCount,parentId,image,version):
        myJson={
            'message':{
                'id': int(id),
                'content': content,
                'date':date,
                'senderUsername': senderUsername,
                'senderName': senderName,
                'likeCount': int(likeCount),
                'parentId': int(parentId),
                'image': image,
                'version': version,
                'read':0,
            }
        }
        #self.writeJsonOpject(myJson)
        self.writeJsonOpjectToMongo(myJson)
    
    def writeJsonOpjectToMongo(self,jsonObject):
        self.collection.insert(jsonObject)
        #self.dbMongo.sahamyab.insert_one(jsonObject)
    

    def initUseAndPass(self):
        config = configparser.ConfigParser()
        path=self.currentPath+r'\sahamyabConfig.ini'
        config.read(path)
        self.username=config.get('Sahamyab','username')
        self.password=config.get('Sahamyab','password')
        print(self.username+self.password)

    def writeJsonOpject(self,jsonObject):
        json.dump(jsonObject,f,ensure_ascii=False, indent=4, sort_keys=True, default=str)
        f.flush()

    def getLastMessageIdFromMongo(self,channelId):
        lastMessageIdCollect = self.lastMessageIdCollection.find({'channelId':channelId})
        if lastMessageIdCollect.count() >= 1:
            return lastMessageIdCollect[0]['lastMessageId']
        else:
            return -1

    def addLastMessageIdToMongo(self,lastMessageId,channelId):
        self.lastMessageIdCollection.insert_one({'channelId':channelId,'lastMessageId':lastMessageId})

    def updateLastMessageIdToMongo(self,lastMessageId,channelId):
        self.lastMessageIdCollection.update({'channelId':channelId},{'$set':{'lastMessageId':lastMessageId} })

    def get_lastMessageId(self,channelId):
        lastMessageId = self.getLastMessageIdFromMongo(channelId)
        if lastMessageId == -1:
            self.addLastMessageIdToMongo(-2,channelId)
        return lastMessageId

    def __init__(self):#delay between two consecutive requests
        #self.download_delay = 1.5
        connection = pymongo.MongoClient(settings['MONGODB_SERVER'],settings['MONGODB_PORT'])
        db = connection[settings['MONGODB_DB']]
        self.collection = db[settings['MONGODB_COLLECTION']]
        self.lastMessageIdCollection = db[settings['MONGODB_LASTMESSAGEID_COLLECTION']]
        self.state='twit'
        


    def start_requests(self):#first request for collecting comments
        self.initUseAndPass()
        request = scrapy.Request(url=SahamyabCommentsSpider.urlLogin, callback=self.parseLogin, method='GET', body=json.dumps({"username":self.username,"password":self.password,"captchaAnswer":"66577","captchaId":"73ddis2d7b4ghifneioh7e29q6","f":"7b1693f44581b978379ba11a1dd40b4d"})) #
        yield request

    def firstRequstToGetTwit(self,chart):
        headers = {'Authorization' : 'Bearer %s' % self.accessToken}
        if chart :
            requestBody ={ "page": 0,"chart":True,  }
        else:
            requestBody ={ "page": 0,  }
        request = scrapy.Request(url=SahamyabCommentsSpider.urlTwit,headers = headers, callback=self.parse, method='GET', body=json.dumps(requestBody)) #"tag": stock_name
        request.meta['page_number'] = 0
        request.meta['chart']=chart
        debu.write('\n first request= '+str(request.meta))
        debu.flush()
        return request

    def getNextTwit(self,page_number,last_comment_id,chart):
        headers = {'Authorization' : 'Bearer %s' % self.accessToken}
        if chart :
            requestBody ={"page": page_number, "id": str(last_comment_id),"chart":True }
        else:
            requestBody ={"page": page_number, "id": str(last_comment_id), }
        request = scrapy.Request(url=SahamyabCommentsSpider.urlTwit,headers = headers, callback=self.parse, method='POST', dont_filter=True, body=json.dumps(requestBody))
        request.meta['page_number'] = page_number
        request.meta['last_comment_id'] = last_comment_id
        request.meta['chart']=chart
        debu.write('\n request= '+str(requestBody)+'  -- '+str(request.meta))
        debu.flush()
        return request

    def changeToken(self,pageNumber,lastCommentId):
        form_data = {
            'refresh_token': self.refreshToken,
            'client_id': 'sahamyab',
            'grant_type': 'refresh_token',
            # 'uf': 'RS',
        }
        request = scrapy.FormRequest(url=SahamyabCommentsSpider.urlChangeToken, callback=self.parseChangeToken, method='POST', formdata=form_data)
        request.meta['pageNumber']=pageNumber
        request.meta['lastCommentId']=lastCommentId
        return request

    def parseChangeToken(self,response):
        myresp=json.loads(response.body)
        debu.write(self.accessToken)
        debu.write('\n')
        debu.write(self.refreshToken)

        self.accessToken=myresp['access_token']
        self.refreshToken=myresp['refresh_token']
        debu.write('new\n')
        debu.write(self.accessToken)
        debu.write('\n')
        debu.write(self.refreshToken)
        #print(response.body)
        yield self.getNextTwit(response.meta['pageNumber'],response.meta['lastCommentId'],response.meta['chart'])

    def parseLogin(self,response):
        myresp=json.loads(response.body)
        self.accessToken=myresp['access_token']
        self.refreshToken=myresp['refresh_token']
        print(response.body)
        yield self.changeState()
        

    def parseImage(self, response):
        if response.status != 404:
            responseSplit=response.url.split('/')
            filename = '%s.jpg' % responseSplit[-1]
            with open(filename, 'wb') as tPhoto:
                tPhoto.write(response.body)
            imagepathUri = self.currentPath+filename
            debu.write('write image -'+imagepathUri+'\n')
            yield response
        else:
            debu.write('cant get image -'+response+'\n')
            if(response.meta['requestCount']<5):
                requestImage = scrapy.Request(url=response.url, callback=self.parseImage)
                requestImage.meta['requestCount']=response.meta['requestCount']+1
                yield requestImage

    def changeState(self):
        debu.write('\n change state'+str(self.state))
        debu.flush()
        if self.state =='twit':
            self.lastMessageId = self.get_lastMessageId(self.sahamyabTwitChannelIdInMongo)
            self.state = 'chart'
            return self.firstRequstToGetTwit(False)
            
        elif self.state == 'chart':
            self.state = 'sleep'
            self.lastMessageId = self.get_lastMessageId(self.sahamyabChartChannelIdInMongo)
            return self.firstRequstToGetTwit(True)
        elif self.state == 'sleep':
            time.sleep(1)
            self.state = 'twit'
            return self.changeState()# problem and 
        else:
            print('unknown state')
            quit(1)
        


    def parse(self, response):
        page_number=0
        last_comment_id=0
        chart_enable = False
        if response.status == 404:
            page_number = response.meta['page_number']
            last_comment_id = response.meta['last_comment_id']
            f.write('\n')
            yield '\n'
        else:
            body = json.loads(response.body)
            page_number = response.meta['page_number']
            chart_enable = response.meta['chart']
            debu.write('error code:'+str(body['errorCode'])+' '+str(page_number)+'\n')
            debu.flush()
            if body['errorCode'] == '0000':
                debu.write(str(body))
                debu.flush()
                page_number = response.meta['page_number'] + 1
                last_comment_id = body['items'][9]['id']
                if page_number == 1:
                    channelId = self.sahamyabChartChannelIdInMongo if response.meta['chart'] else self.sahamyabTwitChannelIdInMongo
                    debu.write('\n channelId'+str(channelId))
                    debu.flush()
                    self.updateLastMessageIdToMongo(body['items'][0]['id'],channelId)
                for onequote in body['items']:
                    if onequote['id'] == self.lastMessageId:
                        yield self.changeState()
                        return
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
                    '''
                    if flagDownloadImage:
                        debu.write('want to download'+imageUid)
                        requestImage=scrapy.Request(url=self.baseUrlImage+imageUid, callback=self.parseImage)
                        requestImage.meta['requestCount']=0
                        yield requestImage
                    '''
                yield self.getNextTwit(page_number,last_comment_id,chart_enable)
            elif body['errorCode'] == '1006':
                debu.write('changeToken\n')
                yield self.changeState()
                return
                #yield self.changeToken(response.meta['page_number'],response.meta['last_comment_id'])
            else:
                print('unrecognize error\n')
                debu.write('unrecognize erro\n')
                yield self.changeState()
                return
        


