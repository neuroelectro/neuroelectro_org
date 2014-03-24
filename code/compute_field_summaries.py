# -*- coding: utf-8 -*-
"""
Created on Thu Sep 06 17:09:00 2012

@author: Shreejoy
"""

import numpy
from neuroelectro.models import Article, MeshTerm, Substance, Journal
from neuroelectro.models import Neuron, NeuronSyn, Unit, ArticleMetaDataMap
from neuroelectro.models import BrainRegion, InSituExpt, Protein, RegionExpr
from neuroelectro.models import DataTable, ArticleFullText, EphysConceptMap, MetaData
from neuroelectro.models import EphysProp, EphysPropSyn, NeuronArticleMap, get_robot_user
from neuroelectro.models import NeuronConceptMap, NeuronArticleMap, NeuronEphysDataMap
from neuroelectro.models import ArticleSummary, NeuronSummary, EphysPropSummary, NeuronEphysSummary
from neurotree.neuroelectro_integration import define_ephys_grandfathers
from neurotree.author_search import get_article_last_author, get_neurotree_author

from django.db.models import Count, Min, Q
from get_ephys_data_vals_all import filterNedm
import re
import numpy as np
import csv
import nltk

def computeArticleSummaries():
#    articles = Article.objects.filter(articlefulltext__isnull = False, datatable__datasource__neuronconceptmap__isnull = False)
    articles = Article.objects.filter(Q(datatable__datasource__neuronconceptmap__times_validated__gte = 1,
                                        datatable__datasource__neuronephysdatamap__isnull = False) | 
                                        Q(usersubmission__datasource__neuronconceptmap__times_validated__gte = 1,
                                          datatable__datasource__neuronephysdatamap__isnull = False)).distinct()
    articles = articles.filter(articlefulltext__articlefulltextstat__metadata_human_assigned = True ).distinct()
    
    for article in articles:
        nedm_count = NeuronEphysDataMap.objects.filter(source__data_table__article = article).distinct().count()
        nedm_count += NeuronEphysDataMap.objects.filter(source__user_submission__article = article).distinct().count()
        neuron_count = Neuron.objects.filter(neuronconceptmap__source__data_table__article = article).distinct().count()
        neuron_count += Neuron.objects.filter(neuronconceptmap__source__user_submission__article = article).distinct().count()
        #print article.__dict__.keys()
#        author_list = []
#        for author in article.authors.all():
#            curr_author_str = '%s %s' % (author.last, author.initials)
#            author_list.append(curr_author_str)
#            author_list_str = '; '.join(author_list)    
#        author_list_str = author_list_str[0:min(len(author_list_str), 500)]
        asOb = ArticleSummary.objects.get_or_create(article=article, num_nedms = nedm_count,
                                                    num_neurons = neuron_count)[0]
                                                    
def computeArticleSummary(articleQuerySet):
    articleQuerySet = articleQuerySet.annotate(num_nedms =  Count('datatable__datasource__neuronephysdatamap', distinct = True))
    articleQuerySet = articleQuerySet.annotate(num_neurons =  Count('datatable__datasource__neuronconceptmap__neuron', distinct = True))
    article = articleQuerySet[0]
    asOb = ArticleSummary.objects.get_or_create(article=article, num_nedms = article.num_nedms,
                                                num_neurons = article.num_neurons)[0]
    return asOb
    
                                                    
def computeNeuronSummaries():
    neurons = Neuron.objects.all()
    nedmsValid = NeuronEphysDataMap.objects.filter(neuron_concept_map__times_validated__gte = 1, ephys_concept_map__times_validated__gte = 1).distinct()
    for n in neurons:
        neuronNedms = nedmsValid.filter(neuron_concept_map__neuron = n).distinct()
        numNedms = neuronNedms.count()
        articles = Article.objects.filter(datatable__datasource__neuronconceptmap__times_validated__gte = 1, 
                                          datatable__datasource__neuronephysdatamap__isnull = False,
                                          datatable__datasource__neuronconceptmap__neuron = n).distinct()
        articleCount = articles.count()
        print [articleCount, numNedms]
        articles = Article.objects.filter(usersubmission__datasource__neuronconceptmap__times_validated__gte = 1, usersubmission__datasource__neuronconceptmap__neuron = n).distinct()
        articleCount += articles.count()
        print [articleCount, numNedms]
        nsOb = NeuronSummary.objects.get_or_create(neuron = n)[0]
        nsOb.num_nedms = numNedms
        nsOb.num_articles = articleCount  
        nsOb.save()

