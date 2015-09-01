# -*- coding: utf-8 -*-
__author__ = 'stripathy'

#######
# THIS FUNCTION AND ITS METHODS ARE DEPRECATED AND ARE NOT USED
# THEY ARE STORED HERE ONLY FOR HISTORICAL NEEDS
######


import re

import neuroelectro.models as m
import article_text_mining.resolve_data_float

from django.db.models import Count
from bs4 import BeautifulSoup
from fuzzywuzzy import process
import string
from django.core.exceptions import ObjectDoesNotExist

MIN_NEURON_MENTIONS_AUTO = 5

def assignNeuronToTableTag(neuronOb, dataTableOb, tableTag):
    tag_id = tableTag['id']
    headerText = tableTag.text.strip()
    successBool = False
    if headerText is None:
        return successBool
    # check that there isn't already a ncm here
    if m.NeuronConceptMap.objects.filter(dt_id = tag_id, data_table = dataTableOb).exclude(added_by = 'robot').distinct().count() > 0:
        successBool = True
        return successBool
    save_ref_text = headerText[0:min(len(headerText),199)]
    neuronConceptMapOb = m.NeuronConceptMap.objects.get_or_create(ref_text = save_ref_text,
                                                              neuron = neuronOb,
                                                              data_table = dataTableOb,
                                                              dt_id = tag_id,
                                                              added_by = 'robot')[0]
    successBool = True
    return successBool


# use a simple heuristic to tag data table headers for neuron concepts
def assocDataTableNeuronAuto(dataTableOb):
    soup = BeautifulSoup(dataTableOb.table_html)
    ecmObs = m.EphysConceptMap.objects.filter(data_table = dataTableOb)
    ecmTableIds = [ecmOb.dt_id for ecmOb in ecmObs]
    namObs = m.NeuronArticleMap.objects.filter(article__datatable = dataTableOb).order_by('-num_mentions')
    if namObs[0].num_mentions < MIN_NEURON_MENTIONS_AUTO:
        return
    topNeuronOb = namObs[0].neuron

#    numTH = len(soup.findAll('th'))
#    numTR = len(soup.findAll('tr'))
#    numTD = len(soup.findAll('td'))
    ecmAllTD = True
    for e in ecmTableIds:
        if 'td' in e:
            continue
        else:
            ecmAllTD = False
            break
    # if all ephys entities are td, then call first nonblank header element top neuron
    successBool = False
    if ecmAllTD == True:
        headerTags = soup.findAll('th')
        if len(headerTags) >= 2:
            # assign neuron to header tag in 1th position
            firstHeaderTag = headerTags[1]
            successBool = assignNeuronToTableTag(topNeuronOb, dataTableOb, firstHeaderTag)
            # call first nonblank header element top neuron
#             if successBool == False:
#                 firstHeaderTag = soup.findAll('th', text != None)
#                 successBool = assignNeuronToTableTag(topNeuronOb, dataTableOb, firstHeaderTag)
    print dataTableOb.pk, successBool

def assocDataTableNeuronAutoMult(dataTableObs):
    cnt = 0
    for dt in dataTableObs:
        cnt = cnt + 1
        if cnt % 100 == 0:
            print '%d of %d tables' % (cnt, dataTableObs.count())
        assocDataTableNeuronAuto(dt)
