# -*- coding: utf-8 -*-
"""
Created on Sat Dec 03 15:46:54 2011

@author: Shreejoy
"""

from pubapp.models import Neuron, Synonym, Article
from nltk import *
# search all articles which include the term HCN1 in the text
#
#Synonym.objects.filter(IonChannel)
#articles = Article.objects.filter(abstract__icontains='HCN4')
#
#ionChanSyns = Synonym.objects.filter(ionchannel__name__isnull=False)
#[ionChanNames.append(syn.term) for syn in ionChanSyns]
#
#neuronSyns = Synonym.objects.filter(neuron__name__isnull=False)
#
#ionChanNames = []
#[ionChanNames.append(ionChannel.name) for ionChannel in IonChannel.objects.all()]
#
#ionChanSyns = ionChanNames.append(ionChanSyns)
porter = nltk.PorterStemmer()

# for each article stem and then search stemmed against list of neurons
articles = Article.objects.all()
articleCnt = 0
articleNeuronList = []
for article in articles:
    text = article.title + ' ' + article.abstract
    stemmed = tok_stem(text)
    # check if article contains of the neurons
    neuronInd = 0
    neuronSet = set()
    for neuronTerms in neuronTermList:
        for syns in neuronTerms:
            if set(syns).issubset(set(stemmed)):
                neuronSet.add(neuronInd)
                flag = True
#                print article.title
#                print syns                
                #neuronSet.append(neuronInd)
        neuronInd += 1
    articleNeuronList.append(neuronSet)
    articleCnt += 1
#    if flag is True:
#        cnt += 1
        
# generate neuronTermList, a matrix of neuron synonyms
neuronTermList = []
for neuron in Neuron.objects.all():
    name = neuron.name
    synonyms = Synonym.objects.filter(neuron__name__exact=name)
    synList = []
    for syn in synonyms:
        # stem and toeknize each syn
        stems = tok_stem(syn.term)
        synList.append(stems)
    synList.append(tok_stem(name))
    neuronTermList.append(synList)
    
# add neurons
cnt = 0
arts = []
for i in range(len(articleNeuronList)):
    for neuronInd in articleNeuronList[i]:
        neuron = Neuron.objects.get(pk = neuronInd + 1)
        a = Article.objects.get(pk = i + 1)
        neuron.articles.add(a)
        
    
def tok_stem(inp):
#    stopwords = nltk.corpus.stopwords.words('english')
#    text = [w for w in inp if w.lower() not in stopwords]
    inp = re.sub(r'[()/]', r' ', inp)
    tokens = nltk.word_tokenize(inp.lower())
    stems = [porter.stem(t) for t in tokens]
    return stems
    
