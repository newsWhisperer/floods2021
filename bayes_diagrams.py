import pandas as pd
import numpy as np
import math
import random

import datetime as dt
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.ticker as mticker
import matplotlib.cm as cm
import seaborn as sns

from pathlib import Path
import os.path

DATA_PATH = Path.cwd()

if(not os.path.exists(DATA_PATH / 'img')):
    os.mkdir(DATA_PATH / 'img')

#Colors:
#https://matplotlib.org/stable/gallery/color/colormap_reference.html#sphx-glr-gallery-color-colormap-reference-py
#https://matplotlib.org/stable/gallery/color/named_colors.html#sphx-glr-gallery-color-named-colors-py
#Newspaper
#Topics
#Parties

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

def log_tick_formatter(val, pos=None):
    return f"$10^{{{int(val)}}}$"  # remove int() if you don't use MaxNLocator
    # return f"{10**val:.2e}"      # e-Notation

def sqrt_tick_formatter(val, pos=None):
    return f"${{{int(val)}}}^2$"  # remove int() if you don't use MaxNLocator
    # return f"{10**val:.2e}"      # e-Notation



germanTopicsDate = pd.read_csv(DATA_PATH / "csv" / 'dates_bayes_article_count.csv', delimiter=',')
germanTopicsDate = germanTopicsDate.sort_values(by=['Unnamed: 0'], ascending=True)
#print(germanTopicsDate)
#colorsTopics

xa = []
xl = []
ya = []
yl = []
za = []
ca = []

relativePercentage = True
relativePercentage = False

if(relativePercentage):
    for index, column in germanTopicsDate.iterrows():
        suma = 0
        for topic in colorsTopics:
            suma += column[topic]
        for topic in colorsTopics:
            germanTopicsDate.loc[index,topic] = column[topic] / suma

#for idx in germanPartiesDate.index.values.tolist():
for idx, column in germanTopicsDate.iterrows():
    p = 0
    for topic in colorsTopics:
        xa.append(idx) # date
        xl.append(column['Unnamed: 0'])
        ya.append(p)   #
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

colorLeg = list(colorsTopics.values())#.reverse()
colorLeg.reverse()
labelLeg = list(colorsTopics.keys())#.reverse()
labelLeg.reverse()
custom_lines = [plt.Line2D([],[], ls="", marker='.', 
                mec='k', mfc=c, mew=.1, ms=30) for c in colorLeg]
             
leg = ax.legend(custom_lines, labelLeg, 
          loc='center left', fontsize=16, bbox_to_anchor=(0.75, .48))
leg.set_title("Topics", prop = {'size':20})            

#i=0
#for ylabel in plt.gca().get_yticklabels():
# ylabel.set_color(list(colorsTopics.values())[i])
# i += 1 

#plt.show()
if(relativePercentage):
    plt.savefig(DATA_PATH / "img" / "dates_bayes_article_relative.png", dpi=300)
else:
    plt.savefig(DATA_PATH / "img" / "dates_bayes_article_count.png", dpi=300)
plt.close('all')



germanTopicsDate = pd.read_csv(DATA_PATH / "csv" / 'dates_bayes_sentence_count.csv', delimiter=',')
germanTopicsDate = germanTopicsDate.sort_values(by=['Unnamed: 0'], ascending=True)
#print(germanTopicsDate)
#colorsTopics

xa = []
xl = []
ya = []
yl = []
za = []
ca = []

if(relativePercentage):
    for index, column in germanTopicsDate.iterrows():
        suma = 0
        for topic in colorsTopics:
            suma += column[topic]
        for topic in colorsTopics:
            germanTopicsDate.loc[index,topic] = column[topic] / suma

#for idx in germanPartiesDate.index.values.tolist():
for idx, column in germanTopicsDate.iterrows():
    p = 0
    for topic in colorsTopics:
        xa.append(idx) # date
        xl.append(column['Unnamed: 0'])
        ya.append(p)   #
        yl.append(topic)
        #za.append(math.log(1+column[topic]))
        if(relativePercentage):
            za.append(column[topic]) 
        else:
            za.append(math.sqrt(column[topic]))
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
if(not relativePercentage):
    ax.zaxis.set_major_formatter(mticker.FuncFormatter(sqrt_tick_formatter))
    ax.zaxis.set_major_locator(mticker.MaxNLocator(integer=True))
