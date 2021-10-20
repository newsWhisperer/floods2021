import pandas as pd
import numpy as np
import math

#import datetime as dt
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.cm as cm
#import seaborn as sns

from pathlib import Path
import os.path

DATA_PATH = Path.cwd()
if(not os.path.exists(DATA_PATH / 'img')):
    os.mkdir(DATA_PATH / 'img')

def limitAutopct(pct):
    return ('%1.1f%%' % pct) if pct > 4.0 else ''

colorDomains = {
# 'summary':0,
 'other':'gray', 'www.zeit.de':'firebrick', 'www.focus.de':'darkcyan', 'www.faz.net':'darkturquoise', 'www.sueddeutsche.de':'salmon', 'www.stern.de':'darkred',
 'www.spiegel.de':'orangered', 'www.morgenpost.de':'steelblue', 'www.n-tv.de':'darkmagenta', 'www.welt.de':'mediumblue', 'www.tagesschau.de':'darkgreen',
 'www.handelsblatt.com':'orange', 'www.bild.de':'midnightblue', 'www.tagesspiegel.de':'palegreen', 'www.dw.com':'yellowgreen', 'www.wiwo.de':'gold',
 'taz.de':'red', 'www.heise.de':'fuchsia', 'www.nzz.ch':'wheat', 'www.t-online.de':'purple', 'orf.at':'green', 
 # 'www.diepresse.com':'yellow'
}

colorsParties = {'Linke':'fuchsia', 'AfD':'aqua', 'FDP':'gold', 'Grüne':'green', 'SPD':'red', 'CDU/CSU':'dimgray'}

colorsTopics = {
 'Wine': 'purple',
 'Troublemakers': 'fuchsia',
 'Insurance': 'moccasin',
 'Risk': 'green',
 'Responsability': 'salmon',
 'Pollution': 'lime',
 'Health': 'gold',
 'Causes': 'darkcyan',
 'Warnings': 'darkorange',
 'Solidarity': 'greenyellow',
 'Infrastructure': 'darkgrey',
 'Rescue': 'olivedrab',
 'Politics': 'mediumpurple',
 'Damage':'firebrick', 
 'Weather': 'skyblue', 
 'Victims': 'red',
 'Flood Hazard': 'royalblue', 
}

topicsPi = ['Flood Hazard', 'Weather', 'Victims', 'Damage', 'Causes', 'Health', 'Warnings', 'Infrastructure', 'Solidarity', 
            'Rescue', 'Insurance', 'Pollution', 'Wine', 'Politics']

def filterColors(keyList,colorDict):
    result = []
    for key in keyList:
        if(key in colorDict):
            result.append(colorDict[key])
        else:
            result.append(None)
    return result


#Newspapers Domains Summary
germanDomains = pd.read_csv(DATA_PATH / 'csv' / 'domains_count.csv', delimiter=',')
germanDomains = germanDomains[germanDomains['Unnamed: 0'] != 'www.diepresse.com']
germanDomains = germanDomains.sort_values(by=['count'], ascending=False)
y_pos = np.arange(len(germanDomains['count']))
plt.rcdefaults()
fig, ax = plt.subplots(figsize=(40, 20))
colors = filterColors(germanDomains['Unnamed: 0'], colorDomains)
ax.barh(y_pos, germanDomains['count'], align='center', color=colors)
ax.set_yticks(y_pos)
ax.set_yticklabels(germanDomains['Unnamed: 0'], fontsize=36)
ax.invert_yaxis()  # labels read top-to-bottom
ax.set_xlabel('Number of Articles', fontsize=36)
plt.xticks(fontsize=36)
ax.set_title("Newspapers", fontsize=48)
plt.tight_layout()
plt.savefig(DATA_PATH / 'img' / 'domains_count.png')
plt.close('all')


#Newspaper by Date  
germanDomainsDate = pd.read_csv(DATA_PATH / 'csv' / 'domains_date.csv', delimiter=',')
plt.rcdefaults()
fig, ax = plt.subplots(figsize=(40, 20))
domainsList = list(colorDomains.keys())
germanDomainsDate2 = germanDomainsDate.reindex(domainsList, axis=1)
domainsT = germanDomainsDate2.T
colors = filterColors(list(germanDomainsDate2.head()), colorDomains)
dates = germanDomainsDate['Unnamed: 0']
ax.stackplot(dates, domainsT, colors=colors, labels=list(germanDomainsDate2.head()))
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=7))
plt.gcf().autofmt_xdate()
plt.xticks(fontsize=36)
plt.yticks(fontsize=36)
ax.set_title("Number of Newspaper Articles", fontsize=48)
leg = ax.legend(fontsize=24)
leg.set_title("Domains", prop = {'size':36}) 
plt.savefig(DATA_PATH / 'img' / 'domains_date.png', dpi=300)
plt.close('all')


