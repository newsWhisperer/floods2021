import files
import pandas as pd

from pathlib import Path
import os.path
import re

replaceStrings = {r'… \[\+\d+ chars\]':r'', r'<li>':r' ' ,r'</li>':r' ',r'<ul>':r' ',r'</ul>':r' ',r'<ol>':r' ',r'</ol>':r' ',r'\+\+\+':r' '}

DATA_PATH = Path.cwd()

newsFiles = files.getNewsFiles(state='mining')

for newsFileMining in newsFiles:
    newsFileHarvest = newsFileMining.replace('_mining_','_harvest_')

    dfH = pd.read_csv(newsFileHarvest, delimiter=',',index_col='index')
    diH = dfH.to_dict('index')

    dfM = pd.read_csv(newsFileMining, delimiter=',',index_col='index')
    diM = dfM.to_dict('index')

    for index in diH:
        if(index in diM):
            if(64000 > len(str(diM[index]['quote'])) > 10):
                diH[index]['quote'] = diM[index]['quote']
            diH[index]['archive'] = diM[index]['archive']
            
            if(isinstance(diH[index]['content'], str)):
                for pattern in replaceStrings:
                    newString = replaceStrings[pattern]    
                    diH[index]['content'] = re.sub(pattern, newString, diH[index]['content'])  

    cols = ['url','valid','domain','title','description','image','published','archive','content','quote','language','keyword']
    dfN = pd.DataFrame.from_dict(diH, orient='index', columns=cols)
    dfN.to_csv(newsFileHarvest, index_label='index')         


