# -*- coding: utf-8 -*-
"""
Created on Wed Apr 04 16:18:19 2012

@author: Shreejoy
"""
import os
#import django_startup
#os.chdir('C:\Python27\Scripts\Biophys\Biophysiome')
from neuroelectro.models import EphysProp, EphysPropSyn, NeuronEphysLink, Unit
#os.chdir('C:\Python27\Scripts\Biophys')

import xlrd
import re

os.chdir('/Users/shreejoy/Desktop/biophysiome/data_files')
book = xlrd.open_workbook("Ephys_prop_definitions_3.xls")
#os.chdir('C:\Python27\Scripts\Biophys')
sheet = book.sheet_by_index(0)
ncols = sheet.ncols
nrows = sheet.nrows

table= [ [ 0 for i in range(ncols) ] for j in range(nrows ) ]
for i in range(nrows):
    for j in range(ncols):
        table[i][j] = sheet.cell(i,j).value

for i in range(1,nrows):
    ephysProp = table[i][0]
    rawSyns = table[i][1]
    ephysDef = table[i][2]
    unit = table[i][3]
    ephysOb = EphysProp.objects.get_or_create(name = ephysProp)[0]
    if unit != '':
        ephysOb.unit = unit
    ephysOb.save()
    synList = [ephysProp]
    for s in rawSyns.split(','):
        s = re.sub('<[\w/]+>', '', s)
        s = s.strip()
        synList.append(s)
    synList= list(set(synList))
    for s in synList:
        ephysSynOb = EphysPropSyn.objects.get_or_create(term = s, ephys_prop = ephysOb)[0]
        ephysSynOb.save()
    print synList
            