# -*- coding: utf-8 -*-
"""
Created on Thu Sep 06 17:09:00 2012

@author: Shreejoy
"""
import csv

from django.db.models import Count, Q
import numpy as np

from db_functions.normalize_ephys_data import normalize_nedm_val
import neuroelectro.models as m

# TODO: remove neurotree references here
from db_functions.update_data_table_stats import update_data_table_stat
from neuroelectro import models as m
from helpful_functions.prog import prog


def computeArticleSummaries(*args):
    if args:
        articles = args
    else:
        articles = m.Article.objects.filter(Q(datatable__datasource__neuronconceptmap__times_validated__gte = 1,
                                            datatable__datasource__neuronephysdatamap__isnull = False) | 
                                            Q(usersubmission__datasource__neuronconceptmap__times_validated__gte = 1,
                                              usersubmission__datasource__neuronephysdatamap__isnull = False)).distinct()
        #articles = articles.filter(articlefulltext__articlefulltextstat__metadata_human_assigned = True ).distinct()
    
    for article in articles:
        nedm_count = m.NeuronEphysDataMap.objects.filter(source__data_table__article = article).distinct().count()
        nedm_count += m.NeuronEphysDataMap.objects.filter(source__user_submission__article = article).distinct().count()
        neuron_count = m.Neuron.objects.filter(neuronconceptmap__source__data_table__article = article).distinct().count()
        neuron_count += m.Neuron.objects.filter(neuronconceptmap__source__user_submission__article = article).distinct().count()
        asOb = m.ArticleSummary.objects.get_or_create(article=article)[0]
        asOb.num_nedms = nedm_count
        asOb.num_neurons = neuron_count
        asOb.save()
    
                                                    
def computeNeuronSummaries(*args):
    if args:
        neurons = args[0]
    else:
        neurons = m.Neuron.objects.all()
    nedmsValid = m.NeuronEphysDataMap.objects.filter(neuron_concept_map__times_validated__gte = 1, ephys_concept_map__times_validated__gte = 1).distinct()
    for n in neurons:
        neuronNedms = nedmsValid.filter(neuron_concept_map__neuron = n).distinct()
        numNedms = neuronNedms.count()
        articles = m.Article.objects.filter(datatable__datasource__neuronconceptmap__times_validated__gte = 1, 
                                          datatable__datasource__neuronephysdatamap__isnull = False,
                                          datatable__datasource__neuronconceptmap__neuron = n).distinct()
        articleCount = articles.count()
        print [articleCount, numNedms]
        articles = m.Article.objects.filter(usersubmission__datasource__neuronconceptmap__times_validated__gte = 1, usersubmission__datasource__neuronconceptmap__neuron = n).distinct()
        articleCount += articles.count()
        print [articleCount, numNedms]
        nsOb = m.NeuronSummary.objects.get_or_create(neuron = n)[0]
        nsOb.num_nedms = numNedms
        nsOb.num_articles = articleCount  
        nsOb.save()

def computeSingleNeuronSummary(neuron):
    n = neuron
    neuronNedms = m.NeuronEphysDataMap.objects.filter(neuron_concept_map__neuron = n, neuron_concept_map__times_validated__gte = 1, ephys_concept_map__times_validated__gte = 1).distinct()
    numNedms = neuronNedms.count()
    articles = m.Article.objects.filter(Q(datatable__datasource__neuronconceptmap__times_validated__gte = 1,
                                        datatable__datasource__neuronephysdatamap__isnull = False) | 
                                        Q(usersubmission__datasource__neuronconceptmap__times_validated__gte = 1)).distinct()
    articles = articles.filter(articlefulltext__articlefulltextstat__metadata_human_assigned = True ).distinct()
    #articles = Article.objects.filter(datatable__datasource__neuronconceptmap__times_validated__gte = 1, datatable__datasource__neuronconceptmap__neuron = n)
    articleCount = articles.count()
#    print [articleCount, numNedms]
    nsOb = m.NeuronSummary.objects.get_or_create(neuron = n)[0]
    nsOb.num_nedms = numNedms
    nsOb.num_articles = articleCount  
    nsOb.save()
        
