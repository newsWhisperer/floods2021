import files
import pandas as pd

from pathlib import Path
import os.path

import requests
from urllib.parse import urlparse
import json

from bs4 import BeautifulSoup


def extractZeit(htmlText):
    soup = BeautifulSoup(htmlText, 'html.parser')
    content = ''
    for header in soup.article.find_all(['h1'],class_=['article-heading']):
        content += header.get_text(' ', strip=True)+' \n'
    for summary in soup.article.find_all(['div'],class_=['summary']):
        content += summary.get_text(' ', strip=True)+' \t\n'  
    for paragraph in soup.article.find_all(['p', 'h2'],class_=['article__item']):
         content += paragraph.get_text(' ', strip=True).replace("\n",' ').replace('  ',' ')+' \t\n'  
    return content   

def extractSued(htmlText):
    soup = BeautifulSoup(htmlText, 'html.parser')
    content = ''
    for header in soup.article.header.find_all(['h2']):
        content += header.get_text(' ', strip=True)+' \n'
    for body in soup.article.find_all('div', itemprop='articleBody'):
        for paragraph in body.find_all('p'):
             content += paragraph.get_text(' ', strip=True).replace("\n",' ').replace('  ',' ')+' \t\n'  
    return content  

def extractStern(htmlText):
    soup = BeautifulSoup(htmlText, 'html.parser')
    content = ''
    for header in soup.main.article.find_all(['div'],class_=['title']):
        content += header.get_text(' ', strip=True)+' \n'
    for summary in soup.main.article.find_all(['div'],class_=['intro']):
        content += summary.get_text(' ', strip=True)+' \t\n'  
    for paragraph in soup.main.article.find_all(['p', 'h2'],class_=['text-element', 'subheadline-element']):
         newCont = paragraph.get_text().replace("\n",' ').replace('  ',' ').strip()
         if(not newCont in content):
            content += newCont+' \t\n'  
    return content             

def extractFocus(htmlText):
    soup = BeautifulSoup(htmlText, 'html.parser')
    content = ''
    for header in soup.article.find_all(['div'],class_=['articleIdentH1']):
        content += header.get_text(' ', strip=True)+' \n'
    for summary in soup.article.find_all(['div'],class_=['leadIn']):
        content += summary.get_text(' ', strip=True)+' \t\n'  
    for body in soup.article.find_all(['div'],class_=['textBlock']):
        for paragraph in body.find_all(['p', 'h2']):
             content += paragraph.get_text(' ', strip=True).replace("\n",' ').replace('  ',' ')+' \t\n'  
    return content   

def extractNtv(htmlText):
    soup = BeautifulSoup(htmlText, 'html.parser')  
    content = ''
    for article in soup.find_all(['div'], class_=['content']):
        for header in article.find_all(['div'],class_=['article__header']):
            content += header.get_text(' - ', strip=True)+' \n'
        for body in article.find_all(['div'],class_=['article__text']):
            for paragraph in body.find_all(['p', 'h2']):
                content += paragraph.get_text(' ', strip=True).replace("\n",' ').replace('  ',' ')+' \t\n'  
    return content 

def extractSpiegel(htmlText):
    soup = BeautifulSoup(htmlText, 'html.parser')
    content = ''
    for header in soup.article.header.find_all(['h2']):
        content += header.get_text(' ', strip=True)+' \n'
    for summary in soup.article.header.find_all(['div'],class_=['leading-loose']):
        content += summary.get_text(' ', strip=True)+' \t\n'  
    for body in soup.article.find_all(['section'],class_=['relative']):
            for paragraph in body.find_all(['p', 'h3']):
                content += paragraph.get_text(' ', strip=True).replace("\n",' ').replace('  ',' ')+' \t\n'  
    return content  

def extractFaz(htmlText):
    soup = BeautifulSoup(htmlText, 'html.parser')
    content = ''
    if(soup.article):
        for header in soup.article.find_all(['div'],class_=['atc-HeadlineContainer']):
            content += header.get_text(' ', strip=True)+' \n'
        for summary in soup.article.find_all(['div'],class_=['atc-Intro']):
            content += summary.get_text(' ', strip=True)+' \t\n'  
        for body in soup.article.find_all(['div'],class_=['atc-Text']):
                for paragraph in body.find_all(['p', 'h3'], class_=['atc-TextParagraph', 'atc-SubHeadline']):
                    content += paragraph.get_text(' ', strip=True).replace("\n",' ').replace('  ',' ')+' \t\n' 
    else:
        content = ''
    return content 

