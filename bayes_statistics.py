import files
import pandas as pd

from pathlib import Path
import os.path

import time
import datetime
from dateutil import parser

import nltk
from HanTa import HanoverTagger as ht
from textblob_de import TextBlobDE

#from sklearn.decomposition import Truncatedpca
from sklearn.decomposition import PCA

import re
import math
import random

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

domainWordsRawDF = pd.read_csv(DATA_PATH / "csv" / "words_bayes_topic_all.csv", delimiter=',',index_col='word')
domainWordsRawDF = domainWordsRawDF[domainWordsRawDF['Unnamed: 0'] != 'summaryOfAllWords']
domainWordsRawDF = domainWordsRawDF[~domainWordsRawDF.index.duplicated(keep='first')] 
domainWordsRelDF = domainWordsRawDF.drop(columns=["Unnamed: 0", "summary"])
print(domainWordsRelDF)
domainWordsRelDI = domainWordsRelDF.to_dict('index')
#print(domainWordsRelDI)


topicList = [
 'Flood Hazard', 
 'Weather', 'Damage', 'Victims', 'Politics', 'Health',
 'Rescue', 'Solidarity', 'Warnings', 'Troublemakers', 'Insurance', 'Pollution',
 'Causes', 'Infrastructure', 'Responsability', 'Risk', 'Wine'
]



language = 'ger'
nltk.download('punkt')
tagger = ht.HanoverTagger('morphmodel_'+language+'.pgz')


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
        #lemma vs orig / single vs double / vs tag-level / split "+" 

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
    if((maxPropabiliyty - nxtPropabiliyty) < 0.1):
        maxTopic = "other"
    return maxTopic    

emptyDomains = {"other":0}
emptyTopics = {}
for topic in topicList:
    emptyDomains[topic] = 0
    emptyTopics[topic] = 0

indexTopicsWords = {}
indexTopicsSentences = {}
indexTopicsDomains = {}
indexTopicsArticles = {}
indexTopicsDates = {}
indexTopicsWeeks = {}
indexTopicsWeeksSentences = {}

bayesDates = {}
bayesWeeks = {} 
#bayesDomains = {}

i=0
for index, column in floodsDF.iterrows():
    #print(column.published)
    #print(i)
    i += 1
    if(i % 50 == 0):
        print(i)
    timetravelDate = '1970-01-01'
    weekC = 'w0'
    pubDate = None
    try:
        pubDate = parser.parse(column.published)
    except:
        print('date parse error 1')
    if(not pubDate):
      try:
        pubDate = parser.isoparse(column.published)
      except:
        print('date parse error 2')   
    if(pubDate):
        timetravelDate = pubDate.strftime('%Y-%m-%d')
        weekC = pubDate.strftime("w%V")

    if(not timetravelDate in indexTopicsWords):
        indexTopicsWords[timetravelDate] = {}
        for topic in emptyDomains:
           indexTopicsWords[timetravelDate][topic] = 0
    if(not timetravelDate in indexTopicsSentences):
        indexTopicsSentences[timetravelDate] = {}
        for topic in emptyDomains:
           indexTopicsSentences[timetravelDate][topic] = 0
    if(not timetravelDate in indexTopicsArticles):
        indexTopicsArticles[timetravelDate] = {}
        for topic in emptyDomains:
           indexTopicsArticles[timetravelDate][topic] = 0
    if(not timetravelDate in indexTopicsDates):
        indexTopicsDates[timetravelDate] = {}
        bayesDates[timetravelDate] = {}
        for topic in emptyDomains:
           indexTopicsDates[timetravelDate][topic] = 0
           bayesDates[timetravelDate][topic] = 0
    if(not weekC in indexTopicsWeeks):
        indexTopicsWeeks[weekC] = {}
        bayesWeeks[weekC] = {}
        indexTopicsWeeksSentences[weekC] = {}
        for topic in emptyDomains:
           indexTopicsWeeks[weekC][topic] = 0
           bayesWeeks[weekC][topic] = 0
           indexTopicsWeeksSentences[weekC][topic] = 0       
    if(not column.domain in indexTopicsDomains):
        indexTopicsDomains[column.domain] = {}
        for topic in emptyDomains:
           indexTopicsDomains[column.domain][topic] = 0

    quote = str(column.title)+' ' +str(column.description)+' '+str(column.content)
    if((len(str(column.quote))>len(quote))):
        quote = str(column.quote)
    bayesArticles = emptyTopics.copy()    
    sentences = nltk.sent_tokenize(quote,language='german')   #todo: language->var
    for sentence in sentences: 
        bayesSentences = emptyTopics.copy()             
        for token in generateTokensFromSentence(sentence):
            bayesWords = emptyTopics.copy()
            if(token in domainWordsRelDI):
                bayesWords = domainWordsRelDI[token]
                for topic in topicList:
                    bayesSentences[topic] += bayesWords[topic]      
                    bayesArticles[topic] += bayesWords[topic]
                    bayesDates[timetravelDate][topic] += bayesWords[topic]
                    bayesWeeks[weekC][topic] += bayesWords[topic]
            maxWord = getMaximumTopic(bayesWords)
            indexTopicsWords[timetravelDate][maxWord] += 1

        maxSentence = getMaximumTopic(bayesSentences)
        indexTopicsSentences[timetravelDate][maxSentence] += 1
        indexTopicsDomains[column.domain][maxSentence] += 1
        indexTopicsWeeksSentences[weekC][maxSentence] += 1

    maxArticle = getMaximumTopic(bayesArticles)
    indexTopicsArticles[timetravelDate][maxArticle] += 1

