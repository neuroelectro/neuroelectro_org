# -*- coding: utf-8 -*-
"""
Created on Sat Mar 24 18:16:42 2012

@author: Shreejoy
"""
import os
import django_startup
import struct
import gc
from matplotlib.pylab import *
os.chdir('C:\Python27\Scripts\Biophys\Biophysiome')
from neuroelectro.models import Article, MeshTerm, Substance, Journal
#from pubapp.models import Neuron, IonChannel, NeuronChanEvid
from neuroelectro.models import BrainRegion, InSituExpt, Protein, RegionExpr
os.chdir('C:\Python27\Scripts\Biophys')

#RegionExpr.objects.all().count()

#===============================================================================
# ionChanObs = Protein.objects.filter(is_channel = True)
# iseList = []
# for ic in ionChanObs:
#     ises = ic.in_situ_expts.all()
#     iseList.extend(ises)
#     
# proteins = Protein.objects.all()
# iseList = []
# for p in proteins:
#     ises = p.in_situ_expts.all()
#     iseList.extend(ises)
# 
# exprMat = zeros([len(iseList), numRegions])
# for i in range(len(iseList)):
#     res = iseList[i].regionexprs.all()
#     for re in res:
#         regInd = re.region.pk - 1
#         exprMat[i,regInd] = re.val
# 
# geneNames = []
# for i in range(len(iseList)):
#     geneNames.append(iseList[i].protein_set.get().gene)
#     
# regionNames = []
# brs = BrainRegion.objects.all()
#
#for br in brs:
#    regionNames.append(br.name)
#===============================================================================
#def getExprMat(ises):
#    numRegions = BrainRegion.objects.all().count()
#    numIses = ises.count()
#    exprMat = zeros([numIses, numRegions])
#    cnt = 0
#    for ise in ises.iterator():
#        print cnt
#        exprVec = getExprVec(ise, numRegions)
#        exprMat[cnt,:] = exprVec
#        cnt += 1
#    return exprMat

def getExprVec(ise, numRegions):
    exprVec = zeros([numRegions])
    res = ise.regionexprs.all()
    values = res.values_list('val', flat = True)
    regionInds = res.values_list('region', flat = True)
    exprVec[regionInds-1] = values
    for i in range(len(regionInds)):
        exprVec[regionInds[i]-1] = values[i]
    del res
    del values
    del regionInds
    return exprVec

def getExprMat():
    res = RegionExpr.objects.values_list('val', 'region', 'insituexpt')
    numRes = 23411881#res.count()
    print '%d num total regexpr elements' % numRes
    exprMat = np.empty((25894, 843,))
    exprMat[:] = np.nan
    blockSize = 1000000
    firstInd = 0
    lastInd = blockSize
    blockCnt = 0
    while firstInd < lastInd:
        print '%d of %d blocks ' % (blockCnt, numRes/blockSize)
        for re in res[firstInd:lastInd].iterator():
            iseInd = int(re[2]) - 1
            regInd = int(re[1]) - 1
            val = re[0]
            exprMat[iseInd,regInd] = val
        firstInd = lastInd + 1
        lastInd = min(lastInd+blockSize, numRes)
        blockCnt += 1
    return exprMat

    
    
    
    