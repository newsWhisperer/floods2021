import files

import pandas as pd
import numpy as np
import math

from pathlib import Path
import os.path

import nltk
from HanTa import HanoverTagger as ht

import matplotlib.pyplot as plt
import networkx as nx

DATA_PATH = Path.cwd()

floodsDF = files.getNewsDF(state='singular')
floodsDF = floodsDF[floodsDF['valid']==1]
floodsDF = floodsDF[floodsDF['language']=='de']

locationsDF = pd.read_csv(DATA_PATH / 'csv' / 'geonames.csv', delimiter=',',index_col='phrase')
## locationsDF = locationsDF[locationsDF['count']>8]
locationsDF = locationsDF[((locationsDF['country']=='Deutschland') | (locationsDF['geotype']=='A'))]
locationsDF = locationsDF[locationsDF['geonames'].notnull()]
locationsDF = locationsDF[locationsDF['geotype']!='S']
locationsDF = locationsDF[locationsDF['geotype']!='L']
locationsDF.index = locationsDF.index.str.lower()
locationsDF = locationsDF[~locationsDF.index.duplicated(keep='first')]
locationsDict = locationsDF.to_dict('index')

organizationsDF = pd.read_csv(DATA_PATH / 'csv' / 'entities_orgs.csv', delimiter=',',index_col='phrase')
## organizationsDF = organizationsDF[organizationsDF['count']>5]
organizationsDF.index = organizationsDF.index.str.lower()
organizationsDF = organizationsDF[~organizationsDF.index.duplicated(keep='first')]
organizationsDict = organizationsDF.to_dict('index')

personsDF = pd.read_csv(DATA_PATH / 'csv' / 'entities_persons.csv', delimiter=',',index_col='phrase')
## personsDF = personsDF[personsDF['count']>3]
personsDF.index = personsDF.index.str.lower()
personsDF.index = personsDF.index.str.strip()
personsDF = personsDF[~personsDF.index.duplicated(keep='first')]
personsDict = personsDF.to_dict('index')

language = 'ger'
nltk.download('punkt')
tagger = ht.HanoverTagger('morphmodel_'+language+'.pgz')

stopWords = ['der', 'die', 'das', 'es', 'von', 'aus', 'image', 'wenn', 'li', '+++', 'coronavirus-liveticker', 'ge', 'information', 'party', 'ads',
  'new', 'data', 'ticker', 'and', 'stern-ticker', 'when', 'live-ticker', 'personal', 'us', 'nan', 'name', 'z', 'et', 'd','e','co']

useGrammar = ['NN','NE']
#useGrammar = ['ADJA','ADJD']
#useGrammar = ['VAFIN', 'VVFIN']
floodNodes = {}
floodEdges = {}

#simplify text
i=0
for index, column in floodsDF.iterrows():
    i += 1
    if(i % 50 == 0):
        print(i)
    quote = str(column.title)+' ' +str(column.description)+' '+str(column.content)
    if((len(str(column.quote))>len(quote))):
        quote = str(column.quote)    
    sentences = nltk.sent_tokenize(quote,language='german')   #todo: language->var
    for sentence in sentences:
        tokens = nltk.tokenize.word_tokenize(sentence,language='german') 
        lemmata = tagger.tag_sent(tokens,taglevel = 2)
        for (orig,lemma,gramma) in lemmata:
          if(gramma in useGrammar):   
            if('+' in lemma):
                new = ' '.join(lemma.split('+')) 
                floodsDF.at[index, 'title'] = str(floodsDF['title'][index]).replace(orig,new)
                floodsDF.at[index, 'description'] = str(floodsDF['description'][index]).replace(orig,new)
                floodsDF.at[index, 'content'] = str(floodsDF['content'][index]).replace(orig,new)
                floodsDF.at[index, 'quote'] = str(floodsDF['quote'][index]).replace(orig,new)
            if('-' in lemma):
                new = ' '.join(lemma.split('-')) 
                floodsDF.at[index, 'title'] = str(floodsDF['title'][index]).replace(orig,new)
                floodsDF.at[index, 'description'] = str(floodsDF['description'][index]).replace(orig,new)
                floodsDF.at[index, 'content'] = str(floodsDF['content'][index]).replace(orig,new)
                floodsDF.at[index, 'quote'] = str(floodsDF['quote'][index]).replace(orig,new)

#then collect nodes
i=0
for index, column in floodsDF.iterrows():
    i += 1
    if(i % 50 == 0):
        print(i)
    quote = str(column.title)+' ' +str(column.description)+' '+str(column.content)
    if((len(str(column.quote))>len(quote))):
        quote = str(column.quote)  
    sentences = nltk.sent_tokenize(quote,language='german')   #todo: language->var
    for sentence in sentences:
        tokens = nltk.tokenize.word_tokenize(sentence,language='german') 
        lemmata = tagger.tag_sent(tokens,taglevel = 2)
        for (orig,lemma,gramma) in lemmata:
         if(not lemma in stopWords):   
          if(gramma in useGrammar):
            if(not lemma in floodNodes):
                floodNodes[lemma] = {'lemma':lemma, 'orig':orig, 'gramma':gramma, 'counter':0}
            floodNodes[lemma]['counter'] += 1
            
