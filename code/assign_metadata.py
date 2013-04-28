# -*- coding: utf-8 -*-
"""
Created on Wed Apr 10 13:41:52 2013

@author: Shreejoy
"""

import neuroelectro.models as m
from html_process_tools import getMethodsTag
import re
import nltk
from html_table_decode import resolveDataFloat
import numpy as np
import string

rat_mesh = m.MeshTerm.objects.get(term = 'Rats')
mouse_mesh = m.MeshTerm.objects.get(term = 'Mice')
guinea_mesh = m.MeshTerm.objects.get(term = 'Guinea Pigs') 
bird_mesh = m.MeshTerm.objects.get(term = 'Songbirds') 
turtle_mesh = m.MeshTerm.objects.get(term = 'Turtles') 
cat_mesh = m.MeshTerm.objects.get(term = 'Cats') 
zebrafish_mesh = m.MeshTerm.objects.get(term = 'Zebrafish')
monkey_mesh = m.MeshTerm.objects.get(term = 'Macaca mulatta')
goldfish_mesh = m.MeshTerm.objects.get(term = 'Goldfish')
aplysia_mesh = m.MeshTerm.objects.get(term = 'Aplysia')
xenopus_mesh = m.MeshTerm.objects.get(term = 'Xenopus')

robot_user = m.get_robot_user()
def assign_species(article):
    terms = article.terms.all()
    if rat_mesh in terms:
        term_str = rat_mesh.term
        metadata_ob = m.MetaData.objects.get_or_create(name='Species', value=term_str, added_by = robot_user)[0]
        article.metadata.add(metadata_ob)
    if mouse_mesh in terms:
        term_str = mouse_mesh.term
        metadata_ob = m.MetaData.objects.get_or_create(name='Species', value=term_str, added_by = robot_user)[0]
        article.metadata.add(metadata_ob)
    if guinea_mesh in terms:
        term_str = guinea_mesh.term
        metadata_ob = m.MetaData.objects.get_or_create(name='Species', value=term_str, added_by = robot_user)[0]
        article.metadata.add(metadata_ob)
    if bird_mesh in terms:
        term_str = bird_mesh.term
        metadata_ob = m.MetaData.objects.get_or_create(name='Species', value=term_str, added_by = robot_user)[0]
        article.metadata.add(metadata_ob)
    if turtle_mesh in terms:
        term_str = turtle_mesh.term
        metadata_ob = m.MetaData.objects.get_or_create(name='Species', value=term_str, added_by = robot_user)[0]
        article.metadata.add(metadata_ob)
    if cat_mesh in terms:
        term_str = cat_mesh.term
        metadata_ob = m.MetaData.objects.get_or_create(name='Species', value=term_str, added_by = robot_user)[0]
        article.metadata.add(metadata_ob)
    if zebrafish_mesh in terms:
        term_str = zebrafish_mesh.term
        metadata_ob = m.MetaData.objects.get_or_create(name='Species', value=term_str, added_by = robot_user)[0]
        article.metadata.add(metadata_ob)
    if monkey_mesh in terms:
        term_str = monkey_mesh.term
        metadata_ob = m.MetaData.objects.get_or_create(name='Species', value=term_str, added_by = robot_user)[0]
        article.metadata.add(metadata_ob)
    if goldfish_mesh in terms:
        term_str = goldfish_mesh.term
        metadata_ob = m.MetaData.objects.get_or_create(name='Species', value=term_str, added_by = robot_user)[0]
        article.metadata.add(metadata_ob)
    if aplysia_mesh in terms:
        term_str = aplysia_mesh.term
        metadata_ob = m.MetaData.objects.get_or_create(name='Species', value=term_str, added_by = robot_user)[0]
        article.metadata.add(metadata_ob)
    if xenopus_mesh in terms:
        term_str = xenopus_mesh.term
        metadata_ob = m.MetaData.objects.get_or_create(name='Species', value=term_str, added_by = robot_user)[0]
        article.metadata.add(metadata_ob)
        
