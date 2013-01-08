# -*- coding: utf-8 -*-
"""
Created on Sun Nov 20 14:31:40 2011

@author: Shreejoy
"""

import re
# scan through articles and store lists of relevant terms in titles/abstracts

#get a list of articles
articles = Article.objects.filter(terms__term__startswith="Olfactory Bulb")
articles = Article.objects.all()
#find terms in articles that conforms to specific regEx

abstract = articles[8].abstract

regEx = r'[\w(]+v[\d)]+\.\d+'
regExHyphen = regEx + '\-[\w\d.\d]+'

matchList = re.findall(regEx, abstract, re.IGNORECASE)

cnt = 0
for article in articles:
    abstract = article.abstract
    if abstract is None:
        continue
    matchList = re.findall(regExHyphen, abstract, re.IGNORECASE)
    if len(matchList) > 0:
        cnt += 1
        print article
        print matchList
    