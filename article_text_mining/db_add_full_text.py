# -*- coding: utf-8 -*-
"""
Created on Tue Mar 20 09:54:11 2012

@author: Shreejoy
"""


import os
import re
import struct
import gc
from matplotlib.pylab import *

from django.db import transaction
from xml.etree.ElementTree import XML
from urllib.parse import quote_plus, quote
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from xml.etree.ElementTree import XML
import json
from pprint import pprint
from bs4 import BeautifulSoup
import time
from article_text_mining.pubmed_functions import add_articles
from html.parser import HTMLParseError


def get_full_text_links():
    NUMHITS = 50
    firstInd = 4900
    maxURLTries = 5
    waitTime = 60
    totalArticles = NUMHITS + firstInd + 1 # just set this later when it gets searched
    searchLinkFull = 'http://jp.physoc.org/search?tmonth=&pubdate_year=&submit=yes&submit=yes&submit=Submit&andorexacttitle=and&format=standard&firstpage=&fmonth=&title=&tyear=&hits=' + str(NUMHITS) + '&titleabstract=&volume=&sortspec=relevance&andorexacttitleabs=and&author2=&tocsectionid=all&andorexactfulltext=and&author1=&fyear=&doi=&fulltext=membrane%20potential%20neuron&FIRSTINDEX=' + str(firstInd)

    #    'http://jn.physiology.org/search?tmonth=Mar&pubdate_year=&submit=yes&submit=yes&submit=Submit&andorexacttitle=and&format=condensed&firstpage=&fmonth=Jan&title=&tyear=2012'
#    searchLinkBase = 'http://jn.physiology.org/search?tmonth=Mar&pubdate_year=&submit=yes&submit=yes&submit=Submit&andorexacttitle=and&format=condensed&firstpage=&fmonth=Jan&title=&tyear=2012&hits=' + str(NUMHITS) + '&titleabstract=&flag=&journalcode=jn&volume=&sortspec=date&andorexacttitleabs=and&author2=&andorexactfulltext=and&author1=&fyear=1997&doi=&fulltext=%22input%20resistance%22%20AND%20neuron&FIRSTINDEX=' + str(firstInd)
    fullTextLinks = []
    pdfLinks = []
    while firstInd + NUMHITS <= totalArticles:
        print('searching %d of %d articles' % (firstInd, totalArticles))
#        searchLinkFull = 'http://jn.physiology.org/search?tmonth=Mar&pubdate_year=&submit=yes&submit=yes&submit=Submit&andorexacttitle=and&format=condensed&firstpage=&fmonth=Jan&title=&tyear=2012&hits=' + str(NUMHITS) + '&titleabstract=&flag=&journalcode=jn&volume=&sortspec=date&andorexacttitleabs=and&author2=&andorexactfulltext=and&author1=&fyear=1997&doi=&fulltext=%22input%20resistance%22%20AND%20neuron&FIRSTINDEX=' + str(firstInd)
#        searchLinkFull = 'http://www.jneurosci.org/search?tmonth=Mar&pubdate_year=&submit=yes&submit=yes&submit=Submit&andorexacttitle=and&format=condensed&firstpage=&fmonth=Jan&title=&tyear=2012&hits=' + str(NUMHITS) + '&titleabstract=&volume=&sortspec=date&andorexacttitleabs=and&author2=&tocsectionid=all&andorexactfulltext=and&author1=&fyear=1997&doi=&fulltext=input%20resistance%20neuron&FIRSTINDEX=' + str(firstInd)       
        handle = urlopen(searchLinkFull) # open the url
        data = handle.read() # read the data
        soup = BeautifulSoup(data)
#        print BeautifulSoup.prettify(soup)
        headerString = soup.find_all('h1')[1].string
        print(headerString)
        numTries = 1
        while (headerString == 'Currently Unavailable' or headerString == 'Your search criteria matched no articles') and numTries < maxURLTries:
            print('URL search failed %d times' % numTries)
            print('now waiting %d secs before trying search again' % (waitTime*numTries))
            time.sleep(waitTime*numTries)
            handle = urlopen(searchLinkFull) # open the url
            data = handle.read() # read the data
            soup = BeautifulSoup(data)
            headerString = soup.find_all('h1')[1].string
            numTries += 1
        if numTries == maxURLTries:
            print('URL search failed %d times' % maxURLTries)
            print('skipping')
            continue
        # get all links to full text docs
        if totalArticles == NUMHITS + firstInd + 1:
            totalArticles = int(soup.find('span', {'class':'results-total'}).text)
        for link in soup.find_all('a'):
        #    print link.get('rel')
            if link.string == 'Full Text':
                currLink = link.get('href')
                fullTextLinks.append(currLink)
            elif link.string == 'Full Text (PDF)':
                currLink = link.get('href')
                pdfLinks.append(currLink)            
