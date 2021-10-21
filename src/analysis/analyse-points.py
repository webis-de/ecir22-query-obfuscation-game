#!/usr/bin/env/python3

"""
------------------------------------------------------------------------------------------------
 @authors       Nicola Lea Libera (117073)
------------------------------------------------------------------------------------------------
 Description: This script loads the relevant data from the log file of the server and computes
              the average value for the points users score in the game.
------------------------------------------------------------------------------------------------
"""
import os
import json
from pyserini.search import SimpleSearcher
import math

SEARCHER = SimpleSearcher("../document-sample/web-search-anserini-sandbox/indexes/lucene-index.cw12.pos+docvectors/")
PATH_TO_GAME = "../prototypes/game/running_prototype/app"
QUERY_DATA = ""
QUERY_LIST = ""
MAX_SEARCH_RESULTS = 8000
MAX_SEARCH_RANGE_RELATED_DOCS = 8000
RETRIEVABILITY_POINTS_DOCUMENT_ENTRY = {'1': [20.0, 10], '50': [19.6, 10], '100': [19.1, 10], '500': [17.1, 20],
                                        '1000': [14.6, 20], '1500': [12.1, 20], '2000': [9.6, 20], '2500': [8.6, 50],
                                        '3000': [7.6, 50], '3500': [6.6, 50], '4000': [5.6, 50], '4500': [4.6, 50],
                                        '5000': [3.6, 100], '5500': [3.1, 100], '6000': [2.6, 100], '6500': [2.1, 100],
                                        '7000': [1.6, 100]}


def load_user_queries_from_log():
    path = PATH_TO_GAME + "/static/data/logging/userlogs.log"
    file = open(path, 'r')
    lines = file.read().splitlines()
    file.close()
    user_data = []

    for line in lines:
        if line[:10] == "INFO:root:":
            line = json.loads(line[10:])
            if line.get("user_query") is not None:
                user_data.append(line)
    return user_data


def load_query_data():
    global QUERY_DATA
    global QUERY_LIST
    path = PATH_TO_GAME + "/static/data/query_data/query_complete_data.json"
    data = json.load(open(path))
    QUERY_DATA = data
    path = PATH_TO_GAME + "/static/data/query_data/query_listing_data.json"
    data = json.load(open(path))
    QUERY_LIST = data


