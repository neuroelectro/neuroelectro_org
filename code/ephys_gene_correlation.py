# -*- coding: utf-8 -*-
"""
Created on Fri Apr 20 14:42:46 2012

@author: Shreejoy
"""

# compute median of ephys props for each neuron
def median_value(queryset,term):
    count = queryset.count()
    return queryset.values_list(term, flat=True).order_by(term)[int(round(count/2))]
    

e = EphysProp.objects.get(name = 'Input resistance')
nels = NeuronEphysLink.objects.all()
neurons = list(set([n.neuron for n in nels]))
n = neurons[3]

valList = []
for n in neurons:
    nels = NeuronEphysLink.objects.filter(neuron = n, ephys_prop = e)
    if nels.count() > 0:
        medVal = median_value(nels, 'val')
#        if medVal < 3 and e.name == 'input resistance':
#            medVal = medVal*1000
        tup = (n, medVal)
        valList.append(tup)
        
sortedTuple = sorted(valList, key=lambda a: a[1])

matchThresh = 80
regionNames = [r.name for r in BrainRegion.objects.all()]
unmatchedNeurons = []
for n in neurons:
    nName = n.name
    bestRegions = process.extract(nName,regionNames)
    bestRegion, matchVal = process.extractOne(nName,regionNames)    
    if matchVal > matchThresh:
        nOb = Neuron.objects.get(name = n)
        rOb = BrainRegion.objects.get(name = bestRegion)
        print nName, bestRegion
        #nOb.regions.add(rOb)
        #nOb.save()
    else:
        unmatchedNeurons.append(nName)
    #print nName, bestRegions


nList =['Colliculus superior deep vertical fusiform cell', 
'Thalamic reticular nucleus cell',
'Globus pallidus intrinsic cell',
'Hippocampus CA1 pyramidal cell',
'Hippocampus CA3 pyramidal cell',
'Neocortex pyramidal cell',
'Hypothalamus oxytocin neuroendocrine magnocellular cell'
]

rList =[
'Superior colliculus, sensory related',
'Reticular nucleus of the thalamus',
'Pallidum, dorsal region',
'Field CA1, pyramidal layer',
'Field CA3, pyramidal layer',
'Isocortex',
'Hypothalamus',
]

cnt = 0
for n in nList:
    nOb = Neuron.objects.get(name = nList[cnt])
    rOb = BrainRegion.objects.get(name = rList[cnt])
    print nOb, rOb.name
    nOb.regions.add(rOb)
    nOb.save()
    cnt += 1

# try the regression!
neuronList = [
'Dentate gyrus granule cell',
'Ventral tegmental area dopamine neuron',
'Hippocampus CA1 pyramidal cell',
'Hippocampus CA3 pyramidal cell',
'Locus coeruleus NA neuron',
'Neostriatum medium spiny neuron',
'Subiculum pyramidal cell',
'Thalamic reticular nucleus cell',
'Thalamus relay cell',
'Trigeminal nucleus motor neuron',
'Dorsal motor nucleus of vagus motor neuron',
'Globus pallidus intrinsic cell',
'Hypoglossal nucleus motor neuron',
]
neurons = [Neuron.objects.get(name = neuronList[i]) for i in xrange(len(neuronList))]

#neurons = Neuron.objects.filter(regions__isnull = False)
ephysVec = zeros([len(neurons)])
geneMat = zeros([len(neurons)])
g = Protein.objects.filter(gene = 'Atp5a1')[0]
ise = g.in_situ_expts.all()[1]
cnt = 0
for n in neurons:   
    nels = NeuronEphysLink.objects.filter(neuron = n, ephys_prop = e)
    if nels.count() > 0:
        medVal = median_value(nels, 'val')
        ephysVec[cnt] = medVal
        regionOb = n.regions.all()[0]
        q = RegionExpr.objects.filter(region = regionOb, insituexpt = ise)
        if q.count() > 0:
            geneMat[cnt] = q[0].val
    cnt += 1

pearsonr(1/(ephysVec), log(geneMat))