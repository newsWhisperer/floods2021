import pandas as pd
import numpy as np
import math
import random
import re

import datetime
from dateutil import parser

import nltk
from HanTa import HanoverTagger as ht

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.patches as patches
import matplotlib.lines as mlines

import seaborn as sns

import folium
import webbrowser
from folium.plugins import HeatMap

import cartopy.crs as ccrs
import cartopy
import cartopy.feature as cfeature

from pathlib import Path
import os.path


DATA_PATH = Path.cwd()




colorsTopics = {
 #'Vulnerability': 'r',
 #'Wiederaufbau': 'y',
 #'Technischer HWS': 'r',  #
 #'Aufräumarbeit': 'g',
 'Wine': 'purple',
 #'Skeptiker': 'r',  #
 'Troublemakers': 'fuchsia',
 'Insurance': 'moccasin',
 'Risk': 'green',
 'Responsability': 'salmon',
 #'Soforthilfe': 'r',
 'Pollution': 'lime',
 'Health': 'gold',
 'Causes': 'darkcyan',
 'Warnings': 'darkorange',
 'Solidarity': 'greenyellow',
 #'Nachbarlaender': 0,
 #'Elsewhere': 0,
 'Infrastructure': 'darkgrey',
 'Rescue': 'olivedrab',
 'Politics': 'mediumpurple',
 'Damage':'firebrick', 
 'Weather': 'skyblue', #'saddlebrown', # 'chocolate', # 'deepskyblue',

 'Victims': 'red',
 #'Center': 0,

 'Flood Hazard': 'royalblue', # 'mediumblue',
}

 

collectedWeightTopicsMap = {}
weightMapTopics = {
 'Wine': 9.52,
 'Troublemakers': 5.01,
 'Insurance': 9.6,
 'Risk': 15.31,
 'Responsability': 9.54,
 'Pollution': 23.49,
 'Health': 9.48,
 'Causes': 25.9,
 'Warnings': 3.01,
 'Solidarity': 9.14,
 'Infrastructure': 0.9,
 'Rescue': 2.1,
 'Politics': 9.96,
 'Damage': 9.02, 
 'Weather': 2.5, #'saddlebrown', # 'chocolate', # 'deepskyblue',
 'Victims': 4.53,
 'Flood Hazard': 1.7, # 'mediumblue',
}

collectedWeightTopicsSentence = {}
weightSentenceTopics = {
 'Wine': 0.02,
 'Troublemakers': 0.16,
 'Insurance': 0.12,
 'Risk': 0.032,
 'Responsability': 0.1,
 'Pollution': 0.02,
 'Health': 0.021,
 'Causes': 0.023,
 'Warnings': 0.79,
 'Solidarity': 0.2,
 'Infrastructure': 0.34,
 'Rescue': 0.02,
 'Politics': 0.064,
 'Damage': 0.4, 
 'Weather': 0.7, #'saddlebrown', # 'chocolate', # 'deepskyblue',
 'Victims': 0.37,
 'Flood Hazard': 0.33, # 'mediumblue',
}


#if exists:
#load:  sentenceWeightsDF.to_csv("weights_topics_sentence.csv", index=True)  
#load:  mapWeightsDF.to_csv("weights_topics_map.csv", index=True) 
sentenceWeightsDF = pd.read_csv('weights_topics_sentence.csv', delimiter=',')

collectedWeightTopicsSentence = sentenceWeightsDF.to_dict('index')

mapWeightsDF = pd.read_csv('weights_topics_map.csv', delimiter=',')

collectedWeightTopicsMap = mapWeightsDF.to_dict('index')


floodsDF06 = pd.read_csv('news_2021_06_harvest.csv', delimiter=',')
floodsDF07 = pd.read_csv('news_2021_07_harvest.csv', delimiter=',')
floodsDF08 = pd.read_csv('news_2021_08_harvest.csv', delimiter=',')
floodsDF09 = pd.read_csv('news_2021_09_harvest.csv', delimiter=',')
floodsDF10 = pd.read_csv('news_2021_10_harvest.csv', delimiter=',')
floodsDF = pd.concat([floodsDF06,floodsDF07,floodsDF08,floodsDF09,floodsDF10])
#
##floodsDF = floodsDF09
print(floodsDF)
floodsDF = floodsDF[floodsDF['valid']==1]
floodsDF = floodsDF[floodsDF['language']=='de']
print(floodsDF)

import time

minDateA = np.min(floodsDF['published'])
maxDateA = np.max(floodsDF['published'])

def generateDataframeFractions(dfAll, steps=2400, span=24*60*60, start=1):
        dfAll = dfAll.sort_values(by=['published'], ascending=True)
        for i in range(0,5):
            yield [str(0).zfill(4), dfAll]
        minDateA = np.min(dfAll['published'])
        maxDateA = np.max(dfAll['published'])
        minTimeA = time.mktime(parser.parse(minDateA).timetuple())
        maxTimeA = time.mktime(parser.parse(maxDateA).timetuple())
        endTimeF = minTimeA
        beginTimeF = minTimeA
        df = dfAll.iloc[0:1]
        dfAll = dfAll[1:]
        delta = (maxTimeA-span-minTimeA)/steps
        for step in range(start,steps+1):
          beginTimeS = minTimeA+step*delta
          endTimeS = beginTimeS+span
          while(endTimeF < endTimeS):
             dfNew = dfAll.iloc[0:1]
             df = pd.concat([df,dfNew])
             dfAll = dfAll[1:]
             maxDateF = np.max(df['published'])            
             endTimeF = time.mktime(parser.parse(maxDateF).timetuple()) 
          while((endTimeF-beginTimeF)>span):
             df = df[1:]
             minDateF = np.min(df['published'])
             beginTimeF = time.mktime(parser.parse(minDateF).timetuple())
          yield [str(step).zfill(4), df]
          if(step==1):
             for i in range(0,5):
                 yield [str(step).zfill(4), df]
        yield [str(steps+1).zfill(4), dfAll]  


