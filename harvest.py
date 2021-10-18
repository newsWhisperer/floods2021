import secrets
import os

import pandas as pd

from pathlib import Path
import os.path

import requests
from urllib.parse import urlparse
import json
import random

import time
import datetime
from dateutil import parser

DATA_PATH = Path.cwd()

keywordsDF = pd.read_csv(DATA_PATH / 'keywords.csv', delimiter=',',index_col='keyword')
searchWords = dict(zip(keywordsDF.index.values, keywordsDF.language.values))

stopDomains = ["www.mydealz.de", "www.techstage.de", "www.nachdenkseiten.de", "www.amazon.de", "www.4players.de", "www.netzwelt.de", "www.nextpit.de",
               "www.mein-deal.com", "www.sparbote.de", "www.xda-developers.com" "www.pcgames.de", "blog.google", "www.ingame.de", "playstation.com",
               "www.pcgameshardware.de", 
                ]

                 
def dataIsNotBlocked(data):
    for blocked in stopDomains: 
        if blocked in data['domain']:
            return False
    return True         


collectedNews = {}

def addNewsToCollection(data):
    global collectedNews
    pubDate = parser.parse(data['published'])
    fileDate = 'news_harvest_'+pubDate.strftime('%Y_%m')+'.csv'
    if(not fileDate in collectedNews):
        if(os.path.isfile(DATA_PATH / 'csv' / fileDate)):
            df = pd.read_csv(DATA_PATH / 'csv' / fileDate, delimiter=',',index_col='index')
            collectedNews[fileDate] = df.to_dict('index')
        else:
            collectedNews[fileDate] = {}
    if(not data['url'] in collectedNews[fileDate]):
        data = archiveUrl(data)
        collectedNews[fileDate][data['url']] = data
        return True
    return False

def storeCollection():
    global collectedNews
    cols = ['url','valid','domain','title','description','image','published','archive','content','quote','language','keyword']
    for dateFile in collectedNews:
        df = pd.DataFrame.from_dict(collectedNews[dateFile], orient='index', columns=cols)
        if(not os.path.exists(DATA_PATH / 'csv')):
            os.mkdir(DATA_PATH / 'csv')
        df.to_csv(DATA_PATH / 'csv' / dateFile, index_label='index') 
    collectedNews = {}

def archiveUrl(data):
    timetravelDate = '19700101'
    pubDate = None
    try:
        pubDate = parser.parse(data['published'])
    except:
        print('date parse error 1')
    if(not pubDate):
      try:
        pubDate = parser.isoparse(data['published'])
      except:
        print('date parse error 2')   
    if(pubDate):
        timetravelDate = pubDate.strftime('%Y%m%d')
    timetravelUrl = 'http://timetravel.mementoweb.org/api/json/'+timetravelDate+'/'+data['url']
    try:
        page = requests.get(timetravelUrl, timeout=10)
        if page.status_code == 200:
            content = page.content
            if(content):
                print(content)
                jsonData = json.loads(content)
                if(jsonData and jsonData['mementos']):
                    data['archive'] = jsonData['mementos']['closest']['uri'][0]
                    if('1970-01-01T00:00:00' == data['published']):
                        data['published'] = jsonData['mementos']['closest']['datetime']
    except requests.exceptions.RequestException as e:  
        print("not archived yet")
        saveUrl = 'https://web.archive.org/save/' + data['url'] 
        try:
            page = requests.get(saveUrl, timeout=240)  
            if page.status_code == 200:
                print('archived!')
        except requests.exceptions.RequestException as e2:
            print("not archivable: " + data['url'])
    return data 

def inqRandomNews():
    apiKey = os.getenv('NEWSAPI_KEY')
    if(apiKey == '1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7'): 
        print('Please set newsapi.org key in file: secrets.py');
        return None
 
    keyWord = random.choice(list(searchWords.keys()))
    language = searchWords[keyWord]
    if(not 'xx'==language):
        page = random.choice(['1','2','3','4','5'])  
        sort = random.choice(['relevancy', 'popularity', 'publishedAt'])
        print('keyword: '+keyWord+'; Page: '+page)
        url = ('https://newsapi.org/v2/everything?'
            'q='+keyWord+'&'
            'language='+language+'&'
            'page='+page+'&'
            'sortBy='+sort+'&'
            'apiKey='+apiKey
            )
        response = requests.get(url)
        response.encoding = response.apparent_encoding
        foundNew = False
        if(response.text):
            jsonData = json.loads(response.text)
            if (('ok'==jsonData['status']) and (jsonData['totalResults']>0)):
                for article in jsonData['articles']:
                    title = article['title']
                    description = article['description']
                    url = article['url']
                    url = url.replace('https://www.zeit.de/zustimmung?url=', '')
                    url = url.replace('%3A', ':')
                    url = url.replace('%2F', '/')                
                    domain = urlparse(url).netloc
                    image = article['urlToImage']
                    published = article['publishedAt']
                    content = article['content']
                    data = {'url':url, 'valid':0, 'domain':domain,'published':published, 'description':description, 'title':title, 
                            'image':image, 'content':content, 'quote':'', 'language': language, 'keyword':keyWord}
                    if (dataIsNotBlocked(data)):                    
                        print(str(keyWord)+': '+str(title)+' '+str(url))
                        if(addNewsToCollection(data)):
                            foundNew = True
                            time.sleep(random.uniform(110.5, 125.5))
                        else:
                            time.sleep(45)
                storeCollection()
            else:
                print(response.text)   
                time.sleep(400) 
        if(not foundNew):
            print("Nothing new")
            searchWords.pop(keyWord)

i=1
while True:
  print(i)  
  inqRandomNews()
  i += 1
  time.sleep(1000)
