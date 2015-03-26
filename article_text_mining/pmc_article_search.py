'''
Created on Oct 6, 2014

@author: stripathy
'''
#import neuroelectro.models as m

from xml.etree.ElementTree import XML, ParseError
from urllib2 import Request, urlopen, URLError, HTTPError
from httplib import BadStatusLine
from urllib import quote
from article_text_mining.pubmed_functions import get_article_full_text_url

esearch = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?&db=pmc&retmode=xml&term=%s&retstart=%d&retmax=%d&sort=relevance"
esummary = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=%s&version=2.0"
safeChars = '' # add characters here you don't want url-hashed

def pmc_article_search():
    id_list = []
    search_string = '((neuron electrophysiology) OR (neurophysiology) OR ("input resistance") OR ("resting potential" OR "resting membrane potential") OR "LTP" OR "synaptic plasticity" OR "LTD")'
    search_string_quoted = quote(search_string, safeChars)
    #print search_string_quoted
    retstart = 0
    retmax = 20
    link = esearch % (search_string_quoted, retstart, retmax)
    req = Request(link)
    handle = urlopen(req)
    data = handle.read()
    xml = XML(data)    
    num_found_articles = 20#int(xml.find('.//Count').text)
    
    while retstart < num_found_articles:
        link = esearch % (search_string_quoted, retstart, retmax)
        req = Request(link)
        handle = urlopen(req)
        data = handle.read()
        #print data
        xml = XML(data)    
        id_list_temp = xml.findall(".//Id")
        if len(id_list_temp) == 0:
            id_list_temp = int(xml.findall(".//Id"))
        for id_elem in id_list_temp:
            id_list.append(int(id_elem.text))
        retstart += retmax
    return id_list

pmc_pmid_url = 'http://www.pubmedcentral.nih.gov/utils/idconv/v1.0/?ids=PMC%d'
def pmc_id_to_pmid(pmc_id_list):
    pmid_list = []
    for pmcid in pmc_id_list:
        link = pmc_pmid_url % (pmcid)
        req = Request(link)
        handle = urlopen(req)
        data = handle.read()
        xml = XML(data) 
        pmid = int(xml.find('record').attrib['pmid'])
        pmid_list.append(pmid)
    return pmid_list

def get_full_text_from_pmid(pmid):
    link = get_article_full_text_url(pmid)
    req = Request(link)
    handle = urlopen(req)
    data = handle.read()
        
        
    