# -*- coding: utf-8 -*-
"""
Created on Fri Jun 08 12:52:43 2012

@author: Shreejoy
"""

def getAbbrevDict(soupOb):
    # extract out all citations - this fcks up the abbrev editor
    refTags = soupOb.find_all("a", {"class" : "xref-bibr"})
    for r in refTags:
        r.string = ""
        
    # write a regex to extract out ( )'s thaat have no word chars
    htmlText = soupOb.text
    htmlText = re.sub('\n', ' ', htmlText)
    htmlText = re.sub('\(\W+\)', '', htmlText)
    htmlText = re.sub('\s+', ' ', htmlText)
    sents = nltk.sent_tokenize(htmlText)
    abrOb = ExtractAbbrev()
    
    #abrOb.extractabbrpairs(sents[0])
    #abrOb.extractabbrpairs(sents[1])
    #abrOb.extractabbrpairs(sents[4])
    #abrOb.extractabbrpairs(sents[5])
    
    for s in sents:
    #    print s.encode("iso-8859-15", "replace")
        abrOb.extractabbrpairs(s)
    return abrOb.abbrevdict, abrOb