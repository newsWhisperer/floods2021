import secrets
import pandas as pd

from pathlib import Path
import os.path

#import requests
#from urllib.parse import urlparse
#import json
#import time
#import smtplib
#import random

import time
#import datetime
#from dateutil import parser

import geocoder
#1000 per hour! 10000 per day.

DATA_PATH = Path.cwd()

if(os.path.isfile(DATA_PATH / 'csv'/ 'geonames.csv')):
    locationsDF = pd.read_csv(DATA_PATH / 'csv'/ 'geonames.csv', delimiter=',',index_col='index')
    locationsDF = locationsDF.sort_values(by=['count'], ascending=False)
else:    
    locationsDF = pd.read_csv(DATA_PATH / 'csv'/ 'entities_locations.csv', delimiter=',')
    locationsDF['geonames'] = 0
    locationsDF['latitude'] = 0.0
    locationsDF['longitude'] = 0.0
    locationsDF['geotype'] = ''
    locationsDF['country'] = ''
    locationsDF.to_csv(DATA_PATH / 'csv'/ 'geonames.csv', index_label='index')

geonamesKey = 'GEONAMES_KEY'
geonamesKey = os.getenv('GEONAMES_KEY')
if(geonamesKey == '1a2b3c4d5'): 
    print('Please set geonames.org key in file: secrets.py');
    exit()

imax = 7000
for index, column in locationsDF.iterrows():
    if(imax>0):
        lang = str(column.language)
        phrase = str(column.phrase)
        if(str(column.geonames) == '0'):
            g = geocoder.geonames(phrase, lang=lang, key=geonamesKey)
            locationsDF.loc[index,'geonames'] = g.geonames_id
            locationsDF.loc[index,'latitude'] = g.lat
            locationsDF.loc[index,'longitude'] = g.lng
            locationsDF.loc[index,'geotype'] = g.feature_class
            locationsDF.loc[index,'country'] = g.country
            imax -= 1
            time.sleep(5) 
    else:
        print("daily geonames limit has been reached, please re-run later.")

locationsDF.to_csv(DATA_PATH / 'csv'/ 'geonames.csv', index_label='index')