ax.set_title("Number of Sentences in Newspaper Articles covering Topics", fontsize=36, y=0.65, pad=-14)

ax.bar3d(xa, ya, 0, 0.8, 0.8, za, color=ca, alpha=0.6)
ax.view_init(elev=30, azim=-70)
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=7))

ax.get_proj = lambda: np.dot(Axes3D.get_proj(ax), np.diag([1.0, 0.7, 0.4, 1]))

colorLeg = list(colorsTopics.values())#.reverse()
colorLeg.reverse()
labelLeg = list(colorsTopics.keys())#.reverse()
labelLeg.reverse()
custom_lines = [plt.Line2D([],[], ls="", marker='.', 
                mec='k', mfc=c, mew=.1, ms=30) for c in colorLeg]
             
leg = ax.legend(custom_lines, labelLeg, 
          loc='center left', fontsize=16, bbox_to_anchor=(0.75, .48))
leg.set_title("Topics", prop = {'size':20})            

#i=0
#for ylabel in plt.gca().get_yticklabels():
# ylabel.set_color(list(colorsTopics.values())[i])
# i += 1 

#plt.show()
if(relativePercentage):
    plt.savefig(DATA_PATH / "img" / "dates_bayes_sentence_relative.png", dpi=300)
else:
    plt.savefig(DATA_PATH / "img" / "dates_bayes_sentence_count.png", dpi=300)
plt.close('all')



germanTopicsDate = pd.read_csv(DATA_PATH / "csv" / 'dates_bayes_word_count.csv', delimiter=',')
germanTopicsDate = germanTopicsDate.sort_values(by=['Unnamed: 0'], ascending=True)
#print(germanTopicsDate)
#colorsTopics

xa = []
xl = []
ya = []
yl = []
za = []
ca = []

if(relativePercentage):
    for index, column in germanTopicsDate.iterrows():
        suma = 0
        for topic in colorsTopics:
            suma += column[topic]
        for topic in colorsTopics:
            germanTopicsDate.loc[index,topic] = column[topic] / suma

#for idx in germanPartiesDate.index.values.tolist():
for idx, column in germanTopicsDate.iterrows():
    p = 0
    for topic in colorsTopics:
        xa.append(idx) # date
        xl.append(column['Unnamed: 0'])
        ya.append(p)   #
        yl.append(topic)
        if(relativePercentage):
            za.append(column[topic]) 
        else:
            za.append(math.log10(1+column[topic]))
        #za.append(math.sqrt(column[topic]))
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
if(not relativePercentage):
    ax.zaxis.set_major_formatter(mticker.FuncFormatter(log_tick_formatter))
    ax.zaxis.set_major_locator(mticker.MaxNLocator(integer=True))
ax.set_title("Number of Words in Newspaper Articles covering Topics", fontsize=36, y=0.65, pad=-14)

ax.bar3d(xa, ya, 0, 0.8, 0.8, za, color=ca, alpha=0.6)
ax.view_init(elev=30, azim=-70)
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=7))

ax.get_proj = lambda: np.dot(Axes3D.get_proj(ax), np.diag([1.0, 0.7, 0.4, 1]))

colorLeg = list(colorsTopics.values())#.reverse()
colorLeg.reverse()
labelLeg = list(colorsTopics.keys())#.reverse()
labelLeg.reverse()
custom_lines = [plt.Line2D([],[], ls="", marker='.', 
                mec='k', mfc=c, mew=.1, ms=30) for c in colorLeg]
             
leg = ax.legend(custom_lines, labelLeg, 
          loc='center left', fontsize=16, bbox_to_anchor=(0.75, .48))
leg.set_title("Topics", prop = {'size':20})            

#i=0
#for ylabel in plt.gca().get_yticklabels():
# ylabel.set_color(list(colorsTopics.values())[i])
# i += 1 

#plt.show()
if(relativePercentage):
    plt.savefig(DATA_PATH / "img" / "dates_bayes_word_relative.png", dpi=300)