patch_mesh = m.MeshTerm.objects.get(term = 'Patch-Clamp Techniques')
whole_re = re.compile(ur'whole\scell|whole-cell|patch\sclamp|patch-clamp' , flags=re.UNICODE|re.IGNORECASE)
sharp_re = re.compile(ur'sharp.+electro' , flags=re.UNICODE|re.IGNORECASE)

def assign_electrode_type(article):
    metadata_added = False
    if article.articlefulltext_set.all().count() > 0:
        full_text_ob = article.articlefulltext_set.all()[0]
        full_text = full_text_ob.get_content()
        methods_tag = getMethodsTag(full_text, article)
        if methods_tag is None:
            print (article.pmid, article.title, article.journal)
        else:
            text = re.sub('\s+', ' ', methods_tag.text)    
            sents = nltk.sent_tokenize(text)
            electrode_set = set()
            
            for s in sents:
                if whole_re.findall(s):
        #            wholeCellSet.add(art)
        #            print 'whole: ' + art.title
        #            print str(idx) + ' : ' + s.encode("iso-8859-15", "replace")
                    electrode_set.add('Patch-clamp')
        #            electrode_list.append('Whole-cell')
        #            electrode_list_text_mine.append('Whole-cell')
                if sharp_re.findall(s):
        #            sharpSet.add(art)
        #            print 'sharp: ' + art.title
        #            print str(idx) + ' : ' + s.encode("iso-8859-15", "replace")
                    electrode_set.add('Sharp')
            if 'Patch-clamp' in electrode_set:
                metadata_ob = m.MetaData.objects.get_or_create(name='ElectrodeType', value='Patch-clamp', added_by = robot_user)[0]
                article.metadata.add(metadata_ob)
                metadata_added = True
            if 'Sharp' in electrode_set:
                metadata_ob = m.MetaData.objects.get_or_create(name='ElectrodeType', value='Sharp', added_by = robot_user)[0]   
                article.metadata.add(metadata_ob)
                metadata_added = True
            aftStatOb = m.ArticleFullTextStat.objects.get_or_create(article_full_text = full_text_ob)[0]
            aftStatOb.methods_tag_found = True
            aftStatOb.save()
    if metadata_added == False:
        mesh_terms = article.terms.all()
        if patch_mesh in mesh_terms:
            metadata_ob = m.MetaData.objects.get_or_create(name='ElectrodeType', value='Patch-clamp', added_by = robot_user)[0]
            article.metadata.add(metadata_ob)
            metadata_added = True
#    if metadata_added == True:
#        print article
#        mds = m.MetaData.objects.filter(article = article)
#        print [(md.name, md.value) for md in mds]
            
fischer_mesh = m.MeshTerm.objects.get(term = 'Rats, Inbred F344')
longevans_mesh = m.MeshTerm.objects.get(term = 'Rats, Long-Evans')
sprague_mesh = m.MeshTerm.objects.get(term = 'Rats, Sprague-Dawley') 
wistar_mesh = m.MeshTerm.objects.get(term = 'Rats, Wistar') 
black6_mesh = m.MeshTerm.objects.get(term = 'Mice, Inbred C57BL') 
balbc_mesh = m.MeshTerm.objects.get(term = 'Mice, Inbred BALB C') 
mouse_transgenic_mesh = m.MeshTerm.objects.get(term = 'Mice, Transgenic')
rat_transgenic_mesh = m.MeshTerm.objects.get(term = 'Rats, Transgenic')
def assign_strain(article):
    terms = article.terms.all()
    if fischer_mesh in terms:
        term_str = fischer_mesh.term
        metadata_ob = m.MetaData.objects.get_or_create(name='Strain', value='Fischer 344', added_by = robot_user)[0]
        article.metadata.add(metadata_ob)
    if longevans_mesh in terms:
        term_str = longevans_mesh.term
        metadata_ob = m.MetaData.objects.get_or_create(name='Strain', value='Long-Evans', added_by = robot_user)[0]
        article.metadata.add(metadata_ob)
    if sprague_mesh in terms:
        term_str = sprague_mesh.term
        metadata_ob = m.MetaData.objects.get_or_create(name='Strain', value='Sprague-Dawley', added_by = robot_user)[0]
        article.metadata.add(metadata_ob)
    if wistar_mesh in terms:
        term_str = wistar_mesh.term
        metadata_ob = m.MetaData.objects.get_or_create(name='Strain', value='Wistar', added_by = robot_user)[0]
        article.metadata.add(metadata_ob)
    if black6_mesh in terms:
        term_str = black6_mesh.term
        metadata_ob = m.MetaData.objects.get_or_create(name='Strain', value='C57BL', added_by = robot_user)[0]
        article.metadata.add(metadata_ob)
    if balbc_mesh in terms:
        term_str = balbc_mesh.term
        metadata_ob = m.MetaData.objects.get_or_create(name='Strain', value='BALB C', added_by = robot_user)[0]
        article.metadata.add(metadata_ob)
    if mouse_transgenic_mesh in terms:
        term_str = mouse_transgenic_mesh.term
        metadata_ob = m.MetaData.objects.get_or_create(name='Strain', value='Mouse, Transgenic', added_by = robot_user)[0]
        article.metadata.add(metadata_ob)
    if rat_transgenic_mesh in terms:
        term_str = rat_transgenic_mesh.term
        metadata_ob = m.MetaData.objects.get_or_create(name='Strain', value='Rat, Transgenic', added_by = robot_user)[0]
        article.metadata.add(metadata_ob)
        
