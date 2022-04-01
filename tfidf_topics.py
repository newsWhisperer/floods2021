import files
import pandas as pd
import numpy as np
from numpy.random import default_rng

from pathlib import Path
import os.path

import nltk
from HanTa import HanoverTagger as ht
from textblob_de import TextBlobDE

import math
import random
from time import time
from datetime import datetime
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation
from sklearn.datasets import fetch_20newsgroups
from nltk.corpus import stopwords

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


n_features = 16000
n_components = 20
n_components = 39
n_top_words = 25
grouping = 'articles'   # '2sentences' , "days' , 'domains'
weighted = False
source = 'recent'   # only for 2sentence:  'all' , 'history'
lowercase = True

setting = source + '_' + grouping + "_" + ("weighted" if weighted else "unweighted") + "_" + ("lower" if lowercase else "upper") + str(n_components) + 'x' + str(n_top_words)


DATA_PATH = Path.cwd()
nltk.download("stopwords")

floodsDF = files.getNewsDF(state='singular')
floodsDF = floodsDF[floodsDF['valid']==1]
floodsDF = floodsDF[floodsDF.index.notnull()]

if(floodsDF.empty):
    print("Make sure, some valid flags are set to '1' in ./csv/news_harvest_????_??.csv")

floodsDF = floodsDF[floodsDF['language']=='de']
floodsDF['description'] = floodsDF['description'].fillna('')
floodsDF['quote'] = floodsDF['quote'].fillna('')
floodsDF['text'] = floodsDF['title'] + floodsDF['description'] + floodsDF['quote'] + ' '
floodsDF['day'] = pd.to_datetime(floodsDF['published']).dt.strftime("%Y-%m-%d")



if(not os.path.exists(DATA_PATH / 'csv')):
    os.mkdir(DATA_PATH / 'csv')
if(not os.path.exists(DATA_PATH / 'img')):
    os.mkdir(DATA_PATH / 'img')

bayesDF2 = pd.read_csv(DATA_PATH / "csv" / "words_topic_all.csv", delimiter=',',index_col='word')
if(lowercase):
   bayesDF2.index = bayesDF2.index.str.lower()
bayesDF2 = bayesDF2[~bayesDF2.index.duplicated(keep='first')]
bayesDF2 = bayesDF2[bayesDF2.index.notnull()]
bayesDict =bayesDF2.to_dict('index')

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

# aggregate text by date
groupedDF = floodsDF.groupby('day').text.apply(lambda x: x.sum()).reset_index()
if(grouping in ['domains']):
# aggregate text by domain
  groupedDF = floodsDF.groupby('domain').text.apply(lambda x: x.sum()).reset_index()
print(groupedDF)

floodsHistoryDF = files.getDFfromFiledok("https://freidok.uni-freiburg.de/fedora/objects/freidok:222040/datastreams/FILE1/content", "news_1804_1910.csv", delimiter=',')
floodsHistoryDF['text'] = floodsHistoryDF['title'] + floodsHistoryDF['quote'] + ' '
floodsHistoryDF['day'] = pd.to_datetime(floodsHistoryDF['published']).dt.strftime("%Y-%m-%d")

# collect sentences
allSentences = []
recentSentences = []
lastSentence = ''
for index, column in floodsDF.iterrows():
        lastSentence = ''
        quote = str(column.title)+'. ' +str(column.description)+'. '+str(column.content)
        if((len(str(column.quote))>len(quote))):
            quote = str(column.quote)
        sentences = nltk.sent_tokenize(quote,language='german') 
        for sentence in sentences:
            allSentences.append(lastSentence+' '+sentence)
            recentSentences.append(lastSentence+' '+sentence)
            lastSentence = sentence

histSentences = []
lastSentence = ''
for index, column in floodsHistoryDF.iterrows():
        lastSentence = ''
        quote = str(column.title)+'. ' +str(column.description)+'. '+str(column.quote)
        sentences = nltk.sent_tokenize(quote,language='german') 
        for sentence in sentences:
            allSentences.append(lastSentence+' '+sentence)
            histSentences.append(lastSentence+' '+sentence)
            lastSentence = sentence            


def extractColors(words):
    summary = {}
    wordColors = []
    maxTopicValue = -1E20 
    maxTopicColor = '#000000'
    maxTopicName = 'None'
    for topic in colorsTopics:
        summary[topic] = 0.0
    for word in words:
        wordColor = '#000000'
        wordValue = -1E20
        wordWeight = words[word]
        if(word in bayesDict):
            bayes = bayesDict[word]
            for topic in colorsTopics:  
                if(bayes[topic] > wordValue):
                    wordValue = bayes[topic]
                    wordColor = colorsTopics[topic]
                if (weighted):
                  summary[topic] += bayes[topic]*wordWeight
                else:
                  summary[topic] += bayes[topic]
        wordColors.append(wordColor)
    for topic in colorsTopics:  
        if(summary[topic] > maxTopicValue):
            maxTopicValue = summary[topic]
            maxTopicColor = colorsTopics[topic]
            maxTopicName = topic
    return {'topic':maxTopicName, 'color':maxTopicColor, 'colors': wordColors}


