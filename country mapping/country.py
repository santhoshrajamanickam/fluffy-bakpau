import json
from rdflib import Graph
from rdflib import URIRef, BNode, Literal
from rdflib.namespace import RDF, FOAF
from rdflib import Namespace
import requests

PROJECT = Namespace("https://UBI_project.org/")
SCHEMA = Namespace("https://schema.org/")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")
graph = Graph()

country_codes = []
with open('DistinctCountry.srj') as json_file:
    data = json.load(json_file)
    for p in data['results']['bindings']:
        country_codes.append(p['c']['value'])

for code in country_codes:
    r = requests.get("https://restcountries.eu/rest/v2/alpha/{}".format(code)).json()
    name = r["name"].replace(" ", "_")
    print("Code {} and name {}".format(code, name))
    graph.add((URIRef(name), RDF.type, SCHEMA.Place))
    graph.add((URIRef(code), RDF.type, FOAF.name))
    graph.add((URIRef(name), PROJECT.has_code, URIRef(code)))

print(graph.serialize(destination='country_codes.nt', format='nt'))





'''
code = "AT"

'''
