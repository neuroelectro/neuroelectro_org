# -*- coding: utf-8 -*-
"""
Created on Sun Jun 17 22:29:03 2012

@author: Shreejoy
"""

import re

#os.chdir('C:\Users\Shreejoy\Desktop\Biophysiome')
from neuroelectro.models import Article, MeshTerm, Substance, Journal
from neuroelectro.models import Neuron, NeuronSyn, Unit
from neuroelectro.models import BrainRegion, InSituExpt, Protein, RegionExpr
from neuroelectro.models import DataTable, ArticleFullText, EphysConceptMap
from neuroelectro.models import NeuronArticleMap
#os.chdir('C:\Python27\Scripts\Biophys')

from bs4 import BeautifulSoup as bs

#from ExtractAbbrev import ExtractAbbrev
from find_neurons_in_text import findNeuronsInText, getMostLikelyNeuron
        
def assocNeuronstoArticleMult2():
    #artObs = Article.objects.filter(datatable__ephysconceptmap__isnull = False).distinct()    
    #artObs = Article.objects.filter(datatable__ephysconceptmap__isnull = False, neuronarticlemap__isnull = True).distinct() 
    artObs = Article.objects.filter(neuronarticlemap__isnull = True, articlefulltext__isnull = False).distinct()
    artObs = artObs[0:10]
    #afts = ArticleFullText.objects.filter(article__data_table__ephys_concept_map__isnull = False)
    tot_count = artObs.count()
    #numRes = 23411881#res.count()
    print '%d num total articles' % tot_count
    blockSize = 100
    firstInd = 0
    lastInd = blockSize
    blockCnt = 0
    while firstInd < lastInd:
        print '%d of %d blocks ' % (blockCnt, tot_count/blockSize)
        for artOb in artObs[firstInd:lastInd].iterator():
            assocArticleNeuron(artOb)
        firstInd = lastInd + 1
        lastInd = min(lastInd+blockSize, tot_count)
        blockCnt += 1
        
def assocArticleNeuron(artOb):
    fullTextOb = artOb.articlefulltext_set.all()[0]
    fullTextHtml = fullTextOb.full_text
    soup = bs(''.join(fullTextHtml))
    full_text = soup.get_text()
    neuronTuple = findNeuronsInText(full_text)    
    for t in neuronTuple:
        neuronOb = t[0]
        neuronSynOb = t[1]
        numMentions = t[2]
        neuronArticleMapOb = NeuronArticleMap.objects.get_or_create(neuron = neuronOb,
                                                              neuron_syn = neuronSynOb,
                                                              num_mentions = numMentions,
                                                              article = artOb,
                                                              added_by = 'robot')[0]

# find data tables which do not contain id elements, and if they don't contain them,
# then add some new ones
def addIdsToTable(dataTableOb):
    try:
        soup = bs(dataTableOb.table_html)
    except:
        return
    tdTags = soup.findAll('td')
    if len(soup.find_all(id=True)) == 0:
        print 'adding id tags to table # %d' %dataTableOb.pk
        # contains no id tags, add them
        tdTags = soup.findAll('td')
        cnt = 1
        for tag in tdTags:
            tag['id'] = 'td-%d' % cnt
            cnt += 1
        thTags = soup.findAll('th')
        cnt = 1
        for tag in thTags:
            tag['id'] = 'th-%d' % cnt
            cnt += 1   
        trTags = soup.findAll('tr')
        cnt = 1
        for tag in trTags:
            tag['id'] = 'tr-%d' % cnt
            cnt += 1  
    
    table_html = str(soup)        
    dataTableOb.table_html = table_html    
    dataTableOb.save()
    return dataTableOb
            
def addIdsToTableMult():
    dts = DataTable.objects.all()
    for dt in dts:
        addIdsToTable(dt)

# these are actually just repeats of the above functions
#def assocNeuronstoArticle(fullTextOb):
#    soup =  BeautifulSoup(fullTextOb.full_text)
#    articleText = soup.get_text()
#    neuronList = findNeuronsInText(articleText)
#    articleOb = fullTextOb.article
#    for l in neuronList:
#        (neuronOb, synOb,  numMentions) = l
#        neuronArtMapOb = NeuronArticleMap.objects.get_or_create(neuron = neuronOb,
##                                                                  ephys_prop = ephysPropOb,
#                                                                  neuron_syn = synOb,
#                                                                  num_mentions = numMentions,
#                                                                  article = articleOb,
##                                                                  match_quality = matchVal,
#                                                                  added_by = 'robot')[0]                                                                          
#        
##    print neuronList
#    
#def assocNeuronstoArticleMult(aftObs):
#    cnt = 0    
#    #afts = ArticleFullText.objects.all()
#    tot_count = aftObs.count()
#    for aft in aftObs:
#        cnt = cnt + 1
#        if cnt % 10 == 0:
#            print '%d of %d tables' % (cnt, tot_count)           
#        assocNeuronstoArticle(aft)