#!/usr/bin/env/python3

"""
------------------------------------------------------------------------------------------------
 @authors       Nicola Lea Libera (117073)
------------------------------------------------------------------------------------------------
 Description: This script loads the relevant data from the log file of the server and
                adds the time a user needed for his query. Furthermore it adds the position
                of the wanted document in chat noir and the index when the query of the user
                is entered.
------------------------------------------------------------------------------------------------
"""


import json
from pyserini.search import SimpleSearcher
from datetime import datetime
import locale
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import argparse
import requests
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer


API_KEY = '265b2795-b7d2-42c6-a0a9-79fce26b3d44'
SEARCHER = SimpleSearcher("/mnt/ceph/storage/data-in-progress/data-teaching/theses/wstud-thesis-libera/indexes/lucene-index.cw12-documents-v1.pos+docvectors/")
PATH_TO_GAME = "../prototypes/game/running_prototype/app"
QUERY_DATA = ""
MAX_SEARCH_RESULTS = 5000


def load_user_queries_from_log():
    print("I am loading stuff from the logs...")
    path = "/mnt/ceph/storage/data-in-progress/data-teaching/theses/wstud-thesis-libera/app-data/logs/" \
                  "user-started-at2021-09-19T06:01:18.log"
    #path = "/mnt/ceph/storage/data-in-progress/data-teaching/theses/wstud-thesis-libera/app-data/logs/" \
    #      "user-started-at2021-09-14T13:58:23.log"
    file = open(path, 'r')
    lines = file.read().splitlines()
    file.close()
    user_data_without_user_query = []
    user_data_with_user_query = []

    for line in lines:
        if line[:10] == "INFO:root:":
            line = json.loads(line[10:])
            if line.get("user query") is not None:
                user_data_with_user_query.append(line)
            else:
                user_data_without_user_query.append(line)
    print("I am length of user data with user query: " + str(len(user_data_with_user_query)))
    return user_data_with_user_query, user_data_without_user_query


def add_time(user_data_query, user_data_no_query):
    print("I am adding time...")
    for i in user_data_no_query:
        query_list = []
        i['tmp_timestamp'] = datetime.strptime(i.get('timestamp'), '%a %b %d %H:%M:%S %Y')
        query_list.append(i)

        for j in user_data_query:
            if i.get('_id') == j.get('_id') and i.get('original query') == j.get('original query'):
                # Convert the strings in timestamp back to datetime objects
                j['tmp_timestamp'] = datetime.strptime(j.get('timestamp'), '%a %b %d %H:%M:%S %Y')
                query_list.append(j)

        query_list.sort(key=lambda item: item['tmp_timestamp'], reverse=False)

        if len(query_list) != 1:
            for h in range(1, len(query_list)):
                query_list[h]['Time to enter Query'] = int((query_list[h]['tmp_timestamp'] -
                                                            query_list[h - 1]['tmp_timestamp']).total_seconds())
        for x in query_list:
            del x['tmp_timestamp']

    return user_data_query


def add_doc_pos_for_analysis(user_data):
    data_count = 0
    unsuccessful_queries_chat_noir = []
    print("number of user queries: " + str(len(user_data)))
    for entry in user_data:
        # current_query = entry['user query']
        print("I am preparing doc pos with: " + str(entry['user query']) + ", " + str(data_count))
        # Get chat noir data from clueweb12 data
        doc_pos_chat_noir, unsuccessful_queries_chat_noir, chat_noir_ranking, related_documents_counter,\
            average_related_doc_position, last_position = search_chat_noir(entry, unsuccessful_queries_chat_noir, 'cw12')

        entry['last position ChatNoir cw12'] = last_position
        entry['response chat noir cw12'] = chat_noir_ranking
        entry['average position of related documents cw12'] = average_related_doc_position
        entry['number of retrieved related documents cw12'] = related_documents_counter

        if len(chat_noir_ranking) != 0:
            entry['document position in ChatNoir cw12'] = round(1 / doc_pos_chat_noir, 10)
        else:
            entry['document position in ChatNoir cw12'] = float('NaN')

        # Get chat noir data from clueweb09 data
        doc_pos_chat_noir, unsuccessful_queries_chat_noir, chat_noir_ranking, related_documents_counter,\
            average_related_doc_position, last_position = search_chat_noir(entry, unsuccessful_queries_chat_noir, 'cw09')

        entry['response ChatNoir cw09'] = chat_noir_ranking
        entry['last position ChatNoir cw09'] = last_position
        entry['average position of related documents cw09'] = average_related_doc_position
        entry['number of retrieved related documents cw09'] = related_documents_counter
        # maybe save just the pos instead of 1/pos
        if len(chat_noir_ranking) != 0:
            entry['document position in ChatNoir cw09'] = round(1 / doc_pos_chat_noir, 10)
            #print("I am pos: " + str(doc_pos_chat_noir) + ", " + str(entry['document position in ChatNoir cw12']))
        else:
            entry['document position in ChatNoir cw09'] = float('NaN')

        # Add the number of keywords the user used for the query
        number_of_used_keywords, used_keywords = check_if_keyword_was_used(entry)
        entry['number of used keywords'] = number_of_used_keywords
        entry['used keywords'] = used_keywords

        doc_pos_index, index_ranking, related_documents_counter, average_related_doc_position,\
            last_position = search_index(entry)
        if len(index_ranking) != 0:
            entry['document position in index'] = round(1 / doc_pos_index, 10)
        else:
            entry['document position in index'] = float('NaN')
            entry['last position in index'] = True
        entry['response index'] = index_ranking
        entry['average position of related documents index'] = average_related_doc_position
        entry['number of retrieved related documents index'] = related_documents_counter
        #print(str(entry['last position in index']) + ", " + str(entry['document position in index']))
        data_count = data_count + 1

    print("number of unsuccessful queries: " + str(len(unsuccessful_queries_chat_noir)))
    print("array of unsuccessful queries: " + str(unsuccessful_queries_chat_noir))
    return user_data


