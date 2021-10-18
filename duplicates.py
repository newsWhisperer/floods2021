import files
import pandas as pd

from pathlib import Path
import os.path

import hashlib
from difflib import SequenceMatcher
import datetime
from dateutil import parser

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

DATA_PATH = Path.cwd()

newsFiles = files.getNewsFiles(state='harvest')

for newsFileHarvest in newsFiles:
    newsFileSingular = newsFileHarvest.replace('_harvest_','_singular_')
    
    df1 = pd.read_csv(newsFileHarvest, delimiter=',',index_col='index')
    df1['md5'] = ''
    df1['group'] = ''
    df1['similarity'] = 0.0
    df1 = df1.sort_values(by=['published'], ascending=True)

    for index, column in df1.iterrows():
        quote = str(column['domain']) + ' ' + str(column['title']) + ' ' + str(column['description']) + ' ' + str(column['content'])
        if(len(str(column['quote'])) > 20):
            quote = str(column['domain']) + ' ' + str(column['quote'])
        md5 = hashlib.md5(quote.encode('utf-8')).hexdigest()
        df1.loc[index,'md5'] = md5

        pubDate = parser.parse(column['published'])
        day = pubDate.strftime('%Y-%m-%d')
        groupTxt = str(column['domain']) +  ' ' + day
        group = hashlib.md5(groupTxt.encode('utf-8')).hexdigest()  
        df1.loc[index,'group'] = group

    df1 = df1[~df1.md5.duplicated(keep='first')]  

    for index1, column1 in df1.iterrows():
        quote1 = str(column1['title']) + ' ' + str(column1['description']) + ' ' + str(column1['content'])
        if(len(str(column1['quote'])) > 20):
            quote1 = str(column1['quote'])
        df2 = df1[df1['group']==column1['group']]
        for index2, column2 in df2.iterrows():
            if(column1['md5']>column2['md5']):
                quote2 = str(column2['title']) + ' ' + str(column2['description']) + ' ' + str(column2['content'])
                if(len(str(column2['quote'])) > 20):
                    quote2 = str(column2['quote'])
                similarity = similar(quote1,quote2)
                if(similarity > df1.loc[index1,'similarity']):
                    df1.loc[index1,'similarity'] = similarity

    df3 = df1[df1['similarity']<0.8]
    df3.drop(columns=['md5', 'group', 'similarity'])
    df3.to_csv(newsFileSingular, index_label='index')