def computeSingleNeuronSummary(neuron):
    n = neuron
    neuronNedms = NeuronEphysDataMap.objects.filter(neuron_concept_map__neuron = n, neuron_concept_map__times_validated__gte = 1, ephys_concept_map__times_validated__gte = 1).distinct()
    numNedms = neuronNedms.count()
    articles = Article.objects.filter(Q(datatable__datasource__neuronconceptmap__times_validated__gte = 1,
                                        datatable__datasource__neuronephysdatamap__isnull = False) | 
                                        Q(usersubmission__datasource__neuronconceptmap__times_validated__gte = 1)).distinct()
    articles = articles.filter(articlefulltext__articlefulltextstat__metadata_human_assigned = True ).distinct()
    #articles = Article.objects.filter(datatable__datasource__neuronconceptmap__times_validated__gte = 1, datatable__datasource__neuronconceptmap__neuron = n)
    articleCount = articles.count()
#    print [articleCount, numNedms]
    nsOb = NeuronSummary.objects.get_or_create(neuron = n)[0]
    nsOb.num_nedms = numNedms
    nsOb.num_articles = articleCount  
    nsOb.save()
        
def computeEphysPropSummaries():
    ephys_props = EphysProp.objects.all()
    nedmsValid = NeuronEphysDataMap.objects.filter(neuron_concept_map__times_validated__gte = 1, ephys_concept_map__times_validated__gte = 1).distinct()
    for e in ephys_props:
        ephysNedms = nedmsValid.filter(ephys_concept_map__ephys_prop = e).distinct()
        numNedms = ephysNedms.count()
        ncms = NeuronConceptMap.objects.filter(neuronephysdatamap__in = ephysNedms)
        neurons = Neuron.objects.filter(neuronconceptmap__in = ncms).distinct()
        numUniqueNeurons = neurons.count() 
        articles = Article.objects.filter(datatable__datasource__ephysconceptmap__times_validated__gte = 1, datatable__datasource__ephysconceptmap__ephys_prop = e).distinct()
        articleCount = articles.count()
        print [articleCount, numNedms]
        esOb = EphysPropSummary.objects.get_or_create(ephys_prop = e)[0]
        esOb.num_articles = articleCount
        esOb.num_neurons = numUniqueNeurons
        esOb.num_nedms = numNedms
        esOb.save()  
            
def computeNeuronEphysSummariesAll():
    neurons = Neuron.objects.all()
    ephys_props = EphysProp.objects.all()
    nedms = NeuronEphysDataMap.objects.filter(val_norm__isnull = False)
    for n in neurons:
        for e in ephys_props:
            curr_nedms = nedms.filter(neuron_concept_map__neuron = n, ephys_concept_map__ephys_prop = e)
            if curr_nedms.count() == 0:
                continue
            curr_articles = Article.objects.filter(Q(datatable__datasource__neuronconceptmap__neuronephysdatamap__in = curr_nedms,
                                                     datatable__datasource__neuronconceptmap__times_validated__gte = 1) | 
                                                     Q(usersubmission__datasource__neuronconceptmap__neuronephysdatamap__in = curr_nedms)).distinct()
            num_articles = curr_articles.count()
            num_nedms = curr_nedms.count()
            curr_value_list = []
            for a in curr_articles:
                art_nedms = curr_nedms.filter(Q(ephys_concept_map__source__data_table__article = a, 
                                                neuron_concept_map__times_validated__gte = 1) | 
                                                Q(ephys_concept_map__source__user_submission__article = a)).distinct()
                if art_nedms.count() == 0:
                    continue
                art_values = [nedm.val_norm for nedm in art_nedms]
                art_value_mean = np.mean(art_values)
                curr_value_list.append(art_value_mean)
            if len(curr_value_list) == 0:
                continue
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
            