legendHandles = []
for topic in colorsTopics:
    patch = mpatches.Patch(color=colorsTopics[topic], label=topic)
    legendHandles.append(patch)
legendHandles.reverse()   


def plot_top_words(model, feature_names, n_top_words, title, filename='topics'):
    
    if (n_components > 20):
        fig, axes = plt.subplots(4, 10, figsize=(17, 12), sharex=True)
    else:
        fig, axes = plt.subplots(4, 5, figsize=(17, 12), sharex=True)    
    axes.flat[39].remove()
    axes = axes.flatten()
    plt.rcParams.update({'font.size': 6 })

    for topic_idx, topic in enumerate(model.components_):
        top_features_ind = topic.argsort()[: -n_top_words - 1 : -1]
        top_features = [feature_names[i] for i in top_features_ind]
        weights = topic[top_features_ind]
        featDict = dict(zip(top_features,weights))
        bayesColors = extractColors(featDict)
        bayesTopic = bayesColors['topic']
        ax = axes[topic_idx]
        ax.barh(top_features, weights, height=0.7, color=bayesColors['colors'])
        ax.set_xscale('log')
        ax.set_title(f"{bayesTopic}", fontdict={"fontsize": 9, "horizontalalignment":"right", "color":bayesColors['color']})
        ax.invert_yaxis()
        ax.tick_params(axis="both", which="major", labelsize=6)
        for i in "top right left".split():
            ax.spines[i].set_visible(False)
        fig.suptitle(title, fontsize=10)

    leg = plt.legend(handles=legendHandles,
        title="Topics",
        loc="center right",
        fontsize=6,
        markerscale=0.7,
        bbox_to_anchor=(1, 0, 2.25, 1.1)
    )
    plt.subplots_adjust(top=0.92, bottom=0.05, wspace=1.20, hspace=0.25)
    plt.savefig(DATA_PATH / "img" / (filename + ".png"), dpi=300)
    plt.close('all')


#articles
data_samples = floodsDF.text
#domains, days
if(grouping in ['domains','days']):
  data_samples = groupedDF.text
#bi-sentences
if(grouping == '2sentences'):
    data_samples = allSentences
    if(source == 'recent'):
      data_samples = recentSentences
    if(source == 'history'):  
      data_samples = histSentences

stop_words = stopwords.words('german')

# Use tf-idf features for NMF.
print("Extracting tf-idf features for NMF...")
t0 = time()
tfidf_vectorizer = TfidfVectorizer(
    max_df=0.95, min_df=2, max_features=n_features, stop_words=stop_words, ngram_range=(1, 1), lowercase=lowercase
)
tfidf = tfidf_vectorizer.fit_transform(data_samples)
print("done in %0.3fs." % (time() - t0))

# Use tf (raw term count) features for LDA.
print("Extracting tf features for LDA...")
t0 = time()
tf_vectorizer = CountVectorizer(
    max_df=0.95, min_df=2, max_features=n_features, stop_words=stop_words, lowercase=lowercase
)
tf = tf_vectorizer.fit_transform(data_samples)
print("done in %0.3fs." % (time() - t0))
print()

# Fit the NMF model
print(
    "Fitting the NMF model (Frobenius norm) with tf-idf features, "
    "n_features=%d..." % (n_features)
)
t0 = time()
nmf = NMF(n_components=n_components, random_state=1, alpha=0.1, l1_ratio=0.5).fit(tfidf)
print("done in %0.3fs." % (time() - t0))

tfidf_feature_names = tfidf_vectorizer.get_feature_names_out()
#print(tfidf_feature_names.shape)
filename = "topics_nmf1_" + setting
plot_top_words(
    nmf, tfidf_feature_names, n_top_words, "Topics in NMF model (Frobenius norm)", filename  
)


# Fit the NMF model
print(
    "\n" * 2,
    "Fitting the NMF model (generalized Kullback-Leibler "
    "divergence) with tf-idf features, n_features=%d..."
    % (n_features),
)
t0 = time()
model = NMF(
    n_components=n_components,
    random_state=1,
    beta_loss="kullback-leibler",
    solver="mu",
    max_iter=1000,
    alpha=0.1,
    l1_ratio=0.5,
)
W = model.fit_transform(tfidf)

print("done in %0.3fs." % (time() - t0))

tfidf_feature_names = tfidf_vectorizer.get_feature_names_out()
filename = "topics_nmf2_" + setting
plot_top_words(
    model,
    tfidf_feature_names,
    n_top_words,
    "Topics in NMF model (generalized Kullback-Leibler divergence)",
    filename
)


