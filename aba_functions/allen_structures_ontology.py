# -*- coding: utf-8 -*-
"""
Created on Tue Jan 31 12:50:37 2012

@author: Shreejoy
"""

from xml.etree.ElementTree import XML
from urllib.request import urlopen
from urllib.parse import quote_plus, quote
import json
from pprint import pprint

import os
import django_startup
from matplotlib.pylab import *
#run django_startup
os.chdir('C:\Python27\Scripts\Biophys\pubdb\pubdir')
from pubapp.models import BrainRegion
os.chdir('C:\Python27\Scripts\Biophys')


link = 'http://mouse.brain-map.org/ontology.json'

handle = urlopen(link)
data = handle.read()

json_data = json.loads(data)

regionDict = {}
for i in range(len(json_data)):
    abbrev = json_data[i]['acronym']
    structId = json_data[i]['structure_id']
    depth = json_data[i]['depth']
    color = json_data[i]['color']
    name = json_data[i]['name']
    regionDict[abbrev]= (structId)
    b = BrainRegion.objects.get_or_create(abbrev = abbrev, name = name, 
                                          isallen = True, treedepth = depth, color = color, 
                                          allenid = structId)[0]
    b.save()