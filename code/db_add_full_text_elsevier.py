# -*- coding: utf-8 -*-
"""
Created on Mon Dec 17 10:30:59 2012

@author: Shreejoy
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Mar 20 09:54:11 2012

@author: Shreejoy
"""


import os
import os.path
#import django_startup
import re
#import struct
#import gc
from matplotlib.pylab import *
#os.chdir('C:\Python27\Scripts\Biophys\Biophysiome')
#from biophysapp.models import Article, MeshTerm, Substance, Journal
##from pubapp.models import Neuron, IonChannel, NeuronChanEvid
#from biophysapp.models import BrainRegion, InSituExpt, Protein, RegionExpr
#from biophysapp.models import DataTable, ArticleFullText
#os.chdir('C:\Python27\Scripts\Biophys')

#from django.db import transaction
from xml.etree.ElementTree import XML
from urllib import quote_plus, quote
from urllib2 import Request, urlopen, URLError, HTTPError
from xml.etree.ElementTree import XML
import json

#from pprint import pprint
#from bs4 import BeautifulSoup

from pprint import pprint
#from bs4 import BeautifulSoup

import time
#from db_add import add_articles
#from HTMLParser import HTMLParseError

def get_full_text_wrapper(queries):
    for queryStr in queries:
        resultList = get_full_text_links(queryStr)
        get_full_text_from_link_all(resultList)


queryStr = "input resistance resting membrane potential neuron"
def get_full_text_links(queryStr):
    NUMHITS = 200
    maxURLTries = 5
    waitTime = 60
    
    queryStrQuoted = re.sub(' ', '+', queryStr)
    testYears = range(1996,2013)
    #testYears = [2000]
    searchLinkBase = 'http://api.elsevier.com/content/search/index:SCIDIR?query=%s&date=%d&count=%d&start=%d&content=k'
    resultList = []
    
    headerDict = {"X-ELS-APIKey":"***REMOVED***",
               "X-ELS-ResourceVersion": "XOCS" ,
               "Accept": "application/json"}
    for currYear in testYears:
            firstInd = 0
        # figure out how many search results are in this year:
            searchLinkFull = searchLinkBase % (queryStrQuoted, currYear, 1, 0)
            
            request = Request(searchLinkFull, headers = headerDict)
            contents = urlopen(request).read()
            resultDict = json.loads(contents)
            totalArticles = int(resultDict['search-results']['opensearch:totalResults'])

            while firstInd <= totalArticles:
                print 'searching %d of %d articles' % (firstInd, totalArticles)
                searchLinkFull = searchLinkBase % (queryStrQuoted, currYear, NUMHITS, firstInd)
                request = Request(searchLinkFull, headers = headerDict)
                contents = urlopen(request).read()
                resultDict = json.loads(contents)
                searchResults = resultDict['search-results']['entry']
                resultList.extend(searchResults)
                firstInd += NUMHITS 
                
    return resultList

def make_xml_filename(title, pmid):
    title = '%s_%s' % (pmid, title)
    title = re.sub('\s', '_', title)
    pattern = '[a-zA-Z0-9_]'
    title = ''.join(re.findall(pattern, title))
    fileName = title[0:min(MAXTITLELEN, len(title))]
    fileName = fileName + '.xml'    
    return fileName

MAXURLTRIES = 2

