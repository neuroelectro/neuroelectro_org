# -*- coding: utf-8 -*-
"""
Created on Tue Jan 31 16:03:13 2012

@author: Shreejoy
"""
from .selenium_test import *
# load data from allen diff search

targetReg = 'MY'
contrastReg = 'CB'
regionDict = load_region_dict()
browser = init_browser(targetReg, contrastReg)

fractList, imageSeriesList, geneNameList = get_all_data(browser, targetReg, contrastReg, regionDict)

targetReg = 'MY'
contrastReg = 'STR'
regionDict = load_region_dict()
browser2 = init_browser(targetReg, contrastReg)

fractList, imageSeriesList, geneNameList = get_all_data(browser2, targetReg, contrastReg, regionDict)