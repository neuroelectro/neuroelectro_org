# -*- coding: utf-8 -*-
"""
NeuroTree Pubmed integration
@author: Shreejoy
"""

import neurotree.models as t
import neuroelectro.models as m
from django.db.models import Q
import sys

def pubmed_count_coauthored_papers(author_1, author_2):
    """
    Count number of co-published papers between author_1 and author_2
    
    co-published defined by number of papers in pubmed where author_1 is first author
    and author_2 is last author
    
    Args:
        author_1 (str): String of first authors name; e.g., Tripathy S
        author_2 (str): String of second authors name; e.g., Urban N
    Returns:
        match_count (int): count of numbers of matching pubmed articles 
    """
    advisee_author_str = author_1
    adviser_author_str = author_2
    esearchlink = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=%s[Author] AND (%s[Author])'
    efetch = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?&db=pubmed&retmode=xml&id=%s"    
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
            if first_author_last_name == advisee_last_name and last_author_last_name == adviser_last_name:
                match_count += 1
    #print '%s, %s, matching pubs = %d' % (advisee_author_str, adviser_author_str, match_count)
    return match_count

def compute_neurotree_coauthorship_histo(last_author_node_list):
    """
    For each author in input list, count how many papers they co-published with
    mentors as defined in NeuroTree
    
    Definition of co-published as in: pubmed_count_coauthored_papers() above
    """
    relationcodes=[1,2]
    coauthored_pubs = []
    for author_node in last_author_node_list:
        if author_node:
            author_node_str = '%s %s' %  (author_node.lastname, author_node.firstname[0])
            parents = [x.node2 for x in author_node.parents.filter(relationcode__in=relationcodes)]
            for parent_node in parents:
                parent_node_str = '%s %s' %  (parent_node.lastname, parent_node.firstname[0])
                coauthor_count = pubmed_count_coauthored_papers(author_node_str, parent_node_str)
                coauthored_pubs.append(coauthor_count)
    return coauthored_pubs
    
def compute_neurotree_coauthorship_histo_uncond(last_author_node_list, all_author_node_list):
    """
    For each author in input list, count how many papers they co-published with
    each of the authors defined in all_author_node_list
    
    Definition of co-published as in: pubmed_count_coauthored_papers() above
    """
    coauthored_pubs = [[0 for i in range(len(last_author_node_list))] for j in range(len(all_author_node_list))]
    #coauthored_pubs = [0]*(len(last_author_node_list)*len(all_author_node_list))
    for i,author_node in enumerate(last_author_node_list):
        if author_node:
            author_node_str = '%s %s' %  (author_node.lastname, author_node.firstname[0])
            print author_node_str
            for j,parent_node in enumerate(all_author_node_list):
                if parent_node:
                    parent_node_str = '%s %s' %  (parent_node.lastname, parent_node.firstname[0])
                    coauthor_count = pubmed_count_coauthored_papers(author_node_str, parent_node_str)
                    coauthored_pubs[j][i] = coauthor_count
    return coauthored_pubs

def prog(num,denom):
    fract = float(num)/denom
    hyphens = int(round(50*fract))
    spaces = int(round(50*(1-fract)))
    sys.stdout.write('\r%.2f%% [%s%s]' % (100*fract,'-'*hyphens,' '*spaces))
    sys.stdout.flush()  