remLocations = [
'NRW', 'Nordrhein-Westfalen', 'Deutschland', 'Rheinland-Pfalz', 'Baden-Württemberg', 'Schaden',
'Landtag', 'Straße', 'Innenstadt', 'Talsperre', 'Bundesrepublik', 'Bundesrepublik Deutschland', 'Freistaat', 'Sonnenschein',
'Altstadt', 'Haus der Geschichte', 'Schuld', 'Landesamt', 'Hagelsturm', 'Land Rheinland-Pfalz', 'Allianz', 'Kummer', 
'Wohnheim', 'Kreise', 'Helfern', 'Gebiet', 'NRW nan', 'Trümmer', 'Ober-', 'Wetter NRW', 'Land NRW', 'Saarland',
'Land Nordrhein-Westfalen', 'kühl', 'Schleuse', 'Höhe', 'daheim', 'Umspannwerk', 'Schock', 'Angst', 'Hitze', 'Johanniter',
'Tagebau', 'Unser Land', 'Wetter/Deutschland', 'NRW Nordrhein-Westfalen', 'Schön', 'Mein Haus', 'Flüssen',
'Bundesbank', 'Bürger', 'Hagels', 'Bayern', 'Oberbayern', 'Hessen', 'Rheinland', 'Ruhrgebiet', 'Flut', 
# 'Baden-Württemberg', 'Niedersachsen', 'Sauerland', 'Norddeutschland', 'Schwarzwald', 'Thüringen', 'Pfalz',
]

weightLocations = {
'Eifel': 0.05,
'Erftstadt': 0.06,
'Landkreis Ahrweiler': 0.31,
'Bad Neuenahr-Ahrweiler': 0.02,
'Ahrweiler': 0.03,
'Steinbachtalsperre': 0.055,
'Wuppertal': 0.46,
'Düsseldorf': 0.11,
'Mayschoß': 1.81,
'Altenahr': 0.014,
'Erftstadt-Blessem': 0.68,
'Neuenahr-Ahrweiler': 1.85,
'Rhein': 0.51,
'Bad Münstereifel': 0.29,
'Münster': 0.30,
'Mainz': 0.30,
'Donau': 0.25,
}



locationsDF = pd.read_csv('geonames_locations_flood.csv', delimiter=',')
#if exists
locationsDF = pd.read_csv('weights_topics_locations.csv', delimiter=',')

print(locationsDF)
locationsDF = locationsDF[locationsDF['country']=='Deutschland']
locationsDF = locationsDF[locationsDF['latitude']<54]
locationsDF = locationsDF[locationsDF['latitude']>48]
locationsDF = locationsDF[locationsDF['longitude']<11.5]
locationsDF = locationsDF[locationsDF['longitude']>4.0]
locationsDF['weight'] = 1.0
for rmLoc in remLocations:
   locationsDF = locationsDF[locationsDF['phrase']!=rmLoc]
'''
for index, column in locationsDF.iterrows():
    if(column['phrase'] in weightLocations):
        locationsDF.loc[index,'weight'] = weightLocations[column['phrase']]
    else:
        distance = math.sqrt((column['latitude'] - 51)**2 + (column['longitude'] - 7)**2)
        locationsDF.loc[index,'weight'] = random.uniform(0.9,1.2)/(0.6+distance)    
'''
locationsDF = locationsDF.sort_values(by=['count'], ascending=False)
print(locationsDF)


domainWordsRelDF = pd.read_csv(DATA_PATH / "words_topic_all.csv", delimiter=',',index_col='word')
domainWordsRelDF = domainWordsRelDF[domainWordsRelDF['Unnamed: 0'] != 'summaryOfAllWords']
domainWordsRelDF = domainWordsRelDF[~domainWordsRelDF.index.duplicated(keep='first')] 
domainWordsRelDF = domainWordsRelDF.drop(columns=["Unnamed: 0", "summary"])
print(domainWordsRelDF)
domainWordsRelDI = domainWordsRelDF.to_dict('index')



#import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import io
from urllib.request import urlopen, Request
from PIL import Image
import shapely


def getMaximumTopic(propDict):
    maxTopic = "other"
    maxPropabiliyty = -1E9
    nxtPropabiliyty = -1E9
    for topic in propDict:
        if(propDict[topic]> maxPropabiliyty):
            maxPropabiliyty = propDict[topic]
            maxTopic = topic
    for topic in propDict:
        if(maxPropabiliyty > propDict[topic] > nxtPropabiliyty):
            nxtPropabiliyty = propDict[topic]
    ##if((maxPropabiliyty - nxtPropabiliyty) < -1E99):
    ##    maxTopic = "other"
    return maxTopic   