def extractMorgenpost(htmlText):
    soup = BeautifulSoup(htmlText, 'html.parser')
    content = ''
    for header in soup.article.find_all(['div'],class_=['article__header__heading']):
        content += header.get_text(' ', strip=True)+' \n'
    for summary in soup.article.find_all(['div'],class_=['article__header__intro']):
        content += summary.get_text(' ', strip=True)+' \t\n'  
    for body in soup.article.find_all(['div'],class_=['article__body']):
            for paragraph in body.find_all(['p', 'h3']):
                content += paragraph.get_text(' ', strip=True).replace("\n",' ').replace('  ',' ')+' \t\n'  
    return content       

def extractWelt(htmlText):
    soup = BeautifulSoup(htmlText, 'html.parser')
    content = ''
    for header in soup.article.find_all(['h2'],class_=['c-headline']):
        content += header.get_text(' ', strip=True)+' \n'
    for summary in soup.article.find_all(['div'],class_=['c-summary']):
        content += summary.get_text(' ', strip=True)+' \t\n'  
    for body in soup.article.find_all(['div'],class_=['c-article-text']):
            for paragraph in body.find_all(['p', 'h3']):
                content += paragraph.get_text(' ', strip=True).replace("\n",' ').replace('  ',' ')+' \t\n'  
    return content  

def extractTagesschau(htmlText):
    soup = BeautifulSoup(htmlText, 'html.parser')
    content = ''
    for header in soup.article.find_all(['h1'],class_=['seitenkopf__headline']):
        content += header.get_text(' ', strip=True)+' \n'
    for paragraph in soup.article.find_all(['p', 'h2'],class_=['textabsatz', 'meldung__subhead']):
         content += paragraph.get_text(' ', strip=True).replace("\n",' ').replace('  ',' ')+' \t\n'  
    return content  

def extractHandelsblatt(htmlText):
    soup = BeautifulSoup(htmlText, 'html.parser')
    content = ''
    for header in soup.article.find_all(['span'],class_=['vhb-headline--onecolumn']):
        content += header.get_text(' ', strip=True)+' \n'
    for summary in soup.article.find_all(['span'],class_=['vhb-article--introduction']):
        content += summary.get_text(' ', strip=True)+' \t\n'  
    for body in soup.article.find_all(['div'],class_=['vhb-article-area--read']):
            for paragraph in body.find_all(['p', 'h3']):
                content += paragraph.get_text(' ', strip=True).replace("\n",' ').replace('  ',' ')+' \t\n'  
    return content  

def extractBild(htmlText):
    soup = BeautifulSoup(htmlText, 'html.parser')
    content = ''
    for header in soup.article.find_all(['h1']):
        content += header.get_text(' - ', strip=True)+' \n'
    for body in soup.article.find_all(['div'],class_=['txt']):
            for paragraph in body.find_all(['p', 'h2']):
                content += paragraph.get_text(' ', strip=True).replace("\n",' ').replace('  ',' ')+' \t\n'  
    for body in soup.article.find_all(['div'],class_=['article-body']):
            for paragraph in body.find_all(['p', 'h2']):
                content += paragraph.get_text(' ', strip=True).replace("\n",' ').replace('  ',' ')+' \t\n'                 
    return content      

def extractTagesspiegel(htmlText):
    soup = BeautifulSoup(htmlText, 'html.parser')
    content = ''
    for header in soup.article.header.find_all(['h1'], class_=['ts-title']):
        content += header.get_text(' ', strip=True)+' \n'
    for summary in soup.article.header.find_all(['p'],class_=['ts-intro']):
        content += summary.get_text(' ', strip=True)+' \t\n'  
    for body in soup.article.find_all(['div'],class_=['ts-article-body']):
            for paragraph in body.find_all(['p', 'h3']):
                content += paragraph.get_text(' ', strip=True).replace("\n",' ').replace('  ',' ')+' \t\n'  
    return content  

def extractOrf(htmlText):
    soup = BeautifulSoup(htmlText, 'html.parser')
    content = ''
    for header in soup.main.find_all(['h1'], class_=['story-lead-headline']):
        content += header.get_text(' ', strip=True)+' \n'
    for summary in soup.main.find_all(['p'],class_=['story-lead-text']):
        content += summary.get_text(' ', strip=True)+' \t\n'  
    for body in soup.main.find_all(['div'],class_=['story-story']):
            for paragraph in body.find_all(['p', 'h2']):
                content += paragraph.get_text(' ', strip=True).replace("\n",' ').replace('  ',' ')+' \t\n'  
    return content      