def get_full_text_from_link(fullTextLink, articleTitle, articleDOI):
    os.chdir('C:\Users\Shreejoy\Desktop\elsevier_xml') 
    headerDict = {"X-ELS-APIKey":"***REMOVED***",
               "X-ELS-ResourceVersion": "XOCS" ,
               "Accept": "text/xml"}
    # actually try to get full text
    success = False
    numTries = 0
    waitTimeLong = .5
    waitTimeShort = 2
    link = fullTextLink + '?view=FULL'
    request = Request(link, headers = headerDict)
    while numTries < MAXURLTRIES and success == False: 
        try:
            
            fullText = urlopen(request).read()
            # fullText get succeeded!
            titleEncoded = articleTitle.encode("iso-8859-15", "replace")
            #now get the pubmed id from a pubmed esearch search
            pmidList = get_pubmed_id_from_doi(articleDOI)
            if len(pmidList) == 0:
                pmidList = get_pubmed_id_from_title(titleEncoded)
            if len(pmidList) > 0:
                pmid = pmidList[0]
            else:
                pmid = False
                with open('failed_pubmed.txt', 'a') as f:
                    f.write('\\\%s' % articleDOI)
                print 'could not find unique pmid for %s' % (titleEncoded)
                break
            #soup = BeautifulSoup(data)    
            
            # save full text to a file
            fileName = make_xml_filename(articleTitle, pmid)
            if os.path.isfile(fileName):
                print 'found identical file'
                pass
            else:
                # file doesn't exist
                f = open(fileName, 'wb')
                f.write(fullText)
                f.close()
                print 'found unique file'
            success = True
            time.sleep(waitTimeShort)
        except Exception, e:
            print e.code
            if e.code == 403:
                #print '%s failed cause access restricted' % (articleTitle)
                fullText = False
                pmid = False
                break
            else:
                print link + ' failed %s times' % numTries 
                numTries += 1
                print 'now waiting %d secs before trying search again' % (waitTimeLong*numTries)
                time.sleep(waitTimeLong*numTries)
    if numTries == MAXURLTRIES:
        fullText = False
        pmid = False
    return fullText, pmid
    
def get_pubmed_id_from_doi(doi):
    searchLink = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=%s[aid]' % (doi)
    handle = urlopen(searchLink)   
    data = handle.read() 
    xml = XML(data) # convert to an xml object so we can apply x-path search fxns to it
    pmidList = [x.text for x in xml.findall('.//Id')] # find xml "Id" elements
    return pmidList
    
def get_pubmed_id_from_title(titleEncoded):
    queryStrQuoted = quote("(%s)" % titleEncoded, '()')
    searchLink = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=%s' % (queryStrQuoted)
    handle = urlopen(searchLink)   
    data = handle.read() 
    xml = XML(data) # convert to an xml object so we can apply x-path search fxns to it
    pmidList = [x.text for x in xml.findall('.//Id')] # find xml "Id" elements
    return pmidList
    
def get_full_text_from_link_all(queryResultList):
    cnt = 0
    validElsevierIds = []
    failedPubmedGet = []
    for resultDict in queryResultList:
        print '%d of %d articles' % (cnt, len(queryResultList))
        paperAbsUrl = resultDict['link'][0]['@href']
        articleTitle = resultDict['dc:title']
        paperApiUrl = resultDict['prism:url']
        # if no doi, then continue
        if not resultDict.has_key('prism:doi'):
            continue
        elif len(resultDict['prism:doi']) == 0:
            continue
        
        articleDOI = resultDict['prism:doi']
        fullText, pmid = get_full_text_from_link(paperApiUrl, articleTitle, articleDOI)
        if fullText != False and pmid != False:
            record = [pmid, articleTitle, paperAbsUrl]
            validElsevierIds.append(record)
        if fullText != False and pmid == False:
            record = [articleTitle, paperAbsUrl]
            failedPubmedGet.append(record)
        cnt = cnt + 1
    return validElsevierIds, failedPubmedGet

elinkBase = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&id=%d&cmd=prlinks&retmode=ref'    
def get_full_text_from_pmid(pmids):
    cnt = 0
    for pmid in pmids:
        print '%d of %d articles' % (cnt, len(pmids))
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
        print '%d of %d articles' % (cnt, len(diffSet))
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
            print link + ' failed %s times' % numTries 
            numTries += 1
            print 'now waiting %d secs before trying search again' % (waitTimeLong*numTries)
            time.sleep(waitTimeLong*numTries)
            url = ''
    return success    
    


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
            #soup = BeautifulSoup(data)    
            success = True
            time.sleep(waitTimeShort)
        except (URLError, HTTPError, HTMLParseError):
            print link + ' failed %s times' % numTries 
            numTries += 1
            print 'now waiting %d secs before trying search again' % (waitTimeLong*numTries)
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
            print link + ' failed %s times' % numTries 
            numTries += 1
            print 'now waiting %d secs before trying search again' % (waitTimeLong*numTries)
            time.sleep(waitTimeLong*numTries)
    if numTries == MAXURLTRIES:
        soup = False
    return soup
    
def checkPdf(link):
    newLink = re.sub(r'+html', '', link)
    if re.search(r'.pdf', newLink) is not None:
        isPdf = True
    return (isPdf, newLink)