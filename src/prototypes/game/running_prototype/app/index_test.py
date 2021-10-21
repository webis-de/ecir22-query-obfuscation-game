#!/usr/bin/env python3

"""
author: Nicola Lea Libera (117073)
description: Script to test if all needed documents are inside the index
            before starting the server.
"""
import json
#from pyserini.search import SimpleSearcher


def check_all_documents(data, index):
    problems = {}
    documents_are_missing = False
    number_of_missing_documents = 0
    for category in data:
        for query in data[category]:
            document_id = data[category][query]['uuid']
            found = index.doc(document_id)
            if found is None:
                number_of_missing_documents = number_of_missing_documents + 1
                documents_are_missing = True
                problems[query] = [document_id]
            for related_id in data[category][query]['related_documents']:
                found = index.doc(related_id)
                if found is None:
                    number_of_missing_documents = number_of_missing_documents + 1
                    documents_are_missing = True
                    if query not in problems:
                        problems[query] = [related_id]
                    else:
                        problems[query].append(related_id)

    json_file = json.dumps(problems, indent=3)
    f = open("missing_documents.json", "w")
    f.write(json_file)
    f.close()
    return documents_are_missing