#                print(link.get('href'))
        firstInd += NUMHITS
        print('now waiting %d secs before next search' % waitTime)
        time.sleep(waitTime)
    return (fullTextLinks, pdfLinks)
    
def get_full_text_from_link(fullTextLink):
#    searchLinkFull = 'http://jn.physiology.org/search?tmonth=Mar&pubdate_year=&submit=yes&submit=yes&submit=Submit&andorexacttitle=and&format=condensed&firstpage=&fmonth=Jan&title=&tyear=2012&hits=' + str(NUMHITS) + '&titleabstract=&flag=&journalcode=jn&volume=&sortspec=date&andorexacttitleabs=and&author2=&andorexactfulltext=and&author1=&fyear=1997&doi=&fulltext=%22input%20resistance%22%20AND%20neuron&FIRSTINDEX=' + str(firstInd)
#    fullTextLink = 'http://jn.physiology.org/content/107/6/1655.full'   
    (soup, fullTextLink) = soupify_plus(fullTextLink) 
#    isPdf = checkPdf(fullTextLink)
    if soup is False:
        return False
    #    print BeautifulSoup.prettify(soup)
    # find pubmed link and pmid
    try:
        tempStr = re.search('access_num=[\d]+', str(soup('a',text=('PubMed citation'))[0])).group()
    except (IndexError):
        return False
    pmid = int(re.search('\d+', tempStr).group())
    if Article.objects.filter(pmid = pmid).count() == 0:
        # add pmid abstract and stuff to db Article list
        add_articles([pmid])
    
    # get Article object
    art = Article.objects.get(pmid = pmid)
    art.full_text_link = fullTextLink
    art.save()
    
    # get article full text and save to object
    fullTextTag = soup.find('div', {'class':'article fulltext-view'})
#    fullTextTag = soup.find('div', {'itemprop':'articleBody'})

#    # tag finder for j-neurophys
#    tags = soup.find_all('div')
#    for t in tags:
#        if 'itemprop' in t.attrs and t['itemprop'] == 'articleBody':
#            fullTextTag = t
#            break
    fullTextOb = ArticleFullText.objects.get_or_create(article = art)[0]
    fullTextOb.full_text = str(fullTextTag)
    fullTextOb.save()
    
    # get article data table links
    # just count number of tables in article
#    tableList = []
    numTables = 0
    for link in soup.find_all('a'):
        linkText = link.get('href')
        if link.string == 'In this window' and linkText.find('T') != -1:
            print(linkText)
            numTables += 1
#            tableList.append(linkText)
    
    print('adding %d tables' % (numTables))
    for i in range(numTables):
        tableLink = fullTextLink[:-5] + '/T' + str(i+1)  
        tableSoup = soupify(tableLink)
        if tableSoup is False:
            continue
        tableTag = tableSoup.find('div', {'class':'table-expansion'})
        if tableTag is None:
            tableTag = soup.find('div', {'itemprop':'articleBody'})
        dataTableOb = DataTable.objects.get_or_create(link = tableLink, article = art)[0]
        table_html = str(tableTag)
        
        dataTableOb.table_html = table_html
        table_text = tableTag.get_text()
        table_text = table_text[0:min(9999,len(table_text))]
        dataTableOb.table_text = table_text
        dataTableOb.save()

elinkBase = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&id=%d&cmd=prlinks&retmode=ref'    
def get_full_text_from_pmid(pmids):
    cnt = 0
    for pmid in pmids:
        print('%d of %d articles' % (cnt, len(pmids)))
        link = elinkBase % pmid
        get_full_text_from_link(link)
        cnt += 1    