def check_if_keyword_was_used(data):
    category = data.get('category')
    original_query = data.get('original query')
    user_query = data.get('user query')
    keywords = QUERY_DATA[category][original_query]['keywords']
    user_query = user_query.split(" ")
    keyword_counter = 0
    used_keywords = []
    for word in user_query:
        for keyword in keywords:
            if word == keyword:
                keyword_counter = keyword_counter + 1
                used_keywords.append(keyword)

    return keyword_counter, used_keywords


def check_if_data_from_webpage_was_used(data):
    print("Checking for keywords and phrases in webpage.")
    stop_words = stopwords.words('english')
    porter = PorterStemmer()
    for entry in data:
        category = entry.get('category')
        original_query = entry.get('original query')
        user_query = entry.get('user query')
        uuid = QUERY_DATA[category][original_query]['uuid']
        url = 'https://www.chatnoir.eu/cache?uuid=' + uuid + '&index=cw12&raw'
        website = requests.get(url)
        soup = BeautifulSoup(website.content, 'html.parser')
        web_content = soup.get_text()

        # tokenize the query and the text of the webpage, remove the stopwords, and use a stemmer
        user_query = word_tokenize(user_query)
        web_content = word_tokenize(web_content)
        filtered_web_content = []
        filtered_user_query = []
        phrase_was_used = False
        number_of_used_keywords = 0
        used_keywords = []
        user_query_no_stopwords = []
        for w in user_query:
            w = w.lower()
            if w not in stop_words:
                user_query_no_stopwords.append(w)
                filtered_user_query.append(porter.stem(w))
        #print("user query no stopwords: " + str(user_query_no_stopwords))
        #print("user query no stopwords and stemmed: " + str(filtered_user_query))
        for w in web_content:
            w = w.lower()
            if w not in stop_words:
                filtered_web_content.append(porter.stem(w))

        # now check if the query contains any words from the webpage
        filtered_web_content = " ".join(filtered_web_content)
        for w in filtered_user_query:
            if w in filtered_web_content:
                number_of_used_keywords = number_of_used_keywords + 1
                idx = filtered_user_query.index(w)
                #print("I am word in web: " + str(w))
                #print("I am corresponding word in user query; " + str(user_query_no_stopwords[idx]))
                used_keywords.append(user_query_no_stopwords[idx])
        filtered_user_query = " ".join(filtered_user_query)
        if filtered_user_query in filtered_web_content:
            phrase_was_used = True

        # Add the collected data to the entry
        entry['number of used keywords from webpage'] = number_of_used_keywords
        entry['used keywords from webpage'] = used_keywords
        entry['user query is phrase from webpage'] = phrase_was_used
        #print(entry)
    return data