else:
    plt.savefig(DATA_PATH / "img" / "dates_bayes_word_count.png", dpi=300)
plt.close('all')



#https://matplotlib.org/stable/gallery/lines_bars_and_markers/bar_stacked.html#sphx-glr-gallery-lines-bars-and-markers-bar-stacked-py
#Newspaper by Date  (dates_domains_floods_count.csv)
germanDomainsDate = pd.read_csv(DATA_PATH / "csv" / 'dates_bayes_article_count.csv', delimiter=',')
plt.rcdefaults()
fig, ax = plt.subplots(figsize=(40, 20))

topicsList = list(colorsTopics.keys())
#print(germanDomainsDate(topicsList))
germanDomainsDate2 = germanDomainsDate.reindex(topicsList, axis=1)
print(germanDomainsDate2)
for index, column in germanDomainsDate2.iterrows():
  suma = 0
  for topic in topicsList:
      suma += column[topic]
  for topic in topicsList:
      germanDomainsDate2.loc[index,topic] = column[topic] / suma
print(germanDomainsDate2)    
#domainsOnly = germanDomainsDate.drop(['Unnamed: 0','summary'],axis=1)
#print(domainsOnly)
#domainsT = np.log(1+germanDomainsDate2.T)
domainsT = germanDomainsDate2.T
colors = filterColors(list(germanDomainsDate2.head()), colorsTopics)
print(colors)
#ax.stackplot(germanDomainsDate['Unnamed: 0'], ,axis=1).T)

dates = germanDomainsDate['Unnamed: 0']
#x = [dt.datetime.strptime(d,'%Y-%m-%d').date() for d in dates]
#print(x)
#plt.xticks(x)
ax.stackplot(dates, domainsT, colors=colors, labels=list(germanDomainsDate2.head()))
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=7))
#plt.gca().xaxis.set_major_locator(mdates.DayLocator(bymonthday=[5,15,25]))
plt.gcf().autofmt_xdate()
plt.xticks(fontsize=36)
plt.yticks(fontsize=36)

ax.set_title("Fraction of articles dominated by topic", fontsize=48)
handles, labels = ax.get_legend_handles_labels()
leg = ax.legend(reversed(handles), reversed(labels),
    fontsize=24, 
    loc="center right",
    bbox_to_anchor=(1.1, 0.70))
leg.set_title("Topics", prop = {'size':36}) 

#plt.show()
plt.savefig(DATA_PATH / "img" / "dates_bayes_article_stacked_bar.png", dpi=300)
plt.close('all')

germanDomainsDate = pd.read_csv(DATA_PATH / "csv" / 'dates_bayes_sentence_count.csv', delimiter=',')
plt.rcdefaults()
fig, ax = plt.subplots(figsize=(40, 20))

topicsList = list(colorsTopics.keys())
#print(germanDomainsDate(topicsList))
germanDomainsDate2 = germanDomainsDate.reindex(topicsList, axis=1)
print(germanDomainsDate2)
for index, column in germanDomainsDate2.iterrows():
  suma = 0
  for topic in topicsList:
      suma += column[topic]
  for topic in topicsList:
      germanDomainsDate2.loc[index,topic] = column[topic] / suma
print(germanDomainsDate2)    
#domainsOnly = germanDomainsDate.drop(['Unnamed: 0','summary'],axis=1)
#print(domainsOnly)
#domainsT = np.log(1+germanDomainsDate2.T)
domainsT = germanDomainsDate2.T
colors = filterColors(list(germanDomainsDate2.head()), colorsTopics)
print(colors)
#ax.stackplot(germanDomainsDate['Unnamed: 0'], ,axis=1).T)

dates = germanDomainsDate['Unnamed: 0']
#x = [dt.datetime.strptime(d,'%Y-%m-%d').date() for d in dates]
#print(x)
#plt.xticks(x)
ax.stackplot(dates, domainsT, colors=colors, labels=list(germanDomainsDate2.head()))
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=7))
#plt.gca().xaxis.set_major_locator(mdates.DayLocator(bymonthday=[5,15,25]))
plt.gcf().autofmt_xdate()
plt.xticks(fontsize=36)
plt.yticks(fontsize=36)

