# -*- coding: utf-8 -*-
"""
Created on Mon Feb 11 13:54:25 2013

@author: Shreejoy
"""

import glob
import re


file_name_list = [f for f in glob.glob("*.html")]
pmid_list = []
for filename in file_name_list:
    temp_pmid = re.search('\d+_', filename).group()
    temp_pmid = re.sub('_', '', temp_pmid)
    pmid_list.append(temp_pmid)
    
article_dict = {}
for f in fullTextLinks:
    pmid = f[1]
    doi = f[0]
    if pmid not in pmid_list:
        article_dict[pmid] = doi
    
    