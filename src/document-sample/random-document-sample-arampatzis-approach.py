import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import random
import sys
import re

doc_counter = 0
uuid_array = list()
uuid_dict = dict()
query_dict = dict()
last_array = dict()
retry_strategy = Retry(
    total=5,
    status_forcelist=[429, 500, 502, 503, 504],
    method_whitelist=["HEAD", "GET", "OPTIONS"]
    )
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()

def save_to_file(PATH, uuid):
    with open(PATH, 'a+') as f:
        f.writelines(uuid+"\n")

def add_to_dict(value, dictionary: dict) -> bool:
    global query_dict, doc_dict
    if value in dictionary.keys():
        return False
    else:
        dictionary[value] = None
        return True

def in_dict(value, dictionary: dict) -> bool:
    global query_dict, doc_dict
    if value in dictionary.keys():
        return True
    else:
        return False

def get_docs_uuid(url):
    try:
        resp = http.get(url, timeout=5)
        uuid_array = [x["uuid"] for x in resp.json()["results"]]
        return uuid_array
    except Exception:
        return []

def get_content(url):
    try:
        content = http.get(url, timeout=5).json()["_source"]["body_lang.en"]
        return content
    except Exception:
        return ""

def get_query(content):
    content = content.split()
    if not len(content):
        return None
    query = content.pop(random.randint(0,len(content) - 1))
    query = re.sub('[0123456789\.\:\?\/\&\%\^\$\#\@\*\|\!\=\[\]\)\(\+\-\_\,\;]','',query)
    while (len(query) < 3 or len(query) > 20 or in_dict(query, query_dict)) and len(content)>0:
        query = content.pop(random.randint(0,len(content) - 1))
        query = re.sub('[0123456789\.\:\?\/\&\%\^\$\#\@\*\|\!\=\[\]\)\(\+\-\_\,\;]','',query)
    
    if in_dict(query, query_dict) or len(query) < 3 or len(query) > 20:
        return None    
    else:
        return query

def docs(key, query, index, k, last_uuid_array):
    global doc_counter, uuid_array
    
    url = f"https://www.chatnoir.eu/api/v1/_search?apikey={key}&query={query}&index={index}&pretty=true&size={k}"
    uuid_array = get_docs_uuid(url)
    print(url)

    if len(uuid_array) == 0 and len(last_uuid_array) == 0:
        print("No uuids anymore")
        sys.exit(0)
    
    iter_array = list(uuid_array)
    for uuid in iter_array:
        if in_dict(uuid, uuid_dict):
            uuid_array.remove(uuid)
            continue

        url = f"http://betaweb022.medien.uni-weimar.de:9200/webis_warc_clueweb09_003/warcrecord/{uuid}"
        content = get_content(url)
        query = get_query(content)
        if query == None:
            uuid_array.remove(uuid)
            continue
        else:
            add_to_dict(query, query_dict)
            add_to_dict(uuid, uuid_dict)
            save_to_file(fielename, uuid)
            uuid_array.remove(uuid)
            if len(uuid_array) > 5: 
                last_uuid_array = list(uuid_array)
            elif len(last_uuid_array) < 10:
                last_uuid_array += uuid_array
            print(doc_counter,query,uuid_array)
            doc_counter += 1
            break
    else:
        for uuid in last_uuid_array:
            url = f"http://betaweb022.medien.uni-weimar.de:9200/webis_warc_clueweb09_003/warcrecord/{uuid}"
            content = get_content(url)
            query = get_query(content)
            if query == None:
                continue
            else:
                add_to_dict(query, query_dict)
                add_to_dict(uuid, uuid_dict)
                save_to_file(fielename, uuid)
                print(doc_counter,query,uuid_array)
                doc_counter += 1
                break
    
    print(url)
    if query is None:
        print("No query found")
        sys.exit(0)
    
    return query, last_uuid_array

if __name__ == "__main__":
    key = sys.argv[1]
    query = sys.argv[2]
    index = sys.argv[3]
    k = sys.argv[4]
    document_number = int(sys.argv[5])
    fielename = sys.argv[6]
    last_uuid_array = list()
    while doc_counter < document_number:
        query, last_uuid_array = docs(key, query, index, k, last_uuid_array)