ax.set_title("Fraction of sentences dominated by topic", fontsize=48)
handles, labels = ax.get_legend_handles_labels()
leg = ax.legend(reversed(handles), reversed(labels),
    fontsize=24, 
    loc="center right",
    bbox_to_anchor=(1.1, 0.70))
leg.set_title("Topics", prop = {'size':36}) 

#plt.show()
plt.savefig(DATA_PATH / "img" / "dates_bayes_sentence_stacked_bar.png", dpi=300)
plt.close('all')

germanDomainsDate = pd.read_csv(DATA_PATH / "csv" / 'dates_bayes_word_count.csv', delimiter=',')
plt.rcdefaults()
fig, ax = plt.subplots(figsize=(40, 20))

topicsList = list(colorsTopics.keys())
#print(germanDomainsDate(topicsList))
germanDomainsDate2 = germanDomainsDate.reindex(topicsList, axis=1)
print(germanDomainsDate2)
for index, column in germanDomainsDate2.iterrows():
  suma = 0
  for topic in topicsList:
      suma += column[topic]
  for topic in topicsList:
      germanDomainsDate2.loc[index,topic] = column[topic] / suma
print(germanDomainsDate2)    
#domainsOnly = germanDomainsDate.drop(['Unnamed: 0','summary'],axis=1)
#print(domainsOnly)
#domainsT = np.log(1+germanDomainsDate2.T)
domainsT = germanDomainsDate2.T
colors = filterColors(list(germanDomainsDate2.head()), colorsTopics)
print(colors)
#ax.stackplot(germanDomainsDate['Unnamed: 0'], ,axis=1).T)

dates = germanDomainsDate['Unnamed: 0']
#x = [dt.datetime.strptime(d,'%Y-%m-%d').date() for d in dates]
#print(x)
#plt.xticks(x)
ax.stackplot(dates, domainsT, colors=colors, labels=list(germanDomainsDate2.head()))
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=7))
#plt.gca().xaxis.set_major_locator(mdates.DayLocator(bymonthday=[5,15,25]))
plt.gcf().autofmt_xdate()
plt.xticks(fontsize=36)
plt.yticks(fontsize=36)

ax.set_title("Fraction of words dominated by topic", fontsize=48)
handles, labels = ax.get_legend_handles_labels()
leg = ax.legend(reversed(handles), reversed(labels),
    fontsize=24, 
    loc="center right",
    bbox_to_anchor=(1.1, 0.70))
leg.set_title("Topics", prop = {'size':36}) 

#plt.show()
plt.savefig(DATA_PATH / "img" / "dates_bayes_word_stacked_bar.png", dpi=300)
plt.close('all')



germanDomainsDate = pd.read_csv(DATA_PATH / "csv" / 'dates_bayes_relative.csv', delimiter=',')
plt.rcdefaults()
fig, ax = plt.subplots(figsize=(40, 20))

topicsList = list(colorsTopics.keys())
#print(germanDomainsDate(topicsList))
germanDomainsDate2 = germanDomainsDate.reindex(topicsList, axis=1)
print(germanDomainsDate2)
for index, column in germanDomainsDate2.iterrows():
  suma = 0
  for topic in topicsList:
      suma += column[topic]
  for topic in topicsList:
      germanDomainsDate2.loc[index,topic] = column[topic] / suma
print(germanDomainsDate2)    
#domainsOnly = germanDomainsDate.drop(['Unnamed: 0','summary'],axis=1)
#print(domainsOnly)
#domainsT = np.log(1+germanDomainsDate2.T)
domainsT = germanDomainsDate2.T
colors = filterColors(list(germanDomainsDate2.head()), colorsTopics)
print(colors)
#ax.stackplot(germanDomainsDate['Unnamed: 0'], ,axis=1).T)

