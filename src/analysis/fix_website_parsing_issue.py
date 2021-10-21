import json
from datetime import datetime
import locale
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import requests
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer


API_KEY = '265b2795-b7d2-42c6-a0a9-79fce26b3d44'
PATH_TO_GAME = "../prototypes/game/running_prototype/app"
QUERY_DATA = ""
#MAX_SEARCH_RESULTS = 5000


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
        merged_filtered_user_query = " ".join(filtered_user_query)
        if (merged_filtered_user_query in filtered_web_content) and (len(filtered_user_query) > 1):
            phrase_was_used = True

        # Add the collected data to the entry
        entry['number of used keywords from webpage'] = number_of_used_keywords
        entry['used keywords from webpage'] = used_keywords
        entry['user query is phrase from webpage'] = phrase_was_used
        print(str(entry['number of used keywords from webpage']) + ", " + str(entry['used keywords from webpage']) + ", " +
            str(entry['user query is phrase from webpage']))
        #print(entry)
    return data


def safe_as_json_file(data, filename):
    print("I am saving...")
    json_file = json.dumps(data, indent=3)
    f = open(filename, "w")
    f.write(json_file)
    f.close()


def load_query_data():
    print("I am loading data...")
    global QUERY_DATA
    path = PATH_TO_GAME + "/static/data/query_data/query_complete_data.json"
    data = json.load(open(path))
    QUERY_DATA = data


def main():
    start = datetime.now()

    locale.setlocale(locale.LC_ALL, 'en_US.utf-8')
    nltk.download('stopwords')
    nltk.download('punkt')
    load_query_data()
    user_data_user_query = json.load(open("/mnt/ceph/storage/data-in-progress/data-teaching/theses/wstud-thesis-libera/resources/query_obfuscation_data.json", "rb"))

    user_data_user_query = check_if_data_from_webpage_was_used(user_data_user_query)
    safe_as_json_file(user_data_user_query, "/mnt/ceph/storage/data-in-progress/data-teaching/theses/wstud-thesis-libera/resources/query_obfuscation_data_final.json")
    print("Time needed for execution: " + str(datetime.now() - start))


if __name__ == '__main__':
    main()