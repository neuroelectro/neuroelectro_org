"""
Solution concentration textmining driver script

Created by: Dmitrii Tebaikin
Updated by: Michael Gottlieb
"""
import neuroelectro.models as m
import article_text_mining.assign_metadata as meta
import article_text_mining.full_text_pipeline as pipe
import db_functions.compute_field_summaries as comp
import os
import subprocess
import multiprocessing
import time
import sys

from multiprocessing import Process, Lock
from buildtools import process
from random import randint
from django.db.models import Q
from os import listdir

mutex = Lock()
mutex2 = Lock()
articlesTotal = 0
articlesProcessed = 0
articlesNoFullText = 0
articlesNoMethodsTag = 0
articlesMethodsTooSmall = 0
jnNoFullText = {}
jnNoMethodsTag = {}
jnMethodsTooSmall = {}
MAX_PROCESS_NUMBER = 16
#execfile('test_meta.py')
def process_articles(inds,j):
    for i in inds:
        article = articles[i]
        call = 'python /Users/dtebaykin/Documents/workspace/neuroelectro_org/neuroelectro_org/process_article.py ' + str(article.id)
        #print 'processing %s' % article.pmid
        process = subprocess.Popen(call, stdout = subprocess.PIPE, shell = True)
        processed, err = process.communicate()
        #print j
    #processOutputCode(processed)        

def processOutputCode(processed):
    mutex2.acquire()
    global num_threads
    if processed == 1:
        articlesProcessed += 1
    if processed == -1:
        articlesNoFullText += 1
    if processed == -2:
        articlesNoMethodsTag += 1
    if processed == -3:
        articlesMethodsTooSmall += 1
    num_threads -= 1
    mutex2.release()

path = os.getcwd()
articles = m.Article.objects.all() 
num_threads = 0
os.chdir("/Users/dtebaykin/Desktop/raw_full_texts")
indices = dict()

for i in range(0, MAX_PROCESS_NUMBER):
    indices[i] = []
for i in range(0, len(articles)):
    indices[i%MAX_PROCESS_NUMBER].append(i)
    
for i in indices:
    print i
    
    #while len(multiprocessing.active_children()) > MAX_PROCESS_NUMBER:
    #    time.sleep(5)
#    while num_threads > MAX_PROCESS_NUMBER:
#        time.sleep(1)
    

    #print "Processing article #%s" % i
    #print "Current number of threads: %s" % len(multiprocessing.active_children())

    #num_threads += 1
    #article = articles[i]    
    p = Process(target = process_articles, args=(indices[i],i))
    print 'Starting:', p.name, p.pid
    sys.stdout.flush()

    p.start()
    print 'Exiting :', p.name, p.pid
    sys.stdout.flush()
    #print i

while len(multiprocessing.active_children()):
    time.sleep(60)

os.chdir(path)
print "Out of %s articles: %s processed, %s no full text, %s no methods tag, %s methods section #too small\n" % (articlesTotal, articlesProcessed, articlesNoFullText, articlesNoMethodsTag, articlesMethodsTooSmall)
#     print "Journals with no full text attached: %s\n" % jnNoFullText
#     print "Journals with no methods tag: %s\n" % jnNoMethodsTag
#     print "Journals with methods section too short: %s\n" % jnMethodsTooSmall
print "done"