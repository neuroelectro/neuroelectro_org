# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 09:09:02 2012

@author: Shreejoy
"""

#check ion channel synonyms for collisions
import re
import os
import django_startup
#run django_startup
os.chdir('C:\Python27\Scripts\Biophys\pubdb\pubdir')
from pubapp.models import IonChannel, IonChannelSyn
os.chdir('C:\Python27\Scripts\Biophys')
from matplotlib.pylab import *

ics = IonChannel.objects.all()
icNames = []
synList = []
for i in range(len(ics)):
    icName = ics[i].name
    synObs = IonChannelSyn.objects.filter(ionchannel = ics[i])
    synStr = u''
    for j in range(len(synObs)):
        syn = synObs[j].term
        syn = re.sub(r'\s', r'_', syn)
        synStr = synStr + ' ' + syn
    print icName + ' ' + synStr
    icNames.append(icName)
    synList.append(synStr)
#    icSynTuple(i) = icName, synStr
#    icSynTuple(i,1) = icName
#    icSynTuple(i,2) = synStr
    
allSynNames = [x.term.lower().strip() for x in IonChannelSyn.objects.all()]
uniqueSyns = list(set(allSynNames))
#mat = zeros([len(neurons), len(channelNameList)])
ics = IonChannel.objects.filter(gene__isnull = False)
icNames = [x.name for x in ics]
mat = zeros([len(icNames), len(uniqueSyns)])
for i in range(len(icNames)):
    icName = ics[i].name
    synObs = IonChannelSyn.objects.filter(ionchannel = ics[i])
    
    for j in range(len(synObs)):
        syn = synObs[j].term.lower().strip()
        ind = uniqueSyns.index(syn)
        mat[i,ind] = 1

for i in range(mat.shape[1]):
    if mat[:,i].sum() > 1:
        print uniqueSyns[i]
        inds = mat[:,i].nonzero()[0]
#        uniqueSyns[array(inds, int)]
        print [icNames[ind] for ind in inds]
#        print uniqueSyns[inds]
    
        
     
