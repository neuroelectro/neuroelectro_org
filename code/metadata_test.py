# -*- coding: utf-8 -*-
"""
Created on Tue Nov 13 10:06:02 2012

@author: Shreejoy
"""

#import biophysapp.models as m
import neuroelectro.models as m
from bs4 import BeautifulSoup
import re
import nltk
import numpy as np

#articles = m.Article.objects.filter(articlesummary__isnull = False)
#
#a = articles[5]
#
#htmlText = a.articlefulltext_set.all()[0].full_text
#htmlText = re.sub('\n', ' ', htmlText)
#htmlText = re.sub('\(\W+\)', '', htmlText)
#ft = re.sub('\s+', ' ', htmlText)
#soup = BeautifulSoup(''.join(ft))
#text = soup.get_text()
#
#temp_re = re.compile(ur'(\d+)°C\s+' , flags=re.UNICODE)
#
#print temp_re.findall(text)
#
#temp_re = re.compile(ur' age' , flags=re.UNICODE)
#print temp_re.findall(text)
#
#wholeCellSet = set()
#sharpSet = set()

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
celsius_re = re.compile(ur'record.+°C|experiment.+°C', flags=re.UNICODE|re.IGNORECASE)
room_temp_re = re.compile(ur'record.+room\stemp|record.+RT|experiment.+room\stemp|', flags=re.UNICODE|re.IGNORECASE)
for idx, art in enumerate(articles[100:130]):
    ft = art.get_full_text().get_content()
    methods_tag = getMethodsTag(ft, art)
    text = re.sub('\s+', ' ', methods_tag.text)
#    soup = BeautifulSoup(''.join(ft))
#    text = soup.get_text()
    sents = nltk.sent_tokenize(text)
    temp_re = re.compile(ur'record.+room temperature|record.+°C|record.+RT|experiment.+°C' , flags=re.UNICODE)
#    temp_re = re.compile(ur'room temperature|°C' , flags=re.UNICODE)
    for s in sents:
        if celsius_re.findall(s):
            print str(idx) + ' : ' + s.encode("iso-8859-15", "replace")
            degree_ind = s.index(u'°C')
            min_sent_ind = 0
            max_sent_ind = len(s)
            degree_close_str = s[np.minimum(min_sent_ind, degree_ind-20):np.minimum(max_sent_ind, degree_ind+10)]
            print resolveDataFloat(degree_close_str)
    methods_tag = []
            
# find a sentence that mentions P#number
age_re = re.compile(ur'\sP(\d+)|\sp(\d+)|\sage|\days\weeks' , flags=re.UNICODE)
age_re = re.compile(ur'P(\d+)-P(\d+)|P(\d+)-(\d+)|P(\d+)–P(\d+)|P(\d+)–(\d+)|(\d+)-(\d+)\sday|(\d+)–(\d+)\sday|(\d+)-(\d+)\sweek|(\d+)–(\d+)\sweek|(\d+)-(\d+)\smonth|(\d+)–(\d+)\smonth' , flags=re.UNICODE|re.IGNORECASE)
p_age_re = re.compile(ur'P(\d+)-P(\d+)|P(\d+)-(\d+)|P(\d+)–P(\d+)|P(\d+)–(\d+)', flags=re.UNICODE|re.IGNORECASE)
day_re = age_re = re.compile(ur'\sday.old|\sday.old' , flags=re.UNICODE|re.IGNORECASE)
for idx, art in enumerate(articles[0:30]):
    ft = art.get_full_text().get_content()
    methods_tag = getMethodsTag(ft, art)
    text = re.sub('\s+', ' ', methods_tag.text)
    sents = nltk.sent_tokenize(text)
    for s in sents:
        if age_re.findall(s):
            print str(idx) + ' : ' + s.encode("iso-8859-15", "replace")
