# -*- coding: utf-8 -*-
"""
Created on Sun Jun 02 12:33:54 2013

@author: Shreejoy
"""

# code to import shawn's annotation of OB data


from xml.etree.ElementTree import XML
from urllib import quote_plus, quote
from urllib2 import Request, urlopen, URLError, HTTPError
import neuroelectro.models as m
# get article

def add_data():
	pmidList = get_pmid_from_str(in_str)
	pmid = pmidList[0]

	# create article object with pmid
	a = add_single_article_full(pmid)
	neuron_type = table[i][5]
	n = m.Neuron.objects.filter(name = neuron_type)[0]
	user = m.User.objects.get(username = 'ShawnBurton') 

	# check if any data tables which include an ncm with this neuron?

	# create a user_submission object
	us_ob = m.UserSubmission.objects.get_or_create(article = a, user = user)

	# create a ncm object
	ncm_ob = m.NeuronConceptMap.objects.get_or_create(source = us_ob, neuron = n, added_by = user)
	
	# create an ecm object for each listed ephys prop
	ecm_ob = m.EphysConceptMap.objects.get_or_create(source = us_ob, ephys_prop = e, added_by = user)




def get_pmid_from_str(in_str):
    search_str = quote_plus(in_str)
    print search_str
    searchLink = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=%s' % (search_str)
    try:
        handle = urlopen(searchLink)   
        data = handle.read() 
        xml = XML(data) # convert to an xml object so we can apply x-path search fxns to it
        pmidList = [x.text for x in xml.findall('.//Id')] # find xml "Id" elements
        if len(pmidList) > 1:
            pmidList = []
    except Exception, e:
        pmidList = []
    return pmidList
# 