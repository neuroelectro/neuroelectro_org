# -*- coding: utf-8 -*-
"""
Created on Wed Dec 14 18:25:15 2011

@author: Shreejoy
"""
import os
import django_startup
from matplotlib.pylab import *
#run django_startup
os.chdir('C:\Python27\Scripts\Biophys\pubdb\pubdir')
from pubapp.models import Neuron, Article, IonChannel, NeuronSyn
from pubapp.models import ArticleNeuronTag, IonChannelSyn, ArticleIonChannelTag
os.chdir('C:\Python27\Scripts\Biophys')


neurons = Neuron.objects.all()

neuronArticleCnts = []
for neuron in neurons:
    neuronArticleCnts.append(len(Article.objects.filter(neuron__name = neuron.name)))

[(neurons[i].name, neuronArticleCnts[i]) for i in range(len(neuronArticleCnts))]

channels = IonChannel.objects.all()
channelArticleCnts = []
for channel in channels:
    channelArticleCnts.append(len(Article.objects.filter(ionchannel__name = channel.name)))

[(channels[i].name, channelArticleCnts[i]) for i in range(len(channelArticleCnts))]

mat = zeros([len(neurons), len(channels)])
for neuron in neurons:
    neuronInd = neuron.pk - 1
    coinChannels = IonChannel.objects.filter(articles__neuron__name__exact = neuron.name)  
    for channel in coinChannels:
        channelInd = channel.pk - 1
        mat[neuronInd][channelInd] += 1

# print out matrix entries wich appear more than n times
numArts = len(Article.objects.all())
probMat = mat / float(numArts)

expProbMat = zeros([len(neurons), len(channels)])
neuronInd = 0
channelInd = 0
for i in range(len(neurons)):
    for j in range(len(channels)):
        expProbMat[i][j] = neuronArticleCnts[i]/float(numArts) * channelArticleCnts[j]/float(numArts)
        if probMat[i][j] > 0 * expProbMat[i][j] and mat[i][j] > 5:
            print neurons[i].name, channels[j].name

# count how similar neurons are based on article co-mentions
matCoinMat = zeros([len(neurons), len(neurons)])
artCoinMat = zeros([len(neurons), len(Article.objects.all())])
for neuron in neurons:
    neuronInd = neuron.pk - 1
    containingArts = Article.objects.filter(neuron=neuron)
    for art in containingArts:
        if len(IonChannel.objects.filter(articles=art)) > 0: # check if article contains channels
            artInd =   art.pk - 1      
            artCoinMat[neuronInd][artInd] += 1
        otherNeurons = Neuron.objects.filter(articles = art)
        for otherNeuron in otherNeurons:
            otherNeuronInd = otherNeuron.pk - 1
            matCoinMat[neuronInd][otherNeuronInd] += 1


    coinNeurons = Neuron.objects.filter(articles__neuron__name__exact = neuron.name)  
    for channel in coinNeurons:
        channelInd = channel.pk - 1
        matCoinMat[neuronInd][channelInd] += 1
        


# count number of times each neuron./channel synonym is picked
neuronsyns = NeuronSyn.objects.all()
numTags = []
for i in range(len(neuronsyns)):
    tags = ArticleNeuronTag.objects.filter(foundsyns = neuronsyns[i])
    numTags.append(len(tags))

for neuron in neurons:
    syns = NeuronSyn.objects.filter(neuron = neuron)
    print neuron.name
    for syn in syns:
        tags = ArticleNeuronTag.objects.filter(foundsyns = syn)
        numTags = len(tags)
        print '\t', syn.term, numTags
    print '\n'

for channel in channels:
    syns = IonChannelSyn.objects.filter(ionchannel = channel)
    print channel.name
    for syn in syns:
        tags = ArticleIonChannelTag.objects.filter(foundsyns = syn)
        numTags = len(tags)
        print '\t', syn.term, ': ', numTags
    print '\n'
#    if len(tags) > 0:
#        print neuronsyns[i], len(tags)
        
# count number of times each neuron./channel synonym is picked
neuronsyns = NeuronSyn.objects.all()
for i in range(len(neuronsyns)):
    tags = ArticleNeuronTag.objects.filter(foundsyns = neuronsyns[i])
    if len(tags) > 0:
        print neuronsyns[i], len(tags)