def computeNeuronEphysSummary(neuronconceptmaps, ephysconceptmaps, nedmObs):
    neurons = Neuron.objects.filter(neuronconceptmap__in = neuronconceptmaps)
    ephys_props = EphysProp.objects.filter(ephysconceptmap__in = ephysconceptmaps)
    for nedm in nedmObs:
        value = normalize_nedm_val(nedm)
        if value != None:
            nedm.val_norm = value
            nedm.save()
    for n in neurons:
        for e in ephys_props:
            curr_nedms = nedmObs.filter(neuron_concept_map__neuron = n, ephys_concept_map__ephys_prop = e)
            if curr_nedms.count() == 0:
                continue
            curr_articles = Article.objects.filter(Q(datatable__datasource__neuronconceptmap__neuronephysdatamap__in = curr_nedms,
                                                     datatable__datasource__neuronconceptmap__times_validated__gte = 1) | 
                                                     Q(usersubmission__datasource__neuronconceptmap__neuronephysdatamap__in = curr_nedms)).distinct()
            num_articles = curr_articles.count()
            num_nedms = curr_nedms.count()
            curr_value_list = []
            for a in curr_articles:
                art_nedms = curr_nedms.filter(source__data_table__article = a)
                art_values = []
                for nedm in art_nedms:
                    if nedm.val_norm:
                        art_values.append(nedm.val_norm)
                if len(art_values) > 0:
                    print art_values
                    art_value_mean = np.mean(art_values)
                    curr_value_list.append(art_value_mean)
            #print curr_value_list
            nes = NeuronEphysSummary.objects.get_or_create(ephys_prop = e, neuron = n)[0]
            if len(curr_value_list) > 0:
                value_mean = np.mean(curr_value_list)
                value_sd = np.std(curr_value_list)
                nes.value_mean = value_mean
                nes.value_sd = value_sd    
            #print [n, e, value_mean, value_sd]
            nes.num_nedms = num_nedms
            nes.num_articles = num_articles                                                           
            nes.save()
        computeSingleNeuronSummary(n)
                                                    
def computeEphysPropValueSummaries():
    ephys_props = EphysProp.objects.all()
    for e in ephys_props:
        eps = EphysPropSummary.objects.get(ephys_prop = e)
        neuron_means = [nes.value_mean for nes in NeuronEphysSummary.objects.filter(ephys_prop = e)]
        neuron_means = filter(None, neuron_means)
        if len(neuron_means) > 0:
            eps.value_mean_neurons = np.mean(neuron_means)
            eps.value_sd_neurons = np.std(neuron_means)
        nedms = NeuronEphysDataMap.objects.filter(val_norm__isnull = False, ephys_concept_map__ephys_prop = e)
        if nedms.count() > 0:
            article_values = [nedm.val_norm for nedm in nedms]
            article_values = filter(None, article_values)
            eps.value_mean_articles = np.mean(article_values)
            eps.value_sd_articles = np.std(article_values)   
        eps.save()
        
def computeArticleNedmSummary(pmid, neuron, ephys_prop):
    nedms = NeuronEphysDataMap.objects.filter(Q(val_norm__isnull = False) & 
                                        Q(ephys_concept_map__ephys_prop = ephys_prop) &
                                        Q(neuron_concept_map__neuron = neuron) & 
                                        ( Q(neuron_concept_map__source__data_table__article__pmid = pmid) |
                                        Q(neuron_concept_map__source__user_submission__article__pmid = pmid)
                                        )).distinct()
    val_list = []
    if nedms.count() > 0:
        [val_list.append(nedm.val_norm) for nedm in nedms]
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
    
def computeAllNeuronMeanData():
    neurons = Neuron.objects.all()
    ephys_list = EphysProp.objects.all()
    ephys_list_str = [e.name for e in ephys_list]
    table = np.zeros([350, len(ephys_list)])
    #valid_nedms = NeuronEphysDataMap.objects.filter(val_norm__isnull = False)
    valid_articles = Article.objects.filter(datatable__datasource__neuronconceptmap__neuronephysdatamap__val_norm__isnull = False)
    pmid_list_all = []
    neuron_name_list = []
    full_text_links = []
    article_cnt = 0
    for n in neurons:
        article_list = valid_articles.filter(datatable__datasource__neuronconceptmap__neuron__in = [n]).distinct()
        pmid_list = [a.pmid for a in article_list]
        if len(pmid_list) == 0:
            continue
        #print pmid_list
        for i,pmid in enumerate(pmid_list):
            neuron_name_list.append(n.name)
            for j,e in enumerate(ephys_list):
                table[article_cnt,j] = computeArticleNedmSummary(pmid, n, e)
            article_cnt += 1
            pmid_list_all.append(pmid)
            full_text_links.append(Article.objects.filter(pmid = pmid)[0].full_text_link)
#        pmid_list_all.append(pmid_list)
    return table, pmid_list_all, ephys_list_str, neuron_name_list, full_text_links
        
