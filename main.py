from wiki_extractor import WikiExtractor
from content_processing import extract_info, add_instances

import spotlight

from rdflib import Graph
from rdflib import URIRef
from rdflib.namespace import RDF, OWL
from rdflib import Namespace

PROJECT = Namespace("https://UBI_project.org/UBI_wiki/")
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
            place = key
            graph.add((PROJECT[place.replace(" ", "_")], RDF.type, SCHEMA.Place))
            try:
                section_annotations = spotlight.annotate('http://api.dbpedia-spotlight.org/en/annotate', place,
                                                         confidence=0.5, filters=only_place_filter)
                graph.add((URIRef(section_annotations[0]['URI']), OWL.sameAs, PROJECT["place/" + place.replace(" ", "_")]))
            except:
                print("")

            for subsection in section[key]:
                if isinstance(subsection, dict):
                    place = list(subsection.keys())[0]
                else:
                    place = subsection

                graph.add((PROJECT["place/" + place.replace(" ", "_")], RDF.type, SCHEMA.Place))
                graph.add(
                    (PROJECT["place/" + key.replace(" ", "_")], SCHEMA.containsPlace,
                     PROJECT["place/" + place.replace(" ", "_")]))
                try:
                    subsection_annotations = spotlight.annotate('http://api.dbpedia-spotlight.org/en/annotate',
                                                                place, confidence=0.5,
                                                                filters=only_place_filter)
                    graph.add((URIRef(subsection_annotations[0]['URI']), OWL.sameAs,
                               PROJECT["place/" + place.replace(" ", "_")]))
                except:
                    print("")

                if isinstance(subsection, dict):
                    for subsubsection in list(subsection.values())[0]:
                        try:
                            subsubsection_annotations = \
                                spotlight.annotate('http://api.dbpedia-spotlight.org/en/annotate',
                                                   subsubsection, confidence=0.5, filters=only_place_filter)
                            place = subsubsection_annotations[0]['surfaceForm']
                            graph.add((PROJECT["place/" + place.replace(" ", "_")], RDF.type, SCHEMA.Place))
                            graph.add((PROJECT["place/" + key.replace(" ", "_")],
                                       SCHEMA.containsPlace, PROJECT["place/" + place.replace(" ", "_")]))
                            graph.add((URIRef(subsubsection_annotations[0]['URI']),
                                       OWL.sameAs, PROJECT["place/" + place.replace(" ", "_")]))
                        except:
                            print("")

                        content = wiki_extract.get_section_content(page_title=page_title, section_title=subsubsection)
                        processed_sentences = extract_info(content)

                        for sentences_tuple in processed_sentences:
                            add_instances(graph, place, PROJECT, sentences_tuple)
                else:
                    content = wiki_extract.get_section_content(page_title=page_title, section_title=subsection)
                    processed_sentences = extract_info(content)

                    for sentences_tuple in processed_sentences:
                        add_instances(graph, place, PROJECT, sentences_tuple)

print(graph.serialize(destination='wiki_UBI.nt', format='nt'))
