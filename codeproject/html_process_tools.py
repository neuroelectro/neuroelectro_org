# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 15:27:21 2012

@author: Shreejoy
"""

from bs4 import BeautifulSoup as bs
from fuzzywuzzy import fuzz, process
import re

sectionList = ['Abstract', 'METHODS', 'RESULTS', 'DISCUSSION', 'REFERENCES', 'Experimental procedures']

def matchSection(sectionStr, sectionList):
    bestStr, matchVal = process.extractOne(sectionStr, sectionList)
    #print bestStr, matchVal
    return bestStr, matchVal
    

def getMethodsTag(fullTextHtml, article):
    soup = bs(fullTextHtml)
    publisher_name = article.get_publisher()
    methodStrTag = 'Methods'
    if publisher_name == 'Highwire':
        matching_tag_name = "h2"
        tag_list = soup.find_all(matching_tag_name)
        matching_tag = getClosestMethodsTag(tag_list, matching_tag_name, soup)
        if matching_tag is None:
            print 'cant find methods tag!'
            return None
        sectionTag = matching_tag.parent.parent
    elif publisher_name == 'Wiley':
        matching_tag_name = "h3"
        tag_list = soup.find_all(matching_tag_name)
        matching_tag = getClosestMethodsTag(tag_list, matching_tag_name, soup)
        if matching_tag is None:
            matching_tag_name = "h2"
            tag_list = soup.find_all(matching_tag_name)
            matching_tag = getClosestMethodsTag(tag_list, matching_tag_name, soup)
            if matching_tag is None:
                print 'cant find methods tag!'
#                 print tag_list
                return None
        sectionTag = matching_tag.parent.parent.parent
    elif publisher_name == 'Elsevier':
        sectionTag = soup.find("ce:section", {"role" : "materials-methods"})
        if sectionTag is None:
            matching_tag_name = "ce:section-title"
            tag_list = soup.find_all(matching_tag_name)
            matching_tag = getClosestMethodsTag(tag_list, matching_tag_name, soup)
            if matching_tag is None:
                print 'cant find methods tag!'
                return None
            sectionTag = matching_tag.parent.parent
    else:
        return None
    return sectionTag
    
def getClosestMethodsTag(tag_list, matching_tag_name, soup):
    methodStrTag = 'Methods'
    tagTexts = [t.text for t in tag_list]
    matching_tag = None
    if len(tagTexts) == 0:
        return None
    bestStr, matchVal = process.extractOne(methodStrTag, tagTexts)
    if matchVal < 70:
        methodStrTag = 'Experimental procedures'
        bestStr, matchVal = process.extractOne(methodStrTag, tagTexts)
        if matchVal < 70:
            return None
    match_tags = soup.find_all(text=bestStr)
    for t in match_tags:
        if t.parent.name == matching_tag_name:
            matching_tag = t
            break
    return matching_tag
    

def getSectionTag(fullTextHtml, sectionStr, article):

    soup = bs(fullTextHtml)
    publisher_name = article.journal.publisher.title
    
    bestStr, matchVal = matchSection(sectionStr, sectionList)
    # print bestStr
    if matchVal < 70:
        print 'Cant match section!'
        return None
    if publisher_name == 'Highwire':
        tags = soup.find_all("h2")
    #    print tags
        tagTexts = [t.text for t in tags]
        bestStr, matchVal = process.extractOne(bestStr, tagTexts)
        sectionTag = soup.find(text=bestStr).parent.parent
    elif publisher_name == 'Wiley':
        tags = soup.find_all("h3")
        tagTexts = [t.text for t in tags]
        bestStr, matchVal = process.extractOne(bestStr, tagTexts)
        match_tags = soup.find_all(text=bestStr)
        for t in match_tags:
            if t.parent.name == 'h3':
                matching_tag = t
                break
        sectionTag = matching_tag.parent.parent.parent
    elif publisher_name == 'Elsevier':
        sectionTag = soup.find("ce:section", {"role" : "materials-methods"})
        if sectionTag is None:
            tags = soup.find_all("ce:section-title")
            tagTexts = [t.text for t in tags]
            bestStr, matchVal = process.extractOne(bestStr, tagTexts)
            match_tags = soup.find_all(text=bestStr)
            for t in match_tags:
                if t.parent.name == 'ce:section-title':
                    matching_tag = t
                    break
            sectionTag = matching_tag.parent.parent
    return sectionTag
#    tagMatches = [process.WRatio(sectionStr,t.text) for t in tags]
#    print t
    #bestStr attrs={'name':re.compile("^description$", re.I)})
#    sectionTag = t.parent
    
    
#    