def getMinimumTopic(propDict):
    minTopic = "other"
    minPropabiliyty = +1E9
    nxtPropabiliyty = +1E9
    for topic in propDict:
        if(propDict[topic] < minPropabiliyty):
            minPropabiliyty = propDict[topic]
            minTopic = topic
    for topic in propDict:
        if(minPropabiliyty < propDict[topic] < nxtPropabiliyty):
            nxtPropabiliyty = propDict[topic]
    ##if((nxtPropabiliyty - minPropabiliyty) < -1E99):
    ##    minTopic = "other"
    return minTopic       

def image_spoof(self, tile): # this function pretends not to be a Python script
    url = self._image_url(tile) # get the url of the street map API
    req = Request(url) # start request
    req.add_header('User-agent','Anaconda 3') # add user agent to request
    fh = urlopen(req) 
    im_data = io.BytesIO(fh.read()) # get image
    fh.close() # close url
    img = Image.open(im_data) # open image with PIL
    img = img.convert(self.desired_tile_form) # set image format
    return img, self.tileextent(tile), 'lower' # reformat for cartopy


language = 'ger'
nltk.download('punkt')
tagger = ht.HanoverTagger('morphmodel_'+language+'.pgz')

def generateTokensWithPosition(sentence):
    positionSentence = 0
    lastWord = None
    tokens = nltk.tokenize.word_tokenize(sentence,language='german') 
    lemmata = tagger.tag_sent(tokens,taglevel = 2)
    for (orig,lemma,gramma) in lemmata:
        positionWord = sentence.find(orig)
        yield [orig, positionSentence+positionWord]
        #if double words
        if(lastWord):
            yield [(lastWord+' '+lemma), positionSentence+positionWord]
        lastWord = lemma 
        #lemma vs orig / single vs double / vs tag-level / split "+" 

def generateTokensFromSentence(sentence):
    lastWord = None
    tokens = nltk.tokenize.word_tokenize(sentence,language='german') 
    lemmata = tagger.tag_sent(tokens,taglevel = 2)
    for (orig,lemma,gramma) in lemmata:
        yield orig
        #if double words
        if(lastWord):
            yield (lastWord+' '+lemma)
        lastWord = lemma 

def getDay(published):
    timetravelDate = '1970-01-01'
    pubDate = None
    try:
        pubDate = parser.parse(published)
    except:
        print('date parse error 1')
    if(not pubDate):
      try:
        pubDate = parser.isoparse(published)
      except:
        print('date parse error 2')   
    if(pubDate):
        timetravelDate = pubDate.strftime('%Y-%m-%d')
    return [timetravelDate, pubDate]    

def filterColors(keyList,colorDict):
    result = []
    for key in keyList:
        if(key in colorDict):
            result.append(colorDict[key])
        else:
            result.append(None)
    return result

def limitAutopct(pct):
    return ('%1.1f%%' % pct) if pct > 4.0 else ''

topicsList = list(colorsTopics.keys())
emptyDomains = {"other":0}
emptyTopics = {}
for topic in colorsTopics:
    emptyDomains[topic] = 0
    emptyTopics[topic] = 0

#domainWordsAbs = {'summaryOfAllWords': emptyDomains.copy()}
indexTopicsWeeksSentences = {}
for index, column in floodsDF.iterrows():
    currDay = getDay(column['published'])
    if(not currDay[0] in indexTopicsWeeksSentences):
        indexTopicsWeeksSentences[currDay[0]] = {}
        for topic in colorsTopics:
           indexTopicsWeeksSentences[currDay[0]][topic] = 0
           indexTopicsWeeksSentences[currDay[0]]['pubDate'] = currDay[1] 

i=0
for index, column in floodsDF.iterrows():
 #if(i<250):  
    i += 1
    if(i % 50 == 0):
        print(i)
    currDay = getDay(column['published'])
    currTs = time.mktime(currDay[1].timetuple())
    quote = str(column.title)+' ' +str(column.description)+' '+str(column.content)
    if((len(str(column.quote))>len(quote))):
        quote = str(column.quote)
    sentences = nltk.sent_tokenize(quote,language='german')   #todo: language->var
    for sentence in sentences: 
        bayesSentences = emptyTopics.copy() 
        for token in generateTokensFromSentence(sentence):
            bayesWords = emptyTopics.copy()
            if(token in domainWordsRelDI):
                bayesWords = domainWordsRelDI[token]
                for topic in topicsList:
                    bayesSentences[topic] += bayesWords[topic]      
        maxSentence = getMaximumTopic(bayesSentences)
        for dayString in indexTopicsWeeksSentences:
            pubDate = indexTopicsWeeksSentences[dayString]['pubDate']
            pubTs = time.mktime(pubDate.timetuple())
            if(currTs < pubTs < (currTs+24*60*60*7)):
                indexTopicsWeeksSentences[dayString][maxSentence] += 1 

indexTopicsWeeksSentencesDF = pd.DataFrame.from_dict(indexTopicsWeeksSentences, orient='index', columns=list(reversed(colorsTopics.keys())))

