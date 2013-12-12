# -*- coding: utf-8 -*-
"""
NeuroTree Pubmed integration
@author: Shreejoy
"""

import neurotree.models as t
import neuroelectro.models as m
from django.db.models import Q
import sys

from xml.etree.ElementTree import XML, ParseError
from urllib import quote_plus, quote
from urllib2 import Request, urlopen, URLError, HTTPError
from httplib import BadStatusLine
from xml.etree.ElementTree import XML
import json

def pubmed_count_coauthored_papers(author_1, author_2):
    """
    Count number of co-published papers between author_1 and author_2
    
    co-published defined by number of papers in pubmed where author_1 is 
    first author and author_2 is last author
    
    Args:
        author_1 (str): String of first authors name; e.g., Tripathy S
        author_2 (str): String of second authors name; e.g., Urban N
    Returns:
        match_count (int): count of numbers of matching pubmed articles 
    """

    advisee_author_str = author_1
    adviser_author_str = author_2
    esearchlink = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?'+\
                  'db=pubmed&term=%s[Author] AND (%s[Author])'
    efetch = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?'+\
             '&db=pubmed&retmode=xml&id=%s'    
    advisee_last_name = advisee_author_str.split()[0]
    #print advisee_last_name
    adviser_last_name = adviser_author_str.split()[0]
    
    match_count = 0
    link = esearchlink % (advisee_author_str, adviser_author_str)
    linkCoded = quote(link, ':=/&()?_')
    req = Request(linkCoded)        
    handle = urlopen(req)
    data = handle.read()
    xml = XML(data)
    matching_pmids = [xml_ob.text for xml_ob in xml.findall('.//Id')]
    for pmid in matching_pmids:
        link = efetch % (pmid)
        req = Request(link)
        handle = urlopen(req)
        data = handle.read()
        xml = XML(data)   
        authorList = xml.findall(".//Author[@ValidYN='Y']")
        if len(authorList) == 0:
		authorList = xml.findall(".//Author")
        #print authorList
        if len(authorList) > 1:
            #print data
            try:
                first_author_last_name = authorList[0].find("./LastName").text
                #print first_author_last_name
                last_author_last_name = authorList[-1].find("./LastName").text
            except Exception:
                continue
            if first_author_last_name == advisee_last_name 
            and last_author_last_name == adviser_last_name:
                match_count += 1
    #print '%s, %s, matching pubs = %d' % \
    #               (advisee_author_str, adviser_author_str, match_count)
    return match_count

def compute_neurotree_coauthorship_distro(last_author_node_list):
    """
    For each author in input list, count how many papers they co-published with
    mentors as defined in NeuroTree
    
    Definition of co-published as in: pubmed_count_coauthored_papers() above
    
    Args: 
        last_author_node_list (list): A list of neurotree.models.Node instances.  
    Returns:
        A unordered distribution (list) of counts.  
    """

    relationcodes=[1,2] # 1 is grad student; 2 is postdoc.  
    coauthored_pubs = []
    for a_node in last_author_node_list:
        if not a_node:
            continue
        a_node_str = '%s %s' % (a_node.lastname, a_node.firstname[0])
        relations = a_node.parents.filter(relationcode__in=relationcodes)
        parents = [x.node2 for x in relations]
        for p_node in parents:
            p_node_str = '%s %s' %  (p_node.lastname, p_node.firstname[0])
            coauthor_count = pubmed_count_coauthored_papers(a_node_str, 
                                                            p_node_str)
            coauthored_pubs.append(coauthor_count)
    return coauthored_pubs
    
def compute_neurotree_coauthorship_histo_uncond(last_author_node_list, 
                                                all_author_node_list):
    """
    For each author in last_author_node_list, count how many papers they 
    co-published with each of the authors defined in all_author_node_list
    
    Definition of co-published as in: pubmed_count_coauthored_papers() above
    """

    coauthored_pubs = [[0 for i in range(len(last_author_node_list))] 
                       for j in range(len(all_author_node_list))]
    for i,a_node in enumerate(last_author_node_list):
        if not a_node:
            continue
        a_node_str = '%s %s' %  (a_node.lastname, a_node.firstname[0])
        print a_node_str
        for j,p_node in enumerate(all_author_node_list):
            if not p_node:
                continue
            p_node_str = '%s %s' %  (p_node.lastname, p_node.firstname[0])
            coauthor_count = pubmed_count_coauthored_papers(a_node_str,
                                                            p_node_str)
            coauthored_pubs[j][i] = coauthor_count
    return coauthored_pubs



