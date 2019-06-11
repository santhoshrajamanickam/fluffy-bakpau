import re
import nltk
import spotlight
from rdflib import URIRef, Literal, Namespace
from rdflib.namespace import RDF, OWL
import spacy
from pycorenlp import StanfordCoreNLP

SCHEMA = Namespace("https://schema.org/")

stanford_nlp = StanfordCoreNLP('http://localhost:9000')
spacy_nlp = spacy.load('en')

only_place_filter = {'policy': "whitelist", 'types': "DBpedia:Place", 'coreferenceResolution': False}
only_person_filter = {'policy': "whitelist", 'types': "DBpedia:Person", 'coreferenceResolution': False}
only_organization_filter = {'policy': "whitelist", 'types': "DBpedia:Organisation", 'coreferenceResolution': False}

currency_regex = "(?:[a-zA-Z]*[\£\$\€]{1}[,\d]+)"
US_dollars_regex = "(?:[,\d]+.U.S. dollars)"
euros_regex = "(?:[,\d]+.euros)"
CUR_regex = "(?:[,\d]+.[A-Z][A-Z][A-Z])"
francs_regex = "(?:[,\d]+.[a-z]*.francs)"


# extract the money related instances
def get_money_instances(sentence):
    money = re.findall(currency_regex, sentence)
    money = set(money)

    us_dollars = re.findall(US_dollars_regex, sentence)
    if len(us_dollars) > 0:
        for us_dollar in us_dollars:
            money.add("US$" + re.split(" ", us_dollar)[0])

    euros = re.findall(euros_regex, sentence)
    if len(euros) > 0:
        for euro in euros:
            money.add("€" + re.split(" ", euro)[0])

    curs = re.findall(CUR_regex, sentence)
    if len(curs) > 0:
        for cur in curs:
            money.add(cur)

    francs = re.findall(francs_regex, sentence)
    if len(francs) > 0:
        for franc in francs:
            money.add(franc)

    return money


# extract the date related instances
def get_date_instances(annotated_sentence):

    dates = set()

    for annotated_word in annotated_sentence["sentences"][0]["tokens"]:
        if annotated_word["ner"] == "DATE":
            dates.add(annotated_word["normalizedNER"])

    return dates


# extract the location related instances
def get_location_instances(annotated_sentence):

    places = set()

    for annotated_word in annotated_sentence["sentences"][0]["tokens"]:
        if annotated_word["ner"] == "LOCATION" or annotated_word["ner"] == "COUNTRY" or annotated_word["ner"] == "CITY":
            if annotated_word["originalText"] != annotated_word["lemma"]:
                continue
            else:
                places.add(annotated_word["word"])

    return places


# extract the person related instances
def get_person_instances(annotated_sentence):

    people = set()
    person = []

    for annotated_word in annotated_sentence["sentences"][0]["tokens"]:
        if annotated_word["ner"] == "PERSON":
            person.append(annotated_word["word"])
            continue
        elif len(person) != 0:
            people.add(" ".join(person))
            person.clear()

    return people


# extract the organization related instances
def get_organization_instances(annotated_sentence):

    organizations = set()
    organization = []

    for annotated_word in annotated_sentence["sentences"][0]["tokens"]:
        if annotated_word["ner"] == "ORGANIZATION":
            organization.append(annotated_word["word"])
            continue
        elif len(organization) != 0:
            organizations.add(" ".join(organization))
            organization.clear()

    return organizations


# process sentences to extract useful information (money, dates, places, people, organizations)
# from the content passed as argument
def extract_info(content):
    processed_sentences = []
    sentences = nltk.sent_tokenize(content)

    for sentence in sentences:
        stanford_annontation = stanford_nlp.annotate(sentence, properties={'annotators': 'ner',
                                                                           'outputFormat': 'json',
                                                                           'timeout': 5000,
                                                                           })
        money = get_money_instances(sentence)
        dates = get_date_instances(stanford_annontation)
        places = get_location_instances(stanford_annontation)
        people = get_person_instances(stanford_annontation)
        organizations = get_organization_instances(stanford_annontation)

        # print(money)
        # print(dates)
        # print(places)
        # print(people)
        # print(organizations)

        processed_sentences.append((money, dates, places, people, organizations))

    return processed_sentences


