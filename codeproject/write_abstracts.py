# -*- coding: utf-8 -*-
"""
Created on Wed Mar 21 14:25:14 2012

@author: Shreejoy
"""
import os
os.chdir('C:\Python27\Scripts\Biophys\pubmed_abstracts')
arts = Article.objects.all()
for a in arts:
    currPmid = a.pmid
    fileName = '%d.txt' % currPmid
    myFile = open(fileName, 'w+')
    absStr = (a.title + '\n' + a.abstract).encode('utf-8')
    myFile.write(absStr)
#    utf8string = unicode(rawstring, ‘utf-8′)
    myFile.close()