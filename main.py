from wiki_extractor import WikiExtractor
from content_processing import UBI_process_content

import spotlight

from rdflib import Graph
from rdflib import URIRef, BNode, Literal
from rdflib.namespace import RDF, FOAF
from rdflib import Namespace

from nltk.parse import CoreNLPParser
from nltk.tree import ParentedTree, Tree

# parser = CoreNLPParser(url='http://localhost:9000')

PROJECT = Namespace("https://UBI_project.org/")
SCHEMA = Namespace("https://schema.org/")
graph = Graph()

wiki_extract = WikiExtractor()
page_title = 'Basic_income_around_the_world'
page = wiki_extract.wikipedia.page(page_title)
all_sections = wiki_extract.get_sections(sections=page.sections)
section_titles = []
subsection_titles = []

only_place_filter = {'policy': "whitelist", 'types': "DBpedia:Place", 'coreferenceResolution': False}


# Adding Continents and Countries RDF
for section in all_sections:
    if isinstance(section, dict):
        for key in section.keys():
            try:
                section_annotations = spotlight.annotate('http://api.dbpedia-spotlight.org/en/annotate', key,
                                                         confidence=0.5, filters=only_place_filter)
                # print(section_annotations)
                graph.add((URIRef(section_annotations[0]['URI']), RDF.type, SCHEMA.Place))
                for subsection in section[key]:
                    if isinstance(subsection, dict):
                        try:
                            subsection_titles.append(list(subsection.keys())[0])
                            subsection_annotations = spotlight.annotate('http://api.dbpedia-spotlight.org/en/annotate',
                                                                        list(subsection.keys())[0], confidence=0.5,
                                                                        filters=only_place_filter)
                        except:
                            continue
                    else:
                        try:
                            subsection_annotations = spotlight.annotate('http://api.dbpedia-spotlight.org/en/annotate',
                                                                        subsection, confidence=0.5,
                                                                        filters=only_place_filter)
                            content = wiki_extract.get_section_content(page_title=page_title, section_title=subsection)
                            sentiment, places, years, plan, economy, positives, negatives = UBI_process_content(content)
                        except:
                            continue
                    # print(subsection_annotations)
                    graph.add((URIRef(subsection_annotations[0]['URI']), RDF.type, SCHEMA.Place))
                    if len(places) != 0:
                        for place in places:
                            graph.add((URIRef(subsection_annotations[0]['URI']), PROJECT.implemented_at, URIRef(place)))
                    if len(years) != 0:
                        for year in years:
                            graph.add((URIRef(subsection_annotations[0]['URI']), PROJECT.associated_year, URIRef(year)))
            except:
                continue

print(graph.serialize(destination='wiki_UBI.nt', format='nt'))


# annotations = spotlight.annotate('http://api.dbpedia-spotlight.org/en/annotate',
#                                  "January")
# print(annotations[0]["types"].split(","))



# sent = 'After the launch, the project was found to have significantly reduced child malnutrition and increased school attendance'
# t = list(parser.raw_parse(sent))[0]
# t = ParentedTree.convert(t)
#
# t.pretty_print()
#
#
#
#
# print(find_subject(t))
# print(find_predicate(t))
# print(find_object(t))