culture_mesh = m.MeshTerm.objects.get(term = 'Cell Culture Techniques')
in_silico_mesh = m.MeshTerm.objects.get(term = 'Computer Simulation')
culture_re = re.compile(ur'culture' , flags=re.UNICODE|re.IGNORECASE)
in_vitro_re = re.compile(ur'slice|in\svitro' , flags=re.UNICODE|re.IGNORECASE)
in_vivo_re = re.compile(ur'in\svivo' , flags=re.UNICODE|re.IGNORECASE)
model_re = re.compile(ur'model' , flags=re.UNICODE|re.IGNORECASE)

def assign_prep_type(article):
    metadata_added = False
    if article.articlefulltext_set.all().count() > 0:
        full_text_ob = article.articlefulltext_set.all()[0]
        full_text = full_text_ob.get_content()
        methods_tag = getMethodsTag(full_text, article)
        if methods_tag is None:
            print (article.pmid, article.title, article.journal)
        else:
            text = re.sub('\s+', ' ', methods_tag.text)    
            sents = nltk.sent_tokenize(text)
            prep_type_set = set()
            
            for s in sents:
                if culture_re.findall(s):
                    prep_type_set.add('cell culture')
                if in_vitro_re.findall(s):
                    prep_type_set.add('in vitro')
                if in_vivo_re.findall(s):
                    prep_type_set.add('in vivo')
                if model_re.findall(s):
                    prep_type_set.add('model')
            if 'cell culture' in prep_type_set:
                metadata_ob = m.MetaData.objects.get_or_create(name='PrepType', value='cell culture', added_by = robot_user)[0]
                article.metadata.add(metadata_ob)
                metadata_added = True
            if 'in vitro' in prep_type_set:
                metadata_ob = m.MetaData.objects.get_or_create(name='PrepType', value='in vitro', added_by = robot_user)[0]   
                article.metadata.add(metadata_ob)
                metadata_added = True
            if 'in vivo' in prep_type_set:
                metadata_ob = m.MetaData.objects.get_or_create(name='PrepType', value='in vivo', added_by = robot_user)[0]   
                article.metadata.add(metadata_ob)
                metadata_added = True
