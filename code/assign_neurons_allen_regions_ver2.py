# -*- coding: utf-8 -*-
"""
Created on Tue Jul 03 09:25:36 2012

@author: Shreejoy
"""

from neuroelectro.models import Article, MeshTerm, Substance, Journal
from neuroelectro.models import Neuron, NeuronSyn, Unit
from neuroelectro.models import BrainRegion, InSituExpt, Protein, RegionExpr
from neuroelectro.models import DataTable, ArticleFullText, EphysConceptMap
from neuroelectro.models import NeuronArticleMap

from fuzzywuzzy import process
def assign_regions(neurons=None):
    if neurons is None:
        neurons = Neuron.objects.filter(regions__isnull = True)
    matchThresh = 60
    regionNames = [r.name for r in BrainRegion.objects.all()]
    regionNames.remove(u'Nucleus x')
    regionNames.remove(u'Nucleus y')
    unmatchedNeurons = []
    for n in neurons:
        nName = n.name
        #bestRegions = process.extract(nName,regionNames)
        #print nName, bestRegions
        bestRegion, matchVal = process.extractOne(nName,regionNames)    
        if matchVal > matchThresh:
            nOb = Neuron.objects.get(name = n)
            rOb = BrainRegion.objects.get(name = bestRegion)
            print nName, bestRegion
            nOb.regions.add(rOb)
            nOb.save()
        else:
            unmatchedNeurons.append(nName)
    return unmatchedNeurons

def assign_more_regions():
    neuronNameList = \
    [
    'Hippocampus CA1 oriens lacunosum moleculare neuron',
    'Substantia nigra pars compacta dopaminergic cell',
    'Colliculus superior wide field vertical cell',
    'Substantia nigra pars reticulata interneuron GABA',
    'Trapezoid body principal cell',
    ]
    neurons = [Neuron.objects.get(name = n) for n in neuronNameList]
    assign_regions(neurons)


'Neocortex basket cell'
'Neocortex Martinotti cell'
'Neocortex bipolar neuron'
'Neocortex bipolar cell'
'Neocortex pyramidal cell layer 2-3'
'Neocortex layer 4 stellate cell'
'Neocortex stellate cell'
'Neocortex pyramidal cell layer 5-6'
'Neocortex Cajal-Retzius cell'



def assign_cortex_neuron_regions():
    neuronNames = \
    [
    'Neocortex basket cell',
    'Neocortex Martinotti cell',
    'Neocortex bipolar neuron',
    'Neocortex bipolar cell',
    'Neocortex pyramidal cell layer 2-3',
    'Neocortex layer 4 stellate cell',
    'Neocortex stellate cell',
    'Neocortex pyramidal cell layer 5-6',
    'Neocortex Cajal-Retzius cell',
    ]
    neuronRegionInds = \
    [
    [315],
    [315],
    [315],
    [315],
    [667,943,962,346,838,201,113,657,854,670,806,556,180,1106,600,251,643,755,905,1066,973,821,269,41,211,296,304,412,582,288,328,163,694,965,434,430,241,1127,888,427],
    [865,654,1047,1094,950,577,1086,1035,148,1010,678,816,759,990,1114,401,573,721,869,501,635,234],
    [865,654,1047,1094,950,577,1086,1035,148,1010,678,816,759,990,1114,401,573,721,869,501,635,234],
    [648,767,921,702,1128,974,625,1111,1090,827,187,1058,252,847,791,1023,233,433,613,778,902,565,1015,772,363,630,620,1125,1101,344,800,774,610,687,683,289,692,988,844,1021,686,889,1038,478,1102,945,9,862,1054,638,857,156,954,249,520,601,1046,74,33,377,257,919,810,84,440,910,608,783,314,675,906,274,590,308,729,335],
    [793],
    ]
#layer 5 only
#[648,767,921,702,1128,974,625,1111,1090,827,187,1058,252,847,791,1023,233,433,613,778,902,565,1015,772,363,630,620,1125,1101,344,800,774,610,687,683,289,692,988]
#layer 6a only
#[844,1021,686,889,1038,478,1102,945,9,862,1054,638,857,156,954,249,520,601,1046,74,33,377,257,919,810,84,440,910,608,783,314,675,906,274,590,308,729,335]
    for ind in range(len(neuronNames)):
        neuronOb = Neuron.objects.get(name = neuronNames[ind])
        print neuronOb
        for regionInd in neuronRegionInds[ind]:
            regionOb = BrainRegion.objects.get(allenid = regionInd)
            #print '\t' + regionOb.name
            neuronOb.regions.add(regionOb)
        neuronOb.save()

def assign_even_more_regions(): 
    neuronNames = \
    [       
    'Amygdaloid nucleus paracapsular intercalated cell',
    'Hippocampus CA1 neurogliaform cell',
    'Olfactory cortex semilunar cell',
    'Olfactory cortex pyramidal cell',
    'Hippocampus CA1 basket cell',
    'Basalis nucleus cholinergic neuron',
    'BNST common spiny neuron',
    'BNST beaded neuron',
    'Olfactory bulb (main) tufted cell (middle)',
    'Olfactory bulb (main) periglomerular cell',
    'Olfactory bulb main tufted cell external',
    'Olfactory bulb (main) Blanes cell',
    'Neocortex chandelier cell',
    'Amygdala basolateral nucleus pyramidal neuron',
    'Amygdala corticomedial nucleus pyramidal cell',
    'Substantia nigra pars reticulata principal cell',
    'Hypothalamus oxytocin neuroendocrine magnocellular cell'
    ]
    neuronRegionNames = \
    [
    'Intercalated amygdalar nucleus',
    'Field CA1, stratum lacunosum-moleculare',
    'Piriform area, pyramidal layer',
    'Piriform area, pyramidal layer',
    'Field CA1, stratum radiatum',
    'Substantia innominata',
    'Bed nuclei of the stria terminalis',
    'Bed nuclei of the stria terminalis',
    'Main olfactory bulb, outer plexiform layer',
    'Main olfactory bulb, glomerular layer',
    'Main olfactory bulb, glomerular layer',
    'Main olfactory bulb, granule layer',
    'Isocortex',
    'Basolateral amygdalar nucleus',
    'Cortical amygdalar area, posterior part, medial zone',
    'Substantia nigra, reticular part',
    'Hypothalamus'
    ]
    for ind in range(len(neuronNames)):
        try:
            neuronOb = Neuron.objects.get(name = neuronNames[ind])
        except Exception:
            continue
        regionName = neuronRegionNames[ind]
        regionOb = BrainRegion.objects.get(name = regionName)
        print neuronOb
        print '\t' + regionOb.name
        neuronOb.regions = [regionOb]
        neuronOb.save()
    
    
#r = BrainRegion.objects.get(name = "Caudoputamen")
#
#neurons = Neuron.objects.filter(name__icontains = "Neostriatum")
#
#for n in neurons:
#    n.regions.clear()
#    n.regions.add(r)
#    n.save()
#    
#regions = BrainRegion.objects.filter(name__icontains = "granular layer")
#regions = regions[1:]
#
#neuron = Neuron.objects.get(name = "Cerebellum granule cell")
#neuron.regions.clear()
#neuron.regions = regions    
        
