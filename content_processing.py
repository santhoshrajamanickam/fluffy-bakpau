import nltk
import spotlight
from nltk.stem.wordnet import WordNetLemmatizer
# from spacy.lang.en import English
import spacy
from svo_extractor import findSVOs, findSVAOs

# from nltk.parse import CoreNLPParser
# from nltk.tree import ParentedTree

from pycorenlp import StanfordCoreNLP

# parser = CoreNLPParser(url='http://localhost:9000')
# nlp = StanfordCoreNLP('http://localhost:9000')
nlp = spacy.load('en')

only_place_filter = {'policy': "whitelist", 'types': "DBpedia:Place", 'coreferenceResolution': False}
only_year_filter = {'policy': "whitelist", 'types': "DBpedia:Year", 'coreferenceResolution': False}



def UBI_process_content(content):
    sentiment = None
    places = set()
    year = set()
    plan = set()
    economy = set()
    positives = set()
    negatives = set()

    sentences = nltk.sent_tokenize(content)

    for sentence in sentences:
        # print(sentence)

        # try:
        #     annotations = spotlight.annotate('http://api.dbpedia-spotlight.org/en/annotate', sentence)
        #     # print(annotations)
        # except:
        #     continue

        try:
            year_annotations = spotlight.annotate('http://api.dbpedia-spotlight.org/en/annotate', sentence,
                                                  filters=only_year_filter)
            for year_info in year_annotations:
                year.add(year_info['URI'])
        except:
            pass

        try:
            place_annotations = spotlight.annotate('http://api.dbpedia-spotlight.org/en/annotate', sentence,
                                                   filters=only_place_filter)
            for place_info in place_annotations:
                places.add(place_info['URI'])
        except:
            pass

        # parse = nlp("Donald Trump is the worst president of USA, but Hillary is better than him")
        # print(findSVAOs(nlp(sentence)))

    return sentiment, places, year, plan, economy, positives, negatives



