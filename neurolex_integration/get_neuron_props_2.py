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

from neuroelectro.models import Neuron, NeuronSyn
from sparql_methods import sparql_get

def load_neuron_names():
    os.chdir('C:\Python27\Scripts\Biophys')
    f = open('neurolex_neuron_list.txt', 'r')
    text = f.read()
    names = text.split('\n')
    return names

neuronNameList = load_neuron_names()
queryTerm = 'Id'
usingTermMethod = 'Label'
for neuronName in neuronNameList:
    ## get all nlex id of neuron name
    nlex =  sparql_get(queryTerm, neuronName, usingTermMethod)
    if nlex:
        print neuronName, nlex[0]
        n = Neuron.objects.get_or_create(nlex_id = nlex[0], name = neuronName)[0]
        n.save()
    else:
        print neuronName + " not found in nlex"
        n = Neuron.objects.get_or_create(nlex_id = 0, name = neuronName)[0]
        n.save()

neurons = Neuron.objects.all()
usingTermMethod = 'Label'
for neuron in neurons:
    queryTerm = 'Synonym'
    synonyms = sparql_get(queryTerm, neuron, usingTermMethod)
    synonyms.insert(0,neuron.name)
    synonyms = [re.sub(r'[()"]', r'', syn) for syn in synonyms]
    synonyms = [syn.lower().strip() for syn in synonyms]
    synonyms = list(set(synonyms))
    print neuron, synonyms
    synObList = []
    for syn in synonyms:
        synOb = NeuronSyn.objects.get_or_create(term = syn)[0]
        synObList.append(synOb)
    neuron.synonyms = synObList 

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