#Piechart Topics 2021,1804,1910  
floodsTopics2021 = pd.read_csv(DATA_PATH / 'csv' / 'topics_count_2021.csv', delimiter=',')
floodsTopics2021 = floodsTopics2021[floodsTopics2021['index'].isin(topicsPi)]
floodsTopics2021 = floodsTopics2021.sort_values(by=['count'], ascending=False)
sortBy = list(floodsTopics2021['index'])
sorterIndex = dict(zip(sortBy, range(len(sortBy))))

floodsTopics1910 = pd.read_csv(DATA_PATH / 'csv' / 'topics_count_1910.csv', delimiter=',')
floodsTopics1910 = floodsTopics1910[floodsTopics1910['index'].isin(topicsPi)]
floodsTopics1910['Rank'] = floodsTopics1910['index'].map(sorterIndex)
floodsTopics1910 = floodsTopics1910.sort_values(by=['Rank'], ascending=True)

floodsTopics1804 = pd.read_csv(DATA_PATH / 'csv' / 'topics_count_1804.csv', delimiter=',')
floodsTopics1804 = floodsTopics1804[floodsTopics1804['index'].isin(topicsPi)]
floodsTopics1804['Rank'] = floodsTopics1804['index'].map(sorterIndex)
floodsTopics1804 = floodsTopics1804.sort_values(by=['Rank'], ascending=True)

fig = plt.figure(figsize=(18, 6), constrained_layout=True)
gs = gridspec.GridSpec(1, 3, figure=fig)

ax2021 = plt.subplot(gs[0,2])
ax2021.set_title("2021", fontsize=24)
colors2021 = filterColors(floodsTopics2021['index'], colorsTopics)
wedges2021, texts2021, auto  =  ax2021.pie(floodsTopics2021['count'], labels=floodsTopics2021['index'], colors=colors2021, 
            autopct=limitAutopct, labeldistance=None, textprops={'fontsize': 12})

ax1804 = plt.subplot(gs[0,0])
ax1804.set_title("1804", fontsize=24)
colors1804 = filterColors(floodsTopics1804['index'], colorsTopics)
wedges, texts, auto  =  ax1804.pie(floodsTopics1804['count'], labels=floodsTopics1804['index'], colors=colors1804,
              autopct=limitAutopct, labeldistance=None, textprops={'fontsize': 12})

ax1910 = plt.subplot(gs[0,1])
ax1910.set_title("1910", fontsize=24)
colors1910 = filterColors(floodsTopics1910['index'], colorsTopics)
wedges, texts, auto  =  ax1910.pie(floodsTopics1910['count'], labels=floodsTopics1910['index'], colors=colors1910, 
          autopct=limitAutopct, labeldistance=None, textprops={'fontsize': 12})

leg  = ax2021.legend(wedges2021, floodsTopics2021['index'],
          title="Topics",
          loc="center right",
          fontsize=16,
          bbox_to_anchor=(1, 0, 0.5, 1))
leg.set_title("Topics", prop = {'size':20})          

plt.savefig(DATA_PATH / 'img' / 'topics_pie_years.png', dpi=300)
plt.close('all')


#3d Bars -> Parties by date 
germanPartiesDate = pd.read_csv(DATA_PATH / 'csv' / 'parties_date.csv', delimiter=',')
germanPartiesDate = germanPartiesDate.sort_values(by=['Unnamed: 0'], ascending=True)
xa = []
xl = []
ya = []
yl = []
za = []
ca = []
for idx, column in germanPartiesDate.iterrows():
    p = 0
    for party in colorsParties:
        xa.append(idx) 
        xl.append(column['Unnamed: 0'])
        ya.append(p)   
        yl.append(party)
        za.append(column[party])
        ca.append(colorsParties[party])
        p += 1
fig = plt.figure(figsize=(30, 20))
axes = fig.gca(projection='3d')
fig.subplots_adjust(left=0, right=1, bottom=0, top=1.5)
ticksx = germanPartiesDate.index.values.tolist()
plt.xticks(ticksx, germanPartiesDate['Unnamed: 0'],rotation=63, fontsize=18)
ticksy = np.arange(1, 7, 1)
plt.yticks(ticksy, colorsParties.keys(), rotation=-4, fontsize=18, horizontalalignment='left')
axes.tick_params(labelsize=18, pad=20)
axes.set_title("Number of Newspaper Articles mentioning Parties", fontsize=36, y=0.65, pad=-14)
axes.bar3d(xa, ya, 0, 0.8, 0.8, za, color=ca, alpha=0.6)
axes.view_init(elev=20, azim=-75)
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=7))
axes.get_proj = lambda: np.dot(Axes3D.get_proj(axes), np.diag([1.0, 0.7, 0.4, 1]))
colorLeg = list(colorsParties.values())
colorLeg.reverse()
labelLeg = list(colorsParties.keys())
labelLeg.reverse()
custom_lines = [plt.Line2D([],[], ls="", marker='.', 
                mec='k', mfc=c, mew=.1, ms=30) for c in colorLeg]
