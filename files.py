import pandas as pd

from pathlib import Path
import os.path

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

#print(getNewsDF(state='harvest'))
print(getNewsFiles(state='harvest'))

