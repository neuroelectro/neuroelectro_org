# -*- coding: utf-8 -*-
"""
Created on Sun Jun 17 22:29:03 2012

@author: Shreejoy
"""

import re
import sys

#os.chdir('C:\Users\Shreejoy\Desktop\Biophysiome')
from neuroelectro.models import Article, MeshTerm, Substance, Journal
from neuroelectro.models import Neuron, NeuronSyn, Unit
from neuroelectro.models import BrainRegion, InSituExpt, Protein, RegionExpr
from neuroelectro.models import DataTable, ArticleFullText, EphysConceptMap
from neuroelectro.models import NeuronArticleMap, User, get_robot_user, ArticleFullTextStat
#os.chdir('C:\Python27\Scripts\Biophys')

from bs4 import BeautifulSoup as bs

#from ExtractAbbrev import ExtractAbbrev
from find_neurons_in_text import findNeuronsInText, getMostLikelyNeuron
        
def assocNeuronstoArticleMult2(artObs):
    #artObs = Article.objects.filter(datatable__ephysconceptmap__isnull = False).distinct()    
    #artObs = Article.objects.filter(datatable__ephysconceptmap__isnull = False, neuronarticlemap__isnull = True).distinct() 
    #artObs = Article.objects.filter(neuronarticlemap__isnull = True, articlefulltext__isnull = False).distinct()
    #artObs = artObs[0:10]
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

robot_user = get_robot_user()
def assocArticleNeuron(artOb):
    fullTextOb = artOb.articlefulltext_set.all()[0]
    fullTextHtml = fullTextOb.get_content()
    if fullTextHtml == 'test':
        return
    soup = bs(''.join(fullTextHtml))
    full_text = soup.get_text()
    neuronTuple = findNeuronsInText(full_text)    
    usedNeurons = []
    for t in neuronTuple:
        neuronOb = t[0]
        numMentions = t[2]
        if neuronOb not in usedNeurons and numMentions > 2:
            #neuronSynOb = t[1]
            neuronArticleMapOb = NeuronArticleMap.objects.get_or_create(neuron = neuronOb,
                                                                  num_mentions = numMentions,
                                                                  article = artOb,
                                                                  added_by = robot_user)[0]
            usedNeurons.append(neuronOb)
        else:
            continue
    aftStatOb = ArticleFullTextStat.objects.get_or_create(article_full_text = fullTextOb)[0]
    aftStatOb.neuron_article_map_processed = True
    aftStatOb.save()

# find data tables which do not contain id elements, and if they don't contain them,
# then add some new ones
def addIdsToTable(dataTableOb):
    try:
        soup = bs(dataTableOb.table_html)
    except:
        return
    tdTags = soup.findAll('td')
    if len(soup.find_all(id=True)) < 5:
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
    num_tables = dts.count()
    print 'adding tags to %d tables' % num_tables
    for i,dt in enumerate(dts):
        prog(i, num_tables)
        addIdsToTable(dt)
        
def removeSpuriousFullTexts():
    #artObs = Article.objects.filter(datatable__ephysconceptmap__isnull = False).distinct()    
    #artObs = Article.objects.filter(datatable__ephysconceptmap__isnull = False, neuronarticlemap__isnull = True).distinct() 
    #artObs = Article.objects.filter(neuronarticlemap__isnull = True, articlefulltext__isnull = False).distinct()
    #artObs = artObs[0:10]
    afts = ArticleFullText.objects.all()
    tot_count = afts.count()
    #numRes = 23411881#res.count()
    print '%d num total articles' % tot_count
    blockSize = 100
    firstInd = 0
    lastInd = blockSize
    blockCnt = 0
    while firstInd < lastInd:
        print '%d of %d blocks ' % (blockCnt, tot_count/blockSize)
        for aft in afts[firstInd:lastInd].iterator():
            if aft.full_text == 'test':
                aft.delete()
        firstInd = lastInd + 1
        lastInd = min(lastInd+blockSize, tot_count)
        blockCnt += 1

def prog(num,denom):
    fract = float(num)/denom
    hyphens = int(round(50*fract))
    spaces = int(round(50*(1-fract)))
    sys.stdout.write('\r%.2f%% [%s%s]' % (100*fract,'-'*hyphens,' '*spaces))
    sys.stdout.flush() 
    
def remove_spurious_table_headers(dt):
    try:
        soup = bs(dt.table_html)
    except:
        return None
    tableTags = soup.findAll('table')
    for tableTag in tableTags:
        hasHeaderTag = False
        hasBodyTag = False
        headerTag = tableTag.findAll('thead')
        if len(headerTag) > 0:
            hasHeaderTag = True
        bodyTag = tableTag.findAll('tbody')
        if len(bodyTag) > 0:
            hasBodyTag = True
        if hasHeaderTag == True and hasBodyTag == False:
#            print 'removing weird header from '
#            print dt.article
#            print dt.article.journal
            tableTag.clear()
            table_html = str(soup)        
            dt.table_html = table_html    
            dt.save()
            # check if has any ecms that are assigned to table tags that have been deleted
            ecms = EphysConceptMap.objects.filter(source__data_table = dt)
            num_ecms = ecms.count()
            if num_ecms > 0:
#                print 'has ecms'
                # remove any concept maps associated with these elements
                remove_untagged_datatable_ecms(dt)   
    return dt
    
def remove_spurious_table_headers_all():
    dts = DataTable.objects.filter(article__journal__publisher__title = 'Elsevier')
    num_tables = dts.count()
    print 'checking table validity of %d tables' % num_tables
    for i,dt in enumerate(dts):
        prog(i, num_tables)
        remove_spurious_table_headers(dt)
    
def remove_untagged_datatable_ecms(dt):
    ecms = EphysConceptMap.objects.filter(source__data_table = dt)
    num_ecms = ecms.count()
    if num_ecms > 0:
        try:
            soup = bs(dt.table_html)
        except:
            return None
        #print 'has ecms'
        # remove any concept maps associated with these elements
        for ecm in ecms:
            if ecm.dt_id:
                if len(soup.findAll(id=ecm.dt_id)) == 0:
                    ecm.delete()
                    #print ecm.dt_id
            
            
        
        
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