def search(user_queries):

    average_points = {'document pos points': 0, 'num related docs points': 0,
                      'avg pos related docs points': 0, 'query length points': 0,
                      'total points': 0}
    query_stats = []
    average_doc_pos = {'document position inside index': 0, 'number of found related documents': 0,
                       'average position of related documents': 0}
    num_found_docs = 0

    document_pos_inside_index = []
    number_of_found_related_documents = []
    average_position_of_related_documents = []
    list_document_pos_points = []
    list_num_related_docs_points = []
    list_avg_pos_related_docs_points = []
    list_query_length_points = []
    list_total_points = []

    for entry in user_queries:
        # Get the query that the user just entered in the search form
        query = entry.get('user_query')
        # get the original query which the user should obscure
        original_query = entry.get('original_query')
        category = entry.get('category')
        level = entry.get('level')

        # uuid of the document for the original query
        query_id = QUERY_DATA[category][original_query]['uuid']

        # defines the position at which the document was found or not
        entry_counter = 1
        # defines whether the document was found or not
        found_document = False

        # searches the index with the query entered by the user
        hits = SEARCHER.search(query, MAX_SEARCH_RESULTS)

        for i in range(0, len(hits)):
            if hits[i].docid == query_id:
                found_document = True
                break
            elif entry_counter != len(hits):
                entry_counter = entry_counter + 1

        if found_document:
            num_found_docs = num_found_docs + 1

            # normal search range for related document must be changed if number of hits for query is smaller
            search_range_related_doc = MAX_SEARCH_RANGE_RELATED_DOCS
            if len(hits) < search_range_related_doc:
                search_range_related_doc = len(hits)

            related_documents_counter = 0
            counter = 0
            average_related_doc_position = 0
            for i in QUERY_DATA[category][original_query]['related_documents']:
                counter = counter + 1
                for j in range(0, search_range_related_doc):
                    if hits[j].docid == i:
                        related_documents_counter = related_documents_counter + 1
                        average_related_doc_position = average_related_doc_position + j
                        break

            document_pos_points, num_related_docs_points, avg_pos_related_docs_points, \
            query_length_points, total_points \
                = compute_points(entry_counter, related_documents_counter, average_related_doc_position, query,
                                 original_query)

            average_points = {'document pos points': average_points['document pos points'] + document_pos_points,
                              'num related docs points': average_points['num related docs points'] + num_related_docs_points,
                              'avg pos related docs points': average_points['avg pos related docs points'] + avg_pos_related_docs_points,
                              'query length points': average_points['query length points'] + query_length_points,
                              'total points': average_points['total points'] + total_points}

            average_doc_pos = {'document position inside index': average_doc_pos['document position inside index'] + entry_counter,
                               'number of found related documents': average_doc_pos['number of found related documents'] + related_documents_counter,
                               'average position of related documents':
                                   average_doc_pos['average position of related documents'] + normal_round(average_related_doc_position/related_documents_counter)}

            document_pos_inside_index.append(entry_counter)
            number_of_found_related_documents.append(related_documents_counter)
            average_position_of_related_documents.append(normal_round(average_related_doc_position/related_documents_counter))
            list_document_pos_points.append(document_pos_points)
            list_num_related_docs_points.append(num_related_docs_points)
            list_avg_pos_related_docs_points.append(avg_pos_related_docs_points)
            list_query_length_points.append(query_length_points)
            list_total_points.append(total_points)
            """
            query_stats.update({query: {'level': level,
                                        'document positions': {'document position inside index': entry_counter,
                                                               'number of found related documents': related_documents_counter,
                                                               'average position of related documents':
                                                                   normal_round(average_related_doc_position/related_documents_counter)},
                                        'points': {'document pos points': document_pos_points,
                                                   'num related docs points': num_related_docs_points,
                                                   'avg pos related docs points': avg_pos_related_docs_points,
                                                   'query length points': query_length_points,
                                                   'total points': total_points
                                        }
                                 }
                                })"""
            query_stats.append({query: {'level': level,
                                        'document positions': {'document position inside index': entry_counter,
                                                               'number of found related documents': related_documents_counter,
                                                               'average position of related documents':
                                                                   normal_round(average_related_doc_position/related_documents_counter)},
                                        'points': {'document pos points': document_pos_points,
                                                   'num related docs points': num_related_docs_points,
                                                   'avg pos related docs points': avg_pos_related_docs_points,
                                                   'query length points': query_length_points,
                                                   'total points': total_points
                                        }
                                 }
                                })
            # query_stats = dict(list(query_stats.items()) + list(new_query.items()))

        # else: here you have to think about how the docs query that did not retrieve the doc will be handeled
        else:
            query_stats.append({query: {'level': level,
                                        'document positions': {'document position inside index': 'not found',
                                                               'number of found related documents': 'not found',
                                                               'average position of related documents':
                                                                   'not found'},
                                        'points': {'document pos points': 0,
                                                   'num related docs points': 0,
                                                   'avg pos related docs points': 0,
                                                   'query length points': 0,
                                                   'total points': 0
                                        }
                                 }
                                })



    # final average points
    average_points = {'average points stats': {'document pos points': normal_round(average_points['document pos points']/num_found_docs),
                      'num related docs points': normal_round(average_points['num related docs points']/num_found_docs),
                      'avg pos related docs points': normal_round(average_points['avg pos related docs points']/num_found_docs),
                      'query length points': normal_round(average_points['query length points']/num_found_docs),
                      'total points': normal_round(average_points['total points']/num_found_docs)
                      }}

    average_doc_pos = {'average document position stats': {'document position inside index':
                           normal_round(average_doc_pos['document position inside index']/num_found_docs),
                       'number of found related documents':
                           normal_round(average_doc_pos['number of found related documents']/num_found_docs),
                       'average position of related documents':
                           normal_round(average_doc_pos['average position of related documents']/num_found_docs)
                       }}

    scoring_range = {'range for positions and points':
        {'document position stats range': {'document position inside index':
                     {'min': min(document_pos_inside_index), 'max': max(document_pos_inside_index)},
                       'number of found related documents': {'min': min(number_of_found_related_documents),
                                                             'max': max(number_of_found_related_documents)},
                       'average position of related documents': {'min': min(average_position_of_related_documents),
                                                                 'max': max(average_position_of_related_documents)}
                       }
                     },
        'points score range': {'document pos points': {'min': min(list_document_pos_points),
                                                                 'max': max(list_document_pos_points)},
                      'num related docs points': {'min': min(list_num_related_docs_points),
                                                                 'max': max(list_num_related_docs_points)},
                      'avg pos related docs points': {'min': min(list_avg_pos_related_docs_points),
                                                                 'max': max(list_avg_pos_related_docs_points)},
                      'query length points': {'min': min(list_query_length_points),
                                                                 'max': max(list_query_length_points)},
                      'total points': {'min': min(list_total_points),
                                                                 'max': max(list_total_points)}
                      }
    }

    query_stats.append(average_points)
    query_stats.append(average_doc_pos)
    query_stats.append(scoring_range)
    return query_stats


