# -*- coding: utf-8 -*-
"""
Created on Wed Feb 08 17:23:54 2012

@author: Shreejoy
"""
import re
import os
import django_startup
import nltk
#run django_startup
os.chdir('C:\Python27\Scripts\Biophys\pubdb\pubdir')
from pubapp.models import Neuron, Article, IonChannel, NeuronSyn
from pubapp.models import ArticleNeuronTag, IonChannelSyn, ArticleIonChannelTag
os.chdir('C:\Python27\Scripts\Biophys')
import tag_articles
import numpy as np

neuron = Neuron.objects.get(name = 'Hippocampus CA1 pyramidal cell')
channel = IonChannel.objects.get(name = 'HCN1')
ca1Arts = Article.objects.filter(neuronchanevid__neuron__name = 'Hippocampus CA1 pyramidal cell',
                                 neuronchanevid__ionchannel = channel)
ca3Arts = Article.objects.filter(neuronchanevid__neuron__name = 'Hippocampus CA3 pyramidal cell',
                                 neuronchanevid__ionchannel = channel)
nsyns = NeuronSyn.objects.filter(neuron = neuron)

#In [17]: x = ['a','b','a','b','c','b']

channels = IonChannel.objects.all()
neurons = Neuron.objects.all()
#arts = Article.objects.all()[39000:39100]
porter = nltk.PorterStemmer()
stopwords = nltk.corpus.stopwords.words('english')

arts = Article.objects.all()[700:800]
for a in arts:
    
    # split article
    atext = u'%s %s' % (a.title, a.abstract)
    print atext.encode('ascii', 'ignore')
#    atext = a.title + u' ' + a.abstract
    asplit = atext.lower().split()
    asplit = [elem.strip(' .,:()/[]-"') for elem in asplit]
    asplit = [porter.stem(elem) for elem in asplit]
    x = asplit
    artDict = dict([[y,asplit.count(y)] for y in set(asplit)])
    for n in neurons:       
        nsyns = n.synonyms.all()
        for s in nsyns:
            syn = s.term
            chunkList = syn.lower().split()
            chunkList = [porter.stem(elem) for elem in chunkList]
            numAppears = np.zeros([len(chunkList)])
            cnt = 0
            for elem in chunkList:
                try: 
                    val = artDict[elem]
                    numAppears[cnt] = val
                    cnt += 1
                except KeyError:
                    break
            if np.min(numAppears) > 0:
                print '%s \t %s ' %(syn, np.min(numAppears))
    for c in channels:
        
        csyns = IonChannelSyn.objects.filter(ionchannel = c)
        cSynList = [syn.term.strip(' .,:()/[]-"') for syn in csyns]
        for s in csyns:
            try:
                print '%s \t %s ' %(s.term, artDict[s.term])
            except KeyError:
    #            print '%s %s ' %(c.term, 0)
                continue
        
    print '\n'  
        


#
#ca1AbStr = u''
#for art in ca1Arts:
#    try:
#        ca1AbStr = ca1AbStr + u' ' + art.title + u' ' + art.abstract
#    except TypeError:
#        continue
#    
#ca3AbStr = u''
#for art in ca3Arts:
#    try:
#        ca3AbStr = ca3AbStr + u' ' + art.title + u' ' + art.abstract
#    except TypeError:
#        continue
    
porter = nltk.PorterStemmer()
stopwords = nltk.corpus.stopwords.words('english')
def remove_stopwords(inp):
    text = [w for w in inp if w.lower() not in stopwords]
    return text
    
def tok_stem(inp):
    text = re.sub(r'[/]', r' ', inp)
    text = re.sub(r'[()]', r'', inp)
    tokens = nltk.word_tokenize(text.lower())
    tokens = remove_stopwords(tokens)
    stems = [porter.stem(t) for t in tokens]
    return stems
    
#fdist = nltk.FreqDist([w.lower() for w in ca3Arts])
#ca3Stemmed = tok_stem(ca3AbStr)
#ca1Stemmed = tok_stem(ca1AbStr)