# -*- coding: utf-8 -*-
"""
Created on Mon Nov 21 12:48:28 2011

@author: Shreejoy
"""

#!/usr/bin/python
# -*- coding: utf-8 -*-

from SPARQLWrapper import SPARQLWrapper, JSON, XML, N3, RDF

sparql = SPARQLWrapper("http://api.talis.com/stores/neurolex-dev1/services/sparql")
sparql.setQuery("""
    prefix xsd: <http://www.w3.org/2001/XMLSchema#>
    prefix property: <http://neurolex.org/wiki/Special:URIResolver/Property-3A>

    select DISTINCT ?name ?id ?def where {?x property:Id "birnlex_779"^^xsd:string .
        ?cells property:Located_in ?x.
        ?cells property:Label ?name.
        ?cells property:Id ?id.
        ?cells property:CellSomaShape ?def}
""")

sparql = SPARQLWrapper("http://api.talis.com/stores/neurolex-dev1/services/sparql")
sparql.setQuery("""
    prefix xsd: <http://www.w3.org/2001/XMLSchema#>
    prefix property: <http://neurolex.org/wiki/Special:URIResolver/Property-3A>

    select DISTINCT ?name ?id ?syns where {?x property:Id "birnlex_779"^^xsd:string .
        ?cells property:Located_in ?x.
        ?cells property:Label ?name.
        ?cells property:Id ?id.
        ?cells property:Synonym ?syns}
""")

sparql = SPARQLWrapper("http://api.talis.com/stores/neurolex-dev1/services/sparql")
sparql.setQuery("""
    prefix xsd: <http://www.w3.org/2001/XMLSchema#>
    prefix property: <http://neurolex.org/wiki/Special:URIResolver/Property-3A>

    select DISTINCT ?name ?Id where {?x property:Id "sao1417703748"^^xsd:string .
        ?cells property:Neurotransmitter ?x.
        ?cells property:Id ?id.
        ?cells property:Label ?name.
        }
""")

sparql = SPARQLWrapper("http://rdf.neuinfo.org/sparql")
sparql.setQuery("""
    prefix nifstd: <http://ontology.neuinfo.org>
    prefix nm: <http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-Molecule.owl#>
    prefix be: <http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-Neuron-BrainRegion-Bridge.owl#>
    prefix nb: <http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-Neuron-NT-Bridge.owl#>
    prefix w3: <http://www.w3.org/2002/07/owl#>
    prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    prefix xsd: <http://www.w3.org/2001/XMLSchema#>

    select  ?e, ?l where {
        ?e rdfs:label ?l. 
        ?e rdfs:subClassOf ?hn.
        ?hn rdfs:label "Cerebellum neuron"^^xsd:string.
        ?e rdfs:subClassOf ?o.
        ?o w3:onProperty nb:has_neurotransmitter.
        ?o w3:someValuesFrom ?gaba.
        ?gaba rdfs:label "GABA"^^xsd:string.
        }
""")

# get all subclasses of kir channels
sparql = SPARQLWrapper("http://rdf.neuinfo.org/sparql")
sparql.setQuery("""
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
prefix sao: <http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-Cell.owl#>
prefix nm: <http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-Molecule.owl#>

SELECT ?y, ?yl
WHERE {
{{
  select *
  where
{
  ?y rdfs:subClassOf ?n
}
}
OPTION (TRANSITIVE, t_distinct, t_in(?n), t_out(?y) )
FILTER (?n = nm:nifext_2513) . ?y rdfs:label ?yl
}
}
""")

# get all subclasses of kir channels
sparql = SPARQLWrapper("http://rdf.neuinfo.org/sparql")
sparql.setQuery("""
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
prefix sao: <http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-Cell.owl#>
prefix nm: <http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-Molecule.owl#>
prefix obo: <http://ccdb.ucsd.edu/NIF/OBO_annotation_properties.owl#>

SELECT ?y, ?yl, ?syns
WHERE {
{{
  select *
  where
{
  ?y rdfs:subClassOf ?n
}
}
OPTION (TRANSITIVE, t_distinct, t_in(?n), t_out(?y) )
FILTER (?n = nm:nifext_2513) . ?y rdfs:label ?yl. 
    ?y obo:synonym ?syns.
}
}
""")

# get all synonyms of kv1.1
sparql = SPARQLWrapper("http://api.talis.com/stores/neurolex-dev1/services/sparql")
sparql.setQuery("""
prefix xsd: <http://www.w3.org/2001/XMLSchema#>
prefix property: <http://neurolex.org/wiki/Special:URIResolver/Property-3A>

select distinct ?label ?syn
where {
    ?x property:Id "nifext_2674"^^xsd:string .   
    ?x property:Label ?label.
    ?x property:Synonym ?syn.
}

""")

# get all subclasses of Multimeric ion channel
sparql = SPARQLWrapper("http://api.talis.com/stores/neurolex-dev1/services/sparql")
sparql.setQuery("""
prefix xsd: <http://www.w3.org/2001/XMLSchema#>
prefix property: <http://neurolex.org/wiki/Special:URIResolver/Property-3A>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>

select distinct ?label
where {
    ?x property:Label "Trimeric_ion_channel"^^xsd:string .
    ?y rdfs:subClassOf ?x.      
    ?y property:Label ?label.
}
""")

# get all categories with role Ion Channel
sparql = SPARQLWrapper("http://api.talis.com/stores/neurolex-dev1/services/sparql")
sparql.setQuery("""
prefix xsd: <http://www.w3.org/2001/XMLSchema#>
prefix property: <http://neurolex.org/wiki/Special:URIResolver/Property-3A>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
prefix nm: <http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-Molecule.owl#>

select distinct ?label
where {
    ?x property:Id "sao940366596"^^xsd:string .
    ?y property:Has_role ?x.
    ?y property:Label ?label.
}
""")

# get all categories with role Ion Channel
sparql = SPARQLWrapper("http://api.talis.com/stores/neurolex-dev1/services/sparql")
sparql.setQuery("""
prefix xsd: <http://www.w3.org/2001/XMLSchema#>
prefix property: <http://neurolex.org/wiki/Special:URIResolver/Property-3A>
select distinct ?id
where {
    ?x property:Label ?label.
    ?x property:Id ?id.
    filter regex(?label, "KCa1.1", "i").
}
""")




results = sparql.query().convert()
print results.toxml()


# XML example
print '\n\n*** XML Example'
sparql.setReturnFormat(XML)
results = sparql.query().convert()
print results.toxml()

# N3 example
print '\n\n*** N3 Example'
sparql.setReturnFormat(N3)
results = sparql.query().convert()
print results

# RDF example
print '\n\n*** RDF Example'
sparql.setReturnFormat(RDF)
results = sparql.query().convert()
print results.serialize()

# JSON example
print '\n\n*** JSON Example'
sparql.setReturnFormat(JSON)
results = sparql.query().convert()
for result in results["results"]["bindings"]:
    print result["label"]["value"]