dates = germanDomainsDate['Unnamed: 0']
#x = [dt.datetime.strptime(d,'%Y-%m-%d').date() for d in dates]
#print(x)
#plt.xticks(x)
ax.stackplot(dates, domainsT, colors=colors, labels=list(germanDomainsDate2.head()))
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=7))
#plt.gca().xaxis.set_major_locator(mdates.DayLocator(bymonthday=[5,15,25]))
plt.gcf().autofmt_xdate()
plt.xticks(fontsize=36)
plt.yticks(fontsize=36)

ax.set_title("Fraction of topics per date", fontsize=48)
handles, labels = ax.get_legend_handles_labels()
leg = ax.legend(reversed(handles), reversed(labels),
    fontsize=24, 
    loc="center right",
    bbox_to_anchor=(1.1, 0.70))
leg.set_title("Topics", prop = {'size':36}) 

#plt.show()
plt.savefig(DATA_PATH / "img" / "dates_bayes_relative_stacked_bar.png", dpi=300)
plt.close('all')




germanDomainsDate = pd.read_csv(DATA_PATH / "csv" / 'dates_bayes_count.csv', delimiter=',')
plt.rcdefaults()
fig, ax = plt.subplots(figsize=(40, 20))

topicsList = list(colorsTopics.keys())
#print(germanDomainsDate(topicsList))
germanDomainsDate2 = germanDomainsDate.reindex(topicsList, axis=1)
print(germanDomainsDate2)
for index, column in germanDomainsDate2.iterrows():
  suma = 0
  for topic in topicsList:
      suma += column[topic]
  for topic in topicsList:
      germanDomainsDate2.loc[index,topic] = column[topic] / suma
print(germanDomainsDate2)    
#domainsOnly = germanDomainsDate.drop(['Unnamed: 0','summary'],axis=1)
#print(domainsOnly)
#domainsT = np.log(1+germanDomainsDate2.T)
domainsT = germanDomainsDate2.T
colors = filterColors(list(germanDomainsDate2.head()), colorsTopics)
print(colors)
#ax.stackplot(germanDomainsDate['Unnamed: 0'], ,axis=1).T)

dates = germanDomainsDate['Unnamed: 0']
#x = [dt.datetime.strptime(d,'%Y-%m-%d').date() for d in dates]
#print(x)
#plt.xticks(x)
ax.stackplot(dates, domainsT, colors=colors, labels=list(germanDomainsDate2.head()))
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=7))
#plt.gca().xaxis.set_major_locator(mdates.DayLocator(bymonthday=[5,15,25]))
plt.gcf().autofmt_xdate()
plt.xticks(fontsize=36)
plt.yticks(fontsize=36)

ax.set_title("Count of topics per date", fontsize=48)
handles, labels = ax.get_legend_handles_labels()
leg = ax.legend(reversed(handles), reversed(labels),
    fontsize=24, 
    loc="center right",
    bbox_to_anchor=(1.1, 0.70))
leg.set_title("Topics", prop = {'size':36}) 

#plt.show()
plt.savefig(DATA_PATH / "img" / "dates_bayes_count_stacked_bar.png", dpi=300)
plt.close('all')


germanDomainsDate = pd.read_csv(DATA_PATH / "csv" / 'weeks_bayes_relative.csv', delimiter=',')
plt.rcdefaults()
fig, ax = plt.subplots(figsize=(40, 20))

topicsList = list(colorsTopics.keys())
#print(germanDomainsDate(topicsList))
germanDomainsDate2 = germanDomainsDate.reindex(topicsList, axis=1)
print(germanDomainsDate2)
for index, column in germanDomainsDate2.iterrows():
  suma = 0
  for topic in topicsList:
      suma += column[topic]
  for topic in topicsList:
      germanDomainsDate2.loc[index,topic] = column[topic] / suma
print(germanDomainsDate2)    
#domainsOnly = germanDomainsDate.drop(['Unnamed: 0','summary'],axis=1)
#print(domainsOnly)
#domainsT = np.log(1+germanDomainsDate2.T)
domainsT = germanDomainsDate2.T
colors = filterColors(list(germanDomainsDate2.head()), colorsTopics)
print(colors)
#ax.stackplot(germanDomainsDate['Unnamed: 0'], ,axis=1).T)

