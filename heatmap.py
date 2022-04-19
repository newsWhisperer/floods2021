import pandas as pd
import numpy as np
import math
import random

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import seaborn as sns

import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.img_tiles as cimgt
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

import io
from urllib.request import urlopen, Request
from PIL import Image

import folium
import webbrowser
from folium.plugins import HeatMap

from pathlib import Path
import os.path

DATA_PATH = Path.cwd()

#adapt limits and zoom-level (scale) according to data
limits = {'latMin':50.0, 'latMax':52.0, 'lonMin':5.0, 'lonMax':9.0}
scale = 10

labels = [{'lon':6.08342, 'lat':50.77664,  'name':"Aachen"},
          {'lon':6.95,'lat':50.93333,'name':"Cologne"},
          {'lon':7.09549,'lat':50.73438,'name':"Bonn"},
          {'lon':7.14816,'lat':51.25627,'name':"Wuppertal"},
          {'lon':7.466,'lat':51.51494,'name':"Dortmund"}, 
          {'lon':7.62571,'lat':51.96236,'name':"Münster"}, 
          {'lon':6.79387,'lat':50.81481,'name':"Erftstadt"}, 
          {'lon':6.95,'lat':50.33333,'name':"Nürburg"}, 
          {'lon':7.57883,'lat':50.35357,'name':"Koblenz"},
          {'lon':6.66667,'lat':50.25,'name':"Eifel"}, 
          {'lon':7.09549,'lat':50.54169,'name':"Ahrweiler"}
]

locationsDF = pd.read_csv(DATA_PATH / 'csv' / 'geonames.csv', delimiter=',')
locationsDF = locationsDF[locationsDF['country']=='Deutschland']
locationsDF = locationsDF.sort_values(by=['count'], ascending=False)
#print(locationsDF)

rivers_10m = cfeature.NaturalEarthFeature('physical', 'rivers_lake_centerlines', '10m')
rivers_europe_10m = cfeature.NaturalEarthFeature('physical', 'rivers_europe', '10m')


def image_spoof(self, tile): 
    url = self._image_url(tile) 
    req = Request(url) 
    req.add_header('User-agent','Anaconda 3') 
    fh = urlopen(req) 
    im_data = io.BytesIO(fh.read()) 
    fh.close() 
    img = Image.open(im_data) 
    img = img.convert(self.desired_tile_form) 
    return img, self.tileextent(tile), 'lower' 

#cartopy OSM
cimgt.Stamen.get_image = image_spoof 
osm_img = cimgt.Stamen('terrain-background') 

fig = plt.figure(figsize=(12,12))
# project using coordinate reference system (CRS) of street map 
ax1 = plt.axes(projection=osm_img.crs) 
ax1.set_title('News Articles Density Map',fontsize=16)
extent = [limits['lonMin'], limits['lonMax'], limits['latMin'], limits['latMax']] 
ax1.set_extent(extent)
ax1.set_xticks(np.linspace(limits['lonMin'],limits['lonMax'],9),crs=ccrs.PlateCarree()) 
ax1.set_yticks(np.linspace(limits['latMin'],limits['latMax'],9)[1:],crs=ccrs.PlateCarree()) 
lon_formatter = LongitudeFormatter(number_format='0.2f',degree_symbol='',dateline_direction_label=True)
lat_formatter = LatitudeFormatter(number_format='0.2f',degree_symbol='') 
ax1.xaxis.set_major_formatter(lon_formatter) 
ax1.yaxis.set_major_formatter(lat_formatter) 
ax1.xaxis.set_tick_params(labelsize=14)
ax1.yaxis.set_tick_params(labelsize=14)
# add OSM with zoom specification
ax1.add_image(osm_img, scale) 

maxCount = np.max(locationsDF['count'])
lat1,long1,size1 = [],[],[]
for index, column in locationsDF.iterrows():
    if((limits['latMin']<column['latitude']<limits['latMax']) and (limits['lonMin']<column['longitude']<limits['lonMax'])):
      if(not column['phrase'] in ['NRW','Nordrhein-Westfalen']):
        for i in range(5+column['count']):
            x=random.gauss(column['longitude'],0.1)
            y=random.gauss(column['latitude'],0.1)
            lat1.append(x)
            long1.append(y)
            ax1.plot(x, y, 
                    markersize=35,marker='o',linestyle='', markeredgecolor=None,
                    color='#0033bb', alpha=0.003,transform=ccrs.PlateCarree())                     
            ax1.plot(x, y, 
                    markersize=15,marker='o',linestyle='', markeredgecolor=None,
                    color='#0022aa', alpha=0.005,transform=ccrs.PlateCarree())  
#contour-plot
sns.kdeplot(x=lat1, y=long1, fill=False,  levels=10, thresh=.0005, color='grey', transform=ccrs.PlateCarree()  )  
ax1.add_feature(rivers_10m, facecolor='None', edgecolor='cyan', linewidth=1.5, zorder=2)
ax1.add_feature(rivers_europe_10m, facecolor='None', edgecolor='cyan', linewidth=1.5, zorder=2)

for label in labels:
    ax1.text(label['lon'],label['lat'],label['name'], color='#200000', fontsize=14, ha='center', va='center',transform=ccrs.PlateCarree())

if(not os.path.exists(DATA_PATH / 'img')):
    os.mkdir(DATA_PATH / 'img')
plt.savefig(DATA_PATH / 'img' / 'heatmap.png', dpi=300)



heatdata = []
for index, column in locationsDF.iterrows():
    if((50<column['latitude']<52) and (6<column['longitude']<8) and not ('Nordrhein-Westfalen' == column['phrase'])):
        print([column['phrase'],column['count']])
        heatdata.append([column['latitude'],column['longitude'],column['count']])

map_osm = folium.Map(location=[51,7],zoom_start=8,tiles='StamenTerrain',control_scale=True)
HeatMap(heatdata).add_to(map_osm)
map_osm.save(str(DATA_PATH / "img" / "heatmap.html"))
