# -*- coding: utf-8 -*-
"""
Created on Tue Dec 13 17:00:30 2011

@author: Shreejoy
"""

import os
import django_startup

os.chdir('C:\Python27\Scripts\Biophys\pubdb\pubdir')
from pubapp.models import NeuronSyn, IonChannelSyn

# remove synonyms from IonChannelSyn and NeuronSyn
icRemoveList = ['potassium channel', 'rat i', '', 'm1', 'brain type i', 'type i channel in t cells', 'brain type ii', 'rat ii', ]
icRemoveList.extend(['sodium channel protein', 'rat 3'])
neuronRemoveList = ['on cell', 'off cell', 'supporting cell', 'pyramidal cell', 'relay cell', 'small pyramidal neuron', 'type i ganglion cell', 'small pyramidal cell']
neuronRemoveList.extend(['ca3 so neuron', 'ca3 so interneuron', 'cerebellar nuclei', 'common spiny cell', 'spiny bipolar cell', 'spiny bipolar neuron', 'superficial spiny cell', 'triangular cell'])
neuronRemoveList.extend(['candelabrum cell', 'candelabrum neuron', 'unipolar brush cell', 'unipolar brush neuron', 'inverted pyramidal cell', 'piriform cell', 'piriform neuron', 'pyramidal cell'])
neuronRemoveList.extend(['stellate neuron', 'temperature cell', 'hilar cell', u'hilar neuron', 'mossy cell', 'macula', 'basket cell'])
neuronRemoveList.extend(['chendelier-type cell', 'deep interneuron', 'medium-sized spiny neuron', 'medium spiny neuron', 'external tufted cell', 'external tufted neuron'])
neuronRemoveList.extend(['olfactory horizontal cell', 'horizontal cell olfactory','semilunar cell', 'semilunar neuron', 'sustentacular cell'])
neuronRemoveList.extend(['nucleus of the solitary tract', 'type ii ganglion cell', 'type iii ganglion cell'])

remove: Dentate gyrus basket cell: 'pyramidal basket cell'
Cochlea hair cell
[u'cochlear inner hair cell', u'cochlear outer hair cell',
 
 
add: 
Olfactory bulb (main) granule cell
[u'olfactory bulb granule cell layer', u'olfactory bulb main granule cell']
Olfactory bulb (main) mitral cell
[u'olfactory bulb main mitral cell']


for elem in icRemoveList:
    syn = ProteinSyn.objects.filter(term = elem)
    if len(syn) > 0:
        syn[0].delete()

for elem in neuronRemoveList:
    syn = NeuronSyn.objects.filter(term = elem)
    if len(syn) > 0:
        syn[0].delete()
#    syn.delete()
#    syn.delete()
    
neurons = Neuron.objects.all()
for neuron in neurons:
    print neuron.name 
    syns = NeuronSyn.objects.filter(neuron = neuron)
    print [syn.term for syn in syns]
    print '\n'
    
    