for data in generateDataframeFractions(floodsDF, steps=2400, span=24*60*60*7, start=2170):
 print([data[0], data[1].shape])

 

 #first: calculate propabilities for locations depending from quotes
 #init propabilities with fraction of overall value
 for topic in colorsTopics:
    locationsDF[topic] = 1.0/len(colorsTopics)  
    for index, column in locationsDF.iterrows():
        if(column['phrase'] in domainWordsRelDI):
            locationsDF.loc[index,topic] = 0.25*domainWordsRelDI[column['phrase']][topic]*math.sqrt(weightMapTopics[topic])
 #print(locationsDF['phrase'])

 j = 0
 firstLoc = True
 indexTopicsSentences = emptyTopics.copy()
 indexTopicsPatches = emptyTopics.copy()

 for index2, column2 in locationsDF.iterrows(): 
  j += 1
  #print(column2)
  phrase = str(column2['phrase'])
  print([j,phrase])
  locationsDF.loc[index2,'count'] = 0
  for index1, column1 in data[1].iterrows():
    quote = str(column1.title)+' ' +str(column1.description)+' '+str(column1.content)
    if((len(str(column1.quote))>len(quote))):
        quote = str(column1.quote)  
    #print(quote)
    if(firstLoc):
     sentences = nltk.sent_tokenize(quote,language='german')   #todo: language->var
     for sentence in sentences:        
        bayesSentences = emptyTopics.copy()             
        for token in generateTokensFromSentence(sentence):
            bayesWords = emptyTopics.copy()
            if(token in domainWordsRelDI):
                bayesWords = domainWordsRelDI[token]
                for topic in topicsList:
                    bayesSentences[topic] += bayesWords[topic]*weightSentenceTopics[topic]      
        maxSentence = getMaximumTopic(bayesSentences)
        indexTopicsSentences[maxSentence] += 1

    if(phrase in quote):  
     countingLoc = len([m.start() for m in re.finditer(phrase, quote)])
     locationsDF.loc[index2,'count'] += countingLoc
     sentences = nltk.sent_tokenize(quote,language='german')   #todo: language->var
     for sentence in sentences:

      if(phrase in sentence): 
       found = 0.0   
       for tokenAndPosition in generateTokensWithPosition(sentence):
        token = tokenAndPosition[0]
        tokenPosition = tokenAndPosition[1]
        #propToken !!! 
        if(token in domainWordsRelDI):
            tokenPropability = domainWordsRelDI[token]  
                #print('x', phrase)
            for keyPosition in [m.start() for m in re.finditer(phrase, sentence)]:
                distance = abs(tokenPosition - keyPosition)
                #print(distance)
                factor = math.sqrt(1/(1+distance*0.25))
                if(factor>found):
                    found = factor 
            #print([phrase, token, found, tokenPropability])   
            for topic in colorsTopics: 
                locationsDF.loc[index2,topic] += found*tokenPropability[topic]*weightMapTopics[topic] 
  firstLoc = False
 #locationsDF.to_csv(DATA_PATH / 'geonames_topics.csv', index_label='index')
 
 print(indexTopicsSentences)
 indexTopicsSentencesDF = pd.DataFrame.from_dict(indexTopicsSentences, orient='index')
 print(indexTopicsSentencesDF)
 indexTopicsSentencesDF.to_csv("topics_count.csv", index_label='index')
 

 data1 = []
 for index, column in locationsDF.iterrows():
    if((48<column['latitude']<54) and (4<column['longitude']<11.5)): 
      if(not column['phrase'] in ['NRW','Nordrhein-Westfalen','Deutschland','Rheinland-Pfalz']):
        #print([column['phrase'],column['count']])
        data1.append([column['latitude'],column['longitude'],column['count']])


