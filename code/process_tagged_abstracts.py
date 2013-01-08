# -*- coding: utf-8 -*-
"""
Created on Wed May 09 09:50:24 2012

@author: Shreejoy
"""

import os

from bs4 import BeautifulSoup

os.chdir('C:\Users\Shreejoy\Downloads\documents-export-2012-05-09')
dirList=os.listdir('C:\Users\Shreejoy\Downloads\documents-export-2012-05-09')

boldSet = set()
for d in dirList:
    os.chdir('C:\Users\Shreejoy\Downloads\documents-export-2012-05-09')
    os.chdir(d)
    f = open(d + '.html')
    text = f.read()
    soup = BeautifulSoup(text)
    tags = soup.find_all('span')
    for t in tags:
        try:
            t['style']
            print t.text
            boldSet.add(d)
        except KeyError:
            a = 1
        

readlines
dirs = ls