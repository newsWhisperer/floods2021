import files
import dates
import pandas as pd

import io
import requests
from pathlib import Path
import os.path

DATA_PATH = Path.cwd()

floodsDF = files.getNewsDF(state='singular')
floodsDF = floodsDF[floodsDF['valid']==1]

if(floodsDF.empty):
    print("Make sure, some valid flags are set to '1' in ./csv/news_harvest_????_??.csv")
if(not os.path.exists(DATA_PATH / 'csv')):
    os.mkdir(DATA_PATH / 'csv')

#count languages
indexLanguages = {}
for index, column in floodsDF.iterrows():
    lang = str(column.language)
    if(not lang in indexLanguages):
        indexLanguages[lang] = {'count':0}
    indexLanguages[lang]['count'] += 1    
indexLanguagesDF = pd.DataFrame.from_dict(indexLanguages, orient='index', columns=['count'])
indexLanguagesDF.to_csv(DATA_PATH / 'csv' / "languages_count.csv", index=True)     

#languages by date
indexDates = {}
for index, column in floodsDF.iterrows():
    dayDate = dates.getDay(column.published)
    if(not dayDate in indexDates):
        indexDates[dayDate] = {'count':0, 'de':0, 'en':0, 'fr':0}
    indexDates[dayDate]['count'] += 1
    if(column.language in indexDates[dayDate]):
        indexDates[dayDate][column.language] += 1      
indexDatesDF = pd.DataFrame.from_dict(indexDates, orient='index', columns=['count', 'de', 'en', 'fr'])
indexDatesDF.to_csv(DATA_PATH / 'csv' / "languages_date.csv", index=True) 


#count domains per language
for lang in indexLanguages:
    #print(lang)
    indexDomains = {}
    for index, column in floodsDF.iterrows():
        if(column.language == lang):
            if(not column.domain in indexDomains):
                indexDomains[column.domain] = {'count':0}
            indexDomains[column.domain]['count'] += 1    
    indexDomainsDF = pd.DataFrame.from_dict(indexDomains, orient='index', columns=['count'])
    indexDomainsDF.to_csv(DATA_PATH / 'csv' / ("domains_"+lang+"_count.csv"), index=True)  

#from here on german only...
floodsDF = floodsDF[floodsDF['language']=='de']


#count keywords used for search
indexKeywords = {}
for index, column in floodsDF.iterrows():
    word = str(column.keyword)
    if(not word in indexKeywords):
        indexKeywords[word] = {'count':0}
    indexKeywords[word]['count'] += 1    
indexKeywordsDF = pd.DataFrame.from_dict(indexKeywords, orient='index', columns=['count'])
indexKeywordsDF.to_csv(DATA_PATH / 'csv' / "keywords_count.csv", index=True) 


emptyDomains = {'summary':0, 'other':0, 'www.zeit.de':0, 'www.stern.de':0, 'www.focus.de':0, 'www.n-tv.de':0, 'www.spiegel.de':0, 'www.sueddeutsche.de':0, 
 'www.faz.net':0, 'www.welt.de':0, 'www.morgenpost.de':0, 'www.tagesschau.de':0, 'www.handelsblatt.com':0, 'www.bild.de':0, 'www.tagesspiegel.de':0, 
 'orf.at':0, 'www.dw.com':0, 'www.nzz.ch':0, 'www.heise.de':0, 'taz.de':0, 'www.wiwo.de':0, 'www.t-online.de':0, 
 #'www.diepresse.com':0, 
}

#count domains
germanDomains = {}
for index, column in floodsDF.iterrows():
    currDomain = 'other'
    if(column.domain in emptyDomains):
        currDomain = column.domain
    if(not currDomain in germanDomains):
        germanDomains[currDomain] = {'count':0}
    germanDomains[currDomain]['count'] += 1    
germanDomainsDF = pd.DataFrame.from_dict(germanDomains, orient='index', columns=['count'])
germanDomainsDF = germanDomainsDF.sort_values(by=['count'], ascending=False)
germanDomainsDF.to_csv(DATA_PATH / 'csv' / "domains_count.csv", index=True)  


