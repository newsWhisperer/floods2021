import pandas as pd

from pathlib import Path
import os.path
import io
import requests

import glob

DATA_PATH = Path.cwd()

def getNewsFiles(state='harvest'):
    fileName = './csv/news_????_??.csv'
    if(state):
        fileName = './csv/news_'+state+'_????_??.csv'
    files = glob.glob(fileName)
    return files    

def getNewsDFbyList(files):
    newsDF = pd.DataFrame(None)
    for file in files:
        df = pd.read_csv(file, delimiter=',')
        if(newsDF.empty):
            newsDF = df
        else:
            newsDF = pd.concat([newsDF, df])
    return newsDF  

def getNewsDF(state='singular'):
    files = getNewsFiles(state)
    newsDF = getNewsDFbyList(files)
    return newsDF            

#print(getNewsDF(state='singular'))
#print(getNewsFiles(state='harvest'))


def getDFfromFiledok(url, fileName, delimiter=','):
    if(os.path.isfile(DATA_PATH / 'csv' / fileName)):
        dataframe = pd.read_csv(DATA_PATH / 'csv' / fileName, delimiter=delimiter)
        return dataframe
    else:
        stream=requests.get(url).content         
        dataframe=pd.read_csv(io.StringIO(stream.decode('utf-8')), delimiter=delimiter)
        dataframe.to_csv(DATA_PATH / 'csv' / fileName, index=True) 
        return dataframe

