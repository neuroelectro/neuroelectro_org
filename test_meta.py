"""
Solution concentration textmining driver script

Created by: Dmitrii Tebaikin
"""
import neuroelectro.models as m
import article_text_mining.assign_metadata as meta
import article_text_mining.full_text_pipeline as pipe
from random import randint
import db_functions.compute_field_summaries as comp
from django.db.models import Q
from os import listdir
import os

path = os.getcwd()

# Out of 117542 articles: 32068 processed, 32228 no full text, 52596 no methods tag, 650 methods section too small
# TODO: no methods tag articles per journal title 


# list_of_texts = ["/Users/dtebaykin/Desktop/raw_full_texts/neuro_full_texts", "/Users/dtebaykin/Desktop/raw_full_texts/wiley_html"]
# for directory in list_of_texts:
# directory = "/Users/dtebaykin/Desktop/raw_full_texts/"
# for f in listdir(directory):
#     print "Processing: %s" % f
#     pipe.add_article_full_text_from_file(f, directory)
    
os.chdir("/Users/dtebaykin/Desktop/raw_full_texts")
articles = m.Article.objects.all() 

# articles_with_texts = m.ArticleFullText.objects.all()
# 
# for text in articles_with_texts:
#     if randint(0, 1000) is 1:
    
#     meta.assign_solution_concs(text)
    
#Textmine the ~300 articles that have been curated and have electrophys. data    
# articles = m.Article.objects.filter(Q(datatable__datasource__neuronconceptmap__times_validated__gte = 1,
#                                             datatable__datasource__neuronephysdatamap__isnull = False) | 
#                                             Q(usersubmission__datasource__neuronconceptmap__times_validated__gte = 1,
#                                             usersubmission__datasource__neuronephysdatamap__isnull = False)).distinct()
# articles = articles.filter(articlefulltext__articlefulltextstat__metadata_human_assigned = True ).distinct()  
#   
articlesTotal = 0
articlesProcessed = 0
articlesNoFullText = 0
articlesNoMethodsTag = 0
articlesMethodsTooSmall = 0
jnNoFullText = {}
jnNoMethodsTag = {}
jnMethodsTooSmall = {}
for article in articles:
    articlesTotal += 1
    processed = meta.assign_solution_concs(article)  
    if processed == 1:
#         meta.assign_species(article)
#         meta.assign_electrode_type(article)
#         meta.assign_strain(article)
#         meta.assign_prep_type(article)
#         meta.assign_rec_temp(article)
#         meta.assign_animal_age(article)
#         meta.assign_jxn_potential(article)
        articlesProcessed += 1
    if processed == -1:
        if article.journal in jnNoFullText:
            jnNoFullText[article.journal] += 1
        else:
            jnNoFullText[article.journal] = 1
        articlesNoFullText += 1
    if processed == -2:
        if article.journal in jnNoMethodsTag:
            jnNoMethodsTag[article.journal] += 1
        else:
            jnNoMethodsTag[article.journal] = 1
        articlesNoMethodsTag += 1
    if processed == -3:
        if article.journal in jnMethodsTooSmall:
            jnMethodsTooSmall[article.journal] += 1
        else:
            jnMethodsTooSmall[article.journal] = 1
        articlesMethodsTooSmall += 1

# Write ephys value and metadata to a CSV from curated articles
# comp.getAllArticleNedmMetadataSummary(True)

# Curated 30 articles
# article_list = [3449, 3977, 4128, 4321, 4443, 4697, 4981, 5129, 5177, 5497, 5592, 5686, 5731, 5989, 7181, 7273, 8919, 9075, 9102, 9476, 9763, 9788, 9921, 10706, 10775, 10777, 11195, 11328, 11495, 11498]

# Second curation 30 articles
#article_list = [11674, 11711, 11742, 11852, 11918, 12070, 12377, 12666, 12758, 12881, 12955, 13615, 13617, 14171, 14292, 23163, 23211, 23482, 23747, 23807, 23920, 24352, 24843, 24867, 25307, 25371, 25379, 25599, 25710, 25973, 26026, 26039, 26319, 26468, 26931]

# for a in article_list:
#     meta.assign_solution_concs( m.Article.objects.get(id = a) )

os.chdir(path)
print "Out of %s articles: %s processed, %s no full text, %s no methods tag, %s methods section too small\n" % (articlesTotal, articlesProcessed, articlesNoFullText, articlesNoMethodsTag, articlesMethodsTooSmall)
# print "Journals with no full text attached: %s\n" % jnNoFullText
# print "Journals with no methods tag: %s\n" % jnNoMethodsTag
# print "Journals with methods section too short: %s\n" % jnMethodsTooSmall
print "done"
        
        
