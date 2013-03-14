# -*- coding: utf-8 -*-
"""
Created on Tue Nov 13 10:06:02 2012

@author: Shreejoy
"""

import biophysapp.models as m
from bs4 import BeautifulSoup
import re
import nltk

articles = m.Article.objects.filter(articlesummary__isnull = False)

a = articles[5]

htmlText = a.articlefulltext_set.all()[0].full_text
htmlText = re.sub('\n', ' ', htmlText)
htmlText = re.sub('\(\W+\)', '', htmlText)
ft = re.sub('\s+', ' ', htmlText)
soup = BeautifulSoup(''.join(ft))
text = soup.get_text()

temp_re = re.compile(ur'(\d+)°C\s+' , flags=re.UNICODE)

print temp_re.findall(text)

temp_re = re.compile(ur' age' , flags=re.UNICODE)
print temp_re.findall(text)

wholeCellSet = set()
sharpSet = set()

whole_re = re.compile(ur'whole\scell|whole-cell|patch\sclamp|patch-clamp' , flags=re.UNICODE)
sharp_re = re.compile(ur'sharp.+electro' , flags=re.UNICODE)
for idx, art in enumerate(articles):
    ft = art.articlefulltext_set.all()[0].full_text
    methods_tag = getSectionTag(ft, 'METHODS')
    text = re.sub('\s+', ' ', methods_tag.text)
#    soup = BeautifulSoup(''.join(ft))
#    text = soup.get_text()
    sents = nltk.sent_tokenize(text)
    for s in sents:
        if whole_re.findall(s):
            wholeCellSet.add(art)
            print 'whole: ' + art.title
            print str(idx) + ' : ' + s.encode("iso-8859-15", "replace")
        if sharp_re.findall(s):
            sharpSet.add(art)
            print 'sharp: ' + art.title
            print str(idx) + ' : ' + s.encode("iso-8859-15", "replace")
            
# find a sentence that mentions recording and temperature or degree celsius
for idx, art in enumerate(articles):
    ft = art.articlefulltext_set.all()[0].full_text
    methods_tag = getSectionTag(ft, 'METHODS')
    text = re.sub('\s+', ' ', methods_tag.text)
#    soup = BeautifulSoup(''.join(ft))
#    text = soup.get_text()
    sents = nltk.sent_tokenize(text)
#    temp_re = re.compile(ur'recording.+room temperature|recording.+°C' , flags=re.UNICODE)
    temp_re = re.compile(ur'room temperature|°C' , flags=re.UNICODE)
    for s in sents:
        if temp_re.findall(s):
            print str(idx) + ' : ' + s.encode("iso-8859-15", "replace")
    methods_tag = []
            
# find a sentence that mentions P#number
age_re = re.compile(ur'\sP(\d+)|\sp(\d+)|\sage|\days\weeks' , flags=re.UNICODE)
for idx, art in enumerate(articles):
    ft = art.articlefulltext_set.all()[0].full_text
    methods_tag = getSectionTag(ft, 'METHODS')
    text = re.sub('\s+', ' ', methods_tag.text)
    sents = nltk.sent_tokenize(text)
    for s in sents:
        if age_re.findall(s):
            print str(idx) + ' : ' + s.encode("iso-8859-15", "replace")
