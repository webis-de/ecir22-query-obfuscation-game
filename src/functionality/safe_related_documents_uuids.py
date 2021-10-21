#!/usr/bin/env/python3

# ------------------------------------------------------------------------------------------------
# @authors       Nicola Lea Libera (117073)
#
# ------------------------------------------------------------------------------------------------
# Description: This program loads the first x documents which are retrieved by a query request
#              and safes their uuids.
#
# ------------------------------------------------------------------------------------------------

import requests
import json
import csv
from datetime import timedelta
from failsafe import Failsafe, RetryPolicy, Backoff, Delay
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

API_KEY = '265b2795-b7d2-42c6-a0a9-79fce26b3d44'


def safe_related_documents(data):
    retry_strategy = Retry(
        total=15,
        backoff_factor=500,
        status_forcelist=[429, 500, 502, 503, 504],
        method_whitelist=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("https://", adapter)
    http.mount("http://", adapter)

    counter = 0
    for key in data:
        print(key)
        print("I was called " + str(counter))
        try:
            response = http.get('https://www.chatnoir.eu/api/v1/_search',
                                   params={'apikey': API_KEY, 'query': key, 'size': 1000,
                                           'index': 'cw12', 'raw': True})
            data[key]['related_documents_uuids'] = []
            counter = counter + 1
            print(response.status_code)
            response = response.json()
            #print(response)

            for entry in response['results']:
                data[key]['related_documents_uuids'].append(entry['uuid'])
        except:
            print("I am an error")
            # print(data)
            safe_as_json_file(data)
            break

    safe_as_json_file(data)


def load_data():
    data = {}
    with open('queries_for_index.csv', encoding='utf-8') as csvf:
        csv_reader = csv.DictReader(csvf)

        # Convert each row into a dictionary
        # and add it to data
        for rows in csv_reader:
            key = rows['query']
            del (rows['query'])
            data[key] = rows
    return data


def safe_as_json_file(data):
    json_file = json.dumps(data, indent=3)
    f = open("queries_index_7.json", "w")
    f.write(json_file)
    f.close()


def main():
    data = load_data()
    safe_related_documents(data)


if __name__ == '__main__':
    main()