#            if 'model' in prep_type_set:
#                metadata_ob = m.MetaData.objects.get_or_create(name='PrepType', value='model', added_by = robot_user)[0]   
#                article.metadata.add(metadata_ob)
#                metadata_added = True
            aftStatOb = m.ArticleFullTextStat.objects.get_or_create(article_full_text = full_text_ob)[0]
            aftStatOb.methods_tag_found = True
            aftStatOb.save()
    if metadata_added == False:
        mesh_terms = article.terms.all()
        if culture_mesh in mesh_terms:
            metadata_ob = m.MetaData.objects.get_or_create(name='PrepType', value='cell culture', added_by = robot_user)[0]
            article.metadata.add(metadata_ob)
            metadata_added = True
        if in_silico_mesh in mesh_terms:
            metadata_ob = m.MetaData.objects.get_or_create(name='PrepType', value='model', added_by = robot_user)[0]
            article.metadata.add(metadata_ob)
            metadata_added = True

celsius_re = re.compile(ur'record.+°C|experiment.+°C', flags=re.UNICODE|re.IGNORECASE)
room_temp_re = re.compile(ur'record.+room\stemperature|experiment.+room temperature', flags=re.UNICODE|re.IGNORECASE)
def assign_rec_temp(article):
# find a sentence that mentions recording and temperature or degree celsius
    full_text_ob = article.articlefulltext_set.all()[0]
    ft = full_text_ob.get_content()
    methods_tag = getMethodsTag(ft, article)
    text = re.sub('\s+', ' ', methods_tag.text)
    temp_dict_list = []
    sents = nltk.sent_tokenize(text)
    for s in sents:
#        print s.encode("iso-8859-15", "replace")
        if celsius_re.findall(s):
#            print article.pk
#            print s.encode("iso-8859-15", "replace")
            degree_ind = s.rfind(u'°C')
            min_sent_ind = 0
            max_sent_ind = len(s)
            degree_close_str = s[np.maximum(min_sent_ind, degree_ind-20):np.minimum(max_sent_ind, degree_ind+1)]
            retDict = resolveDataFloat(degree_close_str)
            if 'value' in retDict:
                temp_dict_list.append(retDict)
        elif room_temp_re.findall(s):
#            print article.pk
#            print s.encode("iso-8859-15", "replace")
            retDict = {'value':22.0, 'maxRange' : 24.0, 'minRange': 20.0}
            temp_dict_list.append(retDict)
    if len(temp_dict_list) > 0:
#        print temp_dict_list
        temp_dict_fin = validate_temp_list(temp_dict_list)
#        print temp_dict_fin
        if temp_dict_fin:
            min_range = None
            max_range = None
            stderr = None
            if 'minRange' in temp_dict_fin:
                min_range = temp_dict_fin['minRange']
            if 'maxRange' in temp_dict_fin:
                max_range = temp_dict_fin['maxRange']
            if 'error' in temp_dict_fin:
                stderr = temp_dict_fin['error']
            cont_value_ob = m.ContValue.objects.get_or_create(mean = temp_dict_fin['value'], min_range = min_range,
                                                              max_range = max_range, stderr = stderr)[0]
            metadata_ob = m.MetaData.objects.get_or_create(name='RecTemp', cont_value=cont_value_ob, added_by = robot_user)[0]
            article.metadata.add(metadata_ob)
            metadata_added = True
            aftStatOb = m.ArticleFullTextStat.objects.get_or_create(article_full_text = full_text_ob)[0]
            aftStatOb.methods_tag_found = True
            aftStatOb.save()
        # assign metadata!
        
def validate_temp_list(temp_dict_list):
    if len(temp_dict_list) == 1:
        temp_dict_fin = temp_dict_list[0]
    else:
        value_list = [l['value'] for l in temp_dict_list]
        if max(value_list) - min(value_list) > 5:
            return None
        else:
            temp_dict_fin = dict()
            for l in temp_dict_list:
                temp_dict_fin = dict(temp_dict_fin.items() + l.items())
    if temp_dict_fin['value'] > 18 and temp_dict_fin['value'] < 42:
        return temp_dict_fin
    else:
        return None
        