#domains by date
indexDateDomains = {}
for index, column in floodsDF.iterrows():
  if(column.language == 'de'):   
    dayDate = dates.getDay(column.published)
    if(not dayDate in indexDateDomains):
        indexDateDomains[dayDate] = emptyDomains.copy()
    indexDateDomains[dayDate]['summary'] += 1
    if(column.domain in indexDateDomains[dayDate]):
        indexDateDomains[dayDate][column.domain] += 1 
    else:
        indexDateDomains[dayDate]['other'] += 1          
indexDateDomainsDF = pd.DataFrame.from_dict(indexDateDomains, orient='index', columns=emptyDomains.keys())
indexDateDomainsDF.to_csv(DATA_PATH / 'csv' / "domains_date.csv", index=True) 


#political parties by date  
partiesDict = {'Linke':'Linke','AfD':'AfD','FDP':'FDP','Grüne':'Grüne', 'SPD':'SPD','Union':'CDU/CSU','UNION':'CDU/CSU','CSU':'CDU/CSU','CDU':'CDU/CSU'}
partiesList = ['Linke','AfD','FDP','Grüne','SPD','CDU/CSU']
indexParties = {}
for index, column in floodsDF.iterrows():
    dayDate = dates.getDay(column.published)
    if(not dayDate in indexParties):
        indexParties[dayDate] = {}
        for person in partiesList:
           indexParties[dayDate][person] = 0
    quote = str(column.title)+' ' +str(column.description)+' '+str(column.content)
    if((len(str(column.quote))>len(quote))):
        quote = str(column.quote)
    for person in partiesDict:
        #count each mentioning
        ## indexParties[dayDate][partiesDict[person]] += quote.count(person)
        #count only one mentioning per article
        if(person in quote):
            indexParties[dayDate][partiesDict[person]] += 1       
indexPartiesDF = pd.DataFrame.from_dict(indexParties, orient='index', columns=partiesList)
indexPartiesDF.to_csv(DATA_PATH / 'csv' / "parties_date.csv", index=True)      


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
               'Linke','AfD','FDP','Grüne','SPD','Union','UNION','CSU','CDU'
               ],
 'Health': ['Seuchen', 'Ungeziefer', 'Covid', 'Corona','Pandemie','Arztprax','Impfung',
            'Seelsorge', 'Trauma','Emotionen','Schock', 'Limit'
 ],
 'Rescue': ['Feuerwehr', 'Polizei', 'Bundeswehr','THW','DRK','Einsatzkräfte','Arbeitsdienst','Pionier','Militär','Evakuierung'],
 'Solidarity': ['Solidarität','Hilfe','Spende','Helfer','Benefiz','Landwirt','Freiwillig','freiwillig','gesammelt','Sammlungen',
                  'sammlungen','unterstützt'],
 'Warnings': ['EFAS', 'DWD', 'Wetterdienst','BBK','Warnung','Unwetterwarnung','Warnsystem','alarm','Alarm','Sirene','Nina','Evakuierung','Katwarn','Broadcast'],
 'Troublemakers': ['Querdenker','Plünder','Diebstahl','Aluhüte','Rechtsextrem','Betrüger','Reichsbürger','Verschwörung','Gaffer','gaffen','skeptiker', 'leugner'],
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

#topics per date
topicList = topicDict.keys()
indexTopics = {}
for index, column in floodsDF.iterrows():
    dayDate = dates.getDay(column.published)
    if(not dayDate in indexTopics):
        indexTopics[dayDate] = {}
        for topic in topicDict:
           indexTopics[dayDate][topic] = 0
    quote = str(column.title)+' ' +str(column.description)+' '+str(column.content)
    if((len(str(column.quote))>len(quote))):
        quote = str(column.quote)
    for topic in topicDict:
        keywords = topicDict[topic]
        found = False
        counting = 0
        for keyword in keywords:
            if(keyword in quote):
                found = True
                counting += 1
                #counting += quote.count(keyword)
        if(found):
            indexTopics[dayDate][topic] += 1
            #indexTopics[dayDate][topic] += counting
indexTopicsDF = pd.DataFrame.from_dict(indexTopics, orient='index', columns=list(reversed(topicList)))
indexTopicsDF.to_csv(DATA_PATH / 'csv' / "topics_date.csv", index=True)


