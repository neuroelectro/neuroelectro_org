# -*- coding: utf-8 -*-
"""
Created on Thu Feb 07 14:13:18 2013

@author: Shreejoy
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Mar 20 09:54:11 2012

@author: Shreejoy
"""


import os
import os.path
import re
import struct
import gc
from matplotlib.pylab import *


from xml.etree.ElementTree import XML
from urllib import quote_plus, quote
from urllib2 import Request, urlopen, URLError, HTTPError
from xml.etree.ElementTree import XML
import json
from pprint import pprint
from bs4 import BeautifulSoup
import time
from HTMLParser import HTMLParseError


def get_full_text_links():
    NUMHITS = 200
    firstInd = 1
    maxURLTries = 5
    waitTime = 10
    #totalArticles = NUMHITS + firstInd + 1 # just set this later when it gets searched
    totalArticles = 56712
    totalArticles = 3694 
    #searchLinkBase = 'http://onlinelibrary.wiley.com/advanced/search/results/reentry?scope=allContent&dateRange=between&inTheLastList=6&startYear=1996&endYear=2013&queryStringEntered=false&searchRowCriteria[0].queryString=neuron+membrane+potential&searchRowCriteria[0].fieldName=all-fields&searchRowCriteria[0].booleanConnector=and&searchRowCriteria[1].fieldName=all-fields&searchRowCriteria[1].booleanConnector=and&searchRowCriteria[2].fieldName=all-fields&searchRowCriteria[2].booleanConnector=and&start=%s&resultsPerPage=%s&ordering=relevancy&publicationFacet=journal' 
    searchLinkBase = 'http://onlinelibrary.wiley.com/advanced/search/results/reentry?scope=allContent&dateRange=between&inTheLastList=6&startYear=1996&endYear=2013&queryStringEntered=false&searchRowCriteria[0].queryString=neuron+membrane+potential&searchRowCriteria[0].fieldName=all-fields&searchRowCriteria[0].booleanConnector=and&searchRowCriteria[1].queryString=European+Journal+of+Neuroscience&searchRowCriteria[1].fieldName=publication-title&searchRowCriteria[1].booleanConnector=or&searchRowCriteria[2].fieldName=all-fields&searchRowCriteria[2].booleanConnector=and&start=%s&resultsPerPage=%s&ordering=relevancy'

    #    'http://jn.physiology.org/search?tmonth=Mar&pubdate_year=&submit=yes&submit=yes&submit=Submit&andorexacttitle=and&format=condensed&firstpage=&fmonth=Jan&title=&tyear=2012'
#    searchLinkBase = 'http://jn.physiology.org/search?tmonth=Mar&pubdate_year=&submit=yes&submit=yes&submit=Submit&andorexacttitle=and&format=condensed&firstpage=&fmonth=Jan&title=&tyear=2012&hits=' + str(NUMHITS) + '&titleabstract=&flag=&journalcode=jn&volume=&sortspec=date&andorexacttitleabs=and&author2=&andorexactfulltext=and&author1=&fyear=1997&doi=&fulltext=%22input%20resistance%22%20AND%20neuron&FIRSTINDEX=' + str(firstInd)
    fullTextLinks = []
    pdfLinks = []
    while firstInd + NUMHITS <= totalArticles:
        print 'searching %d of %d articles' % (firstInd, totalArticles)
        try:
    #        searchLinkFull = 'http://jn.physiology.org/search?tmonth=Mar&pubdate_year=&submit=yes&submit=yes&submit=Submit&andorexacttitle=and&format=condensed&firstpage=&fmonth=Jan&title=&tyear=2012&hits=' + str(NUMHITS) + '&titleabstract=&flag=&journalcode=jn&volume=&sortspec=date&andorexacttitleabs=and&author2=&andorexactfulltext=and&author1=&fyear=1997&doi=&fulltext=%22input%20resistance%22%20AND%20neuron&FIRSTINDEX=' + str(firstInd)
    #        searchLinkFull = 'http://www.jneurosci.org/search?tmonth=Mar&pubdate_year=&submit=yes&submit=yes&submit=Submit&andorexacttitle=and&format=condensed&firstpage=&fmonth=Jan&title=&tyear=2012&hits=' + str(NUMHITS) + '&titleabstract=&volume=&sortspec=date&andorexacttitleabs=and&author2=&tocsectionid=all&andorexactfulltext=and&author1=&fyear=1997&doi=&fulltext=input%20resistance%20neuron&FIRSTINDEX=' + str(firstInd)       
            searchLinkFull = searchLinkBase % (firstInd, NUMHITS)            
            handle = urlopen(searchLinkFull) # open the url
            data = handle.read() # read the data
            soup = BeautifulSoup(data)
            

        except Exception, e:
            print 'skipping'
            print e
            continue
            
        for link in soup.find_all('a'):
        #    print link.get('rel')
            if link.string == 'Full Article (HTML)':
                currLink = link.get('href')
                # do a check to see if 
                pmid = get_pmid_from_doi(currLink)
                if len(pmid) == 1:
                    fullTextLinks.append((currLink, pmid[0]))
        firstInd += NUMHITS
        print 'now waiting %d secs before next search' % waitTime
        time.sleep(waitTime)
    return fullTextLinks
    
