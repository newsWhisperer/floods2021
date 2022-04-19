import pandas as pd
import numpy as np
import math
import random

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.patches as patches
import matplotlib.lines as mlines

import seaborn as sns

import cartopy.crs as ccrs
import cartopy
import cartopy.feature as cfeature


from pathlib import Path
import os.path


DATA_PATH = Path.cwd()

locationsDF = pd.read_csv(DATA_PATH / "csv" / 'geonames.csv', delimiter=',')
locationsDF = locationsDF[locationsDF['country']=='Deutschland']
locationsDF = locationsDF.sort_values(by=['count'], ascending=False)
print(locationsDF)


domainWordsRelDF = pd.read_csv(DATA_PATH / "csv" / "words_bayes_topic_all.csv", delimiter=',',index_col='word')
domainWordsRelDF = domainWordsRelDF[domainWordsRelDF['Unnamed: 0'] != 'summaryOfAllWords']
domainWordsRelDF = domainWordsRelDF[~domainWordsRelDF.index.duplicated(keep='first')] 
domainWordsRelDF = domainWordsRelDF.drop(columns=["Unnamed: 0", "summary"])
print(domainWordsRelDF)
domainWordsRelDI = domainWordsRelDF.to_dict('index')


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




emptyDomains = {"other":0}
emptyTopics = {}
for topic in colorsTopics:
    emptyDomains[topic] = 0
    emptyTopics[topic] = 0




#import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import io
from urllib.request import urlopen, Request
from PIL import Image
import shapely

rivers_10m = cfeature.NaturalEarthFeature('physical', 'rivers_lake_centerlines', '10m')
rivers_europe_10m = cfeature.NaturalEarthFeature('physical', 'rivers_europe', '10m')



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
    if((maxPropabiliyty - nxtPropabiliyty) < -1E99):
        maxTopic = "other"
    return maxTopic   

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


#######################################
# Formatting the Cartopy plot
#######################################
#
cimgt.Stamen.get_image = image_spoof # reformat web request for street map spoofing
osm_img = cimgt.Stamen('terrain-background') # spoofed, downloaded street map

##fig, ax1 = plt.subplots(figsize=(9, 9))

fig = plt.figure(figsize=(18,12)) # open matplotlib figure
ax1 = plt.axes(projection=osm_img.crs) # project using coordinate reference system (CRS) of street map
ax1.set_title('Flood Articles Density Map',fontsize=16)
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

delta = 0.05
delta = 0.5
delta = 0.025
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
              if(not column['phrase'] in ['NRW','Nordrhein-Westfalen','Deutschland','Rheinland-Pfalz']):
                #print(column['phrase'])

                if(firstRound):
                    for i in range(5+column['count']):
                        x=random.gauss(column['longitude'],0.1)
                        y=random.gauss(column['latitude'],0.1)
                        lat1.append(x)
                        long1.append(y)

                if(column['phrase'] in domainWordsRelDI):

                    topicsProbability = domainWordsRelDI[column['phrase']]
                    #print(topicsProbability)
                    if(firstRound):
                        maxTopic = getMaximumTopic(topicsProbability)
                        #print([column['phrase'],maxTopic,topicsProbability])
                    distance = math.sqrt((column['latitude']-lat2)**2 + (column['longitude']-long2)**2)
                    count = math.sqrt(column['count'])
                    weight = count/(delta+distance*10)
                    weight = 1.0/((delta/10+20*distance)**2)
                    for topic in colorsTopics:
                       #print(topicsProbability[topic])
                       bayesLocation[topic] += topicsProbability[topic]*weight 
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
        """
        for topic in colorsTopics:
            bayesMean[topic] = bayesMean[topic] / meanCounter
        print(bayesMean)
        for topic in colorsTopics:
            bayesLocation[topic] -= bayesMean[topic]
        print(bayesLocation) 
        """ 
        maxTopic = getMaximumTopic(bayesLocation)
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


if(1==1):
    #sns.kdeplot(x=lat1, y=long1, fill=True,  alpha=0.5, levels=100, thresh=.00001, cmap=cm.Blues, transform=ccrs.PlateCarree() )
    sns.kdeplot(x=lat1, y=long1, fill=False,  levels=10, thresh=.0005, alpha=0.5, color='blue', transform=ccrs.PlateCarree(),zorder=3, label='News Density' )  

ax1.add_feature(rivers_10m, facecolor='None', edgecolor='cyan', linewidth=1.5, zorder=2)
ax1.add_feature(rivers_europe_10m, facecolor='None', edgecolor='cyan', linewidth=1.5, zorder=2)

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

leg  = ax1.legend(handles = handles,
          title="Topics",
          loc="upper left",
          fontsize=10,
          bbox_to_anchor=(1.05, 1.00))
leg.set_title("Topics", prop = {'size':12}) 

blueLine = mlines.Line2D([], [], color='blue', label='News Density')
leg2  = ax1.legend(handles = [blueLine],
          title="Contour",
          loc="upper left",
          fontsize=10,
          bbox_to_anchor=(1.05, 0.55))
leg2.set_title("Contour", prop = {'size':12}) 
plt.gca().add_artist(leg)

plt.savefig(DATA_PATH / "img" / 'topics_bayes_map.png', dpi=300)
#plt.show()