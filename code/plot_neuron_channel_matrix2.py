# -*- coding: utf-8 -*-
"""
Created on Tue Jan 24 21:11:46 2012

@author: Shreejoy
"""

from pylab import figure, cm
from matplotlib.colors import LogNorm
import re
import os
import django_startup
from math import *
import numpy as np
from urllib import urlencode
os.chdir('C:\Python27\Scripts\Biophys\pubdb\pubdir')
from pubapp.models import Neuron, Article, IonChannel, NeuronSyn
from pubapp.models import ArticleNeuronTag, IonChannelSyn, ArticleIonChannelTag
os.chdir('C:\Python27\Scripts\Biophys')


# C = some matrix

neuronNames = [n.name for n in neurons]
channelNames = [n.name for n in channels]

f = figure(figsize=(20.0,10))
ax = f.add_axes([0.17, 0.02, 0.72, 0.79])
axcolor = f.add_axes([0.90, 0.02, 0.03, 0.79])
im = ax.matshow(ncExprMat, norm=LogNorm(vmin=.1, vmax=32))
ax.set_yticks(range(len(neuronNames)))
ax.set_xticks(range(len(channelNames)))
nlabels = ax.set_yticklabels(neuronNames, fontsize = 8) 
clabels = ax.set_xticklabels(channelNames, rotation = 90, fontsize = 8) 
t = [.1, .25, .5, 1.0, 2, 4, 8, 16, 32]
f.colorbar(im, cax=axcolor, ticks=t, format='$%.2f$')
ax.set_aspect(.8)
#set_aspect(aspect, adjustable=None, anchor=None)
f.show()

f = figure(figsize=(20.0,10))
ax = f.add_axes([0.17, 0.02, 0.72, 0.79])
axcolor = f.add_axes([0.90, 0.02, 0.03, 0.79])
im = ax.matshow(ncAbMat, norm=LogNorm(vmin=1, vmax=64))
ax.set_yticks(range(len(neuronNames)))
ax.set_xticks(range(len(channelNames)))
nlabels = ax.set_yticklabels(neuronNames, fontsize = 8) 
clabels = ax.set_xticklabels(channelNames, rotation = 90, fontsize = 8)
t = [1, 2, 4, 8, 16, 32, 64]
ax.set_aspect(.8)
f.colorbar(im, cax=axcolor, ticks=t, format='$%.2f$')
f.show()

ncAbMatAns = anscombe_trans(ncAbMat)
f = figure(figsize=(20.0,10))
ax = f.add_axes([0.17, 0.02, 0.72, 0.79])
axcolor = f.add_axes([0.90, 0.02, 0.03, 0.79])
im = ax.matshow(ncAbMatAns, clim = (-2, 2))
ax.set_yticks(range(len(neuronNames)))
ax.set_xticks(range(len(channelNames)))
nlabels = ax.set_yticklabels(neuronNames, fontsize = 8) 
clabels = ax.set_xticklabels(channelNames, rotation = 90, fontsize = 8)
t = [-2, -1, 0, 1, 2]
ax.set_aspect(.8)
f.colorbar(im, cax=axcolor, ticks=t, format='$%.2f$')
f.show()

figure()
plot(ncAbMatAns.flatten(), log2(ncExprMat.flatten()), '.')
a = ncAbMatAns.flatten()
b = log2(ncExprMat.flatten())
plot(a[a>2], b[a>2], '.')
ind = np.where(b == min(b[a>1]))
ind = 21478
nName = ind / len(channelNames)
cName = (ind % len(channelNames)) - 1
print neuronNames[nName] + ' ' + channelNames[cName]

def anscombe_trans(mat):
    newMat = np.sqrt(ncAbMat+3/8)
    expMat = np.outer(mean(mat,1), mean(mat,0))
    expMat = np.sqrt(expMat + 3/8)
    newMat = newMat - expMat
    return newMat

#    (rows, cols) = shape(mat)
#    newMat = mat.flatten() + 3/8
#    newMat = np.sqrt(newMat)
#    newMat = newMat.reshape(cols, rows)
#    expMat = np.outer(mean(mat,0), mean(mat,1))
#    expMat = np.sqrt(expMat.flatten()+ 3/8).reshape(cols, rows)
#    newMat = newMat - expMat
#    return newMat

