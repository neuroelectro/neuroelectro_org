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
from assign_metadata import validate_temp_list, validate_age_list

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

anon_user = m.get_anon_user()
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
        #print a
        
        m.ArticleMetaDataMap.objects.filter(article = a).delete()
        
#        print a
        temp_norm_dict = temp_resolve(unicode(temp))
        #print temp_norm_dict
#        temp_dict_fin = validate_temp_list([temp_norm_dict])
        add_continuous_metadata('RecTemp', temp_norm_dict, a)
        
        age_norm_dict = age_resolve(unicode(age))
        #print age_norm_dict
#        age_dict_fin = validate_age_list([age_norm_dict])
#        print temp_dict_fin
        add_continuous_metadata('AnimalAge', age_norm_dict, a)
        
        weight_norm = weight_resolve(unicode(age))
#        print temp_dict_fin
        add_continuous_metadata('AnimalWeight', weight_norm, a)
        
        strain_norm = strain_resolve(unicode(strain))
        if strain_norm is not '':
            add_nominal_metadata('Strain', strain_norm, a)
        prep_norm = preptype_resolve(unicode(prep_type)) 
        if prep_norm is not '':
            add_nominal_metadata('PrepType', prep_norm, a)
        electrode_norm = electrodetype_resolve(unicode(electrode))
        #print (electrode, electrode_norm)
        if electrode_norm is not '':
            add_nominal_metadata('ElectrodeType', electrode_norm, a)
        species_norm = species_resolve(unicode(species))
        if species_norm is not '':
            add_nominal_metadata('Species', species_norm, a)
        if a.articlefulltext_set.all().count() > 0:
            afts = m.ArticleFullTextStat.objects.get_or_create(article_full_text__article = a)[0]
            afts.metadata_human_assigned = True
            #print afts.metadata_human_assigned
            afts.save()
#        row = [species_norm, strain_norm, age_norm, electrode_norm, temp_norm, prep_norm]
#        for j in range(0,len(row)):
#            table_norm[i,j] = row[j]
#    return table_norm

#name = 'Species', value = 'Rats'
def add_nominal_metadata(name, value, article):
    metadata_ob = m.MetaData.objects.get_or_create(name=name, value=value)[0]
    amd_ob = m.ArticleMetaDataMap.objects.get_or_create(article=article, metadata = metadata_ob)[0]
    if amd_ob.added_by:
        pass
    else:
        amd_ob.added_by = anon_user
    amd_ob.save()
    
def add_continuous_metadata(name, value_dict, article):
    if 'value' in value_dict:
        min_range = None
        max_range = None
        stderr = None
        if 'min_range' in value_dict:
            min_range = value_dict['min_range']
        if 'max_range' in value_dict:
            max_range = value_dict['max_range']
        if 'error' in value_dict:
            stderr = value_dict['error']
        cont_value_ob = m.ContValue.objects.get_or_create(mean = value_dict['value'], min_range = min_range,
                                                          max_range = max_range, stderr = stderr)[0]
        metadata_ob = m.MetaData.objects.get_or_create(name=name, cont_value=cont_value_ob)[0]
        amd_ob = m.ArticleMetaDataMap.objects.get_or_create(article=article, metadata = metadata_ob)[0]
        if amd_ob.added_by:
            # if amd_ob already exists (i.e. added by robot, don't say its assigned by a human)
            pass
        else:
            amd_ob.added_by = anon_user
        amd_ob.save()

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
        inStr = u'20-24'
        retDict = resolveDataFloat(inStr)
#        value = 22
    else:
        retDict = resolveDataFloat(inStr)
#        if 'value' in retDict:
#            value = retDict['value']
#        else:
#            value = ''
    return retDict
    
weight_re = re.compile(ur'weight' , flags=re.UNICODE|re.IGNORECASE)
week_re = re.compile(ur'week|wk' , flags=re.UNICODE|re.IGNORECASE)
month_re = re.compile(ur'month|mo' , flags=re.UNICODE|re.IGNORECASE)
def age_resolve(inStr):
    # check if contains room temp or RT
    if weight_re.findall(inStr):
        retDict = ''
        return retDict
    else:
        retDict = resolveDataFloat(unicode(inStr))
        if 'value' in retDict:
            if week_re.findall(inStr):
                for k in retDict.keys():
                    retDict[k] = retDict[k] * 7
            elif week_re.findall(inStr):
                for k in retDict.keys():
                    retDict[k] = retDict[k] * 30
#            value = retDict['value']
#            if week_re.findall(inStr):
#                value = value * 7
#            elif month_re.findall(inStr):
#                value = value * 30
        else:
            retDict = ''
    return retDict
    
def weight_resolve(inStr):
    if weight_re.findall(inStr):
        retDict = resolveDataFloat(unicode(inStr))
        return retDict
    else:
        return ''


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
        
jxn_list = m.MetaData.objects.filter(name = 'JxnPotential')
jxn_list_values = [md.value for md in jxn_list]
matchThresh = 70
def jxn_resolve(inStr):
    if len(inStr.split()) < 1:
        return ''
    processOut, matchVal = process.extractOne(inStr, jxn_list_values)
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
electrode_list_values.append('Whole-cell')
matchThresh = 70
def electrodetype_resolve(inStr):
    if len(inStr) < 1:
        return ''
#    print inStr
    processOut, matchVal = process.extractOne(inStr, electrode_list_values)
    if matchVal > matchThresh:
        if processOut == 'Whole-cell':
            return 'Patch-clamp'
        else:
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
    

        
        