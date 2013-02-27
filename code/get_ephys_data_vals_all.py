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
from matplotlib.pylab import *
#os.chdir('C:\Users\Shreejoy\Desktop\Biophysiome')
from neuroelectro.models import Article, MeshTerm, Substance, Journal
from neuroelectro.models import Neuron, NeuronSyn, Unit, NeuronEphysSummary
from neuroelectro.models import BrainRegion, InSituExpt, Protein, RegionExpr
from neuroelectro.models import DataTable, ArticleFullText, EphysConceptMap
from neuroelectro.models import EphysProp, EphysPropSyn, NeuronArticleMap
from neuroelectro.models import NeuronConceptMap, NeuronArticleMap, NeuronEphysDataMap



#nedms = NeuronEphysDataMap.objects.all()
#neuronObList = list(set([n.neuron_concept_map.neuron for n in nedms]))
#ephysObList= list(set(EphysProp.objects.all()))
#dataTableObList = list(set([n.data_table for n in nedms]))
#neuronList = [n.name for n in neuronObList]
#ephysList = [n.name for n in ephysObList]
##neurons = Neuron.objects.filter(neuron_ephys_link) 
##nels = NeuronEphysLink.objects.filter(neuron__name = 'Hippocampus CA3 pyramidal cell', ephys_prop__name = 'input resistance')
#
#table = np.zeros([len(dataTableObList),len(ephysObList)])
#rowCnt = 0
#dtCnt = 0
#neuronList = ['' for i in range(len(dataTableObList))]
#linkList = ['' for i in range(len(dataTableObList))]
#regionIndList = [0 for i in range(len(dataTableObList))]
#
#ephysCnt = 0
#for i in ephysObList:
#    for j in neuronObList:
#        dtCnt = 0
#        for k in dataTableObList:
#            nedms = NeuronEphysDataMap.objects.filter(neuron_concept_map__neuron = j, ephys_concept_map__ephys_prop = i, data_table = k).distinct()
#            if nedms.count() == 0:
#                dtCnt += 1
#                continue
#            nedm = nedms[0]
#            if nedm.data_table.needs_expert == True:
#                dtCnt += 1
#                continue
#            val = nedm.val
#            if nedm.ephys_concept_map.ephys_prop.name == 'resting membrane potential' or nedm.ephys_concept_map.ephys_prop.name == 'spike threshold':
#                if val > 0:
#                    dtCnt += 1
#                    val = -nedm.val
#            elif nedm.ephys_concept_map.ephys_prop.name == 'spike half-width':
#                if val > 5:
#                    dtCnt += 1
#                    continue
#            elif nedm.ephys_concept_map.ephys_prop.name == 'spike width':
#                if val > 20:
#                    dtCnt += 1
#                    continue 
#            elif nedm.ephys_concept_map.ephys_prop.name == 'spike amplitude' or nedm.ephys_concept_map.ephys_prop.name == 'membrane time constant'\
#                or nedm.ephys_concept_map.ephys_prop.name == 'spike width':
#                    if re.search(r'psp', nedm.data_table.table_text, re.IGNORECASE) != None \
#                    or re.search(r'psc', nedm.data_table.table_text, re.IGNORECASE) != None \
#                    and nedm.times_validated == 0:
#                        #print nedm.data_table.table_text
#                        dtCnt += 1
#                        continue            
#            #value = nedm[0].val
#            table[dtCnt, ephysCnt]= val
#            print j, dtCnt
#            neuronList[dtCnt] = j.name
#            linkList[dtCnt] = k.link
#            if j.regions.count() > 0:
#                r = j.regions.all()[0]
#                regionIndList[dtCnt] = int(r.pk)
#            dtCnt += 1
#    ephysCnt += 1

def get_neuron_ephys_values():
    table = np.zeros([500,28])
    dts = DataTable.objects.filter(datasource__neuronephysdatamap__isnull = False).distinct()
    neuronNameList = []
    regionList = []
    pmidList = []
    tableInd = 0
    dtInd = 0
    for dt in dts:
        neurons = Neuron.objects.filter(neuronconceptmap__source__data_table = dt)
        #print 'table number %d with %d neurons' %(dtInd, neurons.count())
        for n in neurons:
            nedms = NeuronEphysDataMap.objects.filter(source__data_table = dt, neuron_concept_map__neuron = n).distinct()
            for nedm in nedms:
                if nedm.val_norm:
                    ephys_ind = int(nedm.ephys_concept_map.ephys_prop.pk)-1
                    table[tableInd, ephys_ind] = nedm.val_norm
#                try:
#                    nedmVal = filterNedm(nedm)
#                    #print nedm, nedmVal
#                    if nedmVal is not None:
#                        # add to table
#                        ephys_ind = int(nedm.ephys_concept_map.ephys_prop.pk)-1
#                        table[tableInd, ephys_ind] = nedmVal
#                except Exception:
#                    print 'nedm excepted: %d datatable: %d' % (nedm.pk,  dt.pk)
                    #continue
            neuronNameList.append(n.name)
            pmidList.append(dt.article.pmid)
            regions = BrainRegion.objects.filter(neuron = n)
            if regions is not None:
                regionInds = [r.allenid for r in regions]
            else:
                regionInds = []
            regionList.append(regionInds)
            tableInd += 1
        dtInd += 1
    return table, neuronNameList, regionList, pmidList
    
def get_neuron_ephys_values_dict():
    val_dict = {}
    dts = DataTable.objects.filter(neuronephysdatamap__isnull = False).distinct()
    neuronNameList = []
    regionList = []
    pmidList = []
    tableInd = 0
    dtInd = 0
    neurons = Neuron.objects.filter(neuronsummary__num_nedms__gte = 1)
    for neuron in neurons:
        neuronEphysSummaries = NeuronEphysSummary.objects.filter(neuron = neuron)
        propertyDict = {}
        neuron_name = neuron.name.replace(" ", "_")
        for nes in neuronEphysSummaries:
            value = nes.value_mean
            ephys_name = nes.ephys_prop.name
            ephys_name = ephys_name.replace(" ", "_")
            propertyDict[ephys_name] = value
        val_dict[neuron_name] = propertyDict
    return val_dict
    
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
            
    