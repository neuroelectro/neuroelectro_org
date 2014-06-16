# -*- coding: utf-8 -*-
"""
Created on Sun Nov 27 14:03:34 2011

@author: Shreejoy
"""


#!/usr/bin/python
# -*- coding: utf-8 -*-

from SPARQLWrapper import SPARQLWrapper, JSON, XML, N3, RDF
import re
cd 'C:\Python27\Scripts\biophys\pubdb\pubdir'
from pubapp.models import Neuron

# get all subclasses of kir channels
sparql = SPARQLWrapper("http://rdf.neuinfo.org/sparql")
sparql.setQuery("""
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
prefix sao: <http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-Cell.owl#>

SELECT distinct ?e, ?l
WHERE {
{{
  select *
  where
{
  ?e rdfs:subClassOf ?n
}
}
OPTION (TRANSITIVE, t_distinct, t_in(?n), t_out(?e) )
FILTER (?n = sao:sao1417703748) . ?e rdfs:label ?l
}
}
""")

sparql.setReturnFormat(JSON)
results = sparql.query().convert()

neuronList = []
neuronIdList = []
cnt = 0
for result in results["results"]["bindings"]:
    neuronName = result["l"]["value"]
    neuronID = re.search(r'\#[\w]+', result["e"]["value"]).group()
    neuronID = neuronID[1:] # remove starting hashtag
    n = Neuron.objects.get_or_create(nlexID = neuronID, name = neuronName)[0]  
    neuronList.append(result["l"]["value"])
    neuronIdList.append(neuronID[1:])
    n.save()
