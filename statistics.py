import files
import dates
import pandas as pd

import io
import requests
from pathlib import Path
import os.path

DATA_PATH = Path.cwd()

if(not os.path.exists(DATA_PATH / 'csv')):
    os.mkdir(DATA_PATH / 'csv')

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
partiesDict = {'Linke':'Linke','AfD':'AfD','FDP':'FDP','Gr??ne':'Gr??ne', 'SPD':'SPD','Union':'CDU/CSU','UNION':'CDU/CSU','CSU':'CDU/CSU','CDU':'CDU/CSU'}
partiesList = ['Linke','AfD','FDP','Gr??ne','SPD','CDU/CSU']
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
 'Flood Hazard':['??berflutung','Flut','Hochwasser','Katastrophe','??berschwemmung','Pegel','schwoll','Ufer treten','angewachsen','katastrophe',
                 'Wassermassen'], 
 'Weather': ['Starkregen','Unwetter','Wetter','Dauerregen','Niederschl??ge','Niederschlag','Liter','Quadratmeter','Gewitter','Regen','Bernd',
            'Jetstream','Platzregen','Gewitterregen','regnen','verregnet','Wolkenbruch','Wolkenbr??che'],
 'Damage':['Million','Milliarde','Sch??den','Schaden','Kosten','Ausma??','Zerst??rung','Tr??mmer','Auto', 'Fahrzeug','Krieg', 'Verw??stung',
            'zerst??rt','Erdrutsch','Verw??stung','weggerissen','H??user','Scheune','St??lle','Wiese','Felder','verstopft','vernichtet', 'fortgerissen',
            'wegrei??en','Sachsch??den','Ernte','Pferde','Rinder','getrieben','Stallungen','vergraben','Vieh'], 
 'Victims': ['Tote','Vermisste','Verletzte','Menschen','Tode','Dutzende','Hunderte','Tausende','Betroffene','Leben','Opfer','opfer','ertranken',
           'ertrunken','Ertrunken', 'Menschenleben','todte','Leiche'],
 'Politics': ['Wahlkampf','Politiker','Merkel','Laschet','Scholz','Baerbock','S??der', 'Seehofer', 'Dreyer', 'Pf??hler', 'Steinmeier',
               'Schulze','Habeck','Lindner','Napoleon','Kaiserin','Majest??t', 'Staat',
               'Linke','AfD','FDP','Gr??ne','SPD','Union','UNION','CSU','CDU'
               ],
 'Health': ['Seuchen', 'Ungeziefer', 'Covid', 'Corona','Pandemie','Arztprax','Impfung',
            'Seelsorge', 'Trauma','Emotionen','Schock', 'Limit'
 ],
 'Rescue': ['Feuerwehr', 'Polizei', 'Bundeswehr','THW','DRK','Einsatzkr??fte','Arbeitsdienst','Pionier','Milit??r','Evakuierung'],
 'Solidarity': ['Solidarit??t','Hilfe','Spende','Helfer','Benefiz','Landwirt','Freiwillig','freiwillig','gesammelt','Sammlungen',
                  'sammlungen','unterst??tzt'],
 'Warnings': ['EFAS', 'DWD', 'Wetterdienst','BBK','Warnung','Unwetterwarnung','Warnsystem','alarm','Alarm','Sirene','Nina','Evakuierung','Katwarn','Broadcast'],
 'Troublemakers': ['Querdenker','Pl??nder','Diebstahl','Aluh??te','Rechtsextrem','Betr??ger','Reichsb??rger','Verschw??rung','Gaffer','gaffen','skeptiker', 'leugner'],
 'Insurance': ['Allianz','Munich Re','Pflichtversicherung','Versicherung','Elementarversicherung','Versicher','Elementarsch??den','versichert'],
 'Pollution': ['M??ll','Sperm??ll','Schutt','Sonderm??ll','Schlamm','giftig','Heiz??l','Geruch','Gestank','vergiftet','schlammt','Karbid'],
 'Causes': ['Klima','Klimawandel','rw??rmung','Ursachen','Versiegelung','Schwammstadt','Luisa Neubauer','Regenr??ckhaltebecken',
              'Stefan Rahmstorf','??berflutungsfl??che','Attributionsstudie','Attributionsforschung','Mojib Latif', 'IPCC'],
 'Infrastructure': ['Deutsche Bahn', 'Gas', 'Trinkwasser','Br??cke','Strom','Stra??e','Bahn','Mobilfunk','Internet','Kanalisation','Kl??rwerk',
                   'M??hle','m??hle','Schmiede','Schifffahrt','Telephon', 'Telegraph','br??cke','Ahrbahn','Eisenbahn', 'Lokomotive', 'Lokomobile',
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

# B??rngen, M. & G. Teltzlaff (Hrsg.) (2000):  Quellentexte zur Witterungsgeschichte Europas von der Zeitwende bis zum Jahr 1850. Teil 5. Berlin, Stuttgart, Borntraeger. #
# (Dr. G. Eckertz 1870 ???Chronik u. Weisthum von Mayscho?? an der Ahr??? in ???Fontes adhuc inediti rer. Rhenan.??? II S. 77/8) #
# (J.Fr. Schannat ???Eiflia illustrata etc.???, edid. G. B??rsch 1824/55. 3.Bd. 1.Abt. 1.Abschn. 		S. 382, 454, 478.) #
# Frick, Hans Quellen zur Geschichte von Bad Neuenahr, Bad Neuenahr 1933 #
txt1804 = """
1804 	 21. Juli       Ahrtal	Ahr: ??berschwemmung infolge eines Wolkenbruchs 
Es war die erschreckliche Ahrflut. Den ganzen Tage fiel ein Platzregen, das Wasser str??mte aus der Erde hervor.   Die Ahr f??hrte weggerissene H??user, Scheunen, St??lle, Balken, B??ume, Hausger??th, leere und volle Weinf??sser mit sich. Das Wasser stand auf Bongart bis an den zweiten Stock der H??user bis an das halbe Dorf May, scho?? hinauf. Zu Laach, wo sich der M??hlenberg verstopft hatte, ward die Kapelle oben am Ende des Dorfes ganz vernichtet, von 23 H??usern 17 fortgerissen und 8 zu Bongart. Weing??rten, Wiesen und Felder waren verw??stet, so da?? man die Grenzen nicht finden konnte. Zu Laach ertranken 14 Menschen, ???, zu Rech Herr Joan Meyer, ??? mit seiner Haush??lterin ??? und noch 3 Personen, die sich in seine Wohnung gefl??chtet hatten. 
Des Abends von 8-9 Uhr war diese Verw??stung vollbracht. 

In diesem 1804 ten  Jahr war auch die erschreckliche ??berschwemmung des Ahr flu??, welche am 21. July sich begab, da?? Wasser war ??ber alle massen Gro?? und Hoch, es Stand auf Bongart in den obersten H??usern bi?? an das zweite Stock werck und ??berwalte bi?? in den
amtmanns Pfuhl oder Wayer im Thier garten, es Stand bi?? in das halbe Dorf zu Mayscho??, der Auel Stand zweitheil im Wasser,???
???, ein Solches Wasser war bei Menschen gedenck nicht,???
???, es risse die Br??cken sammt den Pfeilern umb, St??rzte die H??user ein,???
Dann zu lach nahm es die H??u??er meistens bi?? auf vier hinweg, wo 20 bis 24 H??u??er Standen, zu Bongard nahm es 8 - 9 H??u??er mit weg, etliche leut, welche zu Lach in den H??u??ern geblieben, an der Zahl vierzehn, sind mit ihren H??usern fortgetrieben und ertruncken, es war ein Elend ??ber Elend, dan in einer Stunde des abend am 21.July von 8 ??? 9 war alles hinweg, ???, getreide, hau??, Stall und Scheur Sammt weing??rten, ??cker, wie??en, b??sche,  wo das Wasser hin kam, waren in einer Stunde hinn. 

1804 21. Juli Ahr: ??berschwemmung infolge eines Wolkenbruchs, z.B. in Schuld, Ahrweiler, Altenahr u. Laach 

Infolge eines Wolkenbruchs gro??e ??berschwennung der Ahr mit gro??em Schaden.
Schuld. Ahrweiler Gro??e Wasserfluth. Bedeutender Schaden. 
Altenahr. Ahr: ??berschwemmung.
Lach b/Mayscho?? an d. Ahr Wasserflut. Der gr????te Teil des Oreste wird zerst??rt.

Durch Gewitterregen f??hrte die Ahr bereits seit Tagen Hochwasser, als am 21. Juli 1804 ein erneutes Unwetter in der Hoch- und Ahreifel sich mit riesigen Niederschl??gen entlud. Alle zur Ahr f??hrenden Nebenfl??sse, vor allem der Trier-, Adenauer- und Kesselinger Bach, schwollen innerhalb k??rzester Zeit stark an. Eine alles wegrei??ende Flutwelle f??llte die T??ler und lie?? das gesamte Ahrsystem ??ber die Ufer treten. 
Im gesamten Einzugsbereich der Ahr verursachte das Unwetter und das anschlie??ende Hochwasser riesige Sachsch??den und forderte 63 Menschenleben. 129 Wohnh??user, 162 Scheunen und Stallungen, 18 M??hlen, 8 Schmieden und nahezu alle Br??cken, insgesamt 30, wurden von den Wassermassen weggerissen. Weitere 469 Wohnh??user, 234 Scheunen und St??lle, 2 M??hlen und 1 Schmiede wurden besch??digt. 78 Pferde und Zugrinder kamen in den Fluten um, Obstb??ume wurden entwurzelt, Weinberge abgesp??lt, die gesamte Ernte vernichtet und Wiesen und Felder in der Talaue hoch mit Sand und Kies ??bersch??ttet. 
Zur Behebung der Sch??den wurde durch den Pr??fekten des Departements ein Arbeitsdienst eingerichtet, bei dem ??ber 800 M??nner, teilweise von der Mosel kommend, eingesetzt waren. An Steuergeldern wurden 120.000 Francs und Bauholz aus den W??ldern f??r 40.000 Francs zur Verf??gung gestellt. Kaiser Napoleon gab aus seiner Privatschatulle 30.000 Francs, die Kaiserin weitere 4.800 Francs zur Linderung der Not, 45.000 Francs erbrachte eine Spendenaktion.

Den 21. (Juli) bin ich mit He(rrn) Dechant Radermacher ??ber den Berg nach Remagen gegangen und oben auf dem Berg fang es dergestalten an zu regnen, da?? wir beide bis an die Haut na?? in Remagen angekommen. In selber Nacht ist auch die Ahr so angewachsen, da?? das abgeschnittene Korn von den Fudern abgetrieben, alle m??glich Hausger??the, Bauh??lzer und todte Menschen auf dem Felde gefunden worden, die mit der Aar dahin getrieben??.
Antweiler: 1804.21, Juni Nachmittags 3 Uhr st??rzte das Wasser bei einem erschrecklichen Gewitter von Norden in Str??men aus den Wolken, wodurch die Ahr und alle kleineren B??che dergestalt gewachsen, dass hier zu Antweiler 6 H??user, 12 Scheunen und Stallungen, 2 Oehlm??hlen, 1 Schmiede fortgerissen, 8 H??user samt soviel Scheunen und Stallungen bis an die D??cher in Sand vergraben wurden. In M??sch wurden 10 H??user mit ihren Geb??uden g??nzlich besch??digt und 4 Menschen sind daselbst ertrunken. Auf dem ganzen Ahrstrom aber sind 65 Menschen, 147 H??user, 190 Scheunen, 20 M??hlen, 8 Schmieden, 50 Br??cken, nebst vielem Vieh in den Fluten zugrunde gegangen; 428 H??user, 269 Scheunen, 8 M??hlen, wurden g??nzlich besch??digt. Dieser wilde Strom hin-terliess in einer H??he von 8, 10, ja sogar bis zu 20 Schuh hier Steinhaufen, dort einen Kot, dessen Geruch die Luft vergiftet. In diesem w??tenden Strom, welcher die Kirche und alle H??user zwischen der Ahr und H??gerbach, 4 ausgenommen, hoch unter Wasser setzte, welche ??ber das hl. H??uschen ??ber der Ahr ging, blieb das Bildnis des hl. Johannes Nepomuce-nus, so von Holz und nirgends festgemacht, auch vorn mit keinem Gegitter versehen war, wunderlich mit ihrem H??uschen und die Br??cke stehen.
"""

# Ortschronik von Bodendorf angelegt von Clemens v. Lassaulx 1879; gef??hrt bis 1955 (von verschiedenen Chronisten)#
# * Schulchronik der Schule und Gemeinde Bodendorf, begonnen von Lehrer Johann Mies, 1895, gef??hrt vom jeweiligen Schulleiter bis 1962 #
# * Lagerbuch der Pfarrei Bodendorf, begonnen von Pfarrer Bartholom??us Fey 1802, mit Unterbrechungen gef??hrt bis ca. 1955. #
txt1910 = """
Das Fr??hjahr lie?? sich ganz gut an, aber der Sommer war mehr oder weniger verregnet. Ja in der Nacht vom 12. auf den 13. Juni ging ein gewaltiger Wolkenbruch ??ber unser Thal nieder, der ganz grausiges Hochwasser der Ahr verursachte und eine gewaltige ??berschwemmung das Thal heimsuchte. Die durch diese ??berschwemmung entstandenen Sch??den wurden durch im ganzen Reich gesammelte Gelder gedeckt. Am Ahrbett machte das Wasser gro??en Schaden, so da?? wohl ein vollst??ndiger Neubau der Uferbefestigungen notwendig wird??18). ??Am 13. Juni d. J. war die gro??e ??berschwemmung im Ahrtal. An der Oberahr sind ungef??hr 70 Leute ertrunken; es waren dies meist Ausl??nder, die an dem Bahnbau arbeiteten. In Bodendorf hat die ??berschwemmung gro??en Schaden gemacht. Das ??berall in den Wiesen ??ppig stehende Gras war alle ??berschwemmt und beschlammt. Es sind gro??e Geldsammlungen veranstaltet worden. Sr. Majest??t gab 10.000 Mark. Auch hier in Bodendorf sind die Gesch??digten unterst??tzt worden, viele wurden fast schadlos gehalten

Am 13. Juni dieses Jahres war die gro??e Wasserkatastrophe an der Ahr, verursacht durch Wolkenbr??che, welche an der Oberahr zwischen der Hohen Acht und Hillesheim zur Nachtzeit niedergingen
"""

#get news_1804_1910.csv from freidok:  doi.org/10.6094/UNIFR/222040
historyDf = files.getDFfromFiledok("https://freidok.uni-freiburg.de/fedora/objects/freidok:222040/datastreams/FILE1/content", "news_1804_1910.csv", delimiter=',')

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




