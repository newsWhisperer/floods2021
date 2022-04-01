import files
import pandas as pd

from pathlib import Path
import os.path

import nltk
from HanTa import HanoverTagger as ht
from textblob_de import TextBlobDE

import re
import math
import random
#from sklearn.decomposition import Truncatedpca
from sklearn.decomposition import PCA

import matplotlib.pyplot as plt

DATA_PATH = Path.cwd()

floodsDF = files.getNewsDF(state='singular')
floodsDF = floodsDF[floodsDF['valid']==1]

if(floodsDF.empty):
    print("Make sure, some valid flags are set to '1' in ./csv/news_harvest_????_??.csv")
if(not os.path.exists(DATA_PATH / 'csv')):
    os.mkdir(DATA_PATH / 'csv')
if(not os.path.exists(DATA_PATH / 'img')):
    os.mkdir(DATA_PATH / 'img')

language = 'ger'
nltk.download('punkt')
tagger = ht.HanoverTagger('morphmodel_'+language+'.pgz')

def generateTokensWithPosition(quote):
    sentences = nltk.sent_tokenize(quote,language='german')   
    for sentence in sentences:
        positionSentence = quote.find(sentence)
        lastWord = None
        tokens = nltk.tokenize.word_tokenize(sentence,language='german') 
        lemmata = tagger.tag_sent(tokens,taglevel = 2)
        for (orig,lemma,gramma) in lemmata:
            positionWord = sentence.find(orig)
            yield [orig, positionSentence+positionWord]
            if(lastWord):
                yield [(lastWord+' '+lemma), positionSentence+positionWord]
            lastWord = lemma 

topicDict = { \
 'Flood Hazard':['Überflutung','Flut','Hochwasser','Katastrophe','Überschwemmung','Pegel','schwoll','Ufer treten','angewachsen','katastrophe',
                 'Wassermassen'], 
 'Weather': ['Starkregen','Unwetter','Wetter','Dauerregen','Niederschläge','Niederschlag','Liter','Quadratmeter','Gewitter','Regen','Bernd',
            'Jetstream','Platzregen','Gewitterregen','regnen','verregnet','Wolkenbruch','Wolkenbrüche'],
 'Damage':['Million','Milliarde','Schäden','Schaden','Kosten','Ausmaß','Zerstörung','Trümmer','Auto', 'Fahrzeug','Krieg', 'Verwüstung',
            'zerstört','Erdrutsch','Verwüstung','weggerissen','Häuser','Scheune','Ställe','Wiese','Felder','verstopft','vernichtet', 'fortgerissen',
            'wegreißen','Sachschäden','Ernte','Pferde','Rinder','getrieben','Stallungen','vergraben','Vieh'], 
 'Victims': ['Tote','Vermisste','Verletzte','Menschen','Tode','Dutzende','Hunderte','Tausende','Betroffene','Leben','Opfer','opfer','ertranken',
           'ertrunken','Ertrunken', 'Menschenleben','todte','Leiche'],
 'Politics': ['Wahlkampf','Politiker','Merkel','Laschet','Scholz','Baerbock','Söder', 'Seehofer', 'Dreyer', 'Pföhler', 'Steinmeier',
               'Schulze','Habeck','Lindner','Napoleon','Kaiserin','Majestät', 'Staat',
               'Linke','AfD','FDP','Grüne','SPD','Union','UNION','CSU','CDU'],
 'Health': ['Seuchen', 'Ungeziefer', 'Covid', 'Corona','Pandemie','Arztprax','Impfung',
            'Seelsorge', 'Trauma','Emotionen','Schock', 'Limit'],
 'Rescue': ['Feuerwehr', 'Polizei', 'Bundeswehr','THW','DRK','Einsatzkräfte','Arbeitsdienst','Pionier','Militär','Evakuierung'],
 'Solidarity': ['Solidarität','Hilfe','Spende','Helfer','Benefiz','Landwirt','Freiwillig','freiwillig','gesammelt','Sammlungen',
                  'sammlungen','unterstützt'],
 'Warnings': ['EFAS', 'DWD', 'Wetterdienst','BBK','Warnung','Unwetterwarnung','Warnsystem','alarm','Alarm','Sirene','Nina','Evakuierung','Katwarn','Broadcast'],
 'Troublemakers': ['Querdenker','Plünder','Diebstahl','Aluhüte','Rechtsextrem','Betrüger','Reichsbürger','Verschwörung','Gaffer','gaffen'],
 'Insurance': ['Allianz','Munich Re','Pflichtversicherung','Versicherung','Elementarversicherung','Versicher','Elementarschäden','versichert'],
 'Pollution': ['Müll','Spermüll','Schutt','Sondermüll','Schlamm','giftig','Heizöl','Geruch','Gestank','vergiftet','schlammt','Karbid'],
 'Causes': ['Klima','Klimawandel','rwärmung','Ursachen','Versiegelung','Schwammstadt','Luisa Neubauer','Regenrückhaltebecken',
              'Stefan Rahmstorf','Überflutungsfläche','Attributionsstudie','Attributionsforschung','Mojib Latif', 'IPCC'],
 'Infrastructure': ['Deutsche Bahn', 'Gas', 'Trinkwasser','Brücke','Strom','Straße','Bahn','Mobilfunk','Internet','Kanalisation','Klärwerk',
                   'Mühle','mühle','Schmiede','Schifffahrt','Telephon', 'Telegraph','brücke','Ahrbahn','Eisenbahn', 'Lokomotive', 'Lokomobile',
                   'Schienen','schwellen'],
 'Responsability': ['Staatsanwaltschaft', 'Kritik','xxSchuldxx','Rechtsanwalt','Systemversagen','Ermittlung','Verantwortung','versagen','Versagen'],
 'Risk': ['HQ100','1804','Risiko','Risiken'],
 'Wine': ['Winzer', 'Wein'],
}

