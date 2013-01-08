# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 15:27:21 2012

@author: Shreejoy
"""

from bs4 import BeautifulSoup as bs
from fuzzywuzzy import fuzz, process
import re

sectionList = ['Abstract', 'METHODS', 'RESULTS', 'DISCUSSION', 'REFERENCES']

def matchSection(sectionStr):
    bestStr, matchVal = process.extractOne(sectionStr, sectionList)
    #print bestStr, matchVal
    return bestStr, matchVal
    


def getSectionTag(fullTextHtml, sectionStr):

    soup = bs(fullTextHtml)
    
    bestStr, matchVal = matchSection(sectionStr)
    # print bestStr
    if matchVal < 70:
        print 'Cant match section!'
        return None
    tags = soup.find_all("h2")
    [process.WRatio(sectionStr,t.text) for t,i in tags]
    print t
    #bestStr attrs={'name':re.compile("^description$", re.I)})
    sectionTag = t.parent
    return sectionTag
    
#    