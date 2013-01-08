# -*- coding: utf-8 -*-
"""
Created on Thu Aug 30 16:32:04 2012

@author: Shreejoy
"""
import numpy
from neuroelectro.models import Article, MeshTerm, Substance, Journal
from neuroelectro.models import Neuron, NeuronSyn, Unit, Author
from neuroelectro.models import BrainRegion, InSituExpt, Protein, RegionExpr
from neuroelectro.models import DataTable, ArticleFullText, EphysConceptMap
from neuroelectro.models import EphysProp, EphysPropSyn, NeuronEphysLink, NeuronArticleMap
from neuroelectro.models import NeuronConceptMap, NeuronArticleMap, NeuronEphysDataMap

from xml.etree.ElementTree import XML
from urllib import quote_plus, quote
from urllib2 import Request, urlopen, URLError, HTTPError
from xml.etree.ElementTree import XML
#pmids = Article.objects.filter(articlefulltext__isnull = False)
efetch = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?&db=pubmed&retmode=xml&id=%s"
def add_article_authors(articles):
    cnt = 0
    articleCount = articles.count()
    for article in articles:  
        if cnt % 100 == 0:
            print '%d of %d articles' % (cnt, articleCount)
        pmid = article.pmid
        link = efetch % (pmid)
        req = Request(link)
        handle = urlopen(req)    
        data = handle.read()
        xml = XML(data)    
        
        a = article
        
        authorList = xml.findall(".//Author[@ValidYN='Y']")
        for author in authorList:
            try:
                last = author.find("./LastName").text
                fore = author.find("./ForeName").text
                initials = author.find("./Initials").text
                authorOb = Author.objects.get_or_create(first=fore, last=last, initials=initials)[0]
                a.authors.add(authorOb)
            except AttributeError:
                continue
        
#        journalTitle = xml.find('.//Title')
#        if journalTitle is not None:
#            j = Journal.objects.get(title = journalTitle.text)
#            shortJournalTitle = xml.find('.//ISOAbbreviation')
#            if shortJournalTitle is not None and j.short_title is None:
#                j.short_title = shortJournalTitle.text
#                j.save()
#        
#        pub_year = xml.find(".//PubDate/Year")
#        if pub_year is not None:
#            a.pub_year = pub_year
#            a.save()
#        print a
        #a.save()
        #j.save()
        cnt += 1
        
def add_short_titles():
    journals = Journal.objects.all()
    for j in journals:
        art = Article.objects.filter(journal = j)[0]
        pmid = art.pmid
        link = efetch % (pmid)
        req = Request(link)
        handle = urlopen(req)    
        data = handle.read()
        xml = XML(data)
        shortJournalTitleXML = xml.find('.//ISOAbbreviation')
        #print shortJournalTitleXML.text  
        if shortJournalTitleXML is not None and j.short_title is None:
            print shortJournalTitleXML.text  
            j.short_title = shortJournalTitleXML.text   
        j.save()         

def add_dates(articles):
    cnt = 0
    articleCount = articles.count()
    for article in articles:  
        if cnt % 100 == 0:
            print '%d of %d articles' % (cnt, articleCount)
        pmid = article.pmid
        link = efetch % (pmid)
        req = Request(link)
        handle = urlopen(req)    
        data = handle.read()
        xml = XML(data)    
        
        a = article     
        pub_year = xml.find(".//PubDate/Year")
        if pub_year is not None:
            a.pub_year = int(pub_year.text)
            a.save()     
        cnt+=1