def getAllArticleNedmMetadataSummary():
    
    articles = Article.objects.filter(Q(datatable__datasource__neuronconceptmap__times_validated__gte = 1) | 
        Q(usersubmission__datasource__neuronconceptmap__times_validated__gte = 1)).distinct()
    articles = articles.filter(articlefulltext__articlefulltextstat__metadata_human_assigned = True ).distinct()
    nom_vars = ['Species', 'Strain', 'ElectrodeType', 'PrepType', 'JxnPotential']
    cont_vars  = ['JxnOffset', 'RecTemp', 'AnimalAge', 'AnimalWeight']
    cont_var_headers = ['JxnOffset', 'Temp', 'Age', 'Weight']
    num_nom_vars = len(nom_vars)
    #ephys_use_pks = [2, 3, 4, 5, 6, 7]
    #ephys_headers = ['ir', 'rmp', 'tau', 'amp', 'hw', 'thresh']
    ephys_use_pks = range(1,28)

    ephys_list = EphysProp.objects.filter(pk__in = ephys_use_pks)
    ephys_headers = []
    for e in ephys_list:
        ephys_name_str = e.name
        ephys_name_str = ephys_name_str.title()
        ephys_name_str = ephys_name_str.replace(' ', '')
        ephys_name_str = ephys_name_str.replace('-', '')
        ephys_headers.append(ephys_name_str)

    #ephys_headers = [e.name for e in ephys_list]
#    metadata_table = []
#    metadata_table_nom = np.zeros([len(articles), len(nom_vars)])
#    metadata_table_nom = np.zeros([len(articles), len(cont_vars)])
    csvout = csv.writer(open("article_ephys_metadata_summary.csv", "wb"))
    
    
    #metadata_headers = ["Species", "Strain", "ElectrodeType", "PrepType", "Temp", "Age", "Weight"]
    metadata_headers = nom_vars + cont_var_headers
    other_headers = ['NeuronType', 'Title', 'PubYear', 'PubmedLink', 'DataTableLinks', 'ArticleDataLink', 'LastAuthor']
    all_headers = ephys_headers
    all_headers.extend(metadata_headers)
    all_headers.extend(other_headers)
    pubmed_base_link_str = 'http://www.ncbi.nlm.nih.gov/pubmed/%d/'
    table_base_link_str = 'http://neuroelectro.org/data_table/%d/'
    article_base_link_str = 'http://neuroelectro.org/article/%d/'

    csvout.writerow(all_headers)
    for j,a in enumerate(articles):
        amdms = ArticleMetaDataMap.objects.filter(article = a)
        curr_metadata_list = ['']*(len(nom_vars) + len(cont_vars))
        for i,v in enumerate(nom_vars):
            valid_vars = amdms.filter(metadata__name = v)
            temp_metadata_list = [vv.metadata.value for vv in valid_vars]
            if 'in vitro' in temp_metadata_list and 'cell culture' in temp_metadata_list:
                curr_metadata_list[i] = 'cell culture'
            elif v == 'Strain' and amdms.filter(metadata__value = 'Mice').count() > 0:
                 temp_metadata_list = 'C57BL'
                 curr_metadata_list[i] = 'C57BL'
            elif v == 'Strain' and amdms.filter(metadata__value = 'Guinea Pigs').count() > 0:
                 temp_metadata_list = 'Guinea Pigs'
                 curr_metadata_list[i] = 'Guinea Pigs'
            elif len(temp_metadata_list) == 0 and v == 'Strain':
                if amdms.filter(metadata__value = 'Rats').count() > 0:
                    if np.random.randn(1)[0] > 0:
                        curr_metadata_list[i] = 'Sprague-Dawley'
                    else:
                        curr_metadata_list[i] = 'Wistar'
            elif len(temp_metadata_list) > 1: 
                 temp_metadata_list = temp_metadata_list[0]
                 curr_metadata_list[i] = temp_metadata_list
            else:
                curr_metadata_list[i] = u'; '.join(temp_metadata_list)
        for i,v in enumerate(cont_vars):
            valid_vars = amdms.filter(metadata__name = v)
            if valid_vars.count() > 0:
                cont_value_ob = valid_vars[0].metadata.cont_value.mean
    #                curr_str = cont_value_ob
                curr_metadata_list[i+num_nom_vars] = cont_value_ob
            else:
                # check if 
                if v == 'RecTemp' and amdms.filter(metadata__value = 'in vivo').count() > 0:
                    curr_metadata_list[i+num_nom_vars] = 37.0
                else:
                    curr_metadata_list[i+num_nom_vars] = 'NaN'
                    
        neurons = Neuron.objects.filter(Q(neuronconceptmap__times_validated__gte = 1) & 
            ( Q(neuronconceptmap__source__data_table__article = a) | Q(neuronconceptmap__source__user_submission__article = a))).distinct()
            
        
        pmid = a.pmid    
        pubmed_link_str = pubmed_base_link_str % a.pmid
        article_link_str = article_base_link_str % a.pk
        dts = DataTable.objects.filter(article = a, datasource__neuronconceptmap__times_validated__gte = 1).distinct()
        if dts.count() > 0:
            dt_link_list = [table_base_link_str % dt.pk for dt in dts] 
            dt_link_str = u'; '.join(dt_link_list)
        else:
            dt_link_str = ''  
        
        #grandfather = define_ephys_grandfather(a)   
        # grandfather = None
        # if grandfather is not None:
        #     grandfather_name = grandfather.lastname
        #     grandfather_name = grandfather_name.encode("iso-8859-15", "replace")
        # else:
        #     grandfather_name = ''
        last_author = get_article_last_author(a)
        if last_author is not None:
            last_author_name = '%s %s' % (last_author.last, last_author.initials)
            last_author_name = last_author_name.encode("iso-8859-15", "replace")
            # if grandfather_name is '':
            #     neuro_tree_node = get_neurotree_author(last_author)
            #     if neuro_tree_node is None:
            #         grandfather_name = 'Node not found'
        else:
            last_author_name = ''
            
        for n in neurons:
            curr_ephys_prop_list = []
            for j,e in enumerate(ephys_list):
                curr_ephys_prop_list.append(computeArticleNedmSummary(pmid, n, e))
        
