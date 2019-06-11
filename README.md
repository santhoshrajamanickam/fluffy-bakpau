# UBI Project: Extraction, Instance linking and Content pre-processing

This repository consists of the project files related to the "Knowledge Representation for Web" course taken at Vrije Universiteit Amsterdam.

Following are the description of the folders:
  - `OWL` - Contains the ontology of the project (with inferred classes and relationships.)
  - `SPARQL_Queries` - Contains the SPARQL queries of the experiments conducted.

Before you test the extractor and make sure to install the requirements from the `requirements.txt` files:
```
  pip3 install -r requirements.txt
```
In `main.py` can be used to extract the `money`, `dates`, `locations`, `people`, and `organizations` entities from a Wikipedia page and transform the data into RDF triples.

Note: It is to note that, since this script was developed specifically for the project, the extractor was tested on [https://en.wikipedia.org/wiki/Basic_income_around_the_world](https://en.wikipedia.org/wiki/Basic_income_around_the_world) page. But the extractor should work for other Wikipedia pages as well. One do this by changing the `page_title` variable in the `main.py` to extract the entities mentioned above in RDF format.

To run the Wikipedia Extractor:
```
  python3 main.py
```