dates = germanDomainsDate['Unnamed: 0']
#x = [dt.datetime.strptime(d,'%Y-%m-%d').date() for d in dates]
#print(x)
#plt.xticks(x)
ax.stackplot(dates, domainsT, colors=colors, labels=list(germanDomainsDate2.head()))
#plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1))
#plt.gca().xaxis.set_major_locator(mdates.DayLocator(bymonthday=[5,15,25]))
plt.gcf().autofmt_xdate()
plt.xticks(fontsize=36)
plt.yticks(fontsize=36)

ax.set_title("Fraction of topics per date", fontsize=48)
handles, labels = ax.get_legend_handles_labels()
leg = ax.legend(reversed(handles), reversed(labels),
    fontsize=24, 
    loc="center right",
    bbox_to_anchor=(1.1, 0.70))
leg.set_title("Topics", prop = {'size':36}) 

#plt.show()
plt.savefig(DATA_PATH / "img" / "weeks_bayes_relative_stacked_bar.png", dpi=300)
plt.close('all')


germanDomainsDate = pd.read_csv(DATA_PATH / "csv" / 'weeks_bayes_count.csv', delimiter=',')
plt.rcdefaults()
fig, ax = plt.subplots(figsize=(40, 20))

topicsList = list(colorsTopics.keys())
#print(germanDomainsDate(topicsList))
germanDomainsDate2 = germanDomainsDate.reindex(topicsList, axis=1)
print(germanDomainsDate2)
for index, column in germanDomainsDate2.iterrows():
  suma = 0
  for topic in topicsList:
      suma += column[topic]
  for topic in topicsList:
      germanDomainsDate2.loc[index,topic] = column[topic] / suma
print(germanDomainsDate2)    
#domainsOnly = germanDomainsDate.drop(['Unnamed: 0','summary'],axis=1)
#print(domainsOnly)
#domainsT = np.log(1+germanDomainsDate2.T)
domainsT = germanDomainsDate2.T
colors = filterColors(list(germanDomainsDate2.head()), colorsTopics)
print(colors)
#ax.stackplot(germanDomainsDate['Unnamed: 0'], ,axis=1).T)

dates = germanDomainsDate['Unnamed: 0']
#x = [dt.datetime.strptime(d,'%Y-%m-%d').date() for d in dates]
#print(x)
#plt.xticks(x)
ax.stackplot(dates, domainsT, colors=colors, labels=list(germanDomainsDate2.head()))
#plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1))
#plt.gca().xaxis.set_major_locator(mdates.DayLocator(bymonthday=[5,15,25]))
plt.gcf().autofmt_xdate()
plt.xticks(fontsize=36)
plt.yticks(fontsize=36)

ax.set_title("Fraction of topics per date", fontsize=48)
handles, labels = ax.get_legend_handles_labels()
leg = ax.legend(reversed(handles), reversed(labels),
    fontsize=24, 
    loc="center right",
    bbox_to_anchor=(1.1, 0.70))
leg.set_title("Topics", prop = {'size':36}) 

#plt.show()
plt.savefig(DATA_PATH / "img" / "weeks_bayes_count_stacked_bar.png", dpi=300)
plt.close('all')


### weeks_bayes_sentence_count
germanDomainsDate = pd.read_csv(DATA_PATH / "csv" / 'weeks_bayes_sentence_count.csv', delimiter=',')
plt.rcdefaults()
fig, ax = plt.subplots(figsize=(40, 20))

topicsList = list(colorsTopics.keys())
#print(germanDomainsDate(topicsList))
germanDomainsDate2 = germanDomainsDate.reindex(topicsList, axis=1)
print(germanDomainsDate2)
for index, column in germanDomainsDate2.iterrows():
  suma = 0
  for topic in topicsList:
      suma += column[topic]
  for topic in topicsList:
      germanDomainsDate2.loc[index,topic] = column[topic] / suma
print(germanDomainsDate2)    
#domainsOnly = germanDomainsDate.drop(['Unnamed: 0','summary'],axis=1)
#print(domainsOnly)
#domainsT = np.log(1+germanDomainsDate2.T)
domainsT = germanDomainsDate2.T
colors = filterColors(list(germanDomainsDate2.head()), colorsTopics)
print(colors)
#ax.stackplot(germanDomainsDate['Unnamed: 0'], ,axis=1).T)

