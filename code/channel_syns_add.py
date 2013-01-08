# -*- coding: utf-8 -*-
"""
Created on Mon Mar 19 13:37:35 2012

@author: Shreejoy
"""

import os
import django_startup
import re
from matplotlib.pylab import *
#run django_startup
os.chdir('C:\Python27\Scripts\Biophys\Biophysiome')
from neuroelectro.models import Protein, ProteinSyn, SuperProtein
os.chdir('C:\Python27\Scripts\Biophys')


chanList = channelpedia_channel_listtxt

for i in range(len(chanList)):
    chanName = chanList[i][0]
    geneName = chanList[i][2]
    newSynNames = chanList[i][1].split()
    if geneName != '':
        newSynNames.append(chanList[i][2])
    newSynNames = [re.sub(r'_', ' ', syn) for syn in newSynNames]
    newSynNamesCheck = [syn.lower() for syn in newSynNames]
    setdiff = set(newSynNamesCheck)
    print setdiff
    # check whether gene already exists in AllenDB as a Protein
    query = Protein.objects.filter(gene__iexact = geneName)
    if len(query) == 0:
        # add channel as a SuperProtein - ie not a gene coding protein
        ic = SuperProtein.objects.get_or_create(name = chanName, is_channel = True)[0]
    else:
        # add channel as an existing protein
        ic = query[0]
        ic.common_name = chanName
        ic.is_channel = True
    for syn in setdiff:
        synOb = ProteinSyn.objects.get_or_create(term = syn)[0]
        ic.synonyms.add(synOb)
#        print syn
    ic.save()

        
#        print 'existing channel: ' + chanName
#        ic = query[0]
#        retrievedChans.append(ic)
#        # match synonyms
#        oldSynonyms = IonChannelSyn.objects.filter(ionchannel = query[0])
#        oldSynNames = [syn.term for syn in oldSynonyms]
#        newSynNames = chanList[i][1].split()
#        if chanList[i][2] != '':
#            newSynNames.append(chanList[i][2])
#        newSynNames = [re.sub(r'_', ' ', syn) for syn in newSynNames]
#        newSynNamesCheck = [syn.lower() for syn in newSynNames]
#        setdiff = set(newSynNamesCheck).difference(set(oldSynNames))
##        setdiff = set(newSynNamesCheck)
##        ic.synonyms = []
#        # add setdiff to synonyms list
#        synObList = []
#        print 'with synonyms: '
#        for syn in setdiff:
#            synOb = IonChannelSyn.objects.get_or_create(term = syn)[0]
#            ic.synonyms.add(synOb)
#            synObList.append(synOb)
#            print syn
#        # add gene
#        if ic.gene == None and chanList[i][2] != '':
#            ic.gene = chanList[i][2]
#        ic.save()
#        
#chanList = channelpedia_channel_listtxt
#retrievedChans = []
#for i in range(len(chanList)):
#    chanName = chanList[i][0]
#    query = IonChannel.objects.filter(name__exact = chanName)
#    if len(query) == 0:
#        # add channel
#        print 'adding channel: ' + chanName
#        ic = IonChannel.objects.create(nlexID = 0, name = chanName)
#        newSynNames = chanList[i][1].split()
#        if chanList[i][2] != '':
#            newSynNames.append(chanList[i][2])
#        newSynNames = [re.sub(r'_', ' ', syn) for syn in newSynNames]
#        newSynNamesCheck = [syn.lower() for syn in newSynNames]
#        # add setdiff to synonyms list
#        synObList = []
#        print 'with synonyms: '
#        for syn in newSynNamesCheck:
#            synOb = IonChannelSyn.objects.get_or_create(term = syn)[0]
#            synObList.append(synOb)
#            print syn
#        ic.synonyms = synObList
#        ic.save()  