# -*- coding: utf-8 -*-
"""
Created on Wed Feb 08 13:56:39 2012

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
from numpy import ndarray

#regions = BrainRegion.objects.filter(isallen = True)
#iseObs = InSituExpt.objects.filter(ionchannel__isnull = False, valid = True)
#
#regionNames = [region.name for region in regions]
#geneNames = [iseOb.gene for iseOb in iseObs]
#
#ncExprMat = zeros([len(regions), len(iseObs)])
#ncAbMat = zeros([len(regions), len(iseObs)])
#for i in range(len(regions)):
#    for j in range(len(iseObs)):
#        query = RegionExpr.objects.filter(region = regions[i], insituexpt = iseObs[j])
#        if len(query) != 0:
#            exprOb = query[0]
#            ncExprMat[i,j] = exprOb.val
#        
##        query = NeuronChanEvid.objects.filter(neuron = neurons[i], ionchannel = channels[j])
##        if len(query) != 0:
##            evidOb = query[0]
##            ncAbMat[i,j] = evidOb.numarticles
#
#ises = InSituExpt.objects.filter(ionchannel__isnull = False)
#for ise in ises:
#    if ise.valid is None:
#        ise.valid = True
#        ise.save()
#        
#regQuery = RegionExpr.objects.filter(region__abbrev = 'CA3sp', insituexpt__in = iseObs)
#exprValsAll  = []
#for r in regQuery:
#    exprVals.append(r.val)
#
#meanCA3Expr = get_mean_reg_expr_genes('CA3sp')
#meanCA1Expr = get_mean_reg_expr_genes('CA1sp')
#meanDGExpr = get_mean_reg_expr_genes('DG-sg')


#for d in diffChannelObs:
#    print '%s \t %.2f ' % (d[0].name, d[1])
#print diffChannelObs


def get_mean_reg_expr_genes(region):
#    iseObs = InSituExpt.objects.filter(ionchannel__isnull = False, valid = True)
#    regQuery = RegionExpr.objects.filter(region__abbrev = region, insituexpt__in = iseObs)
    regQuery = RegionExpr.objects.filter(region__abbrev = region)
    exprVals  = []
    for r in regQuery:
        exprVals.append(r.val)
    return mean(exprVals)

def find_diff_genes(reg1, reg2, threshReg1, threshRatio, icFlag, corFlag):
    reg1Ob = BrainRegion.objects.get(abbrev = reg1)    
    if icFlag == True:
        iseList = InSituExpt.objects.filter(ionchannel__isnull = False, regionexprs__region = reg1Ob, regionexprs__val__gte = threshReg1)
    else:
        iseList = InSituExpt.objects.filter(regionexprs__region = reg1Ob, regionexprs__val__gte = threshReg1)
    if corFlag == True:
        iseList = iseList.filter(plane = 'coronal')
    reg1ExprObs = RegionExpr.objects.filter(region__abbrev = reg1, insituexpt__in = iseList)
    reg2ExprObs = RegionExpr.objects.filter(region__abbrev = reg2, insituexpt__in = iseList)
    reg1Exprs = array([r.val for r in reg1ExprObs])
    reg2Exprs = array([r.val for r in reg2ExprObs])
#        if norm == True: 
    ratio = reg1Exprs/reg2Exprs
    h = hist(ratio, 20)
    inds = [i for i,x in enumerate(ratio) if x > threshRatio]
    channelObs = []
    for elem in inds:
        ic = IonChannel.objects.get(insituexpt = iseList[elem])
        channelObs.append((ic, ratio[elem], reg1Exprs[elem], reg2Exprs[elem]))
    print '%s vs %s' % (reg1, reg2)
    print '%s \t %s \t %s \t %s' % ('name', 'ratio', reg1, reg2)
    for d in channelObs:
#        print d
        print '%s \t %.2f \t %.2f \t %.2f' % (d[0].name, d[1], d[2], d[3])
    return channelObs, h
        
def swap_regions(reg1, reg2):
    temp = reg1
    reg1 = reg2
    reg2 = temp
    return reg1, reg2


#reg1 = 'SUBd-sp'
#reg2 = 'CA1sp'

reg1 = 'CA1sp'
reg2 = 'SUBd-sp'

threshReg1 = 2
threshRatio = 1.25
icFlag = True
corFlag = True

#reg1, reg2 = swap_regions(reg1, reg2)

diffChannelObs, h = find_diff_genes(reg1, reg2, threshReg1, threshRatio, icFlag, corFlag)