emptyTopics = {'summary':0, 'other':0}
for topic in topicDict:
    emptyTopics[topic] = 0

i=0
topicWordsAbs = {'summaryOfAllWords': emptyTopics.copy()}
for index, column in floodsDF.iterrows():
    i += 1
    if(i % 50 == 0):
        print(i)
    domain = 'other'
    if(column.domain in emptyTopics):
        domain = column.domain
    quote = str(column.title)+' ' +str(column.description)+' '+str(column.content)
    if((len(str(column.quote))>len(quote))):
        quote = str(column.quote)  
    else:
        if(not domain == 'other'):
            print(['quote missing: ', column.url])    
    for tokenAndPosition in generateTokensWithPosition(quote):
        token = tokenAndPosition[0]
        tokenPosition = tokenAndPosition[1]
        if(not token in topicWordsAbs):
            topicWordsAbs[token] = emptyTopics.copy()  
        for topic in topicDict: 
            found = 0.0
            for keyword in topicDict[topic]:
                if(keyword in quote):
                    for keyPosition in [m.start() for m in re.finditer(keyword, quote)]:
                        distance = abs(tokenPosition - keyPosition)
                        factor = math.sqrt(1/(1+distance*0.25))
                        if(factor>found):
                            found = factor  
            topicWordsAbs[token][topic] += found
            topicWordsAbs[token]['summary'] += found
            topicWordsAbs['summaryOfAllWords'][topic] += found
            topicWordsAbs['summaryOfAllWords']['summary'] += found

overallProbability = emptyTopics.copy()
for topic in overallProbability:
    if(not topic == 'summary'):
        overallProbability[topic] = float(topicWordsAbs['summaryOfAllWords'][topic])/float(topicWordsAbs['summaryOfAllWords']['summary']) 

## now increase all counting by sqrt(n), but minimum of overall probability
for word in topicWordsAbs:
    if(word != 'summaryOfAllWords'):
        data = topicWordsAbs[word]
        for topic in overallProbability:   
            if(not topic == 'summary'):
                frac = overallProbability[topic]
                delta = math.sqrt(frac+topicWordsAbs[word][topic])
                topicWordsAbs[word][topic] += delta
                topicWordsAbs['summaryOfAllWords'][topic] += delta
                topicWordsAbs[word]['summary'] += delta
                topicWordsAbs['summaryOfAllWords']['summary'] += delta  

emptyCol = emptyTopics.copy()
emptyCol['word'] = 'oneWord'
topicWordsRel = {}  
for word in topicWordsAbs:
    if(word == 'summaryOfAllWords'):  
        relData = topicWordsAbs[word].copy()
    else:    
        data = topicWordsAbs[word]
        relData = emptyCol.copy()
        relData['word'] = word
        relData['summary'] = topicWordsAbs[word]['summary']
        for topic in data:
            if(not topic in ['word','summary']):
                if(not topicWordsAbs['summaryOfAllWords'][topic] == 0):  
                    relValue = topicWordsAbs[word][topic]*topicWordsAbs['summaryOfAllWords']['summary']/(topicWordsAbs['summaryOfAllWords'][topic]*topicWordsAbs[word]['summary'])   #Bayes
                    relData[topic] = math.log(relValue)
    topicWordsRel[word] = relData 
topicWordsRelDF = pd.DataFrame.from_dict(topicWordsRel, orient='index', columns=emptyCol.keys()) 
topicWordsRelDF.to_csv(DATA_PATH / 'csv' / "words_topic_all.csv", index=True) 


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


topicWordsRelDF = pd.read_csv(DATA_PATH / "csv" / "words_topic_all.csv", delimiter=',',index_col='word')
topicWordsRelDF = topicWordsRelDF[topicWordsRelDF['Unnamed: 0'] != 'summaryOfAllWords']
print(topicWordsRelDF)

numberComponents = 10
dfn = topicWordsRelDF
dfn = dfn.drop(columns=['summary', 'Unnamed: 0'])
dfn['const0'] = 1.0

pca = PCA(n_components=numberComponents)
pca.fit(dfn)
apca = pca.fit_transform(dfn)
dfpca = pd.DataFrame(apca)

dfpca['word'] = topicWordsRelDF.index
dfpca['summary'] = topicWordsRelDF['summary'].values
dfpca.to_csv(DATA_PATH / "csv" /"words_topic_pca.csv", index=False)

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
for index, column in dfpca.iterrows():
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

plt.savefig(DATA_PATH / 'img' / 'words_topic_pca.png', dpi=300)  


