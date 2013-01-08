# -*- coding: utf-8 -*-
"""
Created on Tue Nov 08 16:26:12 2011

@author: Shreejoy
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Nov 07 12:38:43 2011

@author: Shreejoy
"""

import urllib, urllib2, sys
from xml.etree.ElementTree import XML

def chunker(seq, size):
    return (seq[pos:pos + size] for pos in xrange(0, len(seq), size))

#query = '("Na(v)"[TIAB] OR "Nav"[TIAB]) AND "1.1"[TIAB] AND "Purkinje"[TIAB] AND ("neuron"[TIAB] OR "neurons"[TIAB])'
query = '("Na(v)"[TIAB] OR "Nav"[TIAB]) AND "1.1"[TIAB] AND "granule"[TIAB]'
#"ion channels"[mh] AND "neurons"[mh] AND ("mice"[mh] OR "rats"[mh])

esearch = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=xml&retmax=10000000&term=%s' % (query)
handle = urllib.urlopen(esearch)
data = handle.read()

root = etree.fromstring(data)
ids = [x.text for x in root.findall("IdList/Id")]
print 'Got %d articles' % (len(ids))

for group in chunker(ids, 100):
    efetch = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?&db=pubmed&retmode=xml&id=%s" % (','.join(group))
    handle = urllib.urlopen(efetch)
    data = handle.read()

    root = etree.fromstring(data)
    for article in root.findall("PubmedArticle"):
        pmid = article.find("MedlineCitation/PMID").text
        year = article.find("MedlineCitation/Article/Journal/JournalIssue/PubDate/Year")
        title = article.find("MedlineCitation/Article/ArticleTitle").text
        meshHeadingList = article.findall("MedlineCitation/MeshHeadingList")
        if year is None: year = 'NA'
        else: year = year.text
        aulist = article.findall("MedlineCitation/Article/AuthorList/Author")
        #print pmid, year, len(aulist)
        print title
#
#Na<sub>v</sub>1.1
#Na<sub>v</sub>1.2
#Na<sub>v</sub>1.3
#Na<sub>v</sub>1.4
#Na<sub>v</sub>1.5
#Na<sub>v</sub>1.6
#Na<sub>v</sub>1.7
#Na<sub>v</sub>1.8
#Na<sub>v</sub>1.9
#
#Olfactory bulb (main) granule cell

#query = '("Na(v)1.1"[TIAB] OR "Nav1.1"[TIAB]) AND "Purkinje"[TIAB]'
#
#RNA[Title] OR "ribonucleic acid"[Title]) AND ("2009"[Publication Date] : "2009"[Publication Date])'
#
#(Na(v)1.1 OR Nav1.1) AND cerebellum

#currID = "21463282"
#efetch = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?&db=pubmed&retmode=xml&id=%s" % (currID)
#handle = urllib.urlopen(efetch)
#data = handle.read()
#root = ET.fromstring(data)
#ids = [x.text for x in root.findall("Abstract/AbstractText")]
#abst = [x.text for x in root.findall("AbstractText/AbstractText")]
#
#    for article in root.findall("PubmedArticle"):
#        abstract = article.find("MedlineCitation/Article/Abstract/AbstractText").text