"""
Solution concentration textmining driver script

Created by: Dmitrii Tebaikin
Updated by: Michael Gottlieb

Run in python shell: execfile('extract_article_metadata.py')
"""
from django.conf import settings
import neuroelectro.models as m
import article_text_mining.assign_metadata as meta
from article_text_mining.html_process_tools import getMethodsTag
import os, re


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

def run():
    path = os.getcwd()
    
    os.chdir(settings.FULL_TEXTS_DIRECTORY)
    
    articles = m.Article.objects.all()
    articles = [m.Article.objects.get(pk = 35010)]
    
    for a in articles:
        #try:
        if a.articlefulltext_set.all().count() == 0:
            print "No full text associated with article: %s" % a.pk
            continue
        
        full_text_list = m.ArticleFullText.objects.filter(article = a.pk)
    
        if not full_text_list:
            print "Full text file does not exist for article: %s" % a.pk
            continue
    
        try:
            full_text = full_text_list[0].get_content()
        except:
            print "File not found for article: %s" % a.pk
            continue
        
        methods_tag = getMethodsTag(full_text, a)
    
        if methods_tag is None:
            print "No methods tag found article id: %s, pmid: %s" % (a.pk, a.pmid)
            continue
    
        article_text = re.sub('\s+', ' ', methods_tag.text)
    
        if len(article_text) <= 100:
            print "Methods section is too small. Article id: %s, pmid: %s" % (a.pk, a.pmid)
            continue
        
        print "Textmining metadata for article: %s" % a.pk
        meta.assign_solution_concs(a)
        meta.assign_species(a)
        meta.assign_electrode_type(a)
        meta.assign_strain(a)
        meta.assign_prep_type(a)
        meta.assign_rec_temp(a)
        meta.assign_animal_age(a)
        meta.assign_jxn_potential(a)
        # except Exception, e:
            #print "Exception occurred for article %s: %s" % (a.pk, str(e))
        
    os.chdir(path)
    
    #print "Out of %s articles: %s processed, %s no full text, %s no methods tag, %s methods section #too small\n" % (articlesTotal, articlesProcessed, articlesNoFullText, articlesNoMethodsTag, articlesMethodsTooSmall)
    #     print "Journals with no full text attached: %s\n" % jnNoFullText
    #     print "Journals with no methods tag: %s\n" % jnNoMethodsTag
    #     print "Journals with methods section too short: %s\n" % jnMethodsTooSmall
    print "done"

