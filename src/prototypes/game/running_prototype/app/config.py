#!/usr/bin/env python3
"""Flask configuration."""
import os
import logging
from pathlib import Path


class Config(object):
    """Set Flask config variables."""
    FLASK_ENV = 'development'
    TESTING = True
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    
    URL_PREFIX = '/wstud-thesis-libera'
    QUERY_DATA = ''
    QUERY_LIST = ''
    MAX_SEARCH_RESULTS = 8000
    MAX_SEARCH_RANGE_RELATED_DOCS = 8000
    INDEX_PATH = '../../../../document-sample/web-search-anserini-sandbox/indexes/lucene-index.cw12.pos+docvectors/'
    #INDEX_PATH = '/mnt/ceph/storage/data-in-progress/data-teaching/theses/wstud-thesis-libera/indexes/lucene-index.cw12-documents-v1.pos+docvectors/'
    site_root = os.path.realpath(os.path.dirname(__file__))
    logging_path = os.path.join(site_root, "static/data/logging", "userlogs.log")
    logging.basicConfig(filename=logging_path, level=logging.INFO)

    # Database
    MONGO_DBNAME = "users"
    MONGO_URI = "mongodb://localhost:27017/users"

