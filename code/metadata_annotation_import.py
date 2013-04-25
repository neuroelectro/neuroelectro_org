# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 15:37:41 2013

@author: Shreejoy
"""
import neuroelectro.models as m
from fuzzywuzzy import fuzz, process
from html_table_decode import resolveDataFloat
import re
import xlrd
import numpy as np
import csv

def load_annotated_article_ephys():
    print 'Updating ephys defs'
    print 'Loading ephys defs'
    book = xlrd.open_workbook("data/article_metadata_ephys_annotations.xlsx")
    #os.chdir('C:\Python27\Scripts\Biophys')
    sheet = book.sheet_by_index(0)
    ncols = sheet.ncols
    nrows = sheet.nrows
    
    table= [ [ 0 for i in range(ncols) ] for j in range(nrows ) ]
    for i in range(nrows):
        for j in range(ncols):
            value = sheet.cell(i,j).value
            value = value.strip()
            if value is None:
                value = ''
            table[i][j] = value
    return table, ncols, nrows

def process_table(table, ncols, nrows):
    
    table_norm = [ [ 0 for i in range(6) ] for j in range(nrows ) ]
    table_norm = np.zeros([nrows, 6], dtype='a16')
    for i in range(1,nrows):
        pmid = table[i][2]
#        neuron_type = table[i][5]
#n = m.Neuron.objects.filter(name = neuron_type)[0]
        species = table[i][7]
        strain = table[i][8]
        age = table[i][9]
        electrode = table[i][10]
        prep_type = table[i][12]
        temp = table[i][11]
        a = m.Article.objects.filter(pmid = pmid)[0]
        
        
#        print a
        temp_norm = temp_resolve(unicode(temp))
        age_norm = age_resolve(unicode(age))
        strain_norm = strain_resolve(unicode(strain))
        prep_norm = preptype_resolve(unicode(prep_type)) 
        electrode_norm = electrodetype_resolve(unicode(electrode))
        species_norm = species_resolve(unicode(species))
        row = [species_norm, strain_norm, age_norm, electrode_norm, temp_norm, prep_norm]
        for j in range(0,len(row)):
            table_norm[i,j] = row[j]
    return table_norm

def write_metadata(table_norm):
    csvout = csv.writer(open("mydata.csv", "wb"))
    csvout.writerow(("Species", "Strain", "Age", "ElectrodeType", "Temp", "PrepType"))
    for row in table_norm:
        csvout.writerow(row)
#        print temp_resolve(unicode(temp))
        #print age_resolve(unicode(age))
        #print strain_resolve(unicode(strain))
#        print preptype_resolve(unicode(prep_type)) 
#        print resolveDataFloat(temp)

roomtemp_re = re.compile(ur'room|room\stemp|RT' , flags=re.UNICODE|re.IGNORECASE)
def temp_resolve(inStr):
    # check if contains room temp or RT
    if roomtemp_re.findall(inStr):
        value = 22
    else:
        retDict = resolveDataFloat(inStr)
#        print retDict
        if 'value' in retDict:
            value = retDict['value']
        else:
            value = ''
    return value
    
weight_re = re.compile(ur'weight' , flags=re.UNICODE|re.IGNORECASE)
week_re = re.compile(ur'week|wk' , flags=re.UNICODE|re.IGNORECASE)
month_re = re.compile(ur'month|mo' , flags=re.UNICODE|re.IGNORECASE)
def age_resolve(inStr):
    # check if contains room temp or RT
    if weight_re.findall(inStr):
        value = ''
        return value
    else:
        retDict = resolveDataFloat(unicode(inStr))
        if 'value' in retDict:
            value = retDict['value']
            if week_re.findall(inStr):
                value = value * 7
            elif month_re.findall(inStr):
                value = value * 30
        else:
            value = ''
    return value


strain_list = m.MetaData.objects.filter(name = 'Strain')
strain_list_values = [md.value for md in strain_list]
matchThresh = 70
def strain_resolve(inStr):
    if len(inStr.split()) < 1:
        return ''
    processOut, matchVal = process.extractOne(inStr, strain_list_values)
    if matchVal > matchThresh:
        return processOut
    else:
        return ''
        
preptype_list = m.MetaData.objects.filter(name = 'PrepType')
preptype_list_values = [md.value for md in preptype_list]
matchThresh = 70
def preptype_resolve(inStr):
    if len(inStr) < 1:
        return ''
    processOut, matchVal = process.extractOne(inStr, preptype_list_values)
    if matchVal > matchThresh:
        return processOut
    else:
        return ''
        
electrode_list = m.MetaData.objects.filter(name = 'ElectrodeType')
electrode_list_values = [md.value for md in electrode_list]
matchThresh = 70
def electrodetype_resolve(inStr):
    if len(inStr) < 1:
        return ''
#    print inStr
    processOut, matchVal = process.extractOne(inStr, electrode_list_values)
    if matchVal > matchThresh:
        return processOut
    else:
        return ''
        
species_list = m.MetaData.objects.filter(name = 'Species')
species_list_values = [md.value for md in species_list]
rat_re = re.compile('rat|rats', flags=re.UNICODE|re.IGNORECASE)
mouse_re = re.compile('mouse|mice', flags=re.UNICODE|re.IGNORECASE)
def species_resolve(inStr):
    matchThresh = 70
    if len(inStr) < 1:
        species = ''
    elif mouse_re.findall(inStr):
        species = 'Mice'
    elif rat_re.findall(inStr):
        species = 'Rats'
    else:
        processOut, matchVal = process.extractOne(inStr, species_list_values)
        if matchVal > matchThresh:
            species = processOut
            return species
        else:
            species = ''
    return species
    
    
#def strain_resolve(inStr):
    

        
        