# link to dbpedia instance linking
def instance_linking(info_tuple):

    place_annotations = {}
    people_annotations = {}
    organization_annotations = {}

    _, _, places, people, organizations = info_tuple

    for place in places:
        try:
            place_annotations[place] = spotlight.annotate('http://api.dbpedia-spotlight.org/en/annotate',
                                                          place, filters=only_place_filter)[0]['URI']
        except:
            continue

    for person in people:
        try:
            people_annotations[person] = spotlight.annotate('http://api.dbpedia-spotlight.org/en/annotate',
                                                            person, filters=only_person_filter)[0]['URI']
        except:
            continue

    for organization in organizations:
        try:
            organization_annotations[organization] = spotlight.annotate('http://api.dbpedia-spotlight.org/en/annotate',
                                                                        organization,
                                                                        filters=only_organization_filter)[0]['URI']
        except:
            continue

    return place_annotations, people_annotations, organization_annotations


def add_instances(graph, place, project, sentences_tuple):
    money, dates, locations, people, organizations = sentences_tuple
    place_annotations, people_annotations, organization_annotations = instance_linking(sentences_tuple)

    if len(money) != 0:
        for amount in money:
            graph.add((project["place/" + place.replace(" ", "_")], project.associated_scheme, Literal(amount)))

    if len(dates) != 0:
        for date in dates:
            graph.add((project["place/" + place.replace(" ", "_")], project.associated_time, Literal(date)))

    if len(locations) != 0:
        for location in locations:
            graph.add((project["place/" + location.replace(" ", "_")], RDF.type, SCHEMA.Place))
            graph.add((project["place/" + place.replace(" ", "_")], project.associated_place,
                       project["place/" + location.replace(" ", "_")]))
            graph.add((project["place/" + place.replace(" ", "_")], SCHEMA.containsPlace,
                       project["place/" + location.replace(" ", "_")]))
            if location in place_annotations:
                graph.add((project["place/" + location.replace(" ", "_")], OWL.sameAs,
                           URIRef(place_annotations[location])))

    if len(people) != 0:
        for person in people:
            graph.add((project["person/" + person.replace(" ", "_")], RDF.type, SCHEMA.Person))
            graph.add((project["place/" + place.replace(" ", "_")], project.associated_person,
                       project["person/" + person.replace(" ", "_")]))
            if person in people_annotations:
                graph.add((project["person/" + person.replace(" ", "_")], OWL.sameAs,
                           URIRef(people_annotations[person])))

    if len(organizations) != 0:
        for organization in organizations:
            graph.add((project["organization/" + organization.replace(" ", "_")], RDF.type, SCHEMA.Organization))
            graph.add((project["place/" + place.replace(" ", "_")], project.associated_organization,
                       project["organization/" + organization.replace(" ", "_")]))
            if organization in organization_annotations:
                graph.add((project["organization/" + organization.replace(" ", "_")], OWL.sameAs,
                           URIRef(organization_annotations[organization])))

    if len(locations) != 0 and len(dates) != 0 and len(money) != 0:
        for location in locations:
            for date in dates:
                graph.add((project["place/" + location.replace(" ", "_")], project.associated_time, Literal(date)))
                for amount in money:
                    graph.add((project["place/" + location.replace(" ", "_")],
                               project.associated_scheme, Literal(amount)))
    elif len(locations) != 0 and len(dates) != 0:
        for location in locations:
            for date in dates:
                graph.add((project["place/" + location.replace(" ", "_")], project.associated_time, Literal(date)))
    elif len(locations) != 0 and len(money) != 0:
        for location in locations:
            for amount in money:
                graph.add((project["place/" + location.replace(" ", "_")], project.associated_scheme, Literal(amount)))
