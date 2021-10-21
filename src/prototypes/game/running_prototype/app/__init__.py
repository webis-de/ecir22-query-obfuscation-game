from flask import Flask, abort
from .config import Config
from .index_test import check_all_documents
import json
import os
from pyserini.search import SimpleSearcher


def test_index():
    site_root = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(site_root, "static/data/query_data", "query_complete_data.json")
    data = json.load(open(json_url))
    searcher = SimpleSearcher(Config.INDEX_PATH)
    missing_documents = check_all_documents(data, searcher)
    if missing_documents is True:
        abort(500)


#test_index()
app = Flask(__name__, static_url_path=Config.URL_PREFIX + '/static')
app.config.from_object(Config)