txt2021 = ""
for index, column in floodsDF.iterrows():
    quote = str(column.title)+' ' +str(column.description)+' '+str(column.content)
    if((len(str(column.quote))>len(quote))):
        quote = str(column.quote)    
    txt2021 += quote 

# Börngen, M. & G. Teltzlaff (Hrsg.) (2000):  Quellentexte zur Witterungsgeschichte Europas von der Zeitwende bis zum Jahr 1850. Teil 5. Berlin, Stuttgart, Borntraeger. #
# (Dr. G. Eckertz 1870 „Chronik u. Weisthum von Mayschoß an der Ahr“ in „Fontes adhuc inediti rer. Rhenan.“ II S. 77/8) #
# (J.Fr. Schannat „Eiflia illustrata etc.“, edid. G. Bärsch 1824/55. 3.Bd. 1.Abt. 1.Abschn. 		S. 382, 454, 478.) #
# Frick, Hans Quellen zur Geschichte von Bad Neuenahr, Bad Neuenahr 1933 #
txt1804 = """
1804 	 21. Juli       Ahrtal	Ahr: Überschwemmung infolge eines Wolkenbruchs 
Es war die erschreckliche Ahrflut. Den ganzen Tage fiel ein Platzregen, das Wasser strömte aus der Erde hervor.   Die Ahr führte weggerissene Häuser, Scheunen, Ställe, Balken, Bäume, Hausgeräth, leere und volle Weinfässer mit sich. Das Wasser stand auf Bongart bis an den zweiten Stock der Häuser bis an das halbe Dorf May, schoß hinauf. Zu Laach, wo sich der Mühlenberg verstopft hatte, ward die Kapelle oben am Ende des Dorfes ganz vernichtet, von 23 Häusern 17 fortgerissen und 8 zu Bongart. Weingärten, Wiesen und Felder waren verwüstet, so daß man die Grenzen nicht finden konnte. Zu Laach ertranken 14 Menschen, …, zu Rech Herr Joan Meyer, … mit seiner Haushälterin … und noch 3 Personen, die sich in seine Wohnung geflüchtet hatten. 
Des Abends von 8-9 Uhr war diese Verwüstung vollbracht. 

In diesem 1804 ten  Jahr war auch die erschreckliche Überschwemmung des Ahr fluß, welche am 21. July sich begab, daß Wasser war über alle massen Groß und Hoch, es Stand auf Bongart in den obersten Häusern biß an das zweite Stock werck und überwalte biß in den
amtmanns Pfuhl oder Wayer im Thier garten, es Stand biß in das halbe Dorf zu Mayschoß, der Auel Stand zweitheil im Wasser,…
…, ein Solches Wasser war bei Menschen gedenck nicht,…
…, es risse die Brücken sammt den Pfeilern umb, Stürzte die Häuser ein,…
Dann zu lach nahm es die Häußer meistens biß auf vier hinweg, wo 20 bis 24 Häußer Standen, zu Bongard nahm es 8 - 9 Häußer mit weg, etliche leut, welche zu Lach in den Häußern geblieben, an der Zahl vierzehn, sind mit ihren Häusern fortgetrieben und ertruncken, es war ein Elend über Elend, dan in einer Stunde des abend am 21.July von 8 – 9 war alles hinweg, …, getreide, hauß, Stall und Scheur Sammt weingärten, äcker, wießen, büsche,  wo das Wasser hin kam, waren in einer Stunde hinn. 

1804 21. Juli Ahr: Überschwemmung infolge eines Wolkenbruchs, z.B. in Schuld, Ahrweiler, Altenahr u. Laach 

Infolge eines Wolkenbruchs große Überschwennung der Ahr mit großem Schaden.
Schuld. Ahrweiler Große Wasserfluth. Bedeutender Schaden. 
Altenahr. Ahr: Überschwemmung.
Lach b/Mayschoß an d. Ahr Wasserflut. Der größte Teil des Oreste wird zerstört.

Durch Gewitterregen führte die Ahr bereits seit Tagen Hochwasser, als am 21. Juli 1804 ein erneutes Unwetter in der Hoch- und Ahreifel sich mit riesigen Niederschlägen entlud. Alle zur Ahr führenden Nebenflüsse, vor allem der Trier-, Adenauer- und Kesselinger Bach, schwollen innerhalb kürzester Zeit stark an. Eine alles wegreißende Flutwelle füllte die Täler und ließ das gesamte Ahrsystem über die Ufer treten. 
Im gesamten Einzugsbereich der Ahr verursachte das Unwetter und das anschließende Hochwasser riesige Sachschäden und forderte 63 Menschenleben. 129 Wohnhäuser, 162 Scheunen und Stallungen, 18 Mühlen, 8 Schmieden und nahezu alle Brücken, insgesamt 30, wurden von den Wassermassen weggerissen. Weitere 469 Wohnhäuser, 234 Scheunen und Ställe, 2 Mühlen und 1 Schmiede wurden beschädigt. 78 Pferde und Zugrinder kamen in den Fluten um, Obstbäume wurden entwurzelt, Weinberge abgespült, die gesamte Ernte vernichtet und Wiesen und Felder in der Talaue hoch mit Sand und Kies überschüttet. 
Zur Behebung der Schäden wurde durch den Präfekten des Departements ein Arbeitsdienst eingerichtet, bei dem über 800 Männer, teilweise von der Mosel kommend, eingesetzt waren. An Steuergeldern wurden 120.000 Francs und Bauholz aus den Wäldern für 40.000 Francs zur Verfügung gestellt. Kaiser Napoleon gab aus seiner Privatschatulle 30.000 Francs, die Kaiserin weitere 4.800 Francs zur Linderung der Not, 45.000 Francs erbrachte eine Spendenaktion.

Den 21. (Juli) bin ich mit He(rrn) Dechant Radermacher über den Berg nach Remagen gegangen und oben auf dem Berg fang es dergestalten an zu regnen, daß wir beide bis an die Haut naß in Remagen angekommen. In selber Nacht ist auch die Ahr so angewachsen, daß das abgeschnittene Korn von den Fudern abgetrieben, alle möglich Hausgeräthe, Bauhölzer und todte Menschen auf dem Felde gefunden worden, die mit der Aar dahin getrieben«.
Antweiler: 1804.21, Juni Nachmittags 3 Uhr stürzte das Wasser bei einem erschrecklichen Gewitter von Norden in Strömen aus den Wolken, wodurch die Ahr und alle kleineren Bäche dergestalt gewachsen, dass hier zu Antweiler 6 Häuser, 12 Scheunen und Stallungen, 2 Oehlmühlen, 1 Schmiede fortgerissen, 8 Häuser samt soviel Scheunen und Stallungen bis an die Dächer in Sand vergraben wurden. In Müsch wurden 10 Häuser mit ihren Gebäuden gänzlich beschädigt und 4 Menschen sind daselbst ertrunken. Auf dem ganzen Ahrstrom aber sind 65 Menschen, 147 Häuser, 190 Scheunen, 20 Mühlen, 8 Schmieden, 50 Brücken, nebst vielem Vieh in den Fluten zugrunde gegangen; 428 Häuser, 269 Scheunen, 8 Mühlen, wurden gänzlich beschädigt. Dieser wilde Strom hin-terliess in einer Höhe von 8, 10, ja sogar bis zu 20 Schuh hier Steinhaufen, dort einen Kot, dessen Geruch die Luft vergiftet. In diesem wütenden Strom, welcher die Kirche und alle Häuser zwischen der Ahr und Hägerbach, 4 ausgenommen, hoch unter Wasser setzte, welche über das hl. Häuschen über der Ahr ging, blieb das Bildnis des hl. Johannes Nepomuce-nus, so von Holz und nirgends festgemacht, auch vorn mit keinem Gegitter versehen war, wunderlich mit ihrem Häuschen und die Brücke stehen.
"""