def extractNzz(htmlText):
    soup = BeautifulSoup(htmlText, 'html.parser')
    content = ''
    for header in soup.find_all(['h1'], class_=['headline__title']):
        content += header.get_text(' ', strip=True)+' \n'
    for summary in soup.find_all(['p'],class_=['headline__lead']):
        content += summary.get_text(' ', strip=True)+' \t\n'  
    for body in soup.find_all(['div'],class_=['article']):
            for paragraph in body.find_all(['p', 'h2', 'li'], class_=['articlecomponent','enumeration__title','enumeration__item']):
                content += paragraph.get_text(' ', strip=True).replace("\n",' ').replace('  ',' ')+' \t\n'  
    return content   

def extractDw(htmlText):
    soup = BeautifulSoup(htmlText, 'html.parser')
    content = ''
    for body in soup.find_all(['div'],id=['bodyContent']):
        for header in body.find_all(['h1']):
            content += header.get_text(' ', strip=True)+' \n'
    for body in soup.find_all(['div'],id=['bodyContent']):
        for summary in body.find_all(['p'],class_=['intro']):
            content += summary.get_text(' ', strip=True)+' \t\n'  
    for body in soup.find_all(['div'],class_=['longText']):
            for paragraph in body.find_all(['p', 'h2']):
                content += paragraph.get_text(' ', strip=True).replace("\n",' ').replace('  ',' ')+' \t\n'  
    return content   

def extractHeise(htmlText):
    soup = BeautifulSoup(htmlText, 'html.parser')
    content = ''
    for side in soup.find_all(['section'], class_=['article-sidebar']):
        side.decompose() 
    for header in soup.article.find_all(['h1'],class_=['article__heading']):
        content += header.get_text(' ', strip=True)+' \n'
    for paragraph in soup.article.find_all(['p', 'h3','blockquote']):
        content += paragraph.get_text(' ', strip=True).replace("\n",' ').replace('  ',' ')+' \t\n'  
    return content 

def extractTaz(htmlText):
    soup = BeautifulSoup(htmlText, 'html.parser')
    content = ''
    for header in soup.article.find_all(['h1'],itemprop=['headline']):
        content += header.get_text(' ', strip=True)+' \n'
    for paragraph in soup.article.find_all(['p', 'h6']):     
        content += paragraph.get_text(' ', strip=True).replace("\n",' ').replace('  ',' ')+' \t\n'  
    content = content.replace("&shy", '').replace(";\xad","").replace("\xad","")
    return content 

def extractWiwo(htmlText):
    soup = BeautifulSoup(htmlText, 'html.parser')
    content = ''
    for header in soup.article.find_all(['h2'],class_=['c-headline']):
        content += header.get_text(' ', strip=True)+' \n'
    for summary in soup.article.find_all(['p'],class_=['c-leadtext']):
            content += summary.get_text(' ', strip=True)+' \t\n'  
    for body in soup.find_all(['div'],class_=['c-richText']):
            for meta in body.find_all(['div'], class_=['c-metadata']):
                meta.decompose() 
            for paragraph in body.find_all(['p', 'h3']):
                content += paragraph.get_text(' ', strip=True).replace("\n",' ').replace('  ',' ')+' \t\n' 
    return content 

def extractTonline(htmlText):
    soup = BeautifulSoup(htmlText, 'html.parser')
    content = ''
    for header in soup.find_all(['h2'],class_=['Tarthl']):
        content += header.get_text(' - ', strip=True)+' \n'
    for body in soup.find_all(['div'],itemprop=['articleBody']):
            for meta in body.find_all(['span'], class_=['Tiflle']):
                meta.decompose() 
            for paragraph in body.find_all(['p', 'h3']):
                content += paragraph.get_text(' ', strip=True).replace("\n",' ').replace('  ',' ')+' \t\n' 
    return content 

def extractPresse(htmlText):
    soup = BeautifulSoup(htmlText, 'html.parser')
    content = ''
    for header in soup.article.find_all(['h1'],class_=['article__title']):
        content += header.get_text(' - ', strip=True)+' \n'
    for body in soup.find_all(['div'],class_=['article__body']):
            for paragraph in body.find_all(['p', 'h2']):
                content += paragraph.get_text(' ', strip=True).replace("\n",' ').replace('  ',' ')+' \t\n' 
    return content 

