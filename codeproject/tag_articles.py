# -*- coding: utf-8 -*-
"""
Created on Wed Dec 07 18:34:22 2011

@author: Shreejoy
"""

# tag articles for neurons and ion channels
import re
import os
import django_startup
import nltk
#run django_startup
os.chdir('C:\Python27\Scripts\Biophys\pubdb\pubdir')
from pubapp.models import Neuron, Article, IonChannel, NeuronSyn
from pubapp.models import ArticleNeuronTag, IonChannelSyn, ArticleIonChannelTag
os.chdir('C:\Python27\Scripts\Biophys')

porter = nltk.PorterStemmer()
stopwords = nltk.corpus.stopwords.words('english')

def tok_stem(inp):
    text = re.sub(r'[/]', r' ', inp)
    text = re.sub(r'[()]', r'', inp)
    tokens = nltk.word_tokenize(text.lower())
    tokens = remove_stopwords(tokens)
    stems = [porter.stem(t) for t in tokens]
    return stems

def remove_stopwords(inp):
    text = [w for w in inp if w.lower() not in stopwords]
    return text

def tag_neurons(article, neurons):
    articleText = article.title + ' ' + article.abstract
    stemmedArticle = tok_stem(articleText)
    for neuron in neurons:
        synonymObs = NeuronSyn.objects.filter(neuron = neuron)
        synList = [tok_stem(synOb.term) for synOb in synonymObs]
        foundSyns = []
        cnt = 0
        for syn in synList:
            if set(syn).issubset(set(stemmedArticle)):
                foundSyns.append(synonymObs[cnt])
            cnt += 1
        if foundSyns:
            print neuron, foundSyns
            t = ArticleNeuronTag.objects.create(neuron = neuron, article = article)
            t.foundsyns = foundSyns
            t.save()

def tag_ionchannels(article, channels):
    articleText = article.title + ' ' + article.abstract
    stemmedArticle = tok_stem(articleText)
    for channel in channels:
        synonymObs = IonChannelSyn.objects.filter(ionchannel = channel)
        synList = [tok_stem(synOb.term) for synOb in synonymObs]
        foundSyns = []
        cnt = 0
        for syn in synList:
            if set(syn).issubset(set(stemmedArticle)):
                foundSyns.append(synonymObs[cnt])
            cnt += 1
        if foundSyns:
            print channel, foundSyns
            t = ArticleIonChannelTag.objects.create(ionchannel = channel, article = article)
            t.foundsyns = foundSyns
            t.save()

# for each article stem and then search stemmed against list of neurons
def tag_all_articles():
    articles = Article.objects.all()
    neurons = Neuron.objects.all()
    channels = IonChannel.objects.all()
    articleCnt = 1
    articleNeuronList = []
    for i in range(articleCnt, len(articles)):
        article = articles[i]
        print article
        tag_neurons(article, neurons)
        tag_ionchannels(article, channels)
        print i, ' of ' , str(len(articles)) , ' articles \n'
        

#    tag_ionchannels(article, channels)
    # check if article contains of the neurons
#    neuronInd = 0
#    neuronSet = set()
#    for neuronTerms in neuronTermList:
#        for syns in neuronTerms:
#            if set(syns).issubset(set(stemmed)):
#                neuronSet.add(neuronInd)
#                flag = True
##                print article.title
##                print syns                
#                #neuronSet.append(neuronInd)
#        neuronInd += 1
#    articleNeuronList.append(neuronSet)
#    articleCnt += 1
#    if flag is True:
#        cnt += 1
#        
## generate neuronTermList, a matrix of neuron synonyms
#neuronTermList = []
#for neuron in Neuron.objects.all():
#    name = neuron.name
#    synonyms = Synonym.objects.filter(neuron__name__exact=name)
#    synList = []
#    for syn in synonyms:
#        # stem and toeknize each syn
#        stems = tok_stem(syn.term)
#        synList.append(stems)
#    synList.append(tok_stem(name))
#    neuronTermList.append(synList)
#    
## add neurons
#cnt = 0
#arts = []
#for i in range(len(articleNeuronList)):
#    for neuronInd in articleNeuronList[i]:
#        neuron = Neuron.objects.get(pk = neuronInd + 1)
#        a = Article.objects.get(pk = i + 1)
#        neuron.articles.add(a)
#            



    
