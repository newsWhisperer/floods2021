import pandas as pd

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

def getTopicDict():
    return topicDict

def getTopicColors():
    return colorsTopics    