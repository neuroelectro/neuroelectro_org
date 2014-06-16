# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 11:13:40 2012

@author: Shreejoy
"""
import re
from xml.etree.ElementTree import XML
from urllib2 import urlopen
from urllib import quote
import nltk

# define channels, neurons and their synonyms
channelDict = {}
channelDict['HCN1'] = [u'hcn1', u'bcng1', u'hac2', u'hac-2', u'ih1', u'bcng-1']
channelDict['HCN2'] = [u'hcn2', u'bcng2', u'hac1', u'ih2']
channelDict['Kv1.1'] = [u'kv1.1', u'huk(i)', u'rck1', u'rbk1', u'mk1', 
                        u'mbk1', u'hbk1', u'kcna1', u'kcpvd', u'k(v)1.1']
channelDict['Kv4.2'] = [u'kv4.2', u'rk5', u'shal1', u'kcnd2', u'k(v)4.2']
channelDict['Nav1.6'] = [u'nav1.6', u'pn4', u'scn8a', u'ceriii', u'nach6', u'na(v)1.6']
neuronDict = {}
neuronDict['Thalamus relay cell'] = [u'thalamocortical cell', u'thalamocortical neuron', u'thalamus relay cell',
                                     u'thalamic relay neuron', u'thalamus relay neuron']
neuronDict['Hippocampus CA3 pyramidal cell'] = [u'ca3 pyramidal neuron', u'hippocampal ca3 pyramidal neuron', 
                                                u'ca3 pyramidal cell', u'hippocampus ca3 pyramidal cell']
neuronDict['Hippocampus CA1 pyramidal cell'] = [u'hippocampus ca1 pyramidal cell', u'hippocampal ca1 pyramidal neuron', 
                                                u'hippocampal ca1 pyramidal cell', u'ca1 pyramidal neuron']
neuronDict['Cerebellum Purkinje cell'] = [u'corpuscles of purkinje', u"purkinje's corpuscles", u'purkinje cell', u'purkinje neuron', u'cerebellar purkinje neuron', u'cerebellum purkinje cell', u'purkyne cell']
neuronDict['Neostriatum medium spiny neuron'] = [u'striatal spiny neuron', u'striatal medium spiny neuron', u'neostriatum medium spiny neuron', u'neostriatal spiny neuron']

# try an example pubmed search
# this is the base url search string, your specific query goes in the 
# %s term at the end
esearchbase = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=xml&retmax=100000&term=%s'

# define your query, ie this is what you would type into the pubmed search box
queryStr = "(Hippocampus CA3 pyramidal cell) AND HCN1"

# convert query to "url-speak" by adding %'s and whatnot
safeChars = '' # add characters here you don't want url-hashed
queryStrConv = quote(queryStr, safeChars)

# add queryStrConv to esearchbase
fullURL = esearchbase % queryStrConv


handle = urlopen(fullURL) # open the url
data = handle.read() # read the data
xml = XML(data) # convert to an xml object so we can apply x-path search fxns to it
pmidList = [x.text for x in xml.findall('.//Id')] # find xml "Id" elements

# for a specific pubmed id, get the title and abstract

# this is the url base fetch string for fetching data for a particular pmid
efetch = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?&db=pubmed&retmode=xml&id=%s"
pmid = pmidList[0]
link = efetch % (pmid)

# open url and get title and abstract
handle = urlopen(link)
data = handle.read()
xml = XML(data)
title = xml.find('.//ArticleTitle').text

# find all parts of the abstract, and join them together
abstractXML = xml.findall('.//AbstractText') 
if len(abstractXML) > 0:
    abstractList = [x.text for x in abstractXML]
    abstract = ' '.join(abstractList)
    
paperText = '%s %s' % (title, abstract)
print pmid + ' \t' + paperText.encode('ascii', 'ignore') + '\n' # the encode command doesn't print non-ascii chars

# search for specific terms in abstracts
porter = nltk.PorterStemmer() # defines a word-stemmer
stopwords = nltk.corpus.stopwords.words('english') # defines a list of common words (a, the, etc.)

paperSplit = paperText.lower().split() #convert text to lower case, and split words based on whitespace
                                        # note that we could use nltk.word_tokenize(text), but it seems to split more than I'd like

paperSplit = [elem.strip(' .,:()/[]-"') for elem in paperSplit] #removes leading or trailing useless chars
paperStemmed = [porter.stem(elem) for elem in paperSplit] # stems each word using a stemmer

# make a dictionary with unique stems as keys and stem frequency as values
artDict = dict([[y,paperStemmed.count(y)] for y in set(paperStemmed)])

# some more examples with nltk you may find helpful

# find sentences in a block of text
sentences = nltk.sent_tokenize(paperText)

# tag the words in a sentence according to their part of speech (noun, verb, etc)
# look here for more info: http://nltk.googlecode.com/svn/trunk/doc/book/ch05.html
sentence = 'Here we report that HCN1 channels also constrain CA1 distal dendritic Ca2+ spikes, which have been implicated in the induction of LTP at distal excitatory synapses.'
sentenceSplit = sentence.split() # split sentence first
nltk.pos_tag(sentenceSplit)


# pubmed esearch code to get all titles and abstracts for a neuron - channel pair
channelName = channelDict.keys()[0]
neuronName = neuronDict.keys()[0]

pmidListAll = []
for nsyn in neuronDict[neuronName]:
    nsynStr = re.sub(' ', ' AND ', nsyn) # replace white spaces in neuron syn with ANDs for pubmed
    for csyn in channelDict[channelName]:
        queryStr = "%s AND %s" % (nsynStr, csyn)
        queryStrConv = quote(queryStr, safeChars)
        fullURL = esearchbase % queryStrConv
        handle = urlopen(fullURL) # open the url
        data = handle.read() # read the data
        xml = XML(data) # convert to an xml object so we can apply x-path search fxns to it
        pmidList = [x.text for x in xml.findall('.//Id')] # find xml "Id" elements
        pmidListAll.extend(pmidList)

pmidList = list(set(pmidListAll))
# for a specific pubmed id, get the title and abstract

# this is the url base fetch string for fetching data for a particular pmid
efetch = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?&db=pubmed&retmode=xml&id=%s"

# add pmid to efecth base
for pmid in pmidList:
#    pmid = '18155692'
    link = efetch % (pmid)
    
    # open url and get title and abstract
    handle = urlopen(link)
    data = handle.read()
    xml = XML(data)
    title = xml.find('.//ArticleTitle').text
    
    abstractXML = xml.findall('.//AbstractText') # there may be multiple parts of the abstract
    if len(abstractXML) > 0:
        abstractList = [x.text for x in abstractXML]
        abstract = ' '.join(abstractList)
        
    paperText = '%s %s' % (title, abstract)
    print pmid + ' \t' + paperText.encode('ascii', 'ignore') + '\n'

# your assignment: for the following neuron-channel pairs
# 1. Find abstracts associated with each neuron-channel pair
# 2. Manually score each returned abstract based on whether the abstract 
    # provides evidence for that neuron expressing that channel (use your best judgement)
    # note relevant things that you observe, for example if a particular synonym is too permissive
# 3. Write an algorithm to programmitcally filter the results returned 
    # by pubmed to increase the precision (defined below)
    # explain clearly the rationale behind your algorithm,
    # if you try multiple things explain the algorithms you tried 
    # and why you ultimately chose the final one
# 4. Compare the results of your algorithm to your manual scores by computing
    # the precision and recall: http://en.wikipedia.org/wiki/Precision_and_recall#Definition_.28classification_context.29
# 5. enter all this data as code like the example below

# create a dictionary with key = pmid and value = tuple with first element your 
# manual score of the title + abstract and second element the score of your algorithm
Cerebellum_Purkinje_cell_HCN1_dict = {}
Cerebellum_Purkinje_cell_HCN1_dict['19591835'] = (0, 1)
Cerebellum_Purkinje_cell_HCN1_dict['20511331'] = (0, 1)
Cerebellum_Purkinje_cell_HCN1_dict['20303332'] = (0, 1)
Cerebellum_Purkinje_cell_HCN1_dict['14651847'] = (1, 1)
Cerebellum_Purkinje_cell_HCN1_dict['17056011'] = (0, 1)
Cerebellum_Purkinje_cell_HCN1_dict['22091830'] = (0, 1)
Cerebellum_Purkinje_cell_HCN1_dict['15869503'] = (0, 1)
Cerebellum_Purkinje_cell_HCN1_dict['21772812'] = (1, 1)
Cerebellum_Purkinje_cell_HCN1_precision = .25
Cerebellum_Purkinje_cell_HCN1_recall = 1

# Hippocampus_CA1_pyramidal_cell and Kv4.2, ~20 abstradts
Hippocampus_CA1_pyramidal_cell_Kv4_dict = {}

# Hippocampus_CA3_pyramidal_cell and Kv4.2, ~4 abstrats
Hippocampus_CA3_pyramidal_cell_Kv4_dict = {}

# Hippocampus_CA3_pyramidal_cell and Kv1.1, ~9 abstracts
Hippocampus_CA3_pyramidal_cell_Kv1_dict = {}

# Cerebellum Purkinje cell and HCN2, ~4 abstracts
Cerebellum_Purkinje_cell_HCN2_dict = {}

# Thalamus_relay_cell and Kv1.1, ~2 abstracts
Thalamus_relay_cell_Kv1_dict = {}

# Neostriatum_medium_spiny_neuron and Kv1.1, ~2 abstracts
Neostriatum_medium_spiny_neuron_Kv1_dict = {}