#http://python-visualization.github.io/folium/plugins.html
#https://scitools.org.uk/cartopy/docs/v0.13/matplotlib/advanced_plotting.html


 """ 
 map_osm = folium.Map(location=[51,7],zoom_start=8,tiles='StamenTerrain',control_scale=True)
 HeatMap(data1).add_to(map_osm)

 file_path = "heatmap.html"
 #map_osm.save(file_path)
 #webbrowser.open(file_path)
 """




 #######################################
 # Formatting the Cartopy plot
 #######################################
 #
 cimgt.Stamen.get_image = image_spoof # reformat web request for street map spoofing
 osm_img = cimgt.Stamen('terrain-background') # spoofed, downloaded street map

 ##fig, ax1 = plt.subplots(figsize=(9, 9))

 minDate = np.min(data[1]['published'])
 maxDate = np.max(data[1]['published'])

 #may convert data[1]['published'] to array first?
 dateArray = data[1]['published'].values
 medPos = int((len(dateArray)-0.5)/2)
 #medDate = minDate
 medDate = dateArray[medPos]


 fig = plt.figure(figsize=(18,12)) # open matplotlib figure
 fig.suptitle('Ahrtal Flood: '+medDate[0:10],fontsize=24)
 gs = fig.add_gridspec(2, 2,  width_ratios=(80, 20), height_ratios=(70, 30),
                      left=0.05, right=0.99, bottom=0.05, top=0.95,
                      wspace=0.05, hspace=0.05)
 ax1 = fig.add_subplot(gs[0, 0], projection=ccrs.PlateCarree())

 #ax1 = plt.axes(projection=osm_img.crs) # project using coordinate reference system (CRS) of street map
 #ax1.axes(projection=osm_img.crs)
 #ax1.set_option(projection=osm_img.crs)
 #ax1.set_title('Flood Topics Map: '+minDate[0:10]+' .. '+maxDate[0:10],fontsize=24)
 extent = [5.5, 9.5, 49, 53] # Contiguous US bounds
 extent = [5.0, 10.5, 49, 52.5] # Contiguous US bounds 
 #extent = [-179, 179, -89, 89] # Contiguous US bounds
 # extent = [-74.257159,-73.699215,40.495992,40.915568] # NYC bounds
 ax1.set_extent(extent) # set extents
 ax1.set_xticks(np.linspace(extent[0],extent[1],9),crs=ccrs.PlateCarree()) # set longitude indicators
 ax1.set_yticks(np.linspace(extent[2],extent[3],9)[1:],crs=ccrs.PlateCarree()) # set latitude indicators
 lon_formatter = LongitudeFormatter(number_format='0.1f',degree_symbol='',dateline_direction_label=True) # format lons
 lat_formatter = LatitudeFormatter(number_format='0.1f',degree_symbol='') # format lats
 ax1.xaxis.set_major_formatter(lon_formatter) # set lons
 ax1.yaxis.set_major_formatter(lat_formatter) # set lats
 ax1.xaxis.set_tick_params(labelsize=14)
 ax1.yaxis.set_tick_params(labelsize=14)
 scale = 10
 ax1.add_image(osm_img, scale) # add OSM with zoom specification


 #######################################
 # Plot the ASOS stations as points
 #######################################
 #
 maxCount = np.max(locationsDF['count'])
 print(maxCount)
 #ax1.plot(long1, lat1, markersize=15,marker='o',linestyle='',color='#3b3b3b', alpha=0.5,transform=ccrs.PlateCarree())
 lat1,long1,size1 = [],[],[]

 ##delta = 0.5
 delta = 0.05
 #delta = 0.025
 firstRound = True
 for lat2 in np.arange(49,53,delta):
    print([49,lat2,53])
    for long2 in np.arange(5.0,10.5,delta):
        
        bayesLocation = emptyTopics.copy() 
        bayesWeight = emptyTopics.copy()
        bayesMean = emptyTopics.copy()
        meanCounter = 0
        for index, column in locationsDF.iterrows():
            if((48<column['latitude']<54) and (4<column['longitude']<11.5)):
                #print(column['phrase'])
                #TODO: real count....
                if(firstRound):
                    locNumber = 10+3*column['count']
                    locWidth = 0.05
                    if(column['geotype'] in ['A']):
                       locNumber = 4+column['count']
                       locWidth = 0.15
                    if(column['geotype'] in ['T']):
                       locNumber = 6+2*column['count']
                       locWidth = 0.10  
                    for i in range(locNumber):     
                        x=random.gauss(column['longitude'],locWidth)
                        y=random.gauss(column['latitude'],locWidth)
                        lat1.append(x)
                        long1.append(y)

                #if(column['phrase'] in domainWordsRelDI):
                if(1==1):    

                    #topicsProbability = domainWordsRelDI[column['phrase']]
                    topicsProbability = {}
                    for topic in colorsTopics:
                        topicsProbability[topic] = column[topic]  

                    #print(topicsProbability)
                    if(firstRound):
                        maxTopic = getMaximumTopic(topicsProbability)
                        #print([column['phrase'],maxTopic,topicsProbability])
                    distance = math.sqrt((column['latitude']-lat2)**2 + (column['longitude']-long2)**2)
                    distance = distance/column['weight']
                    count = math.sqrt(column['count'])
                    #weight = count/(delta+distance*10)
                    weight = 1.0/((delta/10+20*distance)**2)
                    if(column['geotype'] in ['A']):
                        weight = 0.25/((delta/10+80*distance)**2)
                    if(column['geotype'] in ['T']):
                        weight = 0.5/((delta/10+40*distance)**2)    
                    for topic in colorsTopics:
                       #print(topicsProbability[topic])
                       ## bayesLocation[topic] += topicsProbability[topic]*weight   #try this...
                       bayesLocation[topic] += topicsProbability[topic]*weight*math.sqrt(column['weight']) 
                       bayesWeight[topic] += weight
                       bayesMean[topic] += topicsProbability[topic] 
                       meanCounter += 1
        firstRound = False
        maxColor = '#555555'
        #print(bayesLocation)
        #print(bayesWeight)
        #print(bayesMean)

        for topic in colorsTopics:
            bayesLocation[topic] = bayesLocation[topic] / bayesWeight[topic]
        #print(bayesLocation)        

        maxTopic = getMaximumTopic(bayesLocation)
        indexTopicsPatches[maxTopic] += 1
        #print(maxTopic)
        if(maxTopic in colorsTopics):
            maxColor = colorsTopics[maxTopic]

        ax1.add_patch(
            patches.Rectangle(
                (long2, lat2),   # (x,y)
                delta,          # width
                delta,          # height
                fill=True,
                #color = maxColor,
                #edgecolor = maxColor,
                facecolor = maxColor,
                zorder=2,
                alpha = 0.7,
                transform=ccrs.PlateCarree(),
                #label=maxTopic
                )
            )    

 #normalize Sentence count and patch count 
 weightMapDiffs = emptyTopics.copy()
 weightSentenceDiffs = emptyTopics.copy() 
 weightMapFactors = emptyTopics.copy()
 weightSentenceFactors = emptyTopics.copy()
 sentenceSum = 0
 patchesSum = 0
 for topic in colorsTopics:
    sentenceSum += indexTopicsSentences[topic]
    patchesSum += indexTopicsPatches[topic]
 #recalculate weight for map, so it fits better to pie chart
 for topic in colorsTopics:
   weightFactor = (0.1+patchesSum*indexTopicsSentences[topic]) / (0.1+sentenceSum*indexTopicsPatches[topic]) #might try...
   weightMapFactors[topic] = weightFactor
   if(random.uniform(0.0,1.0) > 0.5):  
     weightMapDiffs[topic] = 0.0
     weightLog = abs(math.log(weightFactor,2))+random.uniform(0.0,0.1)
     if(weightFactor > 1.04):
         weightMapDiffs[topic] = 0.1
         if(weightMapTopics[topic] > 1.0):
           weightMapTopics[topic] *= (1.0+0.021*weightLog)
         else:
           weightMapTopics[topic] *= (1.0+0.046*weightLog)      
     elif(weightFactor < 0.96):
         weightMapDiffs[topic] = -0.1
         if(weightMapTopics[topic] > 1.0):
           weightMapTopics[topic] *= (1.0-0.047*weightLog)
         else:
           weightMapTopics[topic] *= (1.0-0.020*weightLog) 
     weightMapTopics[topic] = min(10000.0, max(0.0001, weightMapTopics[topic]))   
 for topic in colorsTopics:       
    if(weightMapTopics[topic] > 1.0):
        weightMapTopics[topic] *= random.uniform(0.99,1.0)
    else:
        weightMapTopics[topic] *= random.uniform(1.0,1.01) 
 print([data[0],' - map weight per topic: ', weightMapTopics])   
 collectedWeightTopicsMap[data[0]] = weightMapTopics
 mapWeightsDF = pd.DataFrame.from_dict(collectedWeightTopicsMap, orient='index', columns=weightMapTopics.keys())
 mapWeightsDF.to_csv("weights_topics_map.csv", index=True)  



 #recalculate weight for pie, so it fits better to map
 for topic in colorsTopics:
   weightFactor = (0.1+sentenceSum*indexTopicsPatches[topic]) / (0.1+patchesSum*indexTopicsSentences[topic]) #might try...
   weightSentenceFactors[topic] = weightFactor
   if(random.uniform(0.0,1.0) > 0.5):  
     weightSentenceDiffs[topic] = 0.0
     weightLog = abs(math.log(weightFactor,2))+random.uniform(0.0,0.1)
     if(weightFactor > 1.02):
         weightSentenceDiffs[topic] = 0.1
         if(weightSentenceTopics[topic] > 1.0):
           weightSentenceTopics[topic] *= (1.0+0.032*weightLog)
         else:
           weightSentenceTopics[topic] *= (1.0+0.081*weightLog)      
     elif(weightFactor < 0.98):
         weightSentenceDiffs[topic] = -0.1
         if(weightSentenceTopics[topic] > 1.0):
           weightSentenceTopics[topic] *= (1.0-0.082*weightLog)
         else:
           weightSentenceTopics[topic] *= (1.0-0.031*weightLog) 
     weightSentenceTopics[topic] = min(100.0, max(0.01, weightSentenceTopics[topic]))   
 for topic in colorsTopics:       
    if(weightSentenceTopics[topic] > 1.0):
        weightSentenceTopics[topic] *= random.uniform(0.98,1.0)
    else:
        weightSentenceTopics[topic] *= random.uniform(1.0,1.02) 
 print([data[0],' - sentence weight per topic: ', weightSentenceTopics])  
 collectedWeightTopicsSentence[data[0]] = weightSentenceTopics
 sentenceWeightsDF = pd.DataFrame.from_dict(collectedWeightTopicsSentence, orient='index', columns=weightSentenceTopics.keys())
 sentenceWeightsDF.to_csv("weights_topics_sentence.csv", index=True)  

 for index, column in locationsDF.iterrows():
   topicsProbability = {}
   for topic in colorsTopics:
       topicsProbability[topic] = column[topic]  
   maxTopic = getMaximumTopic(topicsProbability)
   if(weightMapFactors[maxTopic]>0.0):
        #print([maxTopic, weightMapFactors[maxTopic]])
        weightLog = abs(math.log(weightMapFactors[maxTopic],2.0))+random.uniform(0.0,0.1)
        #print(weightLog)
        if(random.uniform(0.0,1.0) > 0.5):
            if(weightMapFactors[maxTopic] > 1.10):
                if(column['weight'] > 1.0):
                    locationsDF.loc[index,'weight'] = column['weight']*(1.0+0.098*weightLog)
                else:
                    locationsDF.loc[index,'weight'] = column['weight']*(1.0+0.137*weightLog) 
            elif(weightMapFactors[maxTopic] < 0.90):
                if(column['weight'] > 1.0):
                    locationsDF.loc[index,'weight'] = column['weight']*(1.0-0.138*weightLog)
                else:
                    locationsDF.loc[index,'weight'] = column['weight']*(1.0-0.099*weightLog) 
            locationsDF.loc[index,'weight'] = min(100.0, max(0.01, locationsDF.loc[index,'weight'])) 
            #use minTopic to dim topics?
   minTopic = getMinimumTopic(topicsProbability)
   #print([minTopic, weightMapFactors[minTopic]])
   if(weightMapFactors[minTopic]>0.0):
        weightLog = abs(math.log(weightMapFactors[minTopic],2))
        if(random.uniform(0.0,1.0) > 0.5):
            if(weightMapFactors[minTopic] > 1.15):
                if(column['weight'] > 1.0):
                    locationsDF.loc[index,'weight'] = column['weight']*(1.0-0.034*weightLog)
                else:
                    locationsDF.loc[index,'weight'] = column['weight']*(1.0-0.017*weightLog) 
            elif(weightMapFactors[minTopic] <0.85):
                if(column['weight'] > 1.0):
                    locationsDF.loc[index,'weight'] = column['weight']*(1.0+0.035*weightLog)
                else:
                    locationsDF.loc[index,'weight'] = column['weight']*(1.0+0.018*weightLog) 
            locationsDF.loc[index,'weight'] = min(100.0, max(0.01, locationsDF.loc[index,'weight'])) 
 for index, column in locationsDF.iterrows():
    if(column['weight'] > 1.0):
        locationsDF.loc[index,'weight'] = column['weight']*random.uniform(0.98,1.0)
    else:
        locationsDF.loc[index,'weight'] = column['weight']*random.uniform(1.0,1.02)    
 locationsDF.to_csv("weights_topics_locations.csv", index=True) 

 print([data[0],' - weights per location'])
 for index, column in locationsDF.iterrows():
     if(column['weight']>1.2):
         print([column['phrase'], column['weight']])
     if(column['weight']<0.8):
         print([column['phrase'], column['weight']])

 if(1==1):
    #sns.kdeplot(x=lat1, y=long1, fill=True,  alpha=0.5, levels=100, thresh=.00001, cmap=cm.Blues, transform=ccrs.PlateCarree() )
    sns.kdeplot(ax=ax1,x=lat1, y=long1, fill=False,  levels=10, thresh=.0005, alpha=0.2, color='blue', transform=ccrs.PlateCarree(),zorder=3, label='News Density' )  


 #ax1.add_feature(cartopy.feature.RIVERS)
 ax1.text(6.08342,50.77664,"Aachen", color='#000000', fontsize=12, ha='center', va='center',transform=ccrs.PlateCarree(),zorder=4)
 ax1.text(6.95,50.93333,"Cologne", color='#000000', fontsize=12, ha='center', va='center',transform=ccrs.PlateCarree(),zorder=4)
 ax1.text(7.09549,50.73438,"Bonn", color='#000000', fontsize=12, ha='center', va='center',transform=ccrs.PlateCarree(),zorder=4)
 #ax1.text(7.21877,50.5569,"Bad Bodendorf", color='#aa0000', fontsize=12, ha='center', va='center',transform=ccrs.PlateCarree())
 #ax1.text(6.99206,50.51694,"Altenahr", color='#aa0000', fontsize=12, ha='center', va='center',transform=ccrs.PlateCarree())    
 ax1.text(7.14816,51.25627,"Wuppertal", color='#000000', fontsize=12, ha='center', va='center',transform=ccrs.PlateCarree(),zorder=4)      
 ax1.text(7.466,51.51494,"Dortmund", color='#000000', fontsize=12, ha='center', va='center',transform=ccrs.PlateCarree(),zorder=4)  
 ax1.text(7.62571,51.96236,"Münster", color='#000000', fontsize=12, ha='center', va='center',transform=ccrs.PlateCarree(),zorder=4)  
 ax1.text(6.79387,50.81481,"Erftstadt", color='#000000', fontsize=12, ha='center', va='center',transform=ccrs.PlateCarree(),zorder=4) 
 ax1.text(6.95,50.33333,"Nürburg", color='#000000', fontsize=12, ha='center', va='center',transform=ccrs.PlateCarree(),zorder=4)  
 ax1.text(7.57883,50.35357,"Koblenz", color='#000000', fontsize=12, ha='center', va='center',transform=ccrs.PlateCarree(),zorder=4) 
 ax1.text(6.66667,50.25,"Eifel", color='#000000', fontsize=12, ha='center', va='center',transform=ccrs.PlateCarree(),zorder=4) 
 ax1.text(7.09549,50.54169,"Ahrweiler", color='#000000', fontsize=12, ha='center', va='center',transform=ccrs.PlateCarree(),zorder=4) 



 #ax1.add_feature(cfeature.RIVERS,linewidth=8, edgecolor='black', zorder=10,transform=ccrs.PlateCarree())
 #ax1.add_feature(cfeature.RIVERS,linewidth=8, edgecolor='black', zorder=10)   #png save not working!

 handles = []
 for topic in colorsTopics:   
  patch = patches.Patch(color=colorsTopics[topic], label=topic)
  handles.append(patch)
 handles.reverse()

 ax2 = fig.add_subplot(gs[0, 1])

 ax2.axis("off")
 leg  = ax2.legend(handles = handles,
          title="Topics",
          loc="upper left",
          #fontsize=14,
          fontsize=12,
          bbox_to_anchor=(0.12, +3.0))
 #leg.set_title("Topics", prop = {'size':18}) 
 leg.set_title("Topics", prop = {'size':14}) 


 #blueLine = mlines.Line2D([], [], color='blue', label='News Density')
 #leg2  = ax2.legend(handles = [blueLine],
 #         title="Contour",
 #         loc="upper left",
 #         #fontsize=14,
 #         fontsize=12,
 #         bbox_to_anchor=(0.05, 0.2))
 ##leg2.set_title("Contour", prop = {'size':18}) 
 #leg2.set_title("Contour", prop = {'size':14})  
 #ax2.add_artist(leg)



 #pie for patches
 #ax4.set_title("Relative", fontsize=24)
 colors4b = filterColors(indexTopicsPatches.keys(), colorsTopics)
 wedges, texts, auto  =  ax2.pie(indexTopicsPatches.values(), labels=indexTopicsPatches.keys(), colors=colors4b,
              autopct=limitAutopct, startangle=-270, labeldistance=None, textprops={'fontsize': 12})
 #ax4.text(0,0,"ax3", color='#000000', fontsize=12, ha='center', va='center',transform=ccrs.PlateCarree(),zorder=4)
 ax2.margins(0.01)

 box = ax2.get_position()
 print([box.x0, box.y0, box.width, box.height])
 # [0.8065853658536587, 0.5051219512195121, 0.18341463414634152, 0.2751219512195122]



 #ax2.set_position([0.015+box.x0, box.y0-0.75*box.height, 0.8*box.width, box.height])
 ax2.set_position([0.82, 0.3, 0.15, 0.27]) 
 ax2.autoscale()

 ax3 = fig.add_subplot(gs[1, 0]) #fraction
 #ax3.text(0,0,"ax3", color='#000000', fontsize=12, ha='center', va='center',transform=ccrs.PlateCarree(),zorder=4)
 #ax3.axis("off")
 ax3.axes.get_yaxis().set_visible(False)
 ax3.spines["right"].set_visible(False)
 ax3.spines["left"].set_visible(False)
 ax3.spines["top"].set_visible(False)
 # indexTopicsWeeksSentencesDF
 germanDomainsDate2 = indexTopicsWeeksSentencesDF.reindex(topicsList, axis=1)
 print(germanDomainsDate2)
 for index, column in germanDomainsDate2.iterrows():
    suma = 0
    for topic in topicsList:
        suma += column[topic]
    for topic in topicsList:
        germanDomainsDate2.loc[index,topic] = column[topic] / suma

 domainsT = germanDomainsDate2.T
 colors = filterColors(list(germanDomainsDate2.head()), colorsTopics)
 #print(colors)
 dates = indexTopicsWeeksSentencesDF.index
 #print(dates)
 alphas = []
 for date in dates:
     if(minDate[0:10] < date < maxDate[0:10]):
         alphas.append(1.0)
     else:
         alphas.append(0.5)
 ax3.stackplot(dates, domainsT, colors=colors, labels=list(germanDomainsDate2.head()))
 
 ax3.axvline(x=minDate[0:10], ymin=0.0, ymax = 1.0, linewidth=1, color='black')
 ax3.axvline(x=medDate[0:10], ymin=0.0, ymax = 1.0, linewidth=2, color='black')
 ax3.axvline(x=maxDate[0:10], ymin=0.0, ymax = 1.0, linewidth=1, color='black')

 ax3.axhline(xmin=minDateA[0:10], xmax=minDate[0:10],y=0.5, color = 'white', alpha=0.3, linewidth=0.5, zorder=4)
 ax3.axhline(xmin=maxDate[0:10], xmax=maxDateA[0:10],y=0.5, color = 'white', alpha=0.3, linewidth=0.5, zorder=4)

 """
 poly1 = [(minDateA[0:10],0),(minDateA[0:10],1),(minDate[0:10],1),(minDate[0:10],0)]
 ax3.add_patch(
  patches.Polygon(
    poly1,   # (x,y)
    fill=True,
    facecolor = 'white',
    zorder=2,
    alpha = 0.3,
    )
 )  
 poly2 = [(maxDate[0:10],0),(maxDate[0:10],1),(maxDateA[0:10],1),(maxDateA[0:10],0)]
 ax3.add_patch(
  patches.Polygon(
    poly2,   # (x,y)
    fill=True,
    facecolor = 'white',
    zorder=2,
    alpha = 0.3,
    )
 )  
 """

 #plt.gcf().autofmt_xdate()
 #plt.yticks(fontsize=36)
 #ax3.autofmt_xdate()
 ax3.set_xticks([minDateA[0:10],maxDateA[0:10]])  #rotation=30
 #ax3.set_xticks([0,medDate,2400])


 ax4 = fig.add_subplot(gs[1, 1]) #pie
 #ax4.set_title("Relative", fontsize=24)
 colors4 = filterColors(indexTopicsSentences.keys(), colorsTopics)
 wedges, texts, auto  =  ax4.pie(indexTopicsSentences.values(), labels=indexTopicsSentences.keys(), colors=colors4,
              autopct=limitAutopct, startangle=-270, labeldistance=None, textprops={'fontsize': 12})



 #ax4.text(0,0,"ax3", color='#000000', fontsize=12, ha='center', va='center',transform=ccrs.PlateCarree(),zorder=4)
 ax4.axis("off")
 ax4.margins(0.01)
 ##ax4.tight_layout(0.01)

 plt.savefig(DATA_PATH / 'map' / ('floods_topics_map_'+data[0]+'.png'), dpi=100)
 #plt.show()

