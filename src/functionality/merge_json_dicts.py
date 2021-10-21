#!/usr/bin/env/python3
# ------------------------------------------------------------------------------------------------
# @authors       Nicola Lea Libera (117073)
# ------------------------------------------------------------------------------------------------
# Description: This program merges json dictionaries and safes the final result in a file.
# ------------------------------------------------------------------------------------------------

import json
import csv


def load_data(filename):
    # Opening JSON file
    with open(filename) as json_file:
        data = json.load(json_file)
        json_file.close()
    return data


def safe_as_json_file(data):
    json_file = json.dumps(data, indent=3)
    f = open("document_ids_for_index.json", "w")
    f.write(json_file)
    f.close()


def merge_dicts(dict1, dict2):
    out = dict(list(dict1.items()) + list(dict2.items()))
    return out


def check_if_all_queries_are_inside(data):
    with open('queries_for_index.csv', encoding='utf-8') as csvf:
        csv_reader = csv.DictReader(csvf)
        counter_queries = 0
        counter_documents = 0
        num_of_queries_less_docs = 0
        for rows in csv_reader:
            key = rows['query']
            if key in data.keys():
                counter_queries = counter_queries + 1
                counter_documents = counter_documents + len(data[key]['related_documents_uuids'])
                if len(data[key]['related_documents_uuids']) != 1000:
                    num_of_queries_less_docs = num_of_queries_less_docs + 1
                    print(key)
                    print("length docs: " + str(len(data[key]['related_documents_uuids'])))

        print("queries: " + str(counter_queries))
        print("documents: " + str(counter_documents))
        print("Num of queries with less than 1000 docs: " + str(num_of_queries_less_docs))


def main():
    # Merge the json files
    '''
    data0 = load_data("queries_index.json")
    data1 = load_data("queries_index_2.json")
    data2 = load_data("queries_index_3.json")
    data3 = load_data("queries_index_4.json")
    data4 = load_data("queries_index_5.json")
    data5 = load_data("queries_index_6.json")
    data6 = load_data("queries_index_7.json")
    result = merge_dicts(data0, data1)
    result = merge_dicts(result, data2)
    result = merge_dicts(result, data3)
    result = merge_dicts(result, data4)
    result = merge_dicts(result, data5)
    result = merge_dicts(result, data6)
    safe_as_json_file(result)
    '''
    # Check if everything went well
    data = load_data("document_ids_for_index.json")
    check_if_all_queries_are_inside(data)


if __name__ == '__main__':
    main()