def extractAny(htmlText):
    soup = BeautifulSoup(htmlText, 'html.parser')
    content = ''
    #for side in soup.find_all(['header'], class_=['header']):
    #    side.decompose()     
    for side in soup.find_all(['section'], class_=['article-sidebar']):
        side.decompose() 
    for side in soup.find_all(['div'], id=['navigation']):
        side.decompose() 
    for side in soup.find_all(['div', 'section'], id=['sidebar']):
        side.decompose()         
    for side in soup.find_all(['div'], id=['footer']):
        side.decompose() 
    for side in soup.find_all(['nav']):
        side.decompose()         
    for side in soup.find_all(['footer']):
        side.decompose() 
    for side in soup.find_all(['aside']):
        side.decompose() 

    if(soup.find_all(['main'])):
        soup = soup.main.extract()
    if(soup.find_all(['article'])):
        soup = soup.article.extract()

    for paragraph in soup.find_all(['p','h1','h2','h3','h4','h5','h6','blockquote']):
        content += paragraph.get_text(' ', strip=True).replace("\n",' ').replace('  ',' ')+' \t\n'  
    return content     

domains = {'www.zeit.de': extractZeit, 'www.sueddeutsche.de': extractSued, 'www.stern.de':extractStern, 'www.focus.de':extractFocus, 
           'www.n-tv.de':extractNtv, 'www.spiegel.de':extractSpiegel, 'www.faz.net':extractFaz, 'www.morgenpost.de':extractMorgenpost,
           'www.welt.de':extractWelt, 'www.tagesschau.de':extractTagesschau, 'www.handelsblatt.com':extractHandelsblatt, 
           'www.bild.de':extractBild, 'www.tagesspiegel.de':extractTagesspiegel, 'orf.at':extractOrf, 'www.nzz.ch':extractNzz,
           'www.dw.com':extractDw, 'www.heise.de':extractHeise, 'taz.de':extractTaz, 'www.taz.de':extractTaz, 'www.wiwo.de':extractWiwo, 
           'www.t-online.de':extractTonline, 'www.diepresse.com':extractPresse,
          }          

DATA_PATH = Path.cwd()

pd.set_option('display.max_colwidth', 100000)

newsFiles = files.getNewsFiles(state='harvest')

for newsFileHarvest in newsFiles:
    newsFileMining = newsFileHarvest.replace('_harvest_','_mining_')
    df1 = pd.read_csv(newsFileHarvest, delimiter=',',index_col='index')
    df1['quote'] = ''
    di1 = df1.to_dict('index')

    for index in di1:
        #print(di1[index]['url'])
        if(not di1[index]['quote']):
            if(di1[index]['domain'] in domains):
                quoteOrig = None
                urlOrig = di1[index]['url']
                quoteArchive = None
                urlArchive = None
                domain = di1[index]['domain']
                if((di1[index]['archive']) and (len(str(di1[index]['archive']))>10)):
                    urlArchive = di1[index]['archive']
                if(urlArchive):
                    try:
                        print(urlArchive) 
                        response = requests.get(urlArchive, timeout=120)
                    except Exception as e2:
                        print(['Fail to get url: ', urlArchive,' exc: ' ,e2])
                        response = None    
                    if(response):
                        if(response.text):
                            encoded = response.text.encode(response.encoding).decode('utf-8')
                            quoteArchive =  domains[domain](encoded)
                if(urlOrig):
                    try:
                        print(urlOrig) 
                        response = requests.get(urlOrig, timeout=90)
                    except Exception as e2:
                        print(['Fail to get url: ', urlOrig,' exc: ' ,e2])
                        response = None   
                    if(response):
                        if(response.text):
                            encoded = response.text.encode(response.encoding).decode('utf-8')
                            quoteOrig =  domains[domain](encoded)
                if(quoteOrig):
                    di1[index]['quote'] = quoteOrig        
                if(quoteArchive):
                    di1[index]['quote'] = quoteArchive
                else:
                    di1[index]['archive'] = ""       

    cols = ['url','valid','domain','title','description','image','published','archive','content','quote','language','keyword']
    df3 = pd.DataFrame.from_dict(di1, orient='index', columns=cols)
    df3.to_csv(newsFileMining, index_label='index')


     
     
