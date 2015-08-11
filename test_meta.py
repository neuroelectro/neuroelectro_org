"""
Solution concentration textmining driver script

Created by: Dmitrii Tebaikin
Updated by: Michael Gottlieb

Run in python shell: execfile('test_meta.py')
"""
import neuroelectro.models as m
import article_text_mining.assign_metadata as meta
import article_text_mining.full_text_pipeline as pipe
import db_functions.compute_field_summaries as comp
import os
import time
import sys

from random import randint
from django.db.models import Q
from os import listdir

articlesTotal = 0
articlesProcessed = 0
articlesNoFullText = 0
articlesNoMethodsTag = 0
articlesMethodsTooSmall = 0
jnNoFullText = {}
jnNoMethodsTag = {}
jnMethodsTooSmall = {}
MAX_PROCESS_NUMBER = 16

'''    
    if processed == 1:
        meta.assign_species(article)
        meta.assign_electrode_type(article)
        meta.assign_strain(article)
        meta.assign_prep_type(article)
        meta.assign_rec_temp(article)
        meta.assign_animal_age(article)
        meta.assign_jxn_potential(article)
        
 
    if processed == 1:
        global articlesProcessed 
        articlesProcessed += 1
    if processed == -1:
        global articlesNoFullText 
        articlesNoFullText += 1
    if processed == -2:
        global articlesNoMethodsTag 
        articlesNoMethodsTag += 1
    if processed == -3:
        global articlesMethodsTooSmall
        articlesMethodsTooSmall += 1
'''
path = os.getcwd()
os.chdir("/Users/dtebaykin/Desktop/raw_full_texts")

articles = m.Article.objects.all() 

for a in articles:
    try:
        meta.assign_solution_concs(a)
    except:
        print "Exception occurred for article %s" % a.pk
    
os.chdir(path)

#print "Out of %s articles: %s processed, %s no full text, %s no methods tag, %s methods section #too small\n" % (articlesTotal, articlesProcessed, articlesNoFullText, articlesNoMethodsTag, articlesMethodsTooSmall)
#     print "Journals with no full text attached: %s\n" % jnNoFullText
#     print "Journals with no methods tag: %s\n" % jnNoMethodsTag
#     print "Journals with methods section too short: %s\n" % jnMethodsTooSmall
print "done"