p_age_re = re.compile(ur'P(\d+)-P(\d+)|P(\d+)-(\d+)|P(\d+)–P(\d+)|P(\d+)–(\d+)', flags=re.UNICODE|re.IGNORECASE)
#p_age_re = re.compile(ur'P(\d+)', flags=re.UNICODE|re.IGNORECASE)
day_re = age_re = re.compile(ur'\sday\sold|\sday\sold|\sage.+\sday' , flags=re.UNICODE|re.IGNORECASE)
week_re = age_re = re.compile(ur'\sweek\sold|\sweek\sold|\sage.+\sweek' , flags=re.UNICODE|re.IGNORECASE)
def assign_animal_age(article):
# find a sentence that mentions recording and temperature or degree celsius
    full_text_ob = article.articlefulltext_set.all()[0]
    ft = full_text_ob.get_content()
    methods_tag = getMethodsTag(ft, article)
    text = re.sub('\s+', ' ', methods_tag.text)
    age_dict_list = []
    sents = nltk.sent_tokenize(text)
    for s in sents:
#        print s.encode("iso-8859-15", "replace")
        if p_age_re.findall(s):
#            print article.pk
            print s.encode("iso-8859-15", "replace")
            print 'Pnumber'
            p_iter = re.finditer(ur'P\d', s) 
            matches = [(match.start(0), match.end(0)) for match in p_iter]
            p_ind = matches[-1][0]
#            p_ind = s.rfind(ur'P\d')
            min_sent_ind = 0
            max_sent_ind = len(s)
            p_close_str = s[np.maximum(min_sent_ind, p_ind-15):np.minimum(max_sent_ind, p_ind+15)]
#            print p_close_str
            p_close_str = p_close_str.translate(dict((ord(c), u'') for c in string.ascii_letters)).strip()
#            print p_close_str
            retDict = resolveDataFloat(p_close_str)
#            print retDict
            if 'value' in retDict:
                age_dict_list.append(retDict)
        elif day_re.findall(s):
#            print article.pk
            print s.encode("iso-8859-15", "replace")
            print 'day'
            p_iter = re.finditer(ur'\sday', s) 
            matches = [(match.start(0), match.end(0)) for match in p_iter]
            p_ind = matches[-1][0]
#            p_ind = s.rfind(ur'P\d')
            min_sent_ind = 0
            max_sent_ind = len(s)
            p_close_str = s[np.maximum(min_sent_ind, p_ind-15):np.minimum(max_sent_ind, p_ind+15)]
#            print p_close_str
            p_close_str = p_close_str.translate(dict((ord(c), u'') for c in string.ascii_letters)).strip()
#            print p_close_str
            retDict = resolveDataFloat(p_close_str)
#            print retDict
            if 'value' in retDict:
                age_dict_list.append(retDict)
    if len(age_dict_list) > 0:
#        print temp_dict_list
#        print age_dict_list
        age_dict_fin = validate_age_list(age_dict_list)
#        print age_dict_fin
        if age_dict_fin:
            min_range = None
            max_range = None
            stderr = None
            if 'minRange' in age_dict_fin:
                min_range = age_dict_fin['minRange']
            if 'maxRange' in age_dict_fin:
                max_range = age_dict_fin['maxRange']
            if 'error' in age_dict_fin:
                stderr = age_dict_fin['error']
            cont_value_ob = m.ContValue.objects.get_or_create(mean = age_dict_fin['value'], min_range = min_range,
                                                              max_range = max_range, stderr = stderr)[0]
            metadata_ob = m.MetaData.objects.get_or_create(name='AnimalAge', cont_value=cont_value_ob, added_by = robot_user)[0]
            article.metadata.add(metadata_ob)
            metadata_added = True
            aftStatOb = m.ArticleFullTextStat.objects.get_or_create(article_full_text = full_text_ob)[0]
            aftStatOb.methods_tag_found = True
            aftStatOb.save()
#            print metadata_ob

def validate_age_list(age_dict_list):
    if len(age_dict_list) == 1:
        age_dict_fin = age_dict_list[0]
    else:
        value_list = [l['value'] for l in age_dict_list]
        if max(value_list) - min(value_list) > 10:
            return None
        else:
            age_dict_fin = dict()
            for l in age_dict_list:
                age_dict_fin = dict(age_dict_fin.items() + l.items())
    if age_dict_fin['value'] > 0 :
        return age_dict_fin
    else:
        return None
        