#            print curr_ephys_prop_list
            curr_ephys_prop_list.extend(curr_metadata_list)
            curr_ephys_prop_list.append(n.name)
            curr_ephys_prop_list.append((a.title).encode("iso-8859-15", "replace"))
            curr_ephys_prop_list.append(a.pub_year)
            curr_ephys_prop_list.append(pubmed_link_str)
            curr_ephys_prop_list.append(dt_link_str)
            curr_ephys_prop_list.append(article_link_str)
            curr_ephys_prop_list.append(last_author_name)
            #curr_ephys_prop_list.append(grandfather_name)
            csvout.writerow(curr_ephys_prop_list)
    return articles
            
def getArticleMetaData():
    articles = Article.objects.filter(datatable__datasource__neuronconceptmap__times_validated__gte = 1).distinct()
    nom_vars = ['Species', 'Strain', 'ElectrodeType', 'PrepType']
    cont_vars  = ['RecTemp', 'AnimalAge', 'AnimalWeight']
    
#    metadata_table = []
#    metadata_table_nom = np.zeros([len(articles), len(nom_vars)])
#    metadata_table_nom = np.zeros([len(articles), len(cont_vars)])
    csvout = csv.writer(open("mydata.csv", "wb"))
    csvout.writerow(("Species", "Strain", "ElectrodeType", "PrepType", "Temp", "Age", "Weight"))
    for j,a in enumerate(articles):
        amdms = ArticleMetaDataMap.objects.filter(article = a)
        curr_metadata_list = [None]*7
        for i,v in enumerate(nom_vars):
            valid_vars = amdms.filter(metadata__name = v)
            temp_metadata_list = [vv.metadata.value for vv in valid_vars]
            curr_metadata_list[i] = u', '.join(temp_metadata_list)
        for i,v in enumerate(cont_vars):
            valid_vars = amdms.filter(metadata__name = v)
            if valid_vars.count() > 0:
                cont_value_ob = valid_vars[0].metadata.cont_value.mean
    #                curr_str = cont_value_ob
                curr_metadata_list[i+4] = cont_value_ob
            else:
                # check if 
                if v == 'RecTemp' and amdms.filter(metadata__value = 'in vivo').count() > 0:
                    curr_metadata_list[i+4] = 37.0
                else:
                    curr_metadata_list[i+4] = 'NaN'
        neurons = Neuron.objects.filter(neuronconceptmap__times_validated__gte = 1, neuronconceptmap__source__data_table__article = a).distinct()
        csvout.writerow(curr_metadata_list)
    return articles
    
def getNeuronTypesInDB():
    articles = Article.objects.filter(Q(datatable__datasource__neuronconceptmap__times_validated__gte = 1) | 
        Q(usersubmission__datasource__neuronconceptmap__times_validated__gte = 1)).distinct()
    articles = articles.filter(articlefulltext__articlefulltextstat__metadata_human_assigned = True ).distinct()
    neurons = Neuron.objects.filter(Q(neuronconceptmap__times_validated__gte = 1) & 
            ( Q(neuronconceptmap__source__data_table__article__in = articles) | Q(neuronconceptmap__source__user_submission__article__in = articles))).distinct()
    neuron_link_base = 'http://neuroelectro.org/neuron/%d/'
    csvout = csv.writer(open("neuron_types_list.csv", "wb"))
    csvout.writerow(("Neuron Type", "NeuroElectro Link", "NeuroElectro ID", "NeuroLex ID"))
    for n in neurons:
        curr_row = [None]*4
        curr_row[0] = n.name
        curr_row[1] = neuron_link_base % n.pk
        curr_row[2] = n.pk
        curr_row[3] = n.nlex_id
        csvout.writerow(curr_row)
        
