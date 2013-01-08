# -*- coding: utf-8 -*-
"""
Created on Mon Apr 16 11:12:31 2012

@author: Shreejoy
"""
import os
#import django_startup
import re
import nltk
from matplotlib.pylab import *
#os.chdir('C:\Users\Shreejoy\Desktop\Biophysiome')
from neuroelectro.models import Article, MeshTerm, Substance, Journal
from neuroelectro.models import Neuron, NeuronSyn, ArticleFullText
from neuroelectro.models import BrainRegion, InSituExpt, Protein, RegionExpr
from neuroelectro.models import DataTable, ArticleFullText, NeuronArticleMap
from neuroelectro.models import EphysProp, EphysPropSyn, NeuronEphysLink
#os.chdir('C:\Users\Shreejoy\Desktop\Biophysiome')

porter = nltk.PorterStemmer()
#stopwords = nltk.corpus.stopwords.words('english')

def getSynStemList():
    synsStemList= []
    neuronSyns = NeuronSyn.objects.all()
    for s in neuronSyns:
        chunkList = s.term.lower().split()
        chunkList = [porter.stem(elem) for elem in chunkList]
        tempTup = (s, chunkList, s.neuron_set.all()[0])
        synsStemList.append(tempTup)
    return synsStemList
    
synStemsList = getSynStemList()
def findNeuronsInText(text):
    textsplit = text.lower().split()
    textsplit = [elem.strip(' .,:()/[]-"') for elem in textsplit]
    textsplit = [porter.stem(elem) for elem in textsplit]
    artDict = dict([[y,textsplit.count(y)] for y in set(textsplit)])
    containingNeuronList = []
    artKeys = set(artDict.keys())
    for s in synStemsList:
        #print s
        # check if chunks in s are contained in keys        
        synChunks = s[1]
        if set(synChunks).issubset(artKeys):
            numMentions = artDict[synChunks[0]]
            for c in synChunks[1:]:
                numMentions = min(numMentions, artDict[c])
            # check if this synonmy is mapped to mult neuron types
            # if so, then return longest neuron with longer name
            matchingNeuronObs = s[0].neuron_set.all()
            if len(matchingNeuronObs) > 1:
                neuronNames = [n.name for n in matchingNeuronObs]
                longestNeuronName = max(neuronNames, key=len)
                neuronIndex = neuronNames.index(longestNeuronName)
                keepNeuronOb = matchingNeuronObs[neuronIndex]
            else:
                keepNeuronOb = matchingNeuronObs[0]
            retTuple = (keepNeuronOb, s[0], numMentions)
            containingNeuronList.append(retTuple)
#            for n in matchingNeuronObs: 
#                retTuple = (n, s[0], numMentions)
#                containingNeuronList.append(retTuple)
#            print s[0], numMentions
    containingNeuronList = list(set(containingNeuronList))
    sortedTuple = sorted(containingNeuronList, key=lambda a: -a[2])
    return sortedTuple      

minSelectFreq = 5
def getMostLikelyNeuron(text):
    neuronTupleList = findNeuronsInText(text)
    if len(neuronTupleList) > 0:
        if neuronTupleList[0][1] >= minSelectFreq:
            return neuronTupleList[0][0]
    return None
# tag tables if they contain ephys props in their headers



       
#        syn = s.term
#        chunkList = syn.lower().split()
#        chunkList = [porter.stem(elem) for elem in chunkList]
#        numAppears = np.zeros([len(chunkList)])
#        cnt = 0
#        for elem in chunkList:
#            try: 
#                val = artDict[elem]
#                numAppears[cnt] = val
#                cnt += 1
#            except KeyError:
#                break
#        if np.min(numAppears) > 0:
#            #print '%s \t %s ' %(syn, np.min(numAppears))
#            retTuple = (s.neuron_set.all()[0], np.min(numAppears))
#            containingNeuronList.append(retTuple)
##            containingNeuronList.append(s.neuron_set.all()[0])
##            appearsList.append(np.min(numAppears))
##            containingNeuronList.append(s.neuron_set.all()[0])
##            appearsList.append(np.min(numAppears))
#    containingNeuronList = list(set(containingNeuronList))
#    sortedTuple = sorted(containingNeuronList, key=lambda a: -a[1])
##    print sortedTuple
#    return sortedTuple
    
#synStemsList = getSynStemList()
#def findNeuronsInText(text):
#    textsplit = text.lower().split()
#    textsplit = [elem.strip(' .,:()/[]-"') for elem in textsplit]
#    textsplit = [porter.stem(elem) for elem in textsplit]
#    artDict = dict([[y,textsplit.count(y)] for y in set(textsplit)])
#    neuronSyns = NeuronSyn.objects.all()
#    containingNeuronList = []
##    appearsList = []
#    for s in neuronSyns:
#        syn = s.term
#        chunkList = syn.lower().split()
#        chunkList = [porter.stem(elem) for elem in chunkList]
#        numAppears = np.zeros([len(chunkList)])
#        cnt = 0
#        for elem in chunkList:
#            try: 
#                val = artDict[elem]
#                numAppears[cnt] = val
#                cnt += 1
#            except KeyError:
#                break
#        if np.min(numAppears) > 0:
#            #print '%s \t %s ' %(syn, np.min(numAppears))
#            retTuple = (s.neuron_set.all()[0], np.min(numAppears))
#            containingNeuronList.append(retTuple)
##            containingNeuronList.append(s.neuron_set.all()[0])
##            appearsList.append(np.min(numAppears))
##            containingNeuronList.append(s.neuron_set.all()[0])
##            appearsList.append(np.min(numAppears))
#    containingNeuronList = list(set(containingNeuronList))
#    sortedTuple = sorted(containingNeuronList, key=lambda a: -a[1])
##    print sortedTuple
#    return sortedTuple
    