def safe_as_json_file(data):
    print("Saving file...")
    json_file = json.dumps(data, indent=3)
    f = open("points_data.json", "w")
    f.write(json_file)
    f.close()


# Compute the points for the position of the given document
def compute_points(entry_counter, related_documents_counter, average_related_doc_position, query, original_query):

    document_pos_points = points_document_pos(entry_counter)
    document_pos_points = int(document_pos_points)
    num_related_docs_points = points_number_related_documents(related_documents_counter)
    avg_pos_related_docs_points = points_average_pos_related_documents(related_documents_counter,
                                                                       average_related_doc_position)
    query_length_points = points_query_length(query, original_query)

    total_points = document_pos_points + num_related_docs_points + avg_pos_related_docs_points + query_length_points

    return document_pos_points, num_related_docs_points, avg_pos_related_docs_points, query_length_points, total_points


# Eventuell auch überarbeiten, nicht mehr unterschiedlich große Schrittlängen haben
def points_document_pos(entry_counter):
    points = 0
    # First check if entry_counter is larger than 7000, if so then points is a fixed value
    if entry_counter > 7000:
        points = 1.0
        return points
    else:
        # determine bounds
        for key in RETRIEVABILITY_POINTS_DOCUMENT_ENTRY:
            if entry_counter == int(key):
                points = RETRIEVABILITY_POINTS_DOCUMENT_ENTRY[key][0]
                return points

            if entry_counter > int(key):
                lower_bound = key

            if entry_counter < int(key):
                upper_bound = key
                break

        # Now determine if entry_counter is nearer the upper or the lower bound
        difference_lower_bound = entry_counter - int(lower_bound)
        difference_upper_bound = int(upper_bound) - entry_counter
        step_size = RETRIEVABILITY_POINTS_DOCUMENT_ENTRY[upper_bound][1]

        if difference_lower_bound < difference_upper_bound:
            step = int(lower_bound)
            points = RETRIEVABILITY_POINTS_DOCUMENT_ENTRY[lower_bound][0]

        if difference_lower_bound > difference_upper_bound:
            step = int(upper_bound)
            points = RETRIEVABILITY_POINTS_DOCUMENT_ENTRY[upper_bound][0]

        # compute the actual value of the range in which the pos of the document lies
        while step < entry_counter:
            if difference_lower_bound < difference_upper_bound:
                points = points - 0.1
                points = round(points, 1)
                step = step + step_size

            if difference_lower_bound > difference_upper_bound:
                points = points + 0.1
                step = step - step_size

    return 10 * points


def points_number_related_documents(related_documents_counter):
    if related_documents_counter > 149:
        return 150
    else:
        return related_documents_counter


# Hier auch vllt. lieber -1 anstatt -2 Punkte abzug
def points_average_pos_related_documents(related_documents_counter, average_related_doc_position):
    if related_documents_counter == 0:
        return 0

    average_related_doc_position = normal_round(average_related_doc_position/related_documents_counter)
    points = 100
    for i in range(160, MAX_SEARCH_RESULTS, 160):
        if average_related_doc_position <= i:
            return points
        else:
            points = points - 2
    return points


def points_query_length(query, original_query):
    query_length = len(query.split())
    original_query_length = len(original_query.split())

    if query_length < original_query_length or query_length == original_query_length:
        return 50

    else:
        length_difference = query_length - original_query_length
        return 50 - length_difference


def normal_round(n):
    if n - math.floor(n) < 0.5:
        return math.floor(n)
    return math.ceil(n)


def main():
    user_data = load_user_queries_from_log()
    load_query_data()
    data = search(user_data)
    safe_as_json_file(data)


if __name__ == '__main__':
    main()