def computeEphysPropSummaries(*args):
    if args:
        ephys_props = args[0]
    else:
        ephys_props = m.EphysProp.objects.all()
    nedmsValid = m.NeuronEphysDataMap.objects.filter(neuron_concept_map__times_validated__gte = 1, ephys_concept_map__times_validated__gte = 1).distinct()
    for e in ephys_props:
        ephysNedms = nedmsValid.filter(ephys_concept_map__ephys_prop = e).distinct()
        numNedms = ephysNedms.count()
        ncms = m.NeuronConceptMap.objects.filter(neuronephysdatamap__in = ephysNedms)
        neurons = m.Neuron.objects.filter(neuronconceptmap__in = ncms).distinct()
        numUniqueNeurons = neurons.count() 
        articles = m.Article.objects.filter(Q(datatable__datasource__ephysconceptmap__times_validated__gte = 1,
                                            datatable__datasource__ephysconceptmap__ephys_prop = e) | 
                                            Q(usersubmission__datasource__ephysconceptmap__times_validated__gte = 1,
                                              usersubmission__datasource__ephysconceptmap__ephys_prop = e)).distinct()
        articleCount = articles.count()
        print [articleCount, numNedms]
        esOb = m.EphysPropSummary.objects.get_or_create(ephys_prop = e)[0]
        esOb.num_articles = articleCount
        esOb.num_neurons = numUniqueNeurons
        esOb.num_nedms = numNedms
        esOb.save()  
            
