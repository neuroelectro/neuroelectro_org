# -*- coding: utf-8 -*-
"""
Created on Wed Nov 30 10:49:31 2011

@author: Shreejoy
"""
from pubapp.models import Neuron, IonChannel
from matplotlib.pylab import *
# plot a matrix of all channels and neurons

# get all channels
channels = IonChannel.objects.all()

channelNameList = []
[channelNameList.append(x.name) for x in channels]
channelNameList = sort(channelNameList)

# get neurons with ion channels, and sort them by name
neurons = Neuron.objects.filter(ionChannels__isnull = False)
neurons = list(set(neurons))

mat = zeros([len(neurons), len(channelNameList)])
for i in range(len(neurons)):
    for j in range(len(channelNameList)):
        currNeuron = neurons[i]
        currChannel = IonChannel.objects.filter(name__exact = channelNameList[j])
        checkSet = Neuron.objects.filter(name__exact = currNeuron.name).filter(ionChannels__name__exact = channelNameList[j])
        if len(checkSet) is not 0: 
            mat[i][j] = len(checkSet)

#matshow(mat)

fig = plt.figure()
ax = fig.add_subplot(111)
ax.matshow(log2(mat))
ax.set_yticks(range(len(neurons)))
ax.set_xticks(range(len(channelNameList)))

neuronNameList = []
[neuronNameList.append(neuron.name) for neuron in neurons]
nlabels = ax.set_yticklabels(neuronNameList, fontsize = 8) 
clabels = ax.set_xticklabels(channelNameList, rotation = 90, fontsize = 8)   

for tick in ax.xaxis.get_major_ticks():
    tick.label.set_fontsize(20) 
#plt.colorbar() 
#plt.show()

fig = plt.figure()
ax = fig.add_subplot(111)
a = (92, 100)
ax.matshow(mat[a][:])

