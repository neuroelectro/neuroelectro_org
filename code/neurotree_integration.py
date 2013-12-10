# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 16:36:21 2013

@author: Shreejoy
"""

import neurotree.models as t
import neuroelectro.models as m
from neurotree.neurotree_author_search import get_article_last_author, get_neurotree_author
from neurotree.scratch import shortest_path
from django.db.models import Q

from xml.etree.ElementTree import XML, ParseError
from urllib import quote_plus, quote
from urllib2 import Request, urlopen, URLError, HTTPError
from httplib import BadStatusLine
from xml.etree.ElementTree import XML
import json


# this gets all articles which have some nedms in neuroelectro

def assign_articles_grandfathers():
    articles = m.Article.objects.filter(Q(datatable__datasource__neuronconceptmap__times_validated__gte = 1) | 
        Q(usersubmission__datasource__neuronconceptmap__times_validated__gte = 1)).distinct()
    article_info_list = []
    for article in articles:
        grandfather = assign_ephys_grandfather(article)
        author = get_article_last_author(article)
        if author is not None:
            neurotree_node = get_neurotree_author(author)
        else:
            neurotree_node = None
        article_info = [author, neurotree_node, grandfather]
        article_info_list.append(article_info)
    return article_info_list

def assign_ephys_grandfather(article):
    grandfather_list = get_ephys_grandfathers()
    
    last_author_ob = get_article_last_author(article)
    if last_author_ob is not None:
        author_node = get_neurotree_author(last_author_ob)
        if author_node is not None:
            closest_grandfather = get_closest_grandfather(author_node, grandfather_list)
            return closest_grandfather
    return None
        
        
#    articles = m.Article.objects.filter(Q(datatable__datasource__neuronconceptmap__times_validated__gte = 1) | 
#        Q(usersubmission__datasource__neuronconceptmap__times_validated__gte = 1)).distinct()
#    for i,article in enumerate(articles):
        
def get_closest_grandfather(author_node, grandfather_list):
    path_list = []
    max_path_length = 4
    for grandfather in grandfather_list:
        if author_node == grandfather:
            path = [grandfather]
            path_list.append(path)
            continue
        path = shortest_path(author_node,
                             grandfather,
                             directions=['up'],
                             max_path_length=max_path_length)
        if path is not None:
            path_list.append(path)
    if len(path_list) > 0:
        sorted_path_list = sorted(path_list,key=lambda x:len(x),reverse=False)
        closest_grandfather = sorted_path_list[0][-1]
        return closest_grandfather
    else:
        return None

def get_ephys_grandfathers():
    neurotree_pid = [135, 366, 1857, 812, 1209, 1777, 64]
    grandfather_list = []
    # Sakmann, Llinas, Prince, Nicoll, Tank, Tsien, Wiesel
    for pid in neurotree_pid:
        node = t.Node.objects.get(id = pid)
        grandfather_list.append(node)
    return grandfather_list

def get_neurotree_authors():
    articles = m.Article.objects.filter(Q(datatable__datasource__neuronconceptmap__times_validated__gte = 1) | 
        Q(usersubmission__datasource__neuronconceptmap__times_validated__gte = 1)).distinct()
        
    found_count = 0
    cant_resolve_count = 0
    cant_find_count = 0
    last_author_node_list = []
    for i,article in enumerate(articles):
        print i
#        print article
#        print article.author_list_str
        author_list_str = article.author_list_str
        if author_list_str is not None:
            author_list = author_list_str.split(';')
            last_author_str = author_list[-1]
            
            last_author_split_str = last_author_str.split()
            last_author_last_name = last_author_split_str[:-1]
            last_author_last_name = ' '.join(last_author_last_name)

            try:
                if len(last_author_split_str) > 1:
                    last_author_initials = last_author_split_str[-1]
                    author_ob = m.Author.objects.filter(last = last_author_last_name, initials = last_author_initials, article = article)[0]
                else:
                    last_author_initials = None
                    author_ob = m.Author.objects.filter(last = last_author_last_name, article = article)[0]
            except IndexError:
                print 'Cant find author %s' % last_author_str
                cant_find_count += 1
                last_author_node_list.append(None)
                continue
            last_name = author_ob.last
            first_name = author_ob.first.split()[0]
            # get neurotree author object corresponding to pubmed author object
            author_node_query = t.Node.objects.filter(lastname = last_name)
            if author_node_query.count() > 0:
                author_node_query = t.Node.objects.filter(lastname = last_name, firstname__icontains = first_name[0])
                if author_node_query.count() > 1:
                    author_node_query = t.Node.objects.filter(lastname = last_name, firstname__icontains = first_name)
                    if author_node_query.count() > 1: 
                        print 'Author: %s, %s has too many identical nodes in NeuroTree'  % (last_name, first_name)
                        cant_resolve_count += 1
                        last_author_node_list.append(None)
            if author_node_query.count() ==0:
                print 'Author: %s, %s not in NeuroTree'  % (last_name, first_name)
                cant_find_count += 1
            if author_node_query.count() == 1:
                #################################################
                # author_node is author variable in neuro tree  #
                #################################################
                author_node = author_node_query[0]
                last_author_node_list.append(author_node)

                print 'Author: %s, found in NeuroTree' % author_node
                found_count += 1
            print 'a'
        else:
            print 'Article %s does not have an author list string' % article.title
            cant_find_count += 1
            last_author_node_list.append(None)
    return found_count, cant_resolve_count, cant_find_count, last_author_node_list
    
def pubmed_count_coauthored_papers(advisee_author_str, adviser_author_str):
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
        if len(authorList) > 0:
            first_author_last_name = authorList[0].find("./LastName").text
            #print first_author_last_name
            last_author_last_name = authorList[-1].find("./LastName").text
            if first_author_last_name == advisee_last_name and last_author_last_name == adviser_last_name:
                match_count += 1
    print '%s, %s, matching pubs = %d' % (advisee_author_str, adviser_author_str, match_count)
    return match_count
    
def compute_neurotree_coauthorship_histo(last_author_node_list):
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
    
    
            
#        for author in authorList:
#            print author.text
#            last = author.find("./LastName").text
#            print last
#              fore = author.find("./ForeName").text
#              initials = author.find("./Initials").text
#             except AttributeError:
#               continue  
    

        
        

    