# Ortschronik von Bodendorf angelegt von Clemens v. Lassaulx 1879; geführt bis 1955 (von verschiedenen Chronisten)#
# * Schulchronik der Schule und Gemeinde Bodendorf, begonnen von Lehrer Johann Mies, 1895, geführt vom jeweiligen Schulleiter bis 1962 #
# * Lagerbuch der Pfarrei Bodendorf, begonnen von Pfarrer Bartholomäus Fey 1802, mit Unterbrechungen geführt bis ca. 1955. #
txt1910 = """
Das Frühjahr ließ sich ganz gut an, aber der Sommer war mehr oder weniger verregnet. Ja in der Nacht vom 12. auf den 13. Juni ging ein gewaltiger Wolkenbruch über unser Thal nieder, der ganz grausiges Hochwasser der Ahr verursachte und eine gewaltige Überschwemmung das Thal heimsuchte. Die durch diese Überschwemmung entstandenen Schäden wurden durch im ganzen Reich gesammelte Gelder gedeckt. Am Ahrbett machte das Wasser großen Schaden, so daß wohl ein vollständiger Neubau der Uferbefestigungen notwendig wird«18). »Am 13. Juni d. J. war die große Überschwemmung im Ahrtal. An der Oberahr sind ungefähr 70 Leute ertrunken; es waren dies meist Ausländer, die an dem Bahnbau arbeiteten. In Bodendorf hat die Überschwemmung großen Schaden gemacht. Das überall in den Wiesen üppig stehende Gras war alle überschwemmt und beschlammt. Es sind große Geldsammlungen veranstaltet worden. Sr. Majestät gab 10.000 Mark. Auch hier in Bodendorf sind die Geschädigten unterstützt worden, viele wurden fast schadlos gehalten

Am 13. Juni dieses Jahres war die große Wasserkatastrophe an der Ahr, verursacht durch Wolkenbrüche, welche an der Oberahr zwischen der Hohen Acht und Hillesheim zur Nachtzeit niedergingen
"""