dates = germanDomainsDate['Unnamed: 0']
#x = [dt.datetime.strptime(d,'%Y-%m-%d').date() for d in dates]
#print(x)
#plt.xticks(x)
ax.stackplot(dates, domainsT, colors=colors, labels=list(germanDomainsDate2.head()))
#plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1))
#plt.gca().xaxis.set_major_locator(mdates.DayLocator(bymonthday=[5,15,25]))
plt.gcf().autofmt_xdate()
plt.xticks(fontsize=36)
plt.yticks(fontsize=36)

ax.set_title("Fraction of topics in sentences per week", fontsize=48)
handles, labels = ax.get_legend_handles_labels()
leg = ax.legend(reversed(handles), reversed(labels),
    fontsize=24, 
    loc="center right",
    bbox_to_anchor=(1.1, 0.70))
leg.set_title("Topics", prop = {'size':36}) 

#plt.show()
plt.savefig(DATA_PATH / "img" / "weeks_bayes_sentence_count_stacked_bar.png", dpi=300)
plt.close('all')


def limitAutopct(pct):
    return ('%1.1f%%' % pct) if pct > 4.0 else ''

##
colorDomains = {
# 'summary':0,
 'other':'gray', 'www.zeit.de':'firebrick', 'www.focus.de':'darkcyan', 'www.faz.net':'darkturquoise', 'www.sueddeutsche.de':'salmon', 'www.stern.de':'darkred',
 'www.spiegel.de':'orangered', 'www.morgenpost.de':'steelblue', 'www.n-tv.de':'darkmagenta', 'www.welt.de':'mediumblue', 'www.tagesschau.de':'darkgreen',
 'www.handelsblatt.com':'orange', 'www.bild.de':'midnightblue', 'www.tagesspiegel.de':'palegreen', 'www.dw.com':'yellowgreen', 'www.wiwo.de':'gold',
 'taz.de':'red', 'www.heise.de':'fuchsia', 'www.nzz.ch':'wheat', 'www.t-online.de':'purple', 'orf.at':'green', 
 # 'www.diepresse.com':'yellow'
}

germanDomainsTopics = pd.read_csv(DATA_PATH / "csv" / 'domain_bayes_sentence_count.csv', delimiter=',')

fig = plt.figure(figsize=(12, 15), constrained_layout=True)
gs = gridspec.GridSpec(4, 5, figure=fig)
i = 0

wedges = []
texts = []

for index, column in germanDomainsTopics.iterrows():
    domain = column['Unnamed: 0']
    if(domain in colorDomains):
        topicLabels = []
        topicCount = []
        topicColor = []
        for topic in colorsTopics: 
            if(topic in column):
                topicLabels.append(topic)
                topicCount.append(column[topic])
                topicColor.append(colorsTopics[topic]) 
        
        row = math.floor(i/5)
        col = i%5
        i += 1
        domainSimple = domain.replace('www.','').replace('.','_') 
        axDomain = plt.subplot(gs[row,col])
        axDomain.set_title(domain, fontsize=10)
        wedges, texts, auto  = axDomain.pie(topicCount, labels=topicLabels, colors=topicColor, 
                autopct=limitAutopct, labeldistance=None, textprops={'fontsize': 6})


        #ax4 = plt.subplot(gs[0,3])
        #ax4.axis("off")
leg  = axDomain.legend(wedges, topicLabels,
        title="Topics",
        loc="center right",
        fontsize=8,
        bbox_to_anchor=(1, 0, 0.5, 1))
leg.set_title("Topics", prop = {'size':10})          

#plt.setp(autotexts, size=8, weight="bold")
plt.savefig(DATA_PATH / "img" / "domains_bayes_count_pie.png", dpi=300)
plt.close('all')


topicWordsRelDF = pd.read_csv(DATA_PATH / "csv" / "words_bayes_topic_all.csv", delimiter=',',index_col='word')
topicWordsRelDF = topicWordsRelDF[topicWordsRelDF['Unnamed: 0'] != 'summaryOfAllWords']
#print(domainWordsRelDF)

