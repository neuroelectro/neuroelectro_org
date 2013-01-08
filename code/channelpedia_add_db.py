# -*- coding: utf-8 -*-
"""
Created on Wed Jan 18 17:40:01 2012

@author: Shreejoy
"""
import os
import django_startup
import re
from matplotlib.pylab import *
#run django_startup
os.chdir('C:\Python27\Scripts\Biophys\pubdb\pubdir')
from pubapp.models import Neuron, IonChannel, IonChannelSyn
os.chdir('C:\Python27\Scripts\Biophys')


chanList = channelpedia_channel_listtxt
retrievedChans = []
for i in range(len(chanList)):
    chanName = chanList[i][0]
    query = IonChannel.objects.filter(name__exact = chanName)
    if len(query) == 0:
        # add channel
        print 'adding channel: ' + chanName
        ic = IonChannel.objects.create(nlexID = 0, name = chanName)
        newSynNames = chanList[i][1].split()
        if chanList[i][2] != '':
            newSynNames.append(chanList[i][2])
        newSynNames = [re.sub(r'_', ' ', syn) for syn in newSynNames]
        newSynNamesCheck = [syn.lower() for syn in newSynNames]
        # add setdiff to synonyms list
        synObList = []
        print 'with synonyms: '
        for syn in newSynNamesCheck:
            synOb = IonChannelSyn.objects.get_or_create(term = syn)[0]
            synObList.append(synOb)
            print syn
        ic.synonyms = synObList
        ic.save()                 
    else:
        print 'existing channel: ' + chanName
        ic = query[0]
        retrievedChans.append(ic)
        # match synonyms
        oldSynonyms = IonChannelSyn.objects.filter(ionchannel = query[0])
        oldSynNames = [syn.term for syn in oldSynonyms]
        newSynNames = chanList[i][1].split()
        if chanList[i][2] != '':
            newSynNames.append(chanList[i][2])
        newSynNames = [re.sub(r'_', ' ', syn) for syn in newSynNames]
        newSynNamesCheck = [syn.lower() for syn in newSynNames]
        setdiff = set(newSynNamesCheck).difference(set(oldSynNames))
#        setdiff = set(newSynNamesCheck)
#        ic.synonyms = []
        # add setdiff to synonyms list
        synObList = []
        print 'with synonyms: '
        for syn in setdiff:
            synOb = IonChannelSyn.objects.get_or_create(term = syn)[0]
            ic.synonyms.add(synOb)
            synObList.append(synOb)
            print syn
        # add gene
        if ic.gene == None and chanList[i][2] != '':
            ic.gene = chanList[i][2]
        ic.save()

# remove some common channel synonyms
IonChannelSyn.objects.get(term = ' ')
icRemoveList = ['rat i', '', 'm1', 'brain type i', 'type i channel in t cells', 'brain type ii', 'rat ii', ]
icRemoveList.extend(['sodium channel protein', 'rat 3', 'brain type 3', 'brain ii subunit alpha', 'brain iii subunit alpha'])
icRemoveList.extend(['cardiac or smooth muscle dihydropyridine receptor', 'cardiac or smooth muscle l-type ca channel', 'hi'])
for elem in icRemoveList:
    syn = IonChannelSyn.objects.filter(term = elem)
    if len(syn) > 0:
        syn[0].delete()

            
        
