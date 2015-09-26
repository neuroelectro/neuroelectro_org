# -*- coding: utf-8 -*-
"""
Created on Mon Apr 16 11:12:31 2012

@author: Shreejoy
"""

import nltk
import neuroelectro.models as m

porter = nltk.PorterStemmer()
#stopwords = nltk.corpus.stopwords.words('english')

def getSynStemList():
    synsStemList= []
    neuronSyns = m.NeuronSyn.objects.all()
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