##dfpca = pd.read_csv(DATA_PATH / "csv" / "words_bayes_topic_pca.csv", delimiter=',',index_col='word')
dfpca = pd.read_csv(DATA_PATH / "csv" / "words_bayes_topic_pca.csv", delimiter=',')

colorsTopics = {
 'Wine': '800080',
 'Troublemakers': 'FF00FF',
 'Insurance': 'FFE4B5',
 'Risk': '008000',
 'Responsability': 'FA8072',
 'Pollution': '00FF00',
 'Health': 'FFD700',
 'Causes': '008B8B',
 'Warnings': 'FF8C00',
 'Solidarity': 'ADFF2F',
 'Infrastructure': 'A9A9A9',
 'Rescue': '6B8E23',
 'Politics': '9370DB',
 'Damage':'B22222', 
 'Weather': '87CEEB', 
 'Victims': 'FF0000',
 'Flood Hazard': '4169E1', 
}

def combine_hex_values(d):
  d_items = sorted(d.items())
  tot_weight = sum(d.values())
  red = int(sum([int(k[:2], 16)*v for k, v in d_items])/tot_weight)
  green = int(sum([int(k[2:4], 16)*v for k, v in d_items])/tot_weight)
  blue = int(sum([int(k[4:6], 16)*v for k, v in d_items])/tot_weight)
  zpad = lambda x: x if len(x)==2 else '0' + x
  return zpad(hex(red)[2:]) + zpad(hex(green)[2:]) + zpad(hex(blue)[2:])

plt.figure( figsize=(20,15) )
plt.xlim([-3, 6])
plt.ylim([-3, 3])
i=0
for index, column in dfpca.iterrows():
  i += 1
  if(i % 50 == 0):
     print(i)    
  if(not " " in str(column['word'])): 
    maxColor = '000000'
    nxtColor = '555555'
    maxprobabiliyty = -15  #log!
    nxtprobabiliyty = -15  

    for topic in colorsTopics:
        if(str(column['word']) in topicWordsRelDF[topic]):
            if(topicWordsRelDF[topic][str(column['word'])]> maxprobabiliyty):
                maxprobabiliyty = topicWordsRelDF[topic][str(column['word'])]
                maxColor = colorsTopics[topic]
    for topic in colorsTopics:
        if(str(column['word']) in topicWordsRelDF[topic]):
            if(maxprobabiliyty > topicWordsRelDF[topic][str(column['word'])] > nxtprobabiliyty):
                nxtprobabiliyty = topicWordsRelDF[topic][str(column['word'])]
                nxtColor = colorsTopics[topic] 
    if((maxprobabiliyty < -12) & (nxtprobabiliyty < -12)):
        maxColor = '555555'
        nxtColor = '555555'                    
 
    maxColor = '#'+combine_hex_values({maxColor: math.exp(maxprobabiliyty) , nxtColor: math.exp(nxtprobabiliyty)})                           
    x = random.uniform(-0.1, 0.1)+column[0]
    y = random.uniform(-0.1, 0.1)+column[1]
    s = (2+math.sqrt(1+math.sqrt(column['summary'])))
    plt.text(x, y, column['word'], color='#ffffff', fontsize=s, ha='center', va='center', zorder=s-1E-7, fontweight='bold')
    plt.text(x, y, column['word'], color=maxColor, fontsize=s, ha='center', va='center', zorder=s)


colorLeg = list(colorsTopics.values())#.reverse()
colorLeg.reverse()
labelLeg = list(colorsTopics.keys())#.reverse()
labelLeg.reverse()
custom_lines = [plt.Line2D([],[], ls="", marker='.', 
                mec='k', mfc='#'+c, mew=.1, ms=20) for c in colorLeg]
             
leg = plt.legend(custom_lines, labelLeg, 
          loc='center left', fontsize=10, bbox_to_anchor=(0.9, .80))
leg.set_title("Topics", prop = {'size':12}) 

plt.savefig(DATA_PATH / 'img' / 'words_bayes_topic_pca.png', dpi=300)  
