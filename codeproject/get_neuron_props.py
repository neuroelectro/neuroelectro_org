# -*- coding: utf-8 -*-
"""
Created on Mon Nov 28 14:26:44 2011

@author: Shreejoy
"""

from SPARQLWrapper import SPARQLWrapper, JSON, XML, N3, RDF
import re
dir('C:\Python27\Scripts\biophys\pubdb\pubdir')
from pubapp.models import Neuron, Synonym, Species

neurons = Neuron.objects.all()
for neuron in neurons:
    nlex = neuron.nlexID
    ## get all synonyms of nlex
    sparql = SPARQLWrapper("http://api.talis.com/stores/neurolex-dev1/services/sparql")
    sparql.setQuery("""
    prefix xsd: <http://www.w3.org/2001/XMLSchema#>
    prefix property: <http://neurolex.org/wiki/Special:URIResolver/Property-3A>
    
    select distinct ?syn
    where {
        ?x property:Id "%s" ^^xsd:string .   
        ?x property:Synonym ?syn.    
    }
    
    """ % nlex)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    
    for result in results["results"]["bindings"]:
        synoynm = result["syn"]["value"]
        s = Synonym.objects.get_or_create(term = synoynm)[0]
        neuron.synonyms.add(s)
    
    sparql = SPARQLWrapper("http://api.talis.com/stores/neurolex-dev1/services/sparql")
    sparql.setQuery("""
    prefix xsd: <http://www.w3.org/2001/XMLSchema#>
    prefix property: <http://neurolex.org/wiki/Special:URIResolver/Property-3A>
    
    select distinct ?org
    where {
        ?x property:Id "%s" ^^xsd:string .      
        ?x property:Species ?org.
    }
    
    """ % nlex)    
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    
    for result in results["results"]["bindings"]:
        organism = result["org"]["value"]
        organism = re.search(r'A[\w]+', organism).group()
        organism = organism[1:]
        
        o = Species.objects.get_or_create(specie = organism)[0]
        neuron.specie = o
    neuron.save()   
