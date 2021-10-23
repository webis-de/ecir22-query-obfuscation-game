"""Flask configuration."""
import os
import logging
import datetime


class Config(object):
    """Set Flask config variables."""
    FLASK_ENV = 'development'
    TESTING = True
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    
    URL_PREFIX = '/city-of-disguise'
    QUERY_DATA = ''
    QUERY_LIST = ''
    MAX_SEARCH_RESULTS = 8000
    MAX_SEARCH_RANGE_RELATED_DOCS = 8000


    INDEX_PATH = '/lucene-index/current-index'

    logging_path = os.path.join('/var/log/thesis-libera', 'user-started-at' + datetime.datetime.now().replace(microsecond=0).isoformat() + '.log')
    logging.basicConfig(filename=logging_path, level=logging.INFO)

    # Database
    MONGO_DBNAME = "users"
    MONGO_URI = "mongodb://localhost:27017/users"