elinkBase = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&id=%d&cmd=prlinks&retmode=ref'    
def get_pdf_from_pmid(pmids):
    os.chdir('C:\Python27\Scripts\Biophys\pdf_dir')
    cnt = 0
    failedPmids = []
    fullTextPmids = [int(a.pmid) for a in Article.objects.filter(articlefulltext__isnull = False)]
    diffSet = set(pmids).difference(set(fullTextPmids))    
    for pmid in diffSet:
        print('%d of %d articles' % (cnt, len(diffSet)))
        link = elinkBase % pmid
        success = get_pdf_from_link(link, pmid)
        if success == False:
            failedPmids.append(pmid)
        cnt += 1  
    os.chdir('C:\Python27\Scripts\Biophys')
    return failedPmids

MAXURLTRIES = 2
MAXTITLELEN = 100
def get_pdf_from_link(link, pmid):
    success = False
    numTries = 0
    waitTimeLong = 180
    waitTimeShort = 2
    a = Article.objects.get(pmid = pmid)
    title = a.title
    title = '%d_%s' % (pmid, title)
    title = re.sub('\s', '_', title)
    pattern = '[a-zA-Z0-9_]'
    title = ''.join(re.findall(pattern, title))
    fileName = title[0:min(MAXTITLELEN, len(title))]
    fileName = fileName + '.pdf'
    while numTries < MAXURLTRIES and success == False: 
        try:
            handle = urlopen(link) # open the url
            url = handle.geturl()
            newUrl = re.sub('.long', '.full.pdf', url)
            handle = urlopen(newUrl)
            data = handle.read() # read the data
            f = open(fileName, 'wb')
            f.write(data)
            f.close()
#            soup = BeautifulSoup(data)    
            success = True
            time.sleep(waitTimeShort)
        except (URLError, HTTPError, HTMLParseError):
            print(link + ' failed %s times' % numTries) 
            numTries += 1
            print('now waiting %d secs before trying search again' % (waitTimeLong*numTries))
            time.sleep(waitTimeLong*numTries)
            url = ''
    return success    
    
def get_full_text_from_link_all(fullTextLinkList):
    cnt = 0
    for link in fullTextLinkList:
        print('%d of %d articles' % (cnt, len(fullTextLinkList)))
        get_full_text_from_link(link)
        cnt += 1

def convert_links(linkList):
    retLinkList = []
#    linkBase = 'http://jn.physiology.org'
    linkBase = 'http://www.jneurosci.org'
    for currLink in linkList:
        linkPart = re.search('[\d\w/]+.', currLink).group()[:-1]
        newLink = linkBase + linkPart + '.full'
        retLinkList.append(newLink)
    return retLinkList
        
MAXURLTRIES = 2
def soupify_plus(link):
    success = False
    numTries = 0
    waitTimeLong = 180
    waitTimeShort = 2
    while numTries < MAXURLTRIES and success == False: 
        try:
            handle = urlopen(link) # open the url
            url = handle.geturl()
            data = handle.read() # read the data
            soup = BeautifulSoup(data)    
            success = True
            time.sleep(waitTimeShort)
        except (URLError, HTTPError, HTMLParseError):
            print(link + ' failed %s times' % numTries) 
            numTries += 1
            print('now waiting %d secs before trying search again' % (waitTimeLong*numTries))
            time.sleep(waitTimeLong*numTries)
            url = ''
    if numTries == MAXURLTRIES:
        soup = False
    return (soup, url)

#MAXURLTRIES = 2
def soupify(link):
    success = False
    numTries = 0
    waitTimeLong = 180
    waitTimeShort = 2
    while numTries < MAXURLTRIES and success == False: 
        try:
            handle = urlopen(link) # open the url
            data = handle.read() # read the data
            soup = BeautifulSoup(data)    
            success = True
            time.sleep(waitTimeShort)
            
        except (URLError, HTTPError, HTMLParseError):
            print(link + ' failed %s times' % numTries) 
            numTries += 1
            print('now waiting %d secs before trying search again' % (waitTimeLong*numTries))
            time.sleep(waitTimeLong*numTries)
    if numTries == MAXURLTRIES:
        soup = False
    return soup
    
def checkPdf(link):
    newLink = re.sub(r'+html', '', link)
    if re.search(r'.pdf', newLink) is not None:
        isPdf = True
    return (isPdf, newLink)