# Fit the NMF model with init matrices
print(
    "\n" * 2,
    "Fitting the NMF model (generalized Kullback-Leibler "
    "divergence) with tf-idf features, n_features=%d..."
    % (n_features),
)
t0 = time()
model = NMF(
    n_components=n_components,
    random_state=1,
    beta_loss="kullback-leibler",
    solver="mu",
    max_iter=400,
    #alpha=0.1,
    ##alpha_W=0.1,
    ##alpha_H=0.1,
    l1_ratio=0.5,
    init='custom'
)

###  tfidf vs n_features
tfidf_feature_names = tfidf_vectorizer.get_feature_names_out()
Wc = 0.1*default_rng().random((len(data_samples), n_components))
Hc = 0.1*default_rng().random((n_components, len(tfidf_feature_names)))

def initH(Hc, factor=1.5, offset=50.5):
    global bayesDF2
    t = -1
    counter = 0
    ratio = math.ceil(n_components/len(colorsTopics))
    for topic in colorsTopics.keys():
        t =+ 1
        if(t<n_components):
            bayesDF2 = bayesDF2.sort_values(by=[topic], ascending=False)
            words = 0
            for index, column in bayesDF2.iterrows(): 
                if(words < n_top_words):  
                    if(index in tfidf_feature_names):
                        w = np.where(tfidf_feature_names == index)
                        w = w[0][0]
                        counter += 1 
                        words += 1
                        for r in range(0,ratio):
                            if(t+r<n_components):
                                Hc[t+r,w] *= factor   
                                Hc[t+r,w] += offset*(r+1)
                else:
                    break 
    return Hc                        
        
Hc = initH(Hc, 1.0, 50.5)
W = model.fit_transform(tfidf,  W=Wc, H=Hc)
Hc = model.components_
Hc = initH(Hc, 2.0, 20.5)
W = model.fit_transform(tfidf,  W=W, H=Hc)
Hc = model.components_
Hc = initH(Hc, 1.5, 0.5)
W = model.fit_transform(tfidf,  W=W, H=Hc)
H = model.components_

print("done in %0.3fs." % (time() - t0))

filename = "topics_nmf3_" + setting
plot_top_words(
    model,
    tfidf_feature_names,
    n_top_words,
    "Topics in NMF model with custom init (generalized Kullback-Leibler divergence)",
    filename
)

print(
    "\n" * 2,
    "Fitting LDA models with tf features, n_features=%d..."
    % (n_features),
)
lda = LatentDirichletAllocation(
    n_components=n_components,
    max_iter=5,
    learning_method="online",
    learning_offset=50.0,
    random_state=0,
)
t0 = time()
lda.fit(tf)
print("done in %0.3fs." % (time() - t0))

tf_feature_names = tf_vectorizer.get_feature_names_out()
filename = "topics_lda_" + setting
plot_top_words(lda, tf_feature_names, n_top_words, "Topics in LDA model", filename)    





# Show Bayes model
print(
    "\n" * 2,
    "Plotting the Bayes Model"
)
t0 = time()

fig, axes = plt.subplots(4, 5, figsize=(17, 12), sharex=True)
axes = axes.flatten()
plt.rcParams.update({'font.size': 6 })
topic_idx = -1
for topic in reversed(colorsTopics.keys()):
    topic_idx += 1
    topicWords = {}  
    topicColor = colorsTopics[topic]
    bayesDF2 = bayesDF2.sort_values(by=[topic], ascending=False)
    for index, column in bayesDF2.iterrows():    
        if(len(topicWords) < n_top_words):
            if(index and (type(index) == str) and (column[topic]<100)):    
              #don't use 2grams  
              if(not ' ' in index):      
                topicWords[index] = column[topic]
        else:
            break        


    top_features = list(topicWords.keys())
    weights = np.array(list(topicWords.values()))
    bayesColors = extractColors(topicWords)
    bayesTopic = bayesColors['topic']

    ax = axes[topic_idx]
    ax.barh(top_features, weights, height=0.7, color=bayesColors['colors'])
    #ax.set_xscale('log')
    ax.set_title((topic + " ("+bayesTopic+")"), fontdict={"fontsize": 9, "horizontalalignment":"right", "color":bayesColors['color']})
    ax.invert_yaxis()
    ax.tick_params(axis="both", which="major", labelsize=6)
    for i in "top right left".split():
        ax.spines[i].set_visible(False)
    fig.suptitle("Bayes Topics", fontsize=9)

plt.subplots_adjust(top=0.90, bottom=0.05, wspace=0.90, hspace=0.3)
plt.savefig(DATA_PATH / "img" / ("topics_bayes" + ".png"), dpi=300)
plt.close('all')
print("done in %0.3fs." % (time() - t0))