def computeNeuronEphysSummariesAll(*args):
    if args:
        neurons = args[0]
        ephys_props = args[1]
        neses = m.NeuronEphysSummary.objects.filter(neuron__in = neurons, ephys_prop__in = ephys_props)
        [nes.delete() for nes in neses]
        nedms = m.NeuronEphysDataMap.objects.filter(val_norm__isnull = False, neuron_concept_map__neuron__in = neurons, ephys_concept_map__ephys_prop__in = ephys_props)
    else:
        neurons = m.Neuron.objects.all()
        ephys_props = m.EphysProp.objects.all()
        nedms = m.NeuronEphysDataMap.objects.filter(val_norm__isnull = False)
        # delete all existing neses before running
        neses = m.NeuronEphysSummary.objects.all()
        [nes.delete() for nes in neses]
    for n in neurons:
        for e in ephys_props:
            curr_nedms = nedms.filter(neuron_concept_map__neuron = n, ephys_concept_map__ephys_prop = e)
            if curr_nedms.count() == 0:
                continue
            curr_articles = m.Article.objects.filter(Q(datatable__datasource__neuronconceptmap__neuronephysdatamap__in = curr_nedms,
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
            print [n, e, value_mean, value_sd]
            nes = m.NeuronEphysSummary.objects.get_or_create(ephys_prop = e, neuron = n)[0]
            nes.num_nedms = num_nedms
            nes.num_articles = num_articles                                    
            nes.value_mean = value_mean
            nes.value_sd = value_sd                                                    
            nes.save()
            
# I don't think this gets used anywhere. Answer: it does - ephys. curation interface points to this method once all the inputs have been validated
def computeNeuronEphysSummary(neuronconceptmaps, ephysconceptmaps, nedmObs):
    neurons = m.Neuron.objects.filter(neuronconceptmap__in = neuronconceptmaps)
    ephys_props = m.EphysProp.objects.filter(ephysconceptmap__in = ephysconceptmaps)
    for n in neurons:
        for e in ephys_props:
            curr_nedms = nedmObs.filter(neuron_concept_map__neuron = n, ephys_concept_map__ephys_prop = e)
            if curr_nedms.count() == 0:
                continue
            curr_articles = m.Article.objects.filter(Q(datatable__datasource__neuronconceptmap__neuronephysdatamap__in = curr_nedms,
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
                    art_value_mean = np.mean(art_values)
                    curr_value_list.append(art_value_mean)
            #print curr_value_list
            nes = m.NeuronEphysSummary.objects.get_or_create(ephys_prop = e, neuron = n)[0]
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
    ephys_props = m.EphysProp.objects.all()
    for e in ephys_props:
        eps = m.EphysPropSummary.objects.get(ephys_prop = e)
        neuron_means = [nes.value_mean for nes in m.NeuronEphysSummary.objects.filter(ephys_prop = e)]
        neuron_means = filter(None, neuron_means)
        if len(neuron_means) > 0:
            eps.value_mean_neurons = np.mean(neuron_means)
            eps.value_sd_neurons = np.std(neuron_means)
        print neuron_means
        print [e, eps.value_mean_neurons, eps.value_sd_neurons]
        nedms = m.NeuronEphysDataMap.objects.filter(val_norm__isnull = False, ephys_concept_map__ephys_prop = e)
        if nedms.count() > 0:
            article_values = [nedm.val_norm for nedm in nedms]
            article_values = filter(None, article_values)
            eps.value_mean_articles = np.mean(article_values)
            eps.value_sd_articles = np.std(article_values)   
        eps.save()
        
def computeArticleNedmSummary(pmid, neuron, ephys_prop):
    nedms = m.NeuronEphysDataMap.objects.filter(Q(val_norm__isnull = False) & 
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
    n = m.Neuron.objects.get(pk = 85)
    article_list = m.Article.objects.filter(datatable__datasource__neuronconceptmap__neuron = n).distinct()
    #pmid_list = [a.pmid for a in article_list]
    ephys_list = m.EphysProp.objects.all()
    ephys_list_str = [e.name for e in ephys_list]
    table = np.zeros([len(pmid_list), len(ephys_list)])
    for i,pmid in enumerate(pmid_list):
        for j,e in enumerate(ephys_list):
            table[i,j] = computeArticleNedmSummary(pmid, n, e)
    return table, pmid_list, ephys_list_str
    
def computeAllNeuronMeanData():
    neurons = m.Neuron.objects.all()
    ephys_list = m.EphysProp.objects.all()
    ephys_list_str = [e.name for e in ephys_list]
    table = np.zeros([350, len(ephys_list)])
    #valid_nedms = NeuronEphysDataMap.objects.filter(val_norm__isnull = False)
    valid_articles = m.Article.objects.filter(datatable__datasource__neuronconceptmap__neuronephysdatamap__val_norm__isnull = False)
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
            full_text_links.append(m.Article.objects.filter(pmid = pmid)[0].full_text_link)
#        pmid_list_all.append(pmid_list)
    return table, pmid_list_all, ephys_list_str, neuron_name_list, full_text_links


def getArticleMetaData():
    articles = m.Article.objects.filter(datatable__datasource__neuronconceptmap__times_validated__gte = 1).distinct()
    nom_vars = ['Species', 'Strain', 'ElectrodeType', 'PrepType']
    cont_vars  = ['RecTemp', 'AnimalAge', 'AnimalWeight']
    
#    metadata_table = []
#    metadata_table_nom = np.zeros([len(articles), len(nom_vars)])
#    metadata_table_nom = np.zeros([len(articles), len(cont_vars)])
    csvout = csv.writer(open("mydata.csv", "wb"))
    csvout.writerow(("Species", "Strain", "ElectrodeType", "PrepType", "Temp", "Age", "Weight"))
    for j,a in enumerate(articles):
        amdms = m.ArticleMetaDataMap.objects.filter(article = a)
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
        neurons = m.Neuron.objects.filter(neuronconceptmap__times_validated__gte = 1, neuronconceptmap__source__data_table__article = a).distinct()
        csvout.writerow(curr_metadata_list)
    return articles
    
def getNeuronTypesInDB():
    articles = m.Article.objects.filter(Q(datatable__datasource__neuronconceptmap__times_validated__gte = 1) | 
        Q(usersubmission__datasource__neuronconceptmap__times_validated__gte = 1)).distinct()
    articles = articles.filter(articlefulltext__articlefulltextstat__metadata_human_assigned = True ).distinct()
    neurons = m.Neuron.objects.filter(Q(neuronconceptmap__times_validated__gte = 1) & 
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
    nedmsValid = m.NeuronEphysDataMap.objects.filter(neuron_concept_map__times_validated__gte = 1, ephys_concept_map__times_validated__gte = 1, neuron_concept_map__source__data_table__isnull = False).distinct()
    articles_automated = m.Article.objects.filter(datatable__datasource__neuronconceptmap__times_validated__gte = 1).distinct()
    
    robot_user = m.get_robot_user()
    neurons = m.Neuron.objects.filter(neuronconceptmap__neuronephysdatamap__in = nedmsValid).distinct()
    
    ecmsNotValid = m.EphysConceptMap.objects.filter(times_validated = 0).distinct()
    ecms_valid_total = m.EphysConceptMap.objects.filter(times_validated = 1, source__data_table__isnull = False).distinct()
    ecms_valid_robot = m.EphysConceptMap.objects.filter(times_validated = 1,added_by = robot_user, source__data_table__isnull = False).distinct()

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
    nedmsValid = m.NeuronEphysDataMap.objects.filter(neuron_concept_map__times_validated__gte = 1, ephys_concept_map__times_validated__gte = 1).distinct()
    nedmsValidUser = m.NeuronEphysDataMap.objects.filter(neuron_concept_map__times_validated__gte = 1, 
                                                              ephys_concept_map__times_validated__gte = 1,
                                                              neuron_concept_map__source__user_submission__isnull = False).distinct()    
    articles = m.Article.objects.filter(Q(datatable__datasource__neuronconceptmap__times_validated__gte = 1) | 
        Q(usersubmission__datasource__neuronconceptmap__times_validated__gte = 1)).distinct()
    articles_user_submit = m.Article.objects.filter(usersubmission__datasource__neuronconceptmap__times_validated__gte = 1).distinct()
    journals = m.Journal.objects.filter(article__in = articles).distinct()
    robot_user = m.get_robot_user()
    neurons = m.Neuron.objects.filter(neuronconceptmap__neuronephysdatamap__in = nedmsValid).distinct()
    ephys_props = m.EphysProp.objects.filter(ephysconceptmap__neuronephysdatamap__in = nedmsValid).distinct()
    ecmsNotValid = m.EphysConceptMap.objects.filter(times_validated = 0).distinct()
    articles_not_validated_total = m.Article.objects.filter(datatable__datasource__ephysconceptmap__in = ecmsNotValid)
    articles_not_validated = articles_not_validated_total.annotate(ecm_count = Count('datatable__datasource__ephysconceptmap'))
    articles_not_validated = articles_not_validated.filter(ecm_count__gte = 4).distinct()
    ecms_valid_total = m.EphysConceptMap.objects.filter(times_validated = 1).distinct()
    ecms_valid_robot = m.EphysConceptMap.objects.filter(times_validated = 1,added_by = robot_user).distinct()
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
    ncms = m.NeuronConceptMap.objects.filter(times_validated__gte = 1, source__data_table__isnull = False).distinct()
    best_count = 0
    best_three_count = 0
    for ncm in ncms:
        try:
            a = ncm.get_article()
        except Exception:
            print 'no article found'
            continue
        nam = m.NeuronArticleMap.objects.filter(article = a, neuron = ncm.neuron).order_by('-num_mentions')
        if nam.count() > 0:
            nams = m.NeuronArticleMap.objects.filter(article = a, num_mentions__gte = nam[0].num_mentions)
            if nams.count() <= 1:
                best_count += 1
            if nams.count() <= 3:
                best_three_count += 1
    return (best_count, best_three_count, ncms.count())
    
def count_metadata_assign_accuracy():
    articles = m.Article.objects.filter(datatable__datasource__neuronconceptmap__times_validated__gte = 1,
                                      articlefulltext__articlefulltextstat__methods_tag_found = True)
    robot_user = m.get_robot_user()
    metadata_keys = ['Species', 'Strain', 'ElectrodeType', 'PrepType', 'JxnPotential', 'RecTemp', 'AnimalAge']    
    stat_dict = {}
    for metadata_key in metadata_keys:
        temp_dict = {}
        values_all = m.ArticleMetaDataMap.objects.filter(metadata__name = metadata_key,article__in=articles).distinct()
        values_robot = m.ArticleMetaDataMap.objects.filter(metadata__name = metadata_key, article__in = articles, added_by = robot_user).distinct()
        temp_dict['values_all'] = values_all.count()
        temp_dict['values_robot'] = values_robot.count()
        print metadata_key
        print temp_dict
        stat_dict[metadata_key] = temp_dict
    return stat_dict
    
def count_journal_statistics():
    
    NUM_MIN_ECMS = 4
    articles_valid = m.Article.objects.filter(datatable__datasource__neuronconceptmap__times_validated__gte = 1).distinct()
    articles_all = m.Article.objects.all()
    
    articles_manual = m.Article.objects.filter(usersubmission__datasource__neuronconceptmap__times_validated__gte = 1).distinct()
    articles_manual = articles_manual.exclude(id__in=articles_valid)
    
    ecmsNotValid = m.EphysConceptMap.objects.filter(times_validated = 0).distinct()
    articles_not_validated_total = m.Article.objects.filter(datatable__datasource__ephysconceptmap__in = ecmsNotValid)
    articles_not_validated = articles_not_validated_total.annotate(ecm_count = Count('datatable__datasource__ephysconceptmap'))
    articles_not_validated = articles_not_validated.filter(ecm_count__gte = NUM_MIN_ECMS).distinct()
    articles_not_validated = articles_not_validated.exclude(id__in=articles_valid)
    articles_not_validated = articles_not_validated.exclude(id__in=articles_manual)
    
    f = open('journal_count_list.csv','wb')
    f.write(u'\ufeff'.encode('utf8'))
    
    journals = m.Journal.objects.filter(article__in = articles_valid).distinct()
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
    articles = m.Article.objects.filter(Q(datatable__datasource__neuronconceptmap__times_validated__gte = 1) | 
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
    nedm_list = m.NeuronEphysDataMap.objects.all()
    for nedm in nedm_list:
        if nedm.ephys_concept_map.ephys_prop.id in [8, 1, 13, 27]:
            pass
        elif nedm.val_norm:
            continue
        normalized_dict = normalize_nedm_val(nedm)
        if normalized_dict['value']:
            nedm.val_norm = normalized_dict['value']
            nedm.err_norm = normalized_dict['error']

        #print [nedm.ephys_concept_map.ephys_prop, nedm.ephys_concept_map.ref_text, nedm.val, nedm.val_norm]
            nedm.save()


def get_neuron_region_assignments():
    neurons = m.Neuron.objects.filter(neuronconceptmap__times_validated__gte = 1).distinct()
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


def assign_stat_object_to_data_tables():
    """go through each data table object and add info about who curated and when"""

    dts = m.DataTable.objects.filter(datasource__ephysconceptmap__isnull= False)

    num_dts = dts.count()
    for i,dt in enumerate(dts):
        print "updating data tables with summary objects"
        prog(i,num_dts)
        update_data_table_stat(dt)