# -*- coding: utf-8 -*-
"""
Created on Tue Jan 24 16:43:31 2012

@author: Shreejoy
"""
import os
import django_startup
from matplotlib.pylab import *
#run django_startup
os.chdir('C:\Python27\Scripts\Biophys\pubdb\pubdir')
from pubapp.models import BrainRegion, InSituExpt, IonChannel, RegionExpr
from pubapp.models import Neuron, NeuronChanExpr, NeuronChanEvid
os.chdir('C:\Python27\Scripts\Biophys')
from django.db import transaction

neurons = list(set(Neuron.objects.filter(regions__isallen = True)))
channels = list(set(IonChannel.objects.filter(insituexpt__isnull = False)))

ncExprMat = zeros([len(neurons), len(channels)])
ncAbMat = zeros([len(neurons), len(channels)])
for i in range(len(neurons)):
    for j in range(len(channels)):
        query = NeuronChanExpr.objects.filter(neuron = neurons[i], ionchannel = channels[j])
        if len(query) != 0:
            exprOb = query[0]
            ncExprMat[i,j] = exprOb.val
        
        query = NeuronChanEvid.objects.filter(neuron = neurons[i], ionchannel = channels[j])
        if len(query) != 0:
            evidOb = query[0]
            ncAbMat[i,j] = evidOb.numarticles
        

        
