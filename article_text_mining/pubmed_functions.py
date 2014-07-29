'''
Created on Jul 16, 2014

@author: stripathy
'''

import neuroelectro.models as m

from django.db import transaction
from xml.etree.ElementTree import XML, ParseError
from urllib2 import Request, urlopen, URLError, HTTPError
from httplib import BadStatusLine

# TODO: [@Shreejoy] split this up into two functions - one that queries pubmed eutils and one that queries ABA
efetch = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?&db=pubmed&retmode=xml&id=%s"
esummary = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=%s&version=2.0"
def add_articles(pmids):
    if len(pmids) > 5:
        currPmids = [str(article.pmid) for article in m.Article.objects.all()]
        pmids = list(set(pmids).difference(set(currPmids)))
    cnt = 0
    MAXURLTRIES = 5
    print 'adding %u articles into database' % (len(pmids))
    with transaction.commit_on_success():
        failedArts = []
        for article in pmids:
            #check if article already is in db
            if len(m.Article.objects.filter(pmid = article)) > 0:
                cnt += 1
                if cnt % 100 == 0:
                    print '%d of %d articles' % (cnt, len(pmids))
                continue
            else:
                cnt += 1
                add_single_article_full(article)
    return failedArts
    
# adds info for article, first checks if pmid already exists
def add_single_article(pmid):
    MAXURLTRIES = 5
    #check if article already is in db
    if len(m.Article.objects.filter(pmid = pmid)) > 0:
        a = m.Article.objects.get(pmid = pmid)
    else:
        a = add_single_article_full(pmid)
    return a
    
def get_journal(pmid):
    MAXURLTRIES = 5
    numTries = 0
    success = False
    link = esummary % (pmid)
    req = Request(link)
    while numTries < MAXURLTRIES and success == False: 
        try: 
            handle = urlopen(req)
            success = True
        except (URLError, HTTPError, BadStatusLine, ParseError):
            print ' failed %d times' % numTries 
            numTries += 1
    if numTries == MAXURLTRIES:
        journal_title = None 
        return journal_title
    try:                        
        data = handle.read()
        xml = XML(data)    
        journalXML = xml.find('.//FullJournalName')
        if journalXML is not None:
            journal_title = journalXML.text
        else:
            journal_title = None
        return journal_title
    except Exception:
        journal_title = None 
        return journal_title
    
# adds all info for article, doesn't check if already exists
def add_single_article_full(pmid):
    MAXURLTRIES = 5
    numTries = 0
    success = False
    link = efetch % (pmid)
    req = Request(link)
    while numTries < MAXURLTRIES and success == False: 
        try: 
            handle = urlopen(req)
            success = True
        except (URLError, HTTPError, BadStatusLine, ParseError):
            print ' failed %d times' % numTries 
            numTries += 1
    if numTries == MAXURLTRIES:
        a = None 
        return a
    try:                        
        data = handle.read()
        xml = XML(data)    
        titleXML = xml.find('.//ArticleTitle')
        if titleXML is not None:
            title = titleXML.text
        else:
            title = ' '
            
    # generate a new article in db
        a = m.Article.objects.get_or_create(title=title, pmid = pmid)[0]
    except Exception:
        return None
    # add journalTitle to article
    journalTitle = xml.find('.//Title')
    if journalTitle is not None:
        j = m.Journal.objects.get_or_create(title = journalTitle.text)[0]
        a.journal = j
        if j.short_title is None:
            shortJournalTitleXML = xml.find('.//ISOAbbreviation')
            if shortJournalTitleXML is not None:
                j.short_title = shortJournalTitleXML.text 
                j.save()
    
    # add authors to article
    authorList = xml.findall(".//Author[@ValidYN='Y']")
    if len(authorList) == 0:
        authorList = xml.findall(".//Author")
    authorListText = []
    for author in authorList:
        try:
            last = author.find("./LastName").text
            fore = author.find("./ForeName").text
            initials = author.find("./Initials").text
            #print last, fore, initials
            authorOb = m.Author.objects.get_or_create(first=fore, last=last, initials=initials)[0]
            a.authors.add(authorOb)
            currAuthorStr = '%s %s' % (last, initials)
            authorListText.append(currAuthorStr)
        except AttributeError:
            continue  
    author_list_str = '; '.join(authorListText)    
    author_list_str = author_list_str[0:min(len(author_list_str), 500)]
    a.author_list_str = author_list_str         
    
    #get publication year
    pub_year = xml.find(".//PubDate/Year")
    if pub_year is not None:
        a.pub_year = int(pub_year.text)   
    
    # find mesh terms and add them to db
    for x in xml.findall('.//DescriptorName'):
        if x.text is not None:
            mesh = m.MeshTerm.objects.get_or_create(term = x.text)[0]
            a.terms.add(mesh)
    
    # find substances and add them to db
    for x in xml.findall('.//NameOfSubstance'):
        if x.text is not None:
            s = m.Substance.objects.get_or_create(term = x.text)[0]
            a.substances.add(s)    
    
    abstractXML = xml.findall('.//AbstractText')
    abstract = ' '
    if len(abstractXML) > 0:
        abstractList = [x.text for x in abstractXML]
        abstractList = filter(None, abstractList)
        abstract = ' '.join(abstractList)
    a.abstract = abstract

    url = get_article_full_text_url(pmid)
    a.full_text_link = url
    a.save()
    return a
    
def get_article_full_text_url(pmid):
    base_url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&id=%s&cmd=prlinks&retmode=ref'
    url = base_url % pmid
    try:
        req = Request(url)
        res = urlopen(req)
        final_url = res.geturl()
    except Exception:
        final_url = url
    return final_url