def count_automated_database_statistics():
    nedmsValid = NeuronEphysDataMap.objects.filter(neuron_concept_map__times_validated__gte = 1, ephys_concept_map__times_validated__gte = 1, neuron_concept_map__source__data_table__isnull = False).distinct()
    articles_automated = Article.objects.filter(datatable__datasource__neuronconceptmap__times_validated__gte = 1).distinct()
    
    robot_user = get_robot_user()
    neurons = Neuron.objects.filter(neuronconceptmap__neuronephysdatamap__in = nedmsValid).distinct()
    
    ecmsNotValid = EphysConceptMap.objects.filter(times_validated = 0).distinct()
    ecms_valid_total = EphysConceptMap.objects.filter(times_validated = 1, source__data_table__isnull = False).distinct()
    ecms_valid_robot = EphysConceptMap.objects.filter(times_validated = 1,added_by = robot_user, source__data_table__isnull = False).distinct()

    ncms_robot_id, ncms_robot_3_id, ncms_datatable_total = count_matching_neuron_mentions()

    stat_dict = {}
    stat_dict['num_neurons'] = neurons.count()

    stat_dict['num_nemds_valid'] = nedmsValid.count()

    stat_dict['num_articles'] = articles_automated.count()

    stat_dict['num_ecms_valid_total'] = ecms_valid_total.count()
    stat_dict['num_ecms_valid_robot'] = ecms_valid_robot.count()
    stat_dict['ncms_datatable_total'] = ncms_datatable_total
    stat_dict['ncms_robot_id'] = ncms_robot_id
    stat_dict['ncms_robot_3_id'] = ncms_robot_3_id
    return stat_dict

    
def count_database_statistics():
    nedmsValid = NeuronEphysDataMap.objects.filter(neuron_concept_map__times_validated__gte = 1, ephys_concept_map__times_validated__gte = 1).distinct()
    nedmsValidUser = NeuronEphysDataMap.objects.filter(neuron_concept_map__times_validated__gte = 1, 
                                                              ephys_concept_map__times_validated__gte = 1,
                                                              neuron_concept_map__source__user_submission__isnull = False).distinct()    
    articles = Article.objects.filter(Q(datatable__datasource__neuronconceptmap__times_validated__gte = 1) | 
        Q(usersubmission__datasource__neuronconceptmap__times_validated__gte = 1)).distinct()
    articles_user_submit = Article.objects.filter(usersubmission__datasource__neuronconceptmap__times_validated__gte = 1).distinct()
    journals = Journal.objects.filter(article__in = articles).distinct()
    robot_user = get_robot_user()
    neurons = Neuron.objects.filter(neuronconceptmap__neuronephysdatamap__in = nedmsValid).distinct()
    ephys_props = EphysProp.objects.filter(ephysconceptmap__neuronephysdatamap__in = nedmsValid).distinct()
    ecmsNotValid = EphysConceptMap.objects.filter(times_validated = 0).distinct()
    articles_not_validated_total = Article.objects.filter(datatable__datasource__ephysconceptmap__in = ecmsNotValid)
    articles_not_validated = articles_not_validated_total.annotate(ecm_count = Count('datatable__datasource__ephysconceptmap'))
    articles_not_validated = articles_not_validated.filter(ecm_count__gte = 4).distinct()
    ecms_valid_total = EphysConceptMap.objects.filter(times_validated = 1).distinct()
    ecms_valid_robot = EphysConceptMap.objects.filter(times_validated = 1,added_by = robot_user).distinct()
    ncms_robot_id, ncms_robot_3_id, ncms_datatable_total = count_matching_neuron_mentions()
    stat_dict = {}
    stat_dict['num_neurons'] = neurons.count()
    stat_dict['num_journals'] = journals.count()
    stat_dict['num_ephys_props'] = ephys_props.count()
    stat_dict['num_nemds_valid'] = nedmsValid.count()
    stat_dict['num_nemds_valid_user'] = nedmsValidUser.count()
    stat_dict['num_articles'] = articles.count()
    stat_dict['num_articles_user_submit'] = articles_user_submit.count()
    stat_dict['num_articles_unvalid'] = articles_not_validated.count()
    stat_dict['num_ecms_valid_total'] = ecms_valid_total.count()
    stat_dict['num_ecms_valid_robot'] = ecms_valid_robot.count()
    stat_dict['ncms_datatable_total'] = ncms_datatable_total
    stat_dict['ncms_robot_id'] = ncms_robot_id
    stat_dict['ncms_robot_3_id'] = ncms_robot_3_id
    return stat_dict
    
