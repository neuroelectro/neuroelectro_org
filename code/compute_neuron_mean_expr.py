# -*- coding: utf-8 -*-
"""
Created on Tue Jan 24 15:31:29 2012

@author: Shreejoy
"""
import os
import django_startup
from matplotlib.pylab import *
#run django_startup
os.chdir('C:\Python27\Scripts\Biophys\pubdb\pubdir')
from pubapp.models import BrainRegion, InSituExpt, IonChannel, RegionExpr
from pubapp.models import Neuron, NeuronChanExpr
os.chdir('C:\Python27\Scripts\Biophys')
from django.db import transaction

# compute average expression for each neuron which is assigned to an allen region
def compute_neuron_expr():
    with transaction.commit_on_success():
        neurons = list(set(Neuron.objects.filter(regions__isallen = True)))
        channels = list(set(IonChannel.objects.filter(insituexpt__isnull = False)))
        neuronExprMat = zeros([len(neurons), len(channels)])
        neuronCnt = 0
        for n in neurons:
            print n
            regions = BrainRegion.objects.filter(neuron = n)
            chanCnt = 0
            for c in channels:
#                print c.name
                regExprArray = zeros([len(regions)])
                voxelNums = zeros([len(regions)])
                regCnt = 0
                for region in regions:
#                    print region.name
                    # find insitu expt expr for this region and this channel
                    expts = InSituExpt.objects.filter(ionchannel = c)
                    exptExprArray = zeros([len(expts)])
                    cnt = 0
                    for expt in expts:
                        query = RegionExpr.objects.filter(insituexpt = expt, region = region)
                        if len(query) == 0:
                            exptExprArray[cnt] = -1
                            cnt += 1               
                            print 'could not find %s , skipping' % (expt)
                            continue
                        regExpr = query[0]
                        exptExprArray[cnt] = regExpr.val
                        cnt += 1
                    exptExprArray = exptExprArray.compress((exptExprArray>-1).flat)
                    meanExptExpr = mean(exptExprArray)
                    regExprArray[regCnt] = meanExptExpr
                    voxelNums[regCnt] = len(region.voxelinds)
                    regCnt += 1
#                print regExprArray
                meanNeuronExpr = mean(regExprArray * (voxelNums/sum(voxelNums)))
                neuronExprMat[neuronCnt, chanCnt] = meanNeuronExpr
                # add object for neuronChanExpr
                nce = NeuronChanExpr.objects.get_or_create(neuron = n, ionchannel = c)[0]
                nce.val = meanNeuronExpr
                nce.save()
                chanCnt += 1
            neuronCnt += 1
        return neuronExprMat

        

            
            
        