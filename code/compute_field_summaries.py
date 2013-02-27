# -*- coding: utf-8 -*-
"""
Created on Thu Sep 06 17:09:00 2012

@author: Shreejoy
"""

import numpy
from neuroelectro.models import Article, MeshTerm, Substance, Journal
from neuroelectro.models import Neuron, NeuronSyn, Unit
from neuroelectro.models import BrainRegion, InSituExpt, Protein, RegionExpr
from neuroelectro.models import DataTable, ArticleFullText, EphysConceptMap
from neuroelectro.models import EphysProp, EphysPropSyn, NeuronArticleMap
from neuroelectro.models import NeuronConceptMap, NeuronArticleMap, NeuronEphysDataMap
from neuroelectro.models import ArticleSummary, NeuronSummary, EphysPropSummary, NeuronEphysSummary

from django.db.models import Count, Min
from get_ephys_data_vals_all import filterNedm
import re
import numpy as np

def computeArticleSummaries():
    articles = Article.objects.filter(articlefulltext__isnull = False)
    articles = articles.annotate(num_nedms =  Count('datatable__neuronephysdatamap', distinct = True))
    articles = articles.filter(num_nedms__gte = 3)   
    articles = articles.annotate(num_neurons =  Count('datatable__neuronconceptmap__neuron', distinct = True))
    for article in articles:
        #print article.__dict__.keys()
        author_list = []
        for author in article.authors.all():
            curr_author_str = '%s %s' % (author.last, author.initials)
            author_list.append(curr_author_str)
            author_list_str = '; '.join(author_list)    
        author_list_str = author_list_str[0:min(len(author_list_str), 500)]
        asOb = ArticleSummary.objects.get_or_create(article=article, num_nedms = article.num_nedms,
                                                    num_neurons = article.num_neurons, 
                                                    author_list_str = author_list_str)[0]
                                                    
def computeNeuronSummaries():
    neurons = Neuron.objects.all()
    nedmsValid = NeuronEphysDataMap.objects.filter(neuron_concept_map__times_validated__gte = 1, ephys_concept_map__times_validated__gte = 1).distinct()
    for n in neurons:
        neuronNedms = nedmsValid.filter(neuron_concept_map__neuron = n).distinct()
        numNedms = neuronNedms.count()
        articles = Article.objects.filter(datatable__neuronconceptmap__times_validated__gte = 1, datatable__neuronconceptmap__neuron = n)
        articleCount = articles.count()
        print [articleCount, numNedms]
        nsOb = NeuronSummary.objects.get_or_create(neuron = n, num_nedms = numNedms, num_articles = articleCount)[0]    
        
def computeEphysPropSummaries():
    ephys_props = EphysProp.objects.all()
    nedmsValid = NeuronEphysDataMap.objects.filter(neuron_concept_map__times_validated__gte = 1, ephys_concept_map__times_validated__gte = 1).distinct()
    for e in ephys_props:
        ephysNedms = nedmsValid.filter(ephys_concept_map__ephys_prop = e).distinct()
        numNedms = ephysNedms.count()
        ncms = NeuronConceptMap.objects.filter(neuronephysdatamap__in = ephysNedms)
        neurons = Neuron.objects.filter(neuronconceptmap__in = ncms).distinct()
        numUniqueNeurons = neurons.count() 
        articles = Article.objects.filter(datatable__ephysconceptmap__times_validated__gte = 1, datatable__ephysconceptmap__ephys_prop = e)
        articleCount = articles.count()
        print [articleCount, numNedms]
        nsOb = EphysPropSummary.objects.get_or_create(ephys_prop = e, num_nedms = numNedms, num_articles = articleCount,
                                                      num_neurons = numUniqueNeurons)[0]      
    
    
def computeNeuronEphysSummaries():
    neurons = Neuron.objects.all()
    ephys_props = EphysProp.objects.all()
    nedms = NeuronEphysDataMap.objects.filter(val_norm__isnull = False)
    for n in neurons:
        for e in ephys_props:
            curr_nedms = nedms.filter(neuron_concept_map__neuron = n, ephys_concept_map__ephys_prop = e)
            if curr_nedms.count() == 0:
                continue
            curr_articles = Article.objects.filter(datatable__neuronephysdatamap__in = curr_nedms).distinct()
            num_articles = curr_articles.count()
            num_nedms = curr_nedms.count()
            curr_value_list = []
            for a in curr_articles:
                art_nedms = curr_nedms.filter(data_table__article = a)
                art_values = [nedm.val_norm for nedm in art_nedms]
                art_value_mean = np.mean(art_values)
                curr_value_list.append(art_value_mean)
            #print curr_value_list
            value_mean = np.mean(curr_value_list)
            value_sd = np.std(curr_value_list)
            #print [n, e, value_mean, value_sd]
            nes = NeuronEphysSummary.objects.get_or_create(ephys_prop = e, neuron = n)[0]
            nes.num_nedms = num_nedms
            nes.num_articles = num_articles                                    
            nes.value_mean = value_mean
            nes.value_sd = value_sd                                                    
            nes.save()
                                                    