for dateC in bayesDates:
    maxDate = getMaximumTopic(bayesDates[dateC])    
    indexTopicsDates[dateC][maxDate] += 1
    maxPropDate = -1E9
    for topic in bayesDates[dateC]:
        if(maxPropDate < bayesDates[dateC][topic]):
            maxPropDate = bayesDates[dateC][topic]
    for topic in bayesDates[dateC]:
        bayesDates[dateC][topic] = math.exp(bayesDates[dateC][topic]-maxPropDate) 

for weekC in bayesWeeks:
    maxWeek = getMaximumTopic(bayesWeeks[weekC])    
    indexTopicsWeeks[weekC][maxWeek] += 1
    maxPropWeek = -1E9
    for topic in bayesWeeks[weekC]:
        if(maxPropWeek < bayesWeeks[weekC][topic]):
            maxPropWeek = bayesWeeks[weekC][topic]
    for topic in bayesWeeks[weekC]:
        bayesWeeks[weekC][topic] = math.exp(bayesWeeks[weekC][topic]-maxPropWeek) 


indexTopicsWordsDF = pd.DataFrame.from_dict(indexTopicsWords, orient='index', columns=list(reversed(emptyDomains.keys())))
indexTopicsWordsDF.to_csv(DATA_PATH / 'csv'/ "dates_bayes_word_count.csv", index=True)

indexTopicsSentencesDF = pd.DataFrame.from_dict(indexTopicsSentences, orient='index', columns=list(reversed(emptyDomains.keys())))
indexTopicsSentencesDF.to_csv(DATA_PATH / 'csv'/ "dates_bayes_sentence_count.csv", index=True)

indexTopicsArticlesDF = pd.DataFrame.from_dict(indexTopicsArticles, orient='index', columns=list(reversed(emptyDomains.keys())))
indexTopicsArticlesDF.to_csv(DATA_PATH / 'csv'/ "dates_bayes_article_count.csv", index=True)

indexTopicsDomainsDF = pd.DataFrame.from_dict(indexTopicsDomains, orient='index', columns=list(reversed(emptyDomains.keys())))
indexTopicsDomainsDF.to_csv(DATA_PATH / 'csv'/ "domain_bayes_sentence_count.csv", index=True)

indexTopicsWeeksSentencesDF = pd.DataFrame.from_dict(indexTopicsWeeksSentences, orient='index', columns=list(reversed(emptyDomains.keys())))
indexTopicsWeeksSentencesDF.to_csv(DATA_PATH / 'csv'/ "weeks_bayes_sentence_count.csv", index=True)

indexTopicsDatesDF = pd.DataFrame.from_dict(indexTopicsDates, orient='index', columns=list(reversed(emptyDomains.keys())))
indexTopicsDatesDF.to_csv(DATA_PATH / 'csv'/ "dates_bayes_count.csv", index=True)
bayesDatesDF = pd.DataFrame.from_dict(bayesDates, orient='index', columns=list(reversed(emptyDomains.keys())))
bayesDatesDF.to_csv(DATA_PATH / 'csv'/ "dates_bayes_relative.csv", index=True)

indexTopicsWeeksDF = pd.DataFrame.from_dict(indexTopicsWeeks, orient='index', columns=list(reversed(emptyDomains.keys())))
indexTopicsWeeksDF.to_csv(DATA_PATH / 'csv'/ "weeks_bayes_count.csv", index=True)
bayesWeeksDF = pd.DataFrame.from_dict(bayesWeeks, orient='index', columns=list(reversed(emptyDomains.keys())))
bayesWeeksDF.to_csv(DATA_PATH / 'csv'/ "weeks_bayes_relative.csv", index=True)





#topicWordsRelDF = pd.read_csv(DATA_PATH / "csv" / "words_bayes_topic_all.csv", delimiter=',',index_col='word')
#topicWordsRelDF = topicWordsRelDF[topicWordsRelDF['Unnamed: 0'] != 'summaryOfAllWords']
#print(domainWordsRelDF)

numberComponents = 10

dfn = domainWordsRelDF
dfn['const0'] = 1.0

pca = PCA(n_components=numberComponents)
pca.fit(dfn)
apca = pca.fit_transform(dfn)
dfpca = pd.DataFrame(apca)

dfpca['word'] = domainWordsRawDF.index
dfpca['summary'] = domainWordsRawDF['summary'].values
dfpca.to_csv(DATA_PATH / "csv" /"words_bayes_topic_pca.csv", index=False)

