# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 16:36:21 2013

A set of functions for specifically interfacing NeuroTree with NeuroElectro DB

@author: Shreejoy
"""
import sys
import neurotree.models as t
import neuroelectro.models as m
from neurotree.author_search import get_article_last_author,get_neurotree_author
from neurotree.db_ops import shortest_path
from django.db.models import Q

# this gets all articles which have some nedms in neuroelectro

def define_ephys_grandfathers():
    """
    Defines a list of "grandfathers" of in vitro electrophysiology
    based on neurotree ids
    """
    neurotree_pid = [135, 366, 1857, 812, 1209, 1777, 64]
    grandfather_list = []
    # Sakmann, Llinas, Prince, Nicoll, Tank, Tsien, Wiesel
    for pid in neurotree_pid:
        node = t.Node.objects.get(id = pid)
        grandfather_list.append(node)
    return grandfather_list
    
def get_closest_grandfather(author_node, grandfather_list):
    """
    For a given neurotree author_node, find author's most related 
    academic grandfather in grandfather_list
    
    Returns:
        closest_grandfather: neurotree node corresponding to closest grandfather
    """
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

def assign_ephys_grandfather(article):
    """
    Assign 1 of N ephys grandfathers to a NeuroElectro article object
    by searching NeuroTree
    """
    result = None

    grandfather_list = define_ephys_grandfathers()
    last_author_ob = get_article_last_author(article)
    if last_author_ob is not None:
        a_node = get_neurotree_author(last_author_ob)
        if a_node is not None:
            closest_grandfather = get_closest_grandfather(a_node, grandfather_list)
            result = closest_grandfather
    return result

def assign_articles_grandfathers():
    """
    Assign ephys grandfathers to each article containing 
    ephys data in NeuroElectro.
    """
    q1 = Q(datatable__datasource__neuronconceptmap__times_validated__gte = 1)
    q2 = Q(usersubmission__datasource__neuronconceptmap__times_validated__gte = 1)
    articles = m.Article.objects.filter(q1 | q2).distinct()
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
            
#        for author in authorList:
#            print author.text
#            last = author.find("./LastName").text
#            print last
#              fore = author.find("./ForeName").text
#              initials = author.find("./Initials").text
#             except AttributeError:
#               continue  
    

        
        

    