MAXURLTRIES = 2

def get_full_text_from_link(fullTextLink, pmid):
    os.chdir('C:\Users\Shreejoy\Desktop\wiley_html') 

    # actually try to get full text
    success = False
    numTries = 0
    waitTimeLong = .5
    waitTimeShort = 2
    link = 'http://onlinelibrary.wiley.com' + fullTextLink
    request = Request(link)
    while numTries < MAXURLTRIES and success == False: 
        try:
            
            fullText = urlopen(request).read()
            #print 'file opened successfully'
            # fullText get succeeded!
            soup = BeautifulSoup(fullText)
            fullTextTag = soup.find(id = "fulltext")
            accessDeniedTag = soup.find(id = "accessDenied")
            if accessDeniedTag is None:
                titleTag = soup.find(id="articleTitle")
                articleTitle = titleTag.h1.text
                titleEncoded = articleTitle.encode("iso-8859-15", "replace") 
                # save full text to a file
                fileName = make_html_filename(titleEncoded, pmid)
                if os.path.isfile(fileName):
                    print 'found identical file'
                    pass
                else:
                    # file doesn't exist
                    f = open(fileName, 'wb')
                    f.write(str(fullTextTag))
                    f.close()
                    print 'found unique file'
                success = True
                time.sleep(waitTimeShort)
            else:
                print 'access denied to full text'
                print link
                # full text not available for some reason
                break

        except Exception, e:
            print e
#            if e.code == 403:
#                #print '%s failed cause access restricted' % (articleTitle)
#                fullText = False
#                pmid = False
#                break
#            else:
            print link + ' failed %s times' % numTries 
            numTries += 1
            print 'now waiting %d secs before trying search again' % (waitTimeLong*numTries)
            time.sleep(waitTimeLong*numTries)
    if numTries == MAXURLTRIES:
        fullText = False
        pmid = False
    
def get_full_text_from_link_all(fullTextLinkListTuple):
    cnt = 0
    for fullTextLinkList in fullTextLinkListTuple:
        print '%d of %d articles' % (cnt, len(fullTextLinkListTuple))
        link = fullTextLinkList[0]
        pmid = fullTextLinkList[1]
        get_full_text_from_link(link, pmid)
        cnt += 1

MAXURLTRIES = 2
MAXTITLELEN = 100
def make_html_filename(title, pmid):
    title = '%s_%s' % (pmid, title)
    title = re.sub('\s', '_', title)
    pattern = '[a-zA-Z0-9_]'
    title = ''.join(re.findall(pattern, title))
    fileName = title[0:min(MAXTITLELEN, len(title))]
    fileName = fileName + '.html'    
    return fileName
    
def get_pmid_from_doi(doiStr):
    doiSearchStr = re.sub('/doi/', '', doiStr)
    doiSearchStr = re.sub('/full', '', doiSearchStr)
    searchLink = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=%s[aid]' % (doiSearchStr)
    try:
        handle = urlopen(searchLink)   
        data = handle.read() 
        xml = XML(data) # convert to an xml object so we can apply x-path search fxns to it
        pmidList = [x.text for x in xml.findall('.//Id')] # find xml "Id" elements
        if len(pmidList) > 1:
            pmidList = []
    except Exception, e:
        pmidList = []
    return pmidList
    
def get_pubmed_id_from_doi(doi):
    searchLink = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=%s[aid]' % (doi)
    handle = urlopen(searchLink)   
    data = handle.read() 
    xml = XML(data) # convert to an xml object so we can apply x-path search fxns to it
    pmidList = [x.text for x in xml.findall('.//Id')] # find xml "Id" elements
    return pmidList

        
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