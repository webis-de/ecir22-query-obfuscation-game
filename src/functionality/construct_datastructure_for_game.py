#!/usr/bin/env/python3

# ------------------------------------------------------------------------------------------------
# @authors       Nicola Lea Libera (117073)
#
# ------------------------------------------------------------------------------------------------
# Description: This file loads the elasticsearch resources from the chatnoir documents and.
#              returns the top ten keywords that retrieve this specific document inside the search
#              engine.
# ------------------------------------------------------------------------------------------------
import json
import csv
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from nltk import download
import nltk
import inflect
from nltk.stem import WordNetLemmatizer
import requests
from operator import itemgetter
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


API_KEY = '265b2795-b7d2-42c6-a0a9-79fce26b3d44'
ELASTIC_SEARCH_INFO = 'http://betaweb024.medien.uni-weimar.de:9200/webis_warc_clueweb12_011/' \
                      'warcrecord/'
NUMBER_OF_TABOU_WORDS = 10


def safe_as_json_file(data):
    print("Saving file...")
    json_file = json.dumps(data, indent=3)
    f = open("query_listing_data.json", "w")
    f.write(json_file)
    f.close()


def create_json_dict(stop_words):
    """
    This function creates a dict with each category containing all the corresponding
    queries and the needed data like related uuids, file name, forbidden keywords and uuid.
    :return: dict
    """
    data = {'health': {}, 'law': {}, 'politics': {}, 'personal': {}, 'knowledge': {}, 'crime': {}}
    # data = {'health': [], 'law': [], 'politics': [], 'personal': [], 'knowledge': [], 'crime': []}
    with open('/home/nicola/Desktop/thesis-libera/src/data/good_queries_information_collection.csv', encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf)

        for rows in csvReader:
            key = rows['category']
            query = rows['query']
            file_name = rows['file_name']
            uuid = rows['uuid']
            data[key].update({query: {}})
            data[key][query].update({'file_name': file_name})
            data[key][query].update({'uuid': uuid})

            related_uuids_list = add_uuids_of_related_docs(uuid, query)
            data[key][query]['related_documents'] = related_uuids_list

            help_words, forbidden_keywords = add_keywords_to_datastructure(uuid, query, stop_words)
            data[key][query]['keywords'] = help_words
            data[key][query]['forbidden_words'] = forbidden_keywords

            # The next line just creates a dict with the queries and their category as the key
            '''data[key].update({query: {}})
            data[key][query] = [0, 0]'''

    json_file = json.dumps(data, indent=3)
    #print(json_file)
    return data


