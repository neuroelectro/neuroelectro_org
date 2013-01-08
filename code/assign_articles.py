# -*- coding: utf-8 -*-
"""
Created on Tue Nov 29 11:35:47 2011

@author: Shreejoy
"""

from pubapp.models import IonChannel, Synonym, Article
# search all articles which include the term HCN1 in the text
#
#Synonym.objects.filter(IonChannel)
#articles = Article.objects.filter(abstract__icontains='HCN4')
#
#ionChanSyns = Synonym.objects.filter(ionchannel__name__isnull=False)
#[ionChanNames.append(syn.term) for syn in ionChanSyns]
#
#neuronSyns = Synonym.objects.filter(neuron__name__isnull=False)
#
#ionChanNames = []
#[ionChanNames.append(ionChannel.name) for ionChannel in IonChannel.objects.all()]
#
#ionChanSyns = ionChanNames.append(ionChanSyns)

# for each ion channel, find the articles its mentioned in
for ionChannel in IonChannel.objects.all():
    # generate a list of terms to check with other articles
    name = ionChannel.name
    synonyms = Synonym.objects.filter(ionchannel__name__exact=name)
    termList = [syn.term for syn in synonyms]
    termList.append(name)
    
    #for each term, find articles which contain term
    articleList = []
    for term in termList:
        containingArts = Article.objects.filter(abstract__icontains=term)
        articleList.extend(containingArts)
    [ionChannel.articles.add(a) for a in articleList]


    