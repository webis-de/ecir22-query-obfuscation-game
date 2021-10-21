#!/usr/bin/env/python3

# ------------------------------------------------------------------------------------------------
# @authors       Nicola Lea Libera (117073)
#
# ------------------------------------------------------------------------------------------------
# Description: This program loads the first x documents which are retrieved by a query request
#              to chatnoir and safes their uuids.
#
# ------------------------------------------------------------------------------------------------

import requests
import urllib.parse as urlparse
from urllib.parse import parse_qs
import json
import os

API_KEY = '265b2795-b7d2-42c6-a0a9-79fce26b3d44'


def safe_related_documents():
    site_root = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(site_root, "query_data.json")
    data = json.load(open(json_url))

    for query in data:
        #print(query)
        data[query]['related_uuids'] = []

        request = requests.get('https://www.chatnoir.eu/api/v1/_search',
                           params={'apikey': API_KEY, 'query': query, 'size': 100,
                                   'index': 'cw12', 'raw': True})
        request = request.json()

        for entry in request['results']:
            data[query]['related_uuids'].append(entry['uuid'])
        print(data)

    safe_as_json_file(data)


def safe_as_json_file(data):
    json_file = json.dumps(data, indent=3)
    f = open("query_data.json", "w")
    f.write(json_file)
    f.close()


def main():
    safe_related_documents()


if __name__ == '__main__':
    main()