# -*- coding: utf-8 -*-
"""
Created on Wed Jan 18 09:50:08 2012

@author: Shreejoy
"""

import re
from xml.etree.ElementTree import XML
from urllib2 import urlopen
from BeautifulSoup import BeautifulSoup

query = '"ion+channels"[mh]+AND+"neurons"[mh]+AND+("mice"[mh]+OR+"rats"[mh])'

esearch = 'http://channelpedia.epfl.ch'
soup = BeautifulSoup(urlopen(esearch))

channelLinks = soup.findAll('a')[9:-4]

# parse channel links
channelList = []
channelLinkList = []
for link in channelLinks:
    match = re.search(r'>[\w\d\s.-//]+<', str(link)).group()
    channelName = match.strip(r'><')
    channelList.append(channelName)
    match = re.search(r'"[\w\d\s.-//]+"', str(link)).group()
    specLink = match.strip(r'"')
    channelLinkList.append(specLink)
    
channelList = list(set(channelList))

len(set(channelLinkList))

cnt = 0
geneList = []
synList = []
for link in channelLinkList:
    esearch = 'http://channelpedia.epfl.ch'+link
    soup = BeautifulSoup(urlopen(esearch))
    myStr = str(soup.findAll('p')[0])
#    match = re.search(r'Synonyms:[/w/s]+Symbol', myStr)
    match = re.search(r'Synonyms:[\w\d\s\.\-\(\),]+Symbol', myStr)
    if match != None:
        synStr = match.group()
        synStr = re.sub(r'^Synonyms: ', '', synStr)
        synStr = re.sub(r'\. Symbol$', '', synStr)
        synList.append(synStr)
    match = re.search(r'Symbol:[\w\d\s.-]+', myStr)
    if match != None:
        symbolStr = match.group()
        symbolStr = re.sub(r'^Symbol: ', '', symbolStr)
        geneList.append(symbolStr)
    print 'Name: ' + channelList[cnt] + ' Synonyms: ' + synStr
    cnt = cnt + 1