def add_uuids_of_related_docs(uuid, query):
    """
    this function generates a list with 300 uuids of related documents for the query
    :param uuid: uuid of the document for the query
    :param query: original query
    :return: list containing uuids
    """
    print("Adding related uuids... " + str(query))
    related_uuids_list = []

    retry_strategy = Retry(
        total=5,
        backoff_factor=15,
        status_forcelist=[429, 500, 502, 503, 504],
        method_whitelist=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("https://", adapter)
    http.mount("http://", adapter)

    request = http.get('https://www.chatnoir.eu/api/v1/_search',
                       params={'apikey': API_KEY, 'query': query, 'size': 301,
                               'index': 'cw12', 'raw': True})
    request = request.json()
    # query = list(query)
    for entry in request['results']:
        related_uuid = entry['uuid']
        # add only the uuids of related docs and not the uuid of the selected doc for the query
        if str(uuid) != str(related_uuid):
            related_uuids_list.append(related_uuid)

    return related_uuids_list


def add_keywords_to_datastructure(uuid, query, stop_words):
    """
    This function creates two lists containing 10 helping words created out of the termvectors of the queries
    and forbidden words that are created out of the original query
    :param uuid: uuid of document of query
    :param query: original query
    :param stop_words: words that are only fillters
    :return: two lists
    """
    print("Adding keywords to data...")
    # print(str([w for w in query.lower().split() if w not in stop_words]))
    forbidden_keywords = [w for w in query.lower().split() if w not in stop_words]

    # extend the list of forbidden keywords with the singular and/or plural version of the words
    p = inflect.engine()
    snow_stemmer_nltk = SnowballStemmer(language='english')
    lemmatizer = WordNetLemmatizer()

    tmp_singular = []
    tmp_plural = []
    tmp_stem_nltk = []
    tmp_lemm_nltk = []
    # create two lists containing plural and singular version of the words in the forbidden keywords list
    for word in forbidden_keywords:
        tmp = p.plural(word)
        tmp_plural.append(tmp)

        tmp = p.singular_noun(word)
        tmp_singular.append(tmp)

        tmp = snow_stemmer_nltk.stem(word)
        tmp_stem_nltk.append(tmp)

        tmp = lemmatizer.lemmatize(word)
        tmp_lemm_nltk.append(tmp)

    # add all the words of the singular and plural list to the forbidden keywords list if there are not already
    # contained in the list
    forbidden_keywords.extend(x for x in tmp_singular if x not in forbidden_keywords and x is not False)
    forbidden_keywords.extend(x for x in tmp_plural if x not in forbidden_keywords and x is not False)
    forbidden_keywords.extend(x for x in tmp_stem_nltk if x not in forbidden_keywords)
    forbidden_keywords.extend(x for x in tmp_lemm_nltk if x not in forbidden_keywords and x is not False)

    help_words = retrieve_termvector(uuid, forbidden_keywords)

    return help_words, forbidden_keywords


def retrieve_termvector(uuid, forbidden_keywords):
    """
    This function gets the termvectors of a document and returns a list of the 10 terms that
    have the highest ranking score for this document.
    :return: list of keywords
    """
    print("retrieving term vectors...")
    headers = {
        'Content-type': 'application/json',
    }

    data = {"fields": ["body_lang.en"],
            "term_statistics": True,
            "field_statistics": True,
            "positions": False,
            "offsets": False,
            "filter": {
                "min_doc_freq": 10,  # maybe if I change this to 3 or so I will get more keywords just in case
                "max_doc_freq": 1000000
            }
            }

    data = json.dumps(data)

    termvector_url = ELASTIC_SEARCH_INFO + uuid + "/_termvectors?pretty"

    # Ask the server for the termvector of the specific url (document)
    termvector = requests.post(termvector_url, headers=headers, data=data)

    termvector = termvector.json()
    termvector = termvector["term_vectors"]["body_lang.en"]["terms"]

    # convert the terms and their scores into a nested list
    keywords = []
    counter = 0
    for i in termvector:
        keywords.append([])
        keywords[counter].append(i)
        keywords[counter].append(termvector[i]["score"])
        counter = counter + 1

    # Sort the computed list by the value of the scores and keep only a specific number
    # of keywords with the highest scores
    keywords.sort(key=itemgetter(1), reverse=True)

    for j in range(0, len(keywords)):
        if keywords[j][0][-1] == "'":
            print("I am deleting unnecessary char " + str(keywords[j][0]))
            keywords[j][0] = keywords[j][0][:-1]
            print("new keyword: " + str(keywords[j][0]))

    keywords_counter = len(keywords)
    # check if the words in the forbidden keywords list are inside the termvector and if so then delete them
    for entry in forbidden_keywords:
        i = 0
        while i < len(keywords):
            if entry == str(keywords[i][0]).lower() or entry in str(keywords[i][0]).lower() \
                    or str(keywords[i][0]).lower() in entry:
                keywords.pop(i)
            i = i + 1

    # check if there exists a word twice inside the keywords
    help_words = {}
    for i in range(0, len(keywords)):
        if keywords[i][0] not in help_words:
            help_words.update({keywords[i][0]: keywords[i][1]})
            if len(help_words) == 10:
                break

    return help_words


def main():
    download('stopwords')  # Download stopwords list.
    stop_words = stopwords.words('english')
    nltk.download('wordnet')
    data = create_json_dict(stop_words)
    safe_as_json_file(data)


if __name__ == '__main__':
    main()
