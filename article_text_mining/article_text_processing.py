# -*- coding: utf-8 -*-
"""
Created on Sun Jun 17 22:29:03 2012

@author: Shreejoy
"""

from bs4 import BeautifulSoup as bs

import neuroelectro.models as m


def remove_spurious_table_headers(dt):
    try:
        soup = bs(dt.table_html)
    except:
        return None
    tableTags = soup.findAll('table')
    for tableTag in tableTags:
        hasHeaderTag = False
        hasBodyTag = False
        headerTag = tableTag.findAll('thead')
        if len(headerTag) > 0:
            hasHeaderTag = True
        bodyTag = tableTag.findAll('tbody')
        if len(bodyTag) > 0:
            hasBodyTag = True
        if hasHeaderTag == True and hasBodyTag == False:
#            print 'removing weird header from '
#            print dt.article
#            print dt.article.journal
            tableTag.clear()
            table_html = str(soup)        
            dt.table_html = table_html    
            dt.save()
            # check if has any ecms that are assigned to table tags that have been deleted
#             ecms = m.EphysConceptMap.objects.filter(source__data_table = dt)
#             num_ecms = ecms.count()
#             if num_ecms > 0:
# #                print 'has ecms'
#                 # remove any concept maps associated with these elements
#                 remove_untagged_datatable_ecms(dt)   
    return dt
    
def remove_spurious_table_headers_all():
    dts = m.DataTable.objects.filter(article__journal__publisher__title = 'Elsevier')
    num_tables = dts.count()
    print 'checking table validity of %d tables' % num_tables
    for i,dt in enumerate(dts):
        remove_spurious_table_headers(dt)
    
