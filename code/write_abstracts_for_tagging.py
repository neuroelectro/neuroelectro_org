# -*- coding: utf-8 -*-
"""
Created on Tue Apr 24 11:17:28 2012

@author: Shreejoy
"""
import os
import django_startup
import re
import nltk
from matplotlib.pylab import *
os.chdir('C:\Python27\Scripts\Biophys\Biophysiome')
from neuroelectro.models import Article, MeshTerm, Substance, Journal
from neuroelectro.models import Neuron, NeuronSyn
from neuroelectro.models import BrainRegion, InSituExpt, Protein, RegionExpr
from neuroelectro.models import DataTable, ArticleFullText
from neuroelectro.models import EphysProp, EphysPropSyn, NeuronEphysLink
os.chdir('C:\Python27\Scripts\Biophys')

# write abstracts for students to tag
import os
import math
os.chdir('C:\Python27\Scripts\Biophys\pubmed_abstracts')

def convertAbsToStr(pmid):
    a = Article.objects.get(pmid = pmid)
    docStr = ''
    docStr += '\n\n<<<\nAbstract %d\n' % (studentAbsCount + 1)
    absStr = (str(a.pmid) + '\n'+ a.title + '\n' + a.abstract).encode('utf-8')    
    docStr += absStr + '\n>>>'    
    return docStr

#fileName = 'pmidListNeuronsToAnnotate.txt'
#myFile = open(fileName, 'r')
#pmids = (myFile.readlines())
#pmids.sort()
#
#
#numAbsPerStudent = 20
#totStudents = int(math.ceil(len(pmids)/float(numAbsPerStudent)))
#fileNameBase = 'neuron_tagging_'
#os.chdir('C:\Python27\Scripts\Biophys\pubmed_abstracts\Abstracts_to_tag')
#
#pmidCnt = 0
#for i in range(totStudents):
#    studentAbsCount = 0
#    docStr = ''
#    fileName = fileNameBase + str(i+1) + '.txt'
#    myFile = open(fileName, 'w+')
#    while studentAbsCount < numAbsPerStudent and pmidCnt < len(pmids):
#        pmid  = int(pmids[pmidCnt])
#        absStr = convertAbsToStr(pmid)
#        docStr += absStr
#        pmidCnt += 1
#        studentAbsCount += 1
#    myFile.write(docStr)
#    myFile.close()
#        
#os.chdir('C:\Python27\Scripts\Biophys')

fileName = 'pmidList2.txt'
myFile = open(fileName, 'r')
pmids = (myFile.readlines())
pmids.sort()


numAbsPerStudent = 20
totStudents = int(math.ceil(len(pmids)/float(numAbsPerStudent)))
fileNameBase = 'example_tagged_abstracts'
os.chdir('C:\Python27\Scripts\Biophys\pubmed_abstracts\Abstracts_to_tag')

pmidCnt = 0
for i in range(totStudents):
    studentAbsCount = 0
    docStr = ''
    fileName = fileNameBase + str(i+1) + '.txt'
    myFile = open(fileName, 'w+')
    while studentAbsCount < numAbsPerStudent and pmidCnt < len(pmids):
        pmid  = int(pmids[pmidCnt])
        absStr = convertAbsToStr(pmid)
        docStr += absStr
        pmidCnt += 1
        studentAbsCount += 1
    myFile.write(docStr)
    myFile.close()
        
os.chdir('C:\Python27\Scripts\Biophys')