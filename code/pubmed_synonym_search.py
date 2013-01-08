# -*- coding: utf-8 -*-
"""
Created on Thu Jan 19 11:07:47 2012

@author: Shreejoy
"""
import os
import django_startup
from db_add import add_articles
import re
from matplotlib.pylab import *
#run django_startup
os.chdir('C:\Python27\Scripts\Biophys\Biophysiome')
from neuroelectro.models import Neuron, Article, NeuronSyn
from neuroelectro.models import Protein, SuperProtein, ProteinSyn
os.chdir('C:\Python27\Scripts\Biophys')

from xml.etree.ElementTree import XML
from urllib2 import urlopen
from urllib import quote_plus, quote

#query = '"ion+channels"[mh]+AND+"neurons"[mh]+AND+("mice"[mh]+OR+"rats"[mh])'
esearchbase = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=xml&retmax=100000&term=%s'

synTerms = set()
channels = Protein.objects.filter(is_channel = True)
for c in channels:
    synList = ProteinSyn.objects.filter(protein = c)
    synListStrs = [syn.term for syn in synList]
    synTerms = synTerms.union(synListStrs)  

synTerms = list(sort(list(synTerms)))
channelSyns = synTerms

synTerms = set()
channels = SuperProtein.objects.filter(is_channel = True)
for c in channels:
    synList = ProteinSyn.objects.filter(superprotein = c)
    synListStrs = [syn.term for syn in synList]
    synTerms = synTerms.union(synListStrs)  

synTerms = list(sort(list(synTerms)))
channelSyns = synTerms

synTerms = set()
neurons = Neuron.objects.all()
for n in neurons:
    synList = NeuronSyn.objects.filter(neuron = n)
    synListStrs = [syn.term for syn in synList]
    synTerms = synTerms.union(synListStrs)

synTerms = list(sort(list(synTerms)))
neuronSyns = synTerms

# get indicies matching neurons to neuron synonyms
#neurons = Neuron.objects.all()
neuronSynIndList = []
for n in neurons:
    syns = [syn.term for syn in NeuronSyn.objects.filter(neuron = n)]
    print n.name
    print syns
    indList = [neuronSyns.index(term) for term in syns]
    neuronSynIndList.append(indList)

#channels = IonChannel.objects.all()
channelSynIndList = []
for c in channels:
    syns = c.synonyms.all()
#    syns = [syn.term for syn in IonChannelSyn.objects.filter(ionchannel = c)]
    print c.name
    print syns
    indList = [channelSyns.index(syn.term) for syn in syns]
    channelSynIndList.append(indList)

#    
synTerms = channelSyns
channelPmidList = []
channelSynsBad = []
for i in range(len(synTerms)):
    synTerm = synTerms[i]
    if re.search(r'\s', synTerm) is None:
        synTerm = '"'+ synTerm +'"'
#    query = quote_plus(synTerm)
    query = quote(synTerm, ':=/&()?_')
    esearch =  esearchbase % (query)
    handle = urlopen(esearch)
    data = handle.read()
    xml = XML(data)
    pmids = [x.text for x in xml.findall('.//Id')]  
    if len(pmids) == 100000:
        channelSynsBad.append(synTerm)
        print 'bad term: ' + synTerm
    print synTerm
    print len(pmids)
    channelPmidList.append(pmids)


channelsArtNum = [len(x) for x in channelPmidList]
channel_tuples = [(channelSyns[i], channelsArtNum[i]) for i in range(len(channelSyns))]
s = sorted(channel_tuples, key=lambda channel: channel[1])


synTerms = neuronSyns
neuronPmidList = []
neuronSynsBad = []
for i in range(len(synTerms)):
    synTerm = synTerms[i]
    query = quote(synTerm, ':=/&()?_')
    esearch =  esearchbase % (query)
    handle = urlopen(esearch)
    data = handle.read()
    xml = XML(data)
    pmids = [x.text for x in xml.findall('.//Id')]  
    if len(pmids) == 100000:
        neuronSynsBad.append(synTerm)
        print 'bad term: ' + synTerm
    print synTerm
    print len(pmids)
    neuronPmidList.append(pmids)

# make a matrix of neuronsyns by channel syns
ncSynIntNum = zeros([len(neuronPmidList), len(channelPmidList)])
l = []
for i in range(len(neuronPmidList)):
    c = []
    for j in range(len(channelPmidList)):
        if len(neuronPmidList[i]) > 0 and len(channelPmidList[j]) > 0:
            commonPmids = set(neuronPmidList[i]).intersection(set(channelPmidList[j]))
            if len(commonPmids) > 0:
               print neuronSyns[i] + ' ' + channelSyns[j] + ' : ' + str(len(commonPmids)) 
               ncSynIntNum[i][j] = len(commonPmids)
               b = list(commonPmids)
            else:
               b = []
        
        c.append(b)
    
    l.append(c)

ncSynIntPmids = l            
#            ncIntPmids[i][j] = list(commonPmids)
def f(x): return len(x)

flat = [x for sublist in l for x in sublist]
elems = filter(f, flat)

allUniquePmids = set([num for elem in elems for num in elem])
failedArts = add_articles(allUniquePmids)


# make a matrix of neuronsyns by channel syns
ncIntNum = zeros([len(neurons), len(channels)])
l = []
for i in range(len(neurons)):
    neuronInds = neuronSynIndList[i]
    neuronPmids = [neuronPmidList[ind] for ind in neuronInds]
    neuronPmids = set([item for sublist in neuronPmids for item in sublist])
    c = []
    for j in range(len(channels)):
        channelInds = channelSynIndList[j]
        channelPmids = [channelPmidList[ind] for ind in channelInds]
        channelPmids = set([item for sublist in channelPmids for item in sublist])
        if len(neuronPmids) > 0 and len(channelPmids) > 0:
            commonPmids = neuronPmids.intersection(channelPmids)
            if len(commonPmids) > 0:
               print neurons[i].name + ' ' + channels[j].name + ' : ' + str(len(commonPmids)) 
               ncIntNum[i][j] = len(commonPmids)
               b = list(commonPmids)
            else:
               b = []
        
        c.append(b)
    
    l.append(c)

ncIntPmids = l
        

        



        
    

        