#get news_1804_1910.csv from freidok:  doi.org/10.6094/UNIFR/222040
url = "https://freidok.uni-freiburg.de/fedora/objects/freidok:222040/datastreams/FILE1/content"
content=requests.get(url).content
stream = io.StringIO(content.decode('utf-8'))
historyDf = pd.read_csv(stream, delimiter=',',index_col='index')

for index, column in historyDf.iterrows():
    print(column['published'][0:4])
    if('1804' == column['published'][0:4]):
        print([1804, column['title']])
        txt1804 += ' ' + column['quote'] 
    if('1910' == column['published'][0:4]):
        print([1910, column['title']])    
        txt1910 += ' ' + column['quote']    

yearsTxt = {'1804':txt1804, '1910':txt1910, '2021':txt2021}

#count topics for different years
for year in yearsTxt:
    quote = yearsTxt[year]
    indexTopicsAll = {}
    for topic in topicDict:
        keywords = topicDict[topic]
        found = False
        counting = 0
        for keyword in keywords:
            counting += quote.count(keyword)
        indexTopicsAll[topic] = {'count': counting}         
    indexTopicsAllDF = pd.DataFrame.from_dict(indexTopicsAll, orient='index', columns=['count'])
    indexTopicsAllDF.to_csv(DATA_PATH / 'csv' / ("topics_count_"+year+".csv"), index_label='index') 

#count topics for different domains
for domain in emptyDomains:
    if(not domain in ['summary','other']):
        domainSimple = domain.replace('www.','').replace('.','_')
        floodsDomain = floodsDF[floodsDF['domain']==domain]
        text = ""
        for index, column in floodsDomain.iterrows():
            quote = str(column.title)+' ' +str(column.description)+' '+str(column.content)
            if((len(str(column.quote))>len(quote))):
                quote = str(column.quote)    
            text += quote       
        indexTopicsAll = {}
        for topic in topicDict:
            keywords = topicDict[topic]
            found = False
            counting = 0
            for keyword in keywords:
                counting += text.count(keyword)
            indexTopicsAll[topic] = {'count': counting}         
        indexTopicsAllDF = pd.DataFrame.from_dict(indexTopicsAll, orient='index', columns=['count'])
        indexTopicsAllDF.to_csv(DATA_PATH / 'csv' / ("topics_count_"+domainSimple+".csv"), index_label='index')  




