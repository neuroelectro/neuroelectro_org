# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 15:27:21 2012

@author: Shreejoy
Modified by: Dmitry
"""

from bs4 import BeautifulSoup as bs
from fuzzywuzzy import process
from HTMLParser import HTMLParser

from ace import database


sectionList = ['Abstract', 'METHODS', 'RESULTS', 'DISCUSSION', 'REFERENCES', 'Experimental procedures']

def matchSection(sectionStr, sectionList):
    bestStr, matchVal = process.extractOne(sectionStr, sectionList)
    #print bestStr, matchVal
    return bestStr, matchVal
    
def getMethodsTag(fullTextHtml, article):

    # attempt to use ACE to identify methods section
    db = database.Database('sqlite')
    publisher_name = article.get_publisher()
    if publisher_name == 'Elsevier':
        publisher_name = 'ScienceDirect'
    if publisher_name == 'Oxford':
        publisher_name = 'Highwire'
    aft = article.get_full_text()
    file_path = aft.full_text_file.path
    sections = db.file_to_sections(file_path, article.pmid, None, publisher_name)
    if u'methods' in sections:
        return bs(sections['methods'], 'lxml')

    # couldn't use ace to identify section, using old way
    soup = bs(fullTextHtml, 'lxml')
    publisher_name = article.get_publisher()
    if publisher_name == 'Highwire':
        matching_tag_name = "h2"
        tag_list = soup.find_all(matching_tag_name)
        matching_tag = getClosestMethodsTag(tag_list, matching_tag_name, soup)
        if matching_tag is None:
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
                return None
        sectionTag = matching_tag.parent.parent.parent
    elif publisher_name == 'Elsevier':
        sectionTag = soup.find("ce:section", {"role" : "materials-methods"})
        if sectionTag is None:
            matching_tag_name = "ce:section-title"
            tag_list = soup.find_all(matching_tag_name)
            matching_tag = getClosestMethodsTag(tag_list, matching_tag_name, soup)
            if matching_tag is None:
                return None
            sectionTag = matching_tag.parent.parent
    elif publisher_name in ['Frontiers', 'PLoS']:
        sectionTag = soup.find("sec", {"sec-type" : "materials and methods"})
        if sectionTag is None:
            sectionTag = soup.find("sec", {"sec-type" : "materials|methods"})
            if sectionTag is None:
                sectionTag = soup.find("sec", {"sec-type" : "methods"})
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
        return None
    if publisher_name == 'Highwire':
        tags = soup.find_all("h2")
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

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()