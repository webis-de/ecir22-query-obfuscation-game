#!/usr/bin/env/python3

# ------------------------------------------------------------------------------------------------
# @authors       Nicola Lea Libera (117073)
#
# ------------------------------------------------------------------------------------------------
# Description: This file loads the elasticsearch resources from the chatnoir documents and.
#              returns the top ten keywords that retrieve this specific document inside the search
#              engine.
# ------------------------------------------------------------------------------------------------

import requests
import urllib.parse as urlparse
from urllib.parse import parse_qs
import json
from operator import itemgetter

CHATNOIR_URL = 'https://www.chatnoir.eu/cache?uuid=ca562721-447e-525a-801a-12cc5d4d689d&index=cw09' \
               '&raw'
# ELASTIC_SEARCH_INFO = 'http://betaweb023.medien.uni-weimar.de:9200/webis_warc_clueweb09_003/' \
#                      'warcrecord/'

ELASTIC_SEARCH_INFO = 'http://betaweb023.medien.uni-weimar.de:9200/webis_warc_clueweb12_011/' \
                      'warcrecord/'
NUMBER_OF_TABOU_WORDS = 10


def retrieve_termvector(document_url):
    """
    This function gets the termvectors of a document and returns a list of the 10 terms that
    have the highest ranking score for this document.
    :return: list of keywords
    """

    parsed = urlparse.urlparse(document_url)
    uuid = parse_qs(parsed.query)['uuid'][0]

    headers = {
        'Content-type': 'application/json',
    }

    data = {"fields": ["body_lang.en"],
            "term_statistics": True,
            "field_statistics": True,
            "positions": False,
            "offsets": False,
            "filter": {
                "min_doc_freq": 10,
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

    #before doing this I have to go through the words to delete those, that appear inside the query
    # am besten check if word contains one of the words of the query to delete verwandte wörter
    keywords = keywords[:NUMBER_OF_TABOU_WORDS]

    # create a list which contains only the keywords with the highest scores and nothing else
    tabou_words = []
    for i in range(0, len(keywords)):
        tabou_words.append(keywords[i][0])

    return tabou_words


def main():
    tabou_words = retrieve_termvector(CHATNOIR_URL)


if __name__ == '__main__':
    main()