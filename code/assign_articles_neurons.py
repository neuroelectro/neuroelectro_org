# -*- coding: utf-8 -*-
"""
Created on Tue Nov 29 14:12:40 2011

@author: Shreejoy
"""

from pubapp.models import Neuron, Synonym, Article
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
for neuron in Neuron.objects.all():
    # generate a list of terms to check with other articles
    name = neuron.name
    synonyms = Synonym.objects.filter(neuron__name__exact=name)
    termList = [syn.term for syn in synonyms]
    termList.append(name)

    #for each term, find articles which contain term
    articleList = []
    for term in termList:
        containingArts = Article.objects.filter(abstract__icontains=term)
        if len(containingArts) > 500:
            continue
        articleList.extend(containingArts)
    print name
    print 'adding %d articles' % len(articleList)
    [neuron.articles.add(a) for a in articleList]
