import files
import dates
import pandas as pd

import io
import requests
from pathlib import Path
import os.path

import time
import datetime
from dateutil import parser

DATA_PATH = Path.cwd()

if(not os.path.exists(DATA_PATH / 'csv')):
    os.mkdir(DATA_PATH / 'csv')

#get news_1804_1910.csv from freidok:  doi.org/10.6094/UNIFR/223318
news2021Df = files.getDFfromFiledok("https://freidok.uni-freiburg.de/fedora/objects/freidok:223318/datastreams/FILE2/content", "news_flood_2021.csv", delimiter=',')




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


for index, column in news2021Df.iterrows():
    column['valid'] = 1
    column['content'] = ''
    column['quote'] = ''
    column['keyword'] = 'flood2021'
    print(column)
    addNewsToCollection(column)
storeCollection()





