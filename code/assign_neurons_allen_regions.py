# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 18:16:54 2012

@author: Shreejoy
"""
import os
import django_startup
from matplotlib.pylab import *
#run django_startup
os.chdir('C:\Python27\Scripts\Biophys\pubdb\pubdir')
from pubapp.models import BrainRegion, Neuron
os.chdir('C:\Python27\Scripts\Biophys')
import re

data = allen_regions_neurolex_neurons_import

regionNeuronMap = zeros([len(data), 2])
for i in range(len(data)):
    neuron, regionList =  unicode(data[i]).split(',')
    if re.search(';', regionList) is not None:
        regionList = regionList.split(';')
        regionList = [r.strip() for r in regionList]
    else:
        regionList = [regionList]
    
    neuronOb = Neuron.objects.get(name = neuron)
    print neuronOb.name + ' contained in '
    print regionList
    
    neuronOb.regions = []
    for region in regionList:
        # check if region is in db: if so, its an allen region and needs to assigned
        regQuery = BrainRegion.objects.filter(name = region)
        if regQuery.count() > 0:
            # is allen region
            regionOb = regQuery[0]
            if regionOb.abbrev is not u'':
                regionOb.isallen = True
            else:
                regionOb.isallen = False
            
        else:
            regionOB = BrainRegion.objects.create(name = region, abbrev = '')
            regionOb.isallen = False
        
        regionOb.neurons.add(neuronOb)
        neuronOb.regions.add(regionOb)
        regionOb.save()

for b in BrainRegion.objects.all():
    print b.name + ' ' + b.abbrev
    if b.abbrev is not u'':
        b.isallen = True
    else:
        b.isallen = False
    
    b.save()

    
# compute average expression for each neuron which is assigned to an allen region
for n in Neuron.objects.all():
    n.regions = []

for b in BrainRegion.objects.all():
    b.neurons = []
    
        


