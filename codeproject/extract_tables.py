# -*- coding: utf-8 -*-
"""
Created on Thu Mar 15 17:48:50 2012

@author: Shreejoy
"""

import re
from bs4 import BeautifulSoup
soup = BeautifulSoup(html_doc)

from xml.etree.ElementTree import XML
from urllib2 import urlopen
from urllib import quote
import nltk

url= 'http://www.jneurosci.org/search?submit=yes&pubdate_year=&volume=&firstpage=&doi=&author1=&author2=&title=&andorexacttitle=and&titleabstract=&andorexacttitleabs=and&fulltext=input+resistance+neuron&andorexactfulltext=and&fmonth=&fyear=&tmonth=&tyear=&tocsectionid=all&format=standard&hits=250&sortspec=relevance&submit=yes&submit=Submit'
url= 'http://www.jneurosci.org/search?submit=yes&fulltext=input+resistance+neuron&andorexactfulltext=and&fmonth=&fyear=&tmonth=&tyear=&tocsectionid=all&format=standard&hits=250&sortspec=relevance&submit=yes&submit=Submit'

handle = urlopen(url) # open the url
data = handle.read() # read the data
soup = BeautifulSoup(data)

for link in soup.find_all('a'):
#    print link.get('rel')
    if link.string == 'Full Text':
        print(link.get('href'))
        
paper_link = 'http://www.jneurosci.org/content/23/27/9123.full?sid=6eeea838-4577-4992-8a81-46ecdda1e2f9'
handle = urlopen(paper_link) # open the url
data = handle.read() # read the data
soup = BeautifulSoup(data)
for link in soup.find_all('a'):
    if link.string == 'In this window':
        print(link.get('href'))
        
table_link = 'http://www.jneurosci.org/content/23/27/9123/T1'
handle = urlopen(table_link) # open the url
data = handle.read() # read the data
soup = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
print(soup.prettify())

t = soup.find(id='table-1')
dat = [ map(str, row.findAll("td")) for row in t.findAll("tr") ]

url= 'http://jn.physiology.org/search?submit=yes&y=7&fulltext=input+resistance+neuron&x=16&format=standard&hits=250&sortspec=relevance&submit=Go'
handle = urlopen(url) # open the url
data = handle.read() # read the data
soup = BeautifulSoup(data)
# get all links to full text docs
linkList  = []
for link in soup.find_all('a'):
#    print link.get('rel')
    if link.string == 'Full Text':
        currLink = link.get('href')
        linkList.append(currLink)
        print(link.get('href'))

journalBase = 'http://jn.physiology.org/'

allTables = []
for currLink in linkList:
    artLink = journalBase + currLink
    handle = urlopen(artLink) # open the url
    data = handle.read() # read the data
    soup = BeautifulSoup(data)
    tableList = []
    for link in soup.find_all('a'):
        linkText = link.get('href')
        if link.string == 'In this window' and linkText.find('T') != -1:
            print(linkText)
            tableList.append(linkText)
    allTables.append(tableList)
    
dataTableList  = []
fullLinkList = []
for i in range(len(allTables)):
    currLink = linkList[i]
    linkPart = re.search('[\d\w/]+.', currLink).group()[1:-1]
    for j in range(len(allTables[i])):
        tableLink = allTables[i][j]
        tablePart = re.search('/T\d', tableLink).group()
        fullLink = journalBase + linkPart + tablePart
        print fullLink
        handle = urlopen(fullLink) # open the url
        data = handle.read() # read the data
        soup = BeautifulSoup(data)
        t = soup.find('table')
        print t
        dataTableList.append(t)
        fullLinkList.append(fullLink)
        
        
        
# to get full text, do a search for div class = "article fulltext-view" itempprop = "articleBody"