def search_chat_noir(data, issue, clueweb):
    print("I am searching in chat noir...")
    start_time_chatnoir = datetime.now()
    category = data.get('category')
    original_query = data.get('original query')
    query_id = QUERY_DATA[category][original_query]['uuid']
    ranking = []
    last_position = True

    retry_strategy = Retry(
        total=3,
        backoff_factor=100,
        status_forcelist=[429, 500, 502, 503, 504],
        method_whitelist=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("https://", adapter)
    http.mount("http://", adapter)

    try:
        response = http.get('https://www.chatnoir.eu/api/v1/_search',
                           params={'apikey': API_KEY, 'query': data.get('user query'), 'size': MAX_SEARCH_RESULTS,
                                   'index': clueweb, 'raw': True})
        response = response.json()
        # Create smaller list of results only containing the uuids and corresponding scores
        for entry in response['results']:
            ranking.append({'uuid': entry['uuid'], 'score': entry['score'], 'trec id': entry['trec_id']})

        # Sort the list so that we can get the actual ranking position of the document we are looking for
        ranking = sorted(ranking, key=lambda k: k['score'], reverse=True)
        counter = 1
        # Check if document is inside the response
        for entry in ranking:
            if query_id == entry['uuid']:
                break
            if counter != len(ranking):
                counter = counter + 1

        if counter != len(ranking):
            last_position = False

        related_documents_counter = 0
        average_related_doc_position = 0

        for i in QUERY_DATA[category][original_query]['related_documents']:
            for j in range(0, len(ranking)):
                if ranking[j]['uuid'] == i:
                    related_documents_counter = related_documents_counter + 1
                    average_related_doc_position = average_related_doc_position + j + 1
                    break
        if related_documents_counter != 0:
            average_related_doc_position = int(average_related_doc_position/related_documents_counter)
        else:
            average_related_doc_position = float('NaN')
        print("I am time needed in chat noir: " + str(datetime.now() - start_time_chatnoir))
        return counter, issue, ranking, related_documents_counter, average_related_doc_position, last_position

    except:
        print("I am an error!")
        issue.append(data.get('user query'))
        print("I am time needed in chat noir: " + str(datetime.now() - start_time_chatnoir))
        return 0, issue, ranking, 0, 0, last_position


def search_index(data):
    """
    The function computes all the values to compute the points of a query the user entered
    @return: If provided document was found or not, if so then computed points are returned
    @rtype: object
    """

    print("I am searching in index...")
    start_time_index = datetime.now()
    # Get the query that the user just entered in the search form
    query = data.get('user query')
    # get the original query which the user should obscure
    original_query = data.get('original query')
    category = data.get('category')
    query_id = QUERY_DATA[category][original_query]['uuid']
    last_position = True

    # defines the position at which the document was found or not
    entry_counter = 1

    # searches the index with the query entered by the user
    hits = SEARCHER.search(query, MAX_SEARCH_RESULTS)
    ranking = []
    for i in range(0, len(hits)):
        ranking.append({'uuid': hits[i].docid, 'score': hits[i].score})

    # get position of the wanted document
    for i in range(0, len(hits)):
        if hits[i].docid == query_id:
            break
        elif entry_counter != len(hits):
            entry_counter = entry_counter + 1

    if entry_counter != len(hits):
        last_position = False

    related_documents_counter = 0
    average_related_doc_position = 0

    for i in QUERY_DATA[category][original_query]['related_documents']:
        for j in range(0, len(hits)):
            if hits[j].docid == i:
                related_documents_counter = related_documents_counter + 1
                average_related_doc_position = average_related_doc_position + j + 1
                break

    if related_documents_counter != 0:
        average_related_doc_position = int(average_related_doc_position/related_documents_counter)
    else:
        average_related_doc_position = float('NaN')
    print("I am time needed in index: " + str(datetime.now() - start_time_index))
    return entry_counter, ranking, related_documents_counter, average_related_doc_position, last_position


def load_query_data():
    print("I am loading data...")
    global QUERY_DATA
    path = PATH_TO_GAME + "/static/data/query_data/query_complete_data.json"
    data = json.load(open(path))
    QUERY_DATA = data


def safe_as_json_file(data, filename):
    print("I am saving...")
    json_file = json.dumps(data, indent=3)
    f = open(filename, "w")
    f.write(json_file)
    f.close()


def main():
    start = datetime.now()
    # decide which mode to use
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', '-m', help="decide which mode to use. Choose 'control' to test the logging"
                                             "and 'evaluation' to construct ful data for the evaluation process",
                        type=str, default="evaluation")

    args = parser.parse_args()
    mode = args.mode
    locale.setlocale(locale.LC_ALL, 'en_US.utf-8')
    nltk.download('stopwords')
    load_query_data()
    user_data_user_query, user_data_no_user_query = load_user_queries_from_log()

    if mode == "control":
        safe_as_json_file(user_data_user_query, "test_log_data.json")
    else:
        user_data_user_query = add_time(user_data_user_query, user_data_no_user_query)
        user_data_user_query = add_doc_pos_for_analysis(user_data_user_query)
        user_data_user_query = check_if_data_from_webpage_was_used(user_data_user_query)
        safe_as_json_file(user_data_user_query, "prepared_log_data_evaluation_2.json")
    print("Time needed for execution: " + str(datetime.now() - start))


if __name__ == '__main__':
    main()
