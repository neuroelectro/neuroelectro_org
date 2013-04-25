# -*- coding: utf-8 -*-
"""
Created on Wed Apr 10 13:41:52 2013

@author: Shreejoy
"""

import neuroelectro.models as m
from html_process_tools import getMethodsTag
import re
import nltk

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

def assign_species(article):
    terms = article.terms.all()
    if rat_mesh in terms:
        term_str = rat_mesh.term
        metadata_ob = m.MetaData.objects.get_or_create(name='Species', value=term_str)[0]
        article.metadata.add(metadata_ob)
    if mouse_mesh in terms:
        term_str = mouse_mesh.term
        metadata_ob = m.MetaData.objects.get_or_create(name='Species', value=term_str)[0]
        article.metadata.add(metadata_ob)
    if guinea_mesh in terms:
        term_str = guinea_mesh.term
        metadata_ob = m.MetaData.objects.get_or_create(name='Species', value=term_str)[0]
        article.metadata.add(metadata_ob)
    if bird_mesh in terms:
        term_str = bird_mesh.term
        metadata_ob = m.MetaData.objects.get_or_create(name='Species', value=term_str)[0]
        article.metadata.add(metadata_ob)
    if turtle_mesh in terms:
        term_str = turtle_mesh.term
        metadata_ob = m.MetaData.objects.get_or_create(name='Species', value=term_str)[0]
        article.metadata.add(metadata_ob)
    if cat_mesh in terms:
        term_str = cat_mesh.term
        metadata_ob = m.MetaData.objects.get_or_create(name='Species', value=term_str)[0]
        article.metadata.add(metadata_ob)
    if zebrafish_mesh in terms:
        term_str = zebrafish_mesh.term
        metadata_ob = m.MetaData.objects.get_or_create(name='Species', value=term_str)[0]
        article.metadata.add(metadata_ob)
    if monkey_mesh in terms:
        term_str = monkey_mesh.term
        metadata_ob = m.MetaData.objects.get_or_create(name='Species', value=term_str)[0]
        article.metadata.add(metadata_ob)
    if goldfish_mesh in terms:
        term_str = goldfish_mesh.term
        metadata_ob = m.MetaData.objects.get_or_create(name='Species', value=term_str)[0]
        article.metadata.add(metadata_ob)
    if aplysia_mesh in terms:
        term_str = aplysia_mesh.term
        metadata_ob = m.MetaData.objects.get_or_create(name='Species', value=term_str)[0]
        article.metadata.add(metadata_ob)
    if xenopus_mesh in terms:
        term_str = xenopus_mesh.term
        metadata_ob = m.MetaData.objects.get_or_create(name='Species', value=term_str)[0]
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
                metadata_ob = m.MetaData.objects.get_or_create(name='ElectrodeType', value='Patch-clamp')[0]
                article.metadata.add(metadata_ob)
                metadata_added = True
            if 'Sharp' in electrode_set:
                metadata_ob = m.MetaData.objects.get_or_create(name='ElectrodeType', value='Sharp')[0]   
                article.metadata.add(metadata_ob)
                metadata_added = True
            aftStatOb = m.ArticleFullTextStat.objects.get_or_create(article_full_text = full_text_ob)[0]
            aftStatOb.methods_tag_found = True
            aftStatOb.save()
    if metadata_added == False:
        mesh_terms = article.terms.all()
        if patch_mesh in mesh_terms:
            metadata_ob = m.MetaData.objects.get_or_create(name='ElectrodeType', value='Patch-clamp')[0]
            article.metadata.add(metadata_ob)
            metadata_added = True
#    if metadata_added == True:
#        print article
#        mds = m.MetaData.objects.filter(article = article)
#        print [(md.name, md.value) for md in mds]
            


        
#rat_mesh = m.MeshTerm.objects.get(term = 'Rats')
#mouse_mesh = m.MeshTerm.objects.get(term = 'Mice')
#guinea_mesh = m.MeshTerm.objects.get(term = 'Guinea Pigs') 
#bird_mesh = m.MeshTerm.objects.get(term = 'Songbirds') 
#turtle_mesh = m.MeshTerm.objects.get(term = 'Turtles') 
#cat_mesh = m.MeshTerm.objects.get(term = 'Cats') 
#zebrafish_mesh = m.MeshTerm.objects.get(term = 'Zebrafish')
#monkey_mesh = m.MeshTerm.objects.get(term = 'Macaca mulatta')
#goldfish_mesh = m.MeshTerm.objects.get(term = 'Goldfish')
#aplysia_mesh = m.MeshTerm.objects.get(term = 'Aplysia')
#xenopus_mesh = m.MeshTerm.objects.get(term = 'Xenopus')
#Strigiformes
#Crustacea
#Gerbillinae
#Sciuridae
#
#def species_mesh_terms():
    

#
#patch_mesh = m.MeshTerm.objects.get(term = 'Patch-Clamp Techniques')
#
#article_list = m.Article.objects.filter(datatable__datasource__neuronconceptmap__neuronephysdatamap__val_norm__isnull = False).distinct()
#species_list_all = []
#for a in article_list:
#    mesh_terms = a.terms.all()
#    species_list = []
#    if rat_mesh in mesh_terms:
#        print a.pmid, 'rat'
#        species_list.append('rat')
#    if mouse_mesh in mesh_terms:
#        print a.pmid, 'mouse'
#        species_list.append('mouse')
#    if bird_mesh in mesh_terms:
#        print a.pmid, 'bird'
#        species_list.append('bird')
#    if guinea_mesh in mesh_terms:
#        print a.pmid, 'guinea pig'
#        species_list.append('guinea pig')
#    if turtle_mesh in mesh_terms:
#        print a.pmid, 'turtle'
#        species_list.append('turtle')
#    if cat_mesh in mesh_terms:
#        print a.pmid, 'cat'
#        species_list.append('cat')
#    if zebrafish_mesh in mesh_terms:
#        print a.pmid, 'zebrafish'
#        species_list.append('zebrafish')
#    if monkey_mesh in mesh_terms:
#        print a.pmid, 'monkey'
#        species_list.append('monkey')
#    if goldfish_mesh in mesh_terms:
##        print a.pmid, 'monkey'
#        species_list.append('goldfish')
#    if aplysia_mesh in mesh_terms:
##        print a.pmid, 'monkey'
#        species_list.append('aplysia')
#    if xenopus_mesh in mesh_terms:
##        print a.pmid, 'monkey'
#        species_list.append('xenopus')
#    if len(species_list) == 0:
#        species_list.append('not specified')
#    species_list_all.append(species_list)