def count_matching_neuron_mentions():
    #articles = Article.objects.filter(Q(datatable__datasource__neuronconceptmap__times_validated__gte = 1)).distinct()
    ncms = NeuronConceptMap.objects.filter(times_validated__gte = 1, source__data_table__isnull = False).distinct()
    best_count = 0
    best_three_count = 0
    for ncm in ncms:
        try:
            a = ncm.get_article()
        except Exception:
            print 'no article found'
            continue
        nam = NeuronArticleMap.objects.filter(article = a, neuron = ncm.neuron).order_by('-num_mentions')
        if nam.count() > 0:
            nams = NeuronArticleMap.objects.filter(article = a, num_mentions__gte = nam[0].num_mentions)
            if nams.count() <= 1:
                best_count += 1
            if nams.count() <= 3:
                best_three_count += 1
    return (best_count, best_three_count, ncms.count())
    
def count_metadata_assign_accuracy():
    articles = Article.objects.filter(datatable__datasource__neuronconceptmap__times_validated__gte = 1,
                                      articlefulltext__articlefulltextstat__methods_tag_found = True)
    robot_user = get_robot_user()
    metadata_keys = ['Species', 'Strain', 'ElectrodeType', 'PrepType', 'JxnPotential', 'RecTemp', 'AnimalAge']    
    stat_dict = {}
    for metadata_key in metadata_keys:
        temp_dict = {}
        values_all = ArticleMetaDataMap.objects.filter(metadata__name = metadata_key,article__in=articles).distinct()
        values_robot = ArticleMetaDataMap.objects.filter(metadata__name = metadata_key, article__in = articles, added_by = robot_user).distinct()
        temp_dict['values_all'] = values_all.count()
        temp_dict['values_robot'] = values_robot.count()
        print metadata_key
        print temp_dict
        stat_dict[metadata_key] = temp_dict
    return stat_dict
    
def count_journal_statistics():
    
    NUM_MIN_ECMS = 4
    articles_valid = Article.objects.filter(datatable__datasource__neuronconceptmap__times_validated__gte = 1).distinct()
    articles_all = Article.objects.all()
    
    articles_manual = Article.objects.filter(usersubmission__datasource__neuronconceptmap__times_validated__gte = 1).distinct()
    articles_manual = articles_manual.exclude(id__in=articles_valid)
    
    ecmsNotValid = EphysConceptMap.objects.filter(times_validated = 0).distinct()
    articles_not_validated_total = Article.objects.filter(datatable__datasource__ephysconceptmap__in = ecmsNotValid)
    articles_not_validated = articles_not_validated_total.annotate(ecm_count = Count('datatable__datasource__ephysconceptmap'))
    articles_not_validated = articles_not_validated.filter(ecm_count__gte = NUM_MIN_ECMS).distinct()
    articles_not_validated = articles_not_validated.exclude(id__in=articles_valid)
    articles_not_validated = articles_not_validated.exclude(id__in=articles_manual)
    
    f = open('journal_count_list.csv','wb')
    f.write(u'\ufeff'.encode('utf8'))
    
    journals = Journal.objects.filter(article__in = articles_valid).distinct()
    journal_count_dict = []
    for j in journals:
        valid_count = articles_valid.filter(journal = j).distinct().count()
        all_count = articles_all.filter(journal = j).distinct().count()
        not_valid_count = articles_not_validated.filter(journal = j).distinct().count()
        manual_count = articles_manual.filter(journal = j).distinct().count()
        temp_dict = {'Journal': j.short_title,'Articles': unicode(all_count),
                   'Not validated' : unicode(not_valid_count), 'Validated' : unicode(valid_count), 'Manual': unicode(manual_count)}
        journal_count_dict.append(temp_dict)
    writer = DictWriterEx(f, fieldnames=['Journal','Articles', 'Not validated', 'Validated', 'Manual'])
    writer.writeheader()
    for row in journal_count_dict:
        writer.writerow(dict((k, v.encode('utf-8')) for k, v in row.iteritems()))
    f.close()  
    #journal_count_dict[j.short_title].db_count = all_count
    
def article_validated_list():
    articles = Article.objects.filter(Q(datatable__datasource__neuronconceptmap__times_validated__gte = 1) | 
        Q(usersubmission__datasource__neuronconceptmap__times_validated__gte = 1)).distinct()
    articles = articles.filter(articlesummary__num_nedms__gte = 1)
    articles.order_by('pub_year')
    f = open('article_validated_list.csv','wb')
    f.write(u'\ufeff'.encode('utf8'))
    my_dict = []
    pubmed_base = 'http://www.ncbi.nlm.nih.gov/pubmed/%d'
