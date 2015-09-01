# -*- coding: utf-8 -*-
"""
Created on Mon Jul 02 15:51:31 2012

@author: Shreejoy
"""
import os
#import django_startup
import re
import struct
import gc
#import nltk
#os.chdir('C:\Users\Shreejoy\Desktop\Biophysiome')
from neuroelectro.models import Article, MeshTerm, Substance, Journal
from neuroelectro.models import Neuron, NeuronSyn, Unit, NeuronEphysSummary
from neuroelectro.models import BrainRegion, InSituExpt, Protein, RegionExpr
from neuroelectro.models import DataTable, ArticleFullText, EphysConceptMap
from neuroelectro.models import EphysProp, EphysPropSyn, NeuronArticleMap
from neuroelectro.models import NeuronConceptMap, NeuronArticleMap, NeuronEphysDataMap




def filterNedm(nedm):
    #print nedm
    if nedm.data_table.needs_expert == True:
        return None
    val = nedm.val
    if nedm.ephys_concept_map.ephys_prop.name == 'resting membrane potential' or nedm.ephys_concept_map.ephys_prop.name == 'spike threshold':
        if val > 0:
            val = -nedm.val
    if nedm.ephys_concept_map.ephys_prop.name == 'spike half-width':
        if val > 5:
            return None
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
    
def region_list_to_matrix(regionList):
    mat = np.zeros([len(regionList),76])
    rowInd = 0
    for l in regionList:
        colInd = 0
        for e in l:
            regionPK = BrainRegion.objects.get(allenid = e).pk
            mat[rowInd, colInd] = regionPK
            colInd += 1
        rowInd += 1
    return mat
            
    