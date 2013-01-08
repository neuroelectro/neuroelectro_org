# -*- coding: utf-8 -*-
"""
Created on Wed Dec 07 10:58:25 2011

@author: Shreejoy
"""

# do statistics on database - like count how often multiple neurons appear in the same article

import numpy as np

neuronNameList = neurolex_neuron_listcsv.split('\n')
neuronNameList = neuronNameList[:-1]

run django_startup

neuronObs = Neuron.objects.filter(name__in = neuronNameList)
neuronObs = sorted(neuronObs, key=lambda neuron: neuron.name)
numNeurons = len(neuronObs)
neuronNames = [neuron.name for neuron in neuronObs]

# for every neuron in neuronObs, generate a matrix where diags are num articles
# with that term, and off diags are coincidence with other neurons

coinMat = np.zeros((numNeurons))

for n in range(len(neuronObs)):
    currNeuron = neuronObs[n]
    # get articles which mention neuron
    currArts = Article.objects.filter(neuron__name__exact = currNeuron.name)
    if len(currArts) is 0:
        coinMat[n] = -1
        continue
    
    checkNeurons = neuronNames[:n]
    checkNeurons.extend(neuronNames[(n+1):])
    coinArts = currArts.filter(neuron__name__in = checkNeurons)
    coinMat[n] = (float(len(currArts)) - len(set(coinArts))) /float(len(currArts))
    
    # for the articles in the set xor of currArts and coinArts, assign ion channels to the neuron
    validArts = set(currArts).difference(set(coinArts))
    ionchannels = IonChannel.objects.filter(articles__in = validArts)
    if len(validArts) > 1000:
        continue
        for i in ionchannels:
            currNeuron.ionChannels.add(i)
    else:
        currNeuron.ionChannels = ionchannels
    
#    m = n+1 
#    for m in range(len(neuronObs)):
#        nextNeuron = neuronObs[m]
#        coinArts = currArts.filter(neuron__name__exact = nextNeuron.name)
#        coinMat[n][m] = len(coinArts)
[(neuronNames[i], coinMat[i]) for i in range(len(neuronObs))]        

# generate neuron_channel_matrix
numChannels = len(IonChannel.objects.all())
neuronChanMat = zeros((numNeurons, numChannels))
allChannels = IonChannel.objects.all()
for n in range(len(neuronObs)):
    channels = IonChannel.objects.filter(neuron = neuronObs[n])
    for i in range(numChannels):
        if allChannels[i] in channels:
            neuronChanMat[n][i] = 1

#only plot neurons where there is at least 1 channel
(i,j) = where(neuronChanMat!=0)
validNeurons = sort(list(set(i)))
dispMat = neuronChanMat[validNeurons][:]
matshow(dispMat)

fig = plt.figure()
ax = fig.add_subplot(111)
ax.matshow(dispMat)
ax.set_yticks(range(len(validNeurons)))
ax.set_xticks(range(len(allChannels)))

dispNeuronNames = [neuronObs[ind].name for ind in validNeurons]
channelNames = [channel.name for channel in allChannels]
nlabels = ax.set_yticklabels(dispNeuronNames, fontsize = 8) 
clabels = ax.set_xticklabels(channelNames, rotation = 90, fontsize = 8)