leg = axes.legend(custom_lines, labelLeg, 
          loc='center left', fontsize=16, bbox_to_anchor=(0.75, .43))
leg.set_title("Topics", prop = {'size':20})   
plt.savefig(DATA_PATH / 'img' / 'parties_date.png', dpi=300)
plt.close('all')


#3d Bars -> Topics by Date 
germanTopicsDate = pd.read_csv(DATA_PATH / 'csv' / 'topics_date.csv', delimiter=',')
germanTopicsDate = germanTopicsDate.sort_values(by=['Unnamed: 0'], ascending=True)
xa = []
xl = []
ya = []
yl = []
za = []
ca = []

for idx, column in germanTopicsDate.iterrows():
    p = 0
    for topic in colorsTopics:
        xa.append(idx) 
        xl.append(column['Unnamed: 0'])
        ya.append(p)  
        yl.append(topic)
        za.append(column[topic])
        ca.append(colorsTopics[topic])
        p += 1
fig = plt.figure(figsize=(30, 20))
ax = fig.gca(projection='3d')
fig.subplots_adjust(left=0, right=1, bottom=0, top=1.5)
ticksx = germanTopicsDate.index.values.tolist()
plt.xticks(ticksx, germanTopicsDate['Unnamed: 0'],rotation=63, fontsize=18)
ticksy = np.arange(1, len(colorsTopics)+1, 1)
plt.yticks(ticksy, colorsTopics.keys(), rotation=-4, fontsize=18, horizontalalignment='left')
ax.tick_params(axis='z', labelsize=18, pad=20)
ax.tick_params(axis='y', pad=20)
ax.set_title("Number of Newspaper Articles covering Topics", fontsize=36, y=0.65, pad=-14)
ax.bar3d(xa, ya, 0, 0.8, 0.8, za, color=ca, alpha=0.6)
ax.view_init(elev=30, azim=-70)
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=7))
ax.get_proj = lambda: np.dot(Axes3D.get_proj(ax), np.diag([1.0, 0.7, 0.4, 1]))
colorLeg = list(colorsTopics.values())
colorLeg.reverse()
labelLeg = list(colorsTopics.keys())
labelLeg.reverse()
custom_lines = [plt.Line2D([],[], ls="", marker='.', 
                mec='k', mfc=c, mew=.1, ms=30) for c in colorLeg]
leg = ax.legend(custom_lines, labelLeg, 
          loc='center left', fontsize=16, bbox_to_anchor=(0.75, .48))
leg.set_title("Topics", prop = {'size':20})            
plt.savefig(DATA_PATH / 'img' / 'topics_date.png', dpi=300)
plt.close('all')


#Pie Topics for all domains
fig = plt.figure(figsize=(12, 15), constrained_layout=True)
gs = gridspec.GridSpec(4, 5, figure=fig)
i = 0
for domain in colorDomains:
    if(not domain in ['summary','other']):
        row = math.floor(i/5)
        col = i%5
        i += 1
        domainSimple = domain.replace('www.','').replace('.','_')  
        floodsTopics = pd.read_csv(DATA_PATH / 'csv' / ('topics_count_'+domainSimple+'.csv'), delimiter=',')
        axDomain = plt.subplot(gs[row,col])
        axDomain.set_title(domain, fontsize=10)
        if(not floodsTopics.empty):
            floodsTopics = floodsTopics[floodsTopics['index'].isin(topicsPi)]
            floodsTopics['Rank'] = floodsTopics['index'].map(sorterIndex)
            floodsTopics = floodsTopics.sort_values(by=['Rank'], ascending=True)
            colors = filterColors(floodsTopics['index'], colorsTopics)
            wedges, texts, auto  =  axDomain.pie(floodsTopics['count'], labels=floodsTopics['index'], colors=colors, 
                    autopct=limitAutopct, labeldistance=None, textprops={'fontsize': 6})
leg  = axDomain.legend(wedges2021, floodsTopics['index'],
        title="Topics",
        loc="center right",
        fontsize=8,
        bbox_to_anchor=(1, 0, 0.5, 1))
leg.set_title("Topics", prop = {'size':10})          
plt.savefig(DATA_PATH / 'img' / 'topics_pie_domains.png', dpi=300)
plt.close('all')