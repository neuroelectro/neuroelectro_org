# -*- coding: utf-8 -*-
"""
Created on Tue Nov 29 16:05:13 2011

@author: Shreejoy
"""

from pubapp.models import Neuron, Synonym, Article, IonChannel
minArts = 20
# find all neurons which have more than XX articles

numArticles = []
for neuron in Neuron.objects.all():
    numArticles.append(len(Article.objects.filter(neuron__name__exact = neuron.name)))
    
neurons = []
for i in range(len(numArticles)):
    if numArticles[i] > minArts:
        neurons.append(Neuron.objects.get(pk=i+1))
    
for neuron in neurons:
    ic = IonChannel.objects.filter(articles__neuron__name__exact = neuron.name)    
    print '\n' + neuron.name
    print [i.name for i in set(ic)] 
    [neuron.ionChannels.add(i) for i in ic]

