# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 15:06:06 2012

@author: Shreejoy
"""
import numpy
from neuroelectro.models import Article, MeshTerm, Substance, Journal
from neuroelectro.models import Neuron, NeuronSyn, Unit
from neuroelectro.models import BrainRegion, InSituExpt, Protein, RegionExpr
from neuroelectro.models import DataTable, ArticleFullText, EphysConceptMap
from neuroelectro.models import EphysProp, EphysPropSyn, NeuronEphysLink, NeuronArticleMap
from neuroelectro.models import NeuronConceptMap, NeuronArticleMap, NeuronEphysDataMap

from django.db.models import Count, Min
from get_ephys_data_vals_all import filterNedm
#compute statistics of extracted values from data tables

def computeDataTableStats():
    numJournals = Journal.objects.filter(article__articlefulltext__isnull = False).distinct().count()
    numFullTextArticles = ArticleFullText.objects.all().distinct().count()
    numDataTables = DataTable.objects.all().distinct().count()
    numDTsWEphys = DataTable.objects.filter(ephysconceptmap__isnull = False).distinct().count()
    dts = DataTable.objects.all()
    dts = dts.annotate(num_ecms =  Count('ephysconceptmap', distinct = True))
    numDTsWEphysAtLeast4 = dts.filter(num_ecms__gte = 4).count()
    numDTsWNeurons = DataTable.objects.filter(neuronconceptmap__isnull = False).distinct().count()
    numDTsWEphysNeurons = DataTable.objects.filter(neuronconceptmap__isnull = False, ephysconceptmap__isnull = False).distinct().count()
    numDTsWEphysNeuronsValid = DataTable.objects.filter(neuronconceptmap__times_validated__gte = 1, ephysconceptmap__times_validated__gte = 1).distinct().count()
    numNEDMs = NeuronEphysDataMap.objects.all().distinct().count()
    numNEDMsValid = NeuronEphysDataMap.objects.filter(neuron_concept_map__times_validated__gte = 1, ephys_concept_map__times_validated__gte = 1).distinct().count()
    
    outVec = [numJournals, numFullTextArticles, numDataTables, numDTsWEphys, numDTsWEphysAtLeast4, numDTsWNeurons, numDTsWEphysNeurons, numDTsWEphysNeuronsValid, numNEDMs, numNEDMsValid]
    return outVec
#
#
##compute statistics for how many reports and neurons there are for each ephys value
def computeEphysStats():
    ephysNames = []
    ephys_props = EphysProp.objects.all()
    outTable = numpy.zeros([ephys_props.count(), 4], dtype=float)
    nedmsValid = NeuronEphysDataMap.objects.filter(neuron_concept_map__times_validated__gte = 1, ephys_concept_map__times_validated__gte = 1).distinct()
#    nedmsValid = [filterNedm(nedm) for nedm in nedmsValid]
    rowInd = 0    
    for e in EphysProp.objects.all():
        ephysNames.append(e.name)
        ephysNedms = nedmsValid.filter(ephys_concept_map__ephys_prop = e).distinct()
        numNedms = ephysNedms.count()
        ncms = NeuronConceptMap.objects.filter(neuronephysdatamap__in = ephysNedms)
        neurons = Neuron.objects.filter(neuronconceptmap__in = ncms).distinct()
        numUniqueNeurons = neurons.count()
        neuronsWRegions = neurons.filter(regions__isnull = False).distinct()
        neuronsWRegionsCount = neuronsWRegions.count()
        ratio = consistencyRatio(ephysNedms, neuronsWRegions)
        #print [numNedms, numUniqueNeurons, neuronsWRegionsCount, ratio]
        outTable[rowInd, :] = numpy.array([numNedms, numUniqueNeurons, neuronsWRegionsCount, ratio])
        rowInd += 1
    return outTable, ephysNames

def consistencyRatio(ephysNedms, neuronsWRegions):
    meanVals = []
    stdVals = []
    for n in neuronsWRegions:
        nedms = ephysNedms.filter(neuron_concept_map__neuron = n)
        eVals = [filterNedm(nedm) for nedm in nedms]
        eVals = filter(None, eVals)
        if len(eVals) > 0:
#        eVals = [nedm.val for nedm in nedms]
            #print eVals
            meanVal = numpy.mean(eVals)
            stdVal = numpy.std(eVals)
            if stdVal > 0:
                stdVals.append(stdVal)
            meanVals.append(meanVal)
    if len(meanVals) > 0:
        groupStd = numpy.std(meanVals)
        withinGroupStd = numpy.mean(stdVals)
        ratio = groupStd/withinGroupStd
        #print groupStd, withinGroupStd
    else:
        ratio = -1
    return ratio