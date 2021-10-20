import files
import pandas as pd

from pathlib import Path
import os.path

import en_core_web_sm    
import de_core_news_sm
import fr_core_news_sm

DATA_PATH = Path.cwd()

nlpEn = en_core_web_sm.load()
nlpDe = de_core_news_sm.load()
nlpFr = fr_core_news_sm.load()

floodsDF = files.getNewsDF(state='singular')
floodsDF = floodsDF[floodsDF['valid']==1]
floodsDF = floodsDF[floodsDF['language']=='de']
#print(floodsDF)
if(floodsDF.empty):
    print("Make sure, some valid flags are set to '1' in ./csv/news_harvest_????_??.csv")

indexLocations = {}
indexOrganizations = {}
indexPersons = {}
indexMisc = {}
indexMissing = {}

for index, column in floodsDF.iterrows():
    lang = str(column.language)
    if(lang in ['de', 'en', 'fr']):
        text = str(column.title) + ' ' + str(column.description) + ' ' + str(column.content)
        if((len(str(column.quote))>len(text))):
            text = str(column.quote)
        if('de' == lang):
            doc = nlpDe(text)
        elif('fr' == lang):
            doc = nlpFr(text)    
        else:
            doc = nlpEn(text)    
        for entity in doc.ents:
            if(entity.label_ in ['LOC','GPE']):
                if(entity.text in indexLocations):
                    indexLocations[entity.text]['count'] += 1
                else:      
                    indexLocations[entity.text] = {'phrase':entity.text, 'label':entity.label_, 'language':lang,'count':1}
            elif(entity.label_ in ['PER','PERSON']):
                if(entity.text in indexPersons):
                     indexPersons[entity.text]['count'] += 1
                else:    
                    indexPersons[entity.text] = {'phrase':entity.text, 'label':entity.label_, 'language':lang, 'count':1}   
            elif('ORG' == entity.label_):
                if(entity.text in indexOrganizations):
                     indexOrganizations[entity.text]['count'] += 1
                else:    
                    indexOrganizations[entity.text] = {'phrase':entity.text, 'label':entity.label_, 'language':lang, 'count':1} 
            elif('MISC' == entity.label_):
                if(entity.text in indexMisc):
                    indexMisc[entity.text]['count'] += 1
                else:         
                    indexMisc[entity.text] = {'phrase':entity.text, 'label':entity.label_, 'language':lang, 'count':1} 
            else:
                if(entity.text in indexMissing):
                    indexMissing[entity.text]['count'] += 1
                else:
                    indexMissing[entity.text] = {'phrase':entity.text, 'label':entity.label_, 'language':lang, 'count':1}  

if(not os.path.exists(DATA_PATH / 'csv')):
    os.mkdir(DATA_PATH / 'csv')
indexLocationsDF = pd.DataFrame.from_dict(indexLocations, orient='index', columns=['phrase', 'label', 'language', 'count'])
indexLocationsDF.to_csv(DATA_PATH / 'csv' / 'entities_locations.csv', index=True)    
indexPersonsDF = pd.DataFrame.from_dict(indexPersons, orient='index', columns=['phrase', 'label', 'language', 'count'])
indexPersonsDF.to_csv(DATA_PATH / 'csv' / 'entities_persons.csv', index=True)
indexOrganizationsDF = pd.DataFrame.from_dict(indexOrganizations, orient='index', columns=['phrase', 'label', 'language', 'count'])
indexOrganizationsDF.to_csv(DATA_PATH / 'csv' / 'entities_orgs.csv', index=True)
indexMiscDF = pd.DataFrame.from_dict(indexMisc, orient='index', columns=['phrase', 'label', 'language', 'count'])
indexMiscDF.to_csv(DATA_PATH / 'csv' / 'entities_misc.csv', index=True)
indexMissingDF = pd.DataFrame.from_dict(indexMissing, orient='index', columns=['phrase', 'label', 'language', 'count'])
indexMissingDF.to_csv(DATA_PATH / 'csv' / 'entities_missing.csv', index=True)