#    csvout = csv.writer(open("article_validated_list.csv", "wb"))
    for a in articles:
        temp_dict = {'Title': a.title,'Author List': unicode(a.author_list_str),
                   'Journal' : a.journal.short_title, 'Year' : str(a.pub_year), 'PubMed Link' : pubmed_base % a.pmid}
        my_dict.append(temp_dict)
    writer = DictWriterEx(f, fieldnames=['Title','Author List', 'Journal', 'Year', 'PubMed Link'])
    # DictWriter.writeheader() was added in 2.7 (use class above for <= 2.6)
    writer.writeheader()
    for row in my_dict:
        writer.writerow(dict((k, v.encode('utf-8')) for k, v in row.iteritems()))
    f.close()   
    
class DictWriterEx(csv.DictWriter):
    def writeheader(self):
        header = dict(zip(self.fieldnames, self.fieldnames))
        self.writerow(header)
#        curr_row = [None]*4
#        curr_row[0] = a.title
#        curr_row[1] = a.author_list_str
#        curr_row[2] = a.journal.short_title
#        curr_row[3] = a.pub_year
#        csvout.writerow(curr_row)
    
                                
def normalizeNedms():
    nedm_list = NeuronEphysDataMap.objects.all()
    for nedm in nedm_list:
        if nedm.ephys_concept_map.ephys_prop.id in [8, 1, 13, 27]:
            pass
        elif nedm.val_norm:
            continue
        value = normalize_nedm_val(nedm)
        if value != None:
            nedm.val_norm = value
            
        #print [nedm.ephys_concept_map.ephys_prop, nedm.ephys_concept_map.ref_text, nedm.val, nedm.val_norm]
            nedm.save()
    
def normalize_nedm_val(nedm):
#    if nedm.source.data_table.needs_expert == True:
#        return None
    val = nedm.val
    ephys_prop_name = nedm.ephys_concept_map.ephys_prop.name
    if ephys_prop_name == 'resting membrane potential' or nedm.ephys_concept_map.ephys_prop.name == 'spike threshold':
        if val > 0:
            val = -nedm.val
    elif ephys_prop_name == 'spike half-width':
        if val > 10 and val < 100:
            return None
        if val >= 100:
            val = val/1000;
    elif ephys_prop_name == 'input resistance':
        if val < 2:
            val = val * 1000;
    elif ephys_prop_name == 'spike width':
        if val > 20:
            return None 
    elif nedm.ephys_concept_map.ephys_prop.name == 'spike amplitude' or nedm.ephys_concept_map.ephys_prop.name == 'membrane time constant'\
        or nedm.ephys_concept_map.ephys_prop.name == 'spike width':
            if re.search(r'psp', nedm.source.data_table.table_text, re.IGNORECASE) != None \
            or re.search(r'psc', nedm.source.data_table.table_text, re.IGNORECASE) != None \
            and nedm.times_validated == 0:
                #print nedm.data_table.table_text
                return None
    elif ephys_prop_name == 'sag ratio' or ephys_prop_name == 'adaptation ratio':
        ref_text = nedm.ephys_concept_map.ref_text
        toks = nltk.word_tokenize(ref_text)
        not_match_flag = 0
        for tok in toks:
            if tok == '%':
                rep_val = nedm.val
                print '%', ref_text
                not_match_flag = 1
                val = rep_val/100.0
                break
    elif ephys_prop_name == 'cell capacitance':
        ref_text = nedm.ephys_concept_map.ref_text
        toks = nltk.word_tokenize(ref_text)
        not_match_flag = 0
        for tok in toks:
            if tok.lower() == 'pf':
                val = val
                break
            elif tok.lower() == 'nf':
                rep_val = nedm.val
                not_match_flag = 1
                val = rep_val*1000
                break
    elif ephys_prop_name == 'rheobase':
        ref_text = nedm.ephys_concept_map.ref_text
        toks = nltk.word_tokenize(ref_text)
        not_match_flag = 0
        for tok in toks:
            if tok.lower() == 'pa':
                val = val
                break
            elif tok.lower() == 'na':
                rep_val = nedm.val
                not_match_flag = 1
                val = rep_val*1000
                break
    return val
    
def get_neuron_region_assignments():
    neurons = Neuron.objects.filter(neuronconceptmap__times_validated__gte = 1).distinct()
    neuron_region_list = []
    for n in neurons:    
        region_list = n.regions.all()
        region_list_names = [r.name for r in region_list]
        curr_list = [n.name]
        curr_list.extend(region_list_names)
        neuron_region_list.append(curr_list)
    
    with open("neuron_region_assignment.csv", "wb") as f:
        writer = csv.writer(f)
        writer.writerows(neuron_region_list)

        
        

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