def computeEphysPropValueSummaries():
    ephys_props = EphysProp.objects.all()
    for e in ephys_props:
        eps = EphysPropSummary.objects.get(ephys_prop = e)
        neuron_means = [nes.value_mean for nes in NeuronEphysSummary.objects.filter(ephys_prop = e)]
        if len(neuron_means) > 0:
            eps.value_mean_neurons = np.mean(neuron_means)
            eps.value_sd_neurons = np.std(neuron_means)
        nedms = NeuronEphysDataMap.objects.filter(val_norm__isnull = False, ephys_concept_map__ephys_prop = e)
        if nedms.count() > 0:
            article_values = [nedm.val_norm for nedm in nedms]
            eps.value_mean_articles = np.mean(article_values)
            eps.value_sd_articles = np.std(article_values)   
        eps.save()
        
def computeArticleNedmSummary(pmid, neuron, ephys_prop):
    nedms = NeuronEphysDataMap.objects.filter(val_norm__isnull = False, 
                                        ephys_concept_map__ephys_prop = ephys_prop,
                                        neuron_concept_map__neuron = neuron, 
                                        neuron_concept_map__source__data_table__article__pmid = pmid)
    val_list = []
    if nedms.count() > 0:
        [val_list.append(nedm.val) for nedm in nedms]
    #print val_list
    value = np.mean(val_list)
    value_str = '%.2f' % value
    return value_str
    
def computeCA1MeanData(pmid_list):
    n = Neuron.objects.get(pk = 85)
    article_list = Article.objects.filter(datatable__datasource__neuronconceptmap__neuron = n).distinct()
    #pmid_list = [a.pmid for a in article_list]
    ephys_list = EphysProp.objects.all()
    ephys_list_str = [e.name for e in ephys_list]
    table = np.zeros([len(pmid_list), len(ephys_list)])
    for i,pmid in enumerate(pmid_list):
        for j,e in enumerate(ephys_list):
            table[i,j] = computeArticleNedmSummary(pmid, n, e)
    return table, pmid_list, ephys_list_str
            
                                
def normalizeNedms():
    nedm_list = NeuronEphysDataMap.objects.all()
    for nedm in nedm_list:
        value = normalize_nedm_val(nedm)
        if value != None:
            nedm.val_norm = value
            
        #print [nedm.ephys_concept_map.ephys_prop, nedm.ephys_concept_map.ref_text, nedm.val, nedm.val_norm]
            nedm.save()
    
def normalize_nedm_val(nedm):
    if nedm.data_table.needs_expert == True:
        return None
    val = nedm.val
    if nedm.ephys_concept_map.ephys_prop.name == 'resting membrane potential' or nedm.ephys_concept_map.ephys_prop.name == 'spike threshold':
        if val > 0:
            val = -nedm.val
    elif nedm.ephys_concept_map.ephys_prop.name == 'spike half-width':
        if val > 10 and val < 100:
            return None
        if val >= 100:
            val = val/1000;
    elif nedm.ephys_concept_map.ephys_prop.name == 'input resistance':
        if val < 2:
            val = val * 1000;
    elif nedm.ephys_concept_map.ephys_prop.name == 'spike width':
        if val > 20:
            return None 
    elif nedm.ephys_concept_map.ephys_prop.name == 'spike amplitude' or nedm.ephys_concept_map.ephys_prop.name == 'membrane time constant'\
        or nedm.ephys_concept_map.ephys_prop.name == 'spike width':
            if re.search(r'psp', nedm.data_table.table_text, re.IGNORECASE) != None \
            or re.search(r'psc', nedm.data_table.table_text, re.IGNORECASE) != None \
            and nedm.times_validated == 0:
                #print nedm.data_table.table_text
                return None
    return val

#        n.value_count = numNedms
#    articles = Article.objects.filter(articlefulltext__isnull = False)
#    articles = articles.annotate(num_nedms =  Count('datatable__neuronephysdatamap', distinct = True))
#    articles = articles.filter(num_nedms__gte = 3)   
#    articles = articles.annotate(num_neurons =  Count('datatable__neuronconceptmap__neuron', distinct = True))
#    for article in articles:
#        #print article.__dict__.keys()
#        author_list = []
#        for author in article.authors.all():
#            curr_author_str = '%s %s' % (author.last, author.initials)
#            author_list.append(curr_author_str)
#            author_list_str = '; '.join(author_list)    
#            author_list_str = author_list_str[0:min(len(author_list_str), 500)]
#        asOb = ArticleSummary.objects.get_or_create(article=article, num_nedms = article.num_nedms,
#                                                    num_neurons = article.num_neurons, 
#                                                    author_list_str = author_list_str)[0]