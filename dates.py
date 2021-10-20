#import time
import datetime
from dateutil import parser

def getDay(dateString):
    timeDate = '1970-01-01'
    pubDate = None
    try:
        pubDate = parser.parse(dateString)
    except:
        print('date parse error 1')
    if(not pubDate):
      try:
        pubDate = parser.isoparse(dateString)
      except:
        print('date parse error 2')   
    if(pubDate):
        timeDate = pubDate.strftime('%Y-%m-%d')
    return timeDate  