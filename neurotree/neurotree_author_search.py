# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 16:36:21 2013

@author: Shreejoy
"""

import neurotree.models as t
import neuroelectro.models as m
from django.db.models import Q

# this gets all articles which have some nedms in neuroelectro

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
            if author_node_query.count() > 1:
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
    authors = []
    none_count = 0
    duplicate_count = 0
    for author in last_author_node_list:
        if author not in authors:
            if author is not None:
                authors2.append(author)
            else:
                none_count += 1
                found_count -= 1
        else:
            duplicate_count += 1
            found_count -= 1

    return (authors, found_count, cant_resolve_count, 
            cant_find_count, duplicate_count, none_count)