ansTresh = 2
m = anscombe_trans(ncAbMat)
itemindex = np.where(m > ansTresh)
m.compress((m > ansTresh).flat)

for i in range(len(itemindex[0])):
    print neuronNames[itemindex[0][i]] + ' : ' + channelNames[itemindex[1][i]]
    print ncExprMat[itemindex[0][i]][itemindex[1][i]]

    print ncEvids[n]
    nce = NeuronChanExpr.objects.filter(neuron = ncEvids[n].neuron, ionchannel = ncEvids[n].ionchannel)
    if len(nce) > 0:
        ncExprs.append(nce[0])
        vals.append(nce[0].val)
        print u'' + unicode(n) + ' ' + unicode(nce[0].val)

# find examples where number of found abstracts is high or low and gene expression 
# is also high or low

ncEvids = NeuronChanEvid.objects.filter(numarticles__gte = 5, ionchannel__in = channels, neuron__in = neurons)
ncExprs = []
vals = []
for n in range(len(ncEvids)):
    print ncEvids[n]
    nce = NeuronChanExpr.objects.filter(neuron = ncEvids[n].neuron, ionchannel = ncEvids[n].ionchannel)
    if len(nce) > 0:
        ncExprs.append(nce[0])
        vals.append(nce[0].val)
        print u'' + unicode(n) + ' ' + unicode(nce[0].val)

# Kca5.1 and CA3 pyramidal cell - low allen expression
# but I don't know why 4 abstracts showed up for these terms...
nce = ncEvids[144]
chanSyns = IonChannelSyn.objects.filter(ionchannel = nce.ionchannel)
arts = Article.objects.filter(neuronchanevid = nce)
for art in arts:
    print art.title
    print art.pmid
    art.abstract

# Kca5.1 and CA3 pyramidal cell - low allen expression
# but I don't know why 4 abstracts showed up for these terms...
nce = ncEvids[59]
chanSyns = IonChannelSyn.objects.filter(ionchannel = nce.ionchannel)
arts = Article.objects.filter(neuronchanevid = nce)
for art in arts:
    print art.title
    print art.pmid
    print art.abstract + '\n'

# good example - Hippocampus CA1 pyramidal cell : Kv1.1
neuronChanEvidOb = ncEvids[4]
neuronSyns = NeuronSyn.objects.filter(neuron = neuronChanEvidOb.neuron)
chanSyns = IonChannelSyn.objects.filter(ionchannel = neuronChanEvidOb.ionchannel)
print "Neuron : %s" % (neuronChanEvidOb.neuron.name)
print neuronSyns
print "Ion channel : %s" % (neuronChanEvidOb.ionchannel.name)
print chanSyns
arts = Article.objects.filter(neuronchanevid = neuronChanEvidOb)
for art in arts:
    print art.title
    print art.pmid
    art.abstract
    print '\n'
    
# bad example - Neostriatum medium spiny neuron : N (Cav2.2)
neuronChanEvidOb = ncEvids[12]
neuronSyns = NeuronSyn.objects.filter(neuron = neuronChanEvidOb.neuron)
chanSyns = IonChannelSyn.objects.filter(ionchannel = neuronChanEvidOb.ionchannel)
print "Neuron : %s" % (neuronChanEvidOb.neuron.name)
print neuronSyns
print "Ion channel : %s" % (neuronChanEvidOb.ionchannel.name)
print chanSyns
arts = Article.objects.filter(neuronchanevid = neuronChanEvidOb)
for art in arts:
    print art.title
    print art.pmid
    art.abstract
    print '\n'
    
# bad example - Cerebellum Purkinje cell : Kir2.1
neuronChanEvidOb = ncEvids[54]
neuronSyns = NeuronSyn.objects.filter(neuron = neuronChanEvidOb.neuron)
chanSyns = IonChannelSyn.objects.filter(ionchannel = neuronChanEvidOb.ionchannel)
print "Neuron : %s" % (neuronChanEvidOb.neuron.name)
print neuronSyns
print "Ion channel : %s" % (neuronChanEvidOb.ionchannel.name)
print chanSyns
arts = Article.objects.filter(neuronchanevid = neuronChanEvidOb)
for art in arts:
    art.title
    print art.pmid
    art.abstract
    print '\n'

    
