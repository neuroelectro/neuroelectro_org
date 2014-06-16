# -*- coding: utf-8 -*-
"""
Created on Fri Dec 09 14:36:58 2011

@author: Shreejoy
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Dec 07 20:13:41 2011

@author: Shreejoy
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Nov 28 14:26:44 2011

@author: Shreejoy
"""

from SPARQLWrapper import SPARQLWrapper, JSON, XML, N3, RDF
import re
import os
import django_startup
#dir('C:\Python27\Scripts\biophys\pubdb\pubdir')

from pubapp.models import IonChannel, IonChannelSyn, Species
from sparql_methods import sparql_get

def load_channel_names():
    os.chdir('C:\Python27\Scripts\Biophys')
    f = open('IonChannelNames.txt', 'r')
    text = f.read()
    text = re.sub('\<[\w/]+\>', '', text)
    names = text.split('\n')
    return names

def load_channel_genes():
    os.chdir('C:\Python27\Scripts\Biophys')
    f = open('IonChannelNames_genes.txt', 'r')
    text = f.read()
    text = re.sub('\<[\w/]+\>', '', text)
    names = text.split('\n')
    return names

# if synonym term includes underscores or semicolons, process it
def term_process(synonyms):
    synonymList = []
    for synonym in synonyms:
        if re.search(r'[\;\_]', synonym) is not None:
            #first replace underscores with white spaces
            synonym = re.sub(r'\_', r' ', synonym)
            splitList = synonym.split(';')
            synonymList.extend(splitList)
#            for term in splitList:
#               s = Synonym.objects.get_or_create(term = term)[0] 
#            continue
        else:
            synonymList.append(synonym)
    return synonymList

channelNameList = load_channel_names()
channelGenes = load_channel_genes()
queryTerm = 'Id'
usingTermMethod = 'Label'
cnt = -1
for channelName in channelNameList:
    cnt += 1
    ## get all synonyms of nlex
    nlex =  sparql_get(queryTerm, channelName, usingTermMethod)
    if nlex:
        print channelName, nlex[0], channelGenes[cnt]
        c = IonChannel.objects.get_or_create(nlexID = nlex[0], name = channelName)[0]
        # add channel gene as well
        c.gene = channelGenes[cnt]
        c.save()
    else:
        print channelName + " not found in nlex"
        c = IonChannel.objects.get_or_create(nlexID = 0, name = channelName)[0]
        c.gene = channelGenes[cnt]
        c.save()
        print channelName, channelGenes[cnt]

channels = IonChannel.objects.all()
usingTermMethod = 'Label'
for channel in channels:
    queryTerm = 'Synonym'
    synonyms = sparql_get(queryTerm, channel.name, usingTermMethod)
    synonyms = term_process(synonyms)
    synonyms.insert(0,channel.name)
    synonyms.insert(1,channel.gene)
    synonyms = [syn.lower().strip() for syn in synonyms]
    synonyms = list(set(synonyms))
    print channel, synonyms
    synObList = []
    for syn in synonyms:
        synOb = IonChannelSyn.objects.get_or_create(term = syn)[0]
        synObList.append(synOb)
    channel.synonyms = synObList 
#
## add genes to channels
#channelGenes = load_channel_genes()
#cnt = 0
#for channelName in channelNameList:
#    channel = IonChannel.objects.filter(name = channelName)
#    print channelName, channel, channelGenes[cnt]
#    if channelGenes[cnt] is '':
#        cnt += 1
#        continue
##    channel.gene = channelGenes[cnt]
##    channel.save()
#    cnt += 1
#    synOb = IonChannelSyn.objects.get_or_create(term = channel.gene)[0]
#    channel.synonyms.add(synOb) 
#     add gene as a synonym
    
    

  
    
#    queryTerm = 'SomaLocation'
#    location =  sparql_get(queryTerm, neuronName, usingTermMethod)
#    neuron.locatedin =   

 
    
#        s = Synonym.objects.get_or_create(term = synoynm)[0]
#        neuron.synonyms.add(s)
#    
#    sparql = SPARQLWrapper("http://api.talis.com/stores/neurolex-dev1/services/sparql")
#    sparql.setQuery("""
#    prefix xsd: <http://www.w3.org/2001/XMLSchema#>
#    prefix property: <http://neurolex.org/wiki/Special:URIResolver/Property-3A>
#    
#    select distinct ?org
#    where {
#        ?x property:Id "%s" ^^xsd:string .      
#        ?x property:Species ?org.
#    }
#    
#    """ % nlex)    
#    sparql.setReturnFormat(JSON)
#    results = sparql.query().convert()
#    
#    for result in results["results"]["bindings"]:
#        organism = result["org"]["value"]
#        organism = re.search(r'A[\w]+', organism).group()
#        organism = organism[1:]
#        
#        o = Species.objects.get_or_create(specie = organism)[0]
#        neuron.specie = o
#    neuron.save()   
