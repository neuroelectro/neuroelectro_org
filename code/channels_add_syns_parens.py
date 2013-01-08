# -*- coding: utf-8 -*-
"""
Created on Fri Jan 20 11:15:36 2012

@author: Shreejoy
"""

import re

chanList = ion_channels_syn_list_curated_importcsv
for i in range(len(chanList)):
    currSynList = chanList[i][1].split()
    for syn in currSynList:
        multiWordCheck = re.search('_', syn)
        vSearch = re.search('v', syn)
        irSearch = re.search('ir', syn)
        twopSearch = re.search('2p', syn.lower())
        atpSearch = re.search('atp', syn.lower())
        if multiWordCheck is None and vSearch is not None and re.search('\(\w+\)', syn) is None and re.search('\d', syn) is not None:
            newSyn = re.sub('v', '(v)', syn)
            print 'Old Syn: %s New Syn: %s' % (syn, newSyn)
            chanList[i][1] = chanList[i][1] + ' ' + newSyn
        if multiWordCheck is None and irSearch is not None and re.search('\(\w+\)', syn) is None and re.search('\d', syn) is not None:
            newSyn = re.sub('ir', '(ir)', syn)
            print 'Old Syn: %s NewSyn: %s' % (syn, newSyn)
            chanList[i][1] = chanList[i][1] + ' ' + newSyn
        if multiWordCheck is None and twopSearch is not None and re.search('\(\w+\)', syn) is None and re.search('\d', syn) is not None:
            newSyn = re.sub('(?i)2p', '(2p)', syn)
            print 'Old Syn: %s NewSyn: %s' % (syn, newSyn)
            chanList[i][1] = chanList[i][1] + ' ' + newSyn
        if multiWordCheck is None and atpSearch is not None and re.search('\(\w+\)', syn) is None and re.search('\d', syn) is not None:
            newSyn = re.sub('(?i)atp', '(atp)', syn)
            print 'Old Syn: %s NewSyn: %s' % (syn, newSyn)
            chanList[i][1] = chanList[i][1] + ' ' + newSyn