# -*- coding: utf-8 -*-
"""
Created on Tue Nov 08 16:51:31 2011

@author: Shreejoy
"""

from xml.etree.ElementTree import XML
from urllib2 import urlopen
from pubapp.models import Article, MeshTerm, Substance, Journal

query = '"ion+channels"[mh]+AND+"neurons"[mh]+AND+("mice"[mh]+OR+"rats"[mh])'

esearch = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=xml&retmax=100000&term=%s' % (query)

handle = urlopen(esearch)
data = handle.read()
xml = XML(data)
pmids = [x.text for x in xml.findall('.//Id')]  

cellTypes = [u'granule', u'purkinje', u'mitral', u'tufted', u'blanes', ]

#pmids = ['21903816','21905079']

#pmids = pmids[0:1]
cnt = 1236
oldArts = 0
for article in pmids:
    #check if article already is in db
    if len(Article.objects.filter(pmid = article)) > 0:
        cnt+=1
        oldArts+=1
        print cnt
        continue
    else:
        cnt += 1
        print cnt
    efetch = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?&db=pubmed&retmode=xml&id=%s" % (article)
    handle = urlopen(efetch)    
    data = handle.read()
    xml = XML(data)    
    # does a check whether got from pubmed correctly
    while xml.find('.//ArticleTitle') is None:
        data = handle.read()
        xml = XML(data)
        
    title = xml.find('.//ArticleTitle').text
    
    # generate a new article in db
    a = Article.objects.get_or_create(title=title, pmid = article)[0]
    
    # add journalTitle to article
    journalTitle = xml.find('.//Title')
    if journalTitle is not None:
        j = Journal.objects.get_or_create(title = journalTitle.text)[0]
        a.journal = j
    
    # find mesh terms and add them to db
    for x in xml.findall('.//DescriptorName'):
        m = MeshTerm.objects.get_or_create(term = x.text)[0]
        a.terms.add(m)
    
    # find substances and add them to db
    for x in xml.findall('.//NameOfSubstance'):
        s = Substance.objects.get_or_create(term = x.text)[0]
        a.substances.add(s)    
    
    abstractXML = xml.findall('.//AbstractText')
    if len(abstractXML) > 0:
        abstractList = [x.text for x in abstractXML]
        abstract = ' '.join(abstractList)
    a.abstract = abstract
    a.save()

    
    
    
#    abstractToked = abstract.lower().split()
#    for cellType in cellTypes:
#        if cellType in abstractToked:
#            print title, cellType

#def find_neuron_types():
#    return 1