floodNodesDF = pd.DataFrame.from_dict(floodNodes, orient='index', columns=['lemma', 'orig', 'gramma', 'counter'])  
## floodNodesDF = floodNodesDF[floodNodesDF['counter']>175]
floodNodesDF = floodNodesDF.sort_values('counter', ascending=False)
remainingNodes = floodNodesDF['lemma'].tolist()
print(floodNodesDF)

i=0
for index, column in floodsDF.iterrows():
    i += 1
    if(i % 50 == 0):
        print(i)
    quote = str(column.title)+' ' +str(column.description)+' '+str(column.content)
    if((len(str(column.quote))>len(quote))):
        quote = str(column.quote)  
    sentences = nltk.sent_tokenize(quote,language='german')   #todo: language->var
    prevLemma = None
    connector = 0.5
    for sentence in sentences:
        tokens = nltk.tokenize.word_tokenize(sentence,language='german') 
        lemmata = tagger.tag_sent(tokens,taglevel = 2)
        for (orig,lemma,gramma) in lemmata:
          if(lemma in remainingNodes):
            if(prevLemma):
                connect = (prevLemma, lemma)
                if(prevLemma > lemma):
                    connect = (lemma, prevLemma)
                if(not connect in floodEdges):
                    floodEdges[connect] = {'prev': prevLemma, 'curr': lemma, 'counter':0}
                floodEdges[connect]['counter'] += connector
                connector = 1.0
            prevLemma = lemma 


floodEdgesDF = pd.DataFrame.from_dict(floodEdges, orient='index', columns=['prev', 'curr', 'counter'])  
## floodEdgesDF = floodEdgesDF[floodEdgesDF['counter']>12]

floodEdgesDF = floodEdgesDF.sort_values('counter', ascending=False)

prevNodes = floodEdgesDF['prev'].tolist()
currNodes = floodEdgesDF['curr'].tolist()
connectedNodes = prevNodes + currNodes 
floodNodesDF = floodNodesDF[floodNodesDF['lemma'].isin(connectedNodes)]

nodeMin = np.min(floodNodesDF['counter'])
nodeMax = np.max(floodNodesDF['counter'])

G = nx.Graph()
nodeSizes = []
fontSizes = {}
for key, data in floodNodesDF.iterrows():
    nodeSizes.append(math.sqrt(2+data['counter']))
    fontSizes[key] = 9.5+12.5*math.sqrt((data['counter']-nodeMin)/(nodeMax-nodeMin))
    G.add_node(data['lemma'])

edgeSizes = []
edgeColors = []
edgeAlphas = []
for key, data in floodEdgesDF.iterrows():    
    edgeColor = '#555555'
    edgeSizes.append(0.3*math.log(data['counter']))
    edgeColors.append(edgeColor)
    weight8 = 0.01*math.log(100*data['counter'])/math.sqrt( floodNodesDF['counter'][data['prev']]*floodNodesDF['counter'][data['curr']] ) 
    G.add_edge(data['prev'], data['curr'], weight=0-0.0001*math.sqrt(data['counter']), weight8=weight8)
H = nx.Graph(G)
pos = nx.spring_layout(G, seed=7,  weight='weight8', scale=1.5, k=1.0, iterations=4000, threshold=10E-5) 

fig, ax = plt.subplots(figsize=(20, 15))
# Visualize graph components
nx.draw_networkx_edges(H, pos, alpha=0.1, width=edgeSizes, edge_color=edgeColors)
nx.draw_networkx_nodes(H, pos, node_size=nodeSizes, node_color='#888888', alpha=0.3)
label_options = {"ec": "k", "fc": "white", "alpha": 0.3}

i=0
for node, (x, y) in pos.items():
  i += 1
  if(i % 50 == 0):
      print(i)  

  textColor = '#000000'
  if(node.lower() in personsDict):
      textColor = '#bb0000'
  if(floodNodes[node]['orig'].lower() in personsDict):
      textColor = '#bb0000'       
  
  if(node.lower() in organizationsDict):
      textColor = '#00bb00'
  if(floodNodes[node]['orig'].lower() in organizationsDict):
      textColor = '#00bb00'

  if(node.lower() in locationsDict):
      textColor = '#0000bb'
  if(floodNodes[node]['orig'].lower() in locationsDict):
      textColor = '#0000bb'  
  
  if(fontSizes[node]>3):  
      plt.text(x, y, floodNodes[node]['orig'], fontsize=fontSizes[node], ha='center', va='center', color=textColor, alpha=0.9)
ax.margins(0.1, 0.05)
fig.tight_layout()
plt.axis("off")
if(not os.path.exists(DATA_PATH / 'img')):
    os.mkdir(DATA_PATH / 'img')
plt.savefig(DATA_PATH / 'img' / 'wordcloud.png', dpi=300)