#!/usr/bin/env python3
"""
author: Nicola Lea Libera (117073)
description: Server for the game "City of Rebellion" that was developed for
            the Bachelor thesis "Gamification in Information Retrieval".
"""

from app import app
from flask import render_template, url_for, request, jsonify, redirect, make_response
import logging
import json
import os
import time
import datetime
from pyserini.search import SimpleSearcher
from .points import compute_points
from .user_functionality import *
from flask_pymongo import PyMongo
import uuid
from operator import itemgetter


URL_PREFIX = app.config['URL_PREFIX']
QUERY_DATA = app.config['QUERY_DATA']
QUERY_LIST = app.config['QUERY_LIST']
MAX_SEARCH_RESULTS = app.config['MAX_SEARCH_RESULTS']
MAX_SEARCH_RANGE_RELATED_DOCS = app.config['MAX_SEARCH_RANGE_RELATED_DOCS']
SEARCHER = SimpleSearcher(app.config['INDEX_PATH'])
mongo = PyMongo(app)


def create_new_user():
    """
    This function creates a new user with a unique uuid hex string
    and inserts him into the db
    @return: The id of the created user
    @rtype: String
    """
    new_entry = QUERY_LIST
    new_user_id = str(uuid.uuid4())
    new_entry['_id'] = new_user_id
    new_entry = set_default_user_name(new_entry, mongo.db.users)
    mongo.db.users.insert_one(new_entry)
    return new_user_id


def create_new_user_with_specific_id(user_id):
    """
    This function inserts a new user with a given id to the db.
    @param user_id: Already existing user id
    @type user_id: String
    """
    new_entry = QUERY_LIST
    new_entry['_id'] = user_id
    new_entry = set_default_user_name(new_entry, mongo.db.users)
    mongo.db.users.insert_one(new_entry)


def setup_user(user_id, user):
    """
    This function inserts a new user into the db depending whether the user
    already has a legitimate id or not.
    @param user_id: Legitimate id of a user
    @type user_id: String
    @param user: db entry of the user with the given id
    @type user: Dictionary
    @return: The id of the newly inserted user
    @rtype: String
    """
    if user_id is None:
        user_id = create_new_user()
    elif user_id is not None and user is None:
        create_new_user_with_specific_id(user_id)

    user = mongo.db.users.find_one({'_id': user_id})
    today = datetime.datetime.now()
    today = today.strftime("%d/%m/%Y")
    stats = {'points_total': 0, 'points_squid': 0, 'points_chameleon': 0, 'queries_total': 0, 'queries_squid': 0,
             'queries_chameleon': 0}
    if today not in user['statistics'].keys():
        mongo.db.users.update_one({'_id': user_id}, [{'$set': {'statistics': {today: stats}}}])
    return user_id


@app.route(URL_PREFIX + '/reset', methods=['GET'])
def reset_game_data():
    """
    This function resets the points counter and the counter of game rounds back
    to zero.
    """
    user_id = request.cookies.get('user_id')
    mongo.db.users.update_one({'_id': user_id}, {'$set': {'game_round': 0}})
    mongo.db.users.update_one({'_id': user_id}, {'$set': {'total_points_game': 0}})
    return jsonify(1)


@app.route(URL_PREFIX + '/updateIntro', methods=['POST'])
def update_intro_second_level():
    """
    This function updates the entry in the db that decides if the 
    introduction of the second level was already played or not.
    If this function is called then the introduction was played and is not displayed again.
    """
    user_id = request.cookies.get('user_id')
    mongo.db.users.update_one({'_id': user_id}, {'$set': {'introduction_second_level_was_played': True}})
    return jsonify(1)


@app.route(URL_PREFIX + '/updatePoints', methods=['POST'])
def update_user_data_points():
    """
    Here the achieved points and the number of solved queries are updated in the db. 
    """
    
    # The achived points, the selected level, user data and date is determined 
    points = request.get_json('accumulatedPoints')
    points = points['accumulatedPoints']
    
    level = request.get_json('currentLevel')
    level = level['currentLevel']

    category = request.get_json('currentCategory')
    category = category['currentCategory']

    original_query = request.get_json('originalQuery')
    original_query = original_query['originalQuery']

    user_id = request.cookies.get('user_id')
    user = mongo.db.users.find_one({'_id': user_id})

    today = datetime.datetime.now()
    today = today.strftime("%d/%m/%Y")

    # The number of total points is being updated
    total_points = user['total_points']
    mongo.db.users.update_one({'_id': user_id}, {'$set': {'total_points': total_points + points}})
    total_points = user['statistics'][today]['points_total']
    mongo.db.users.update_one({'_id': user_id}, {'$set': {'statistics.' + today + ".points_total": total_points + points}})

    total_points_game = user['total_points_game']
    mongo.db.users.update_one({'_id': user_id}, {'$set': {'total_points_game': total_points_game + points}})

    index = 0
    # Depending on the selected level, the points and statistics for that level get updated
    if level == "chameleon":
        index = 1
        level_points = user['total_points_level_two']
        mongo.db.users.update_one({'_id': user_id}, {'$set': {'total_points_level_two': level_points + points}})
        level_points = user['statistics'][today]['points_chameleon']
        mongo.db.users.update_one({'_id': user_id},
                                  {'$set': {'statistics.' + today + ".points_chameleon": level_points + points}})
    else:
        level_points = user['total_points_level_one']
        mongo.db.users.update_one({'_id': user_id}, {'$set': {'total_points_level_one': level_points + points}})
        level_points = user['statistics'][today]['points_squid']
        mongo.db.users.update_one({'_id': user_id},
                                  {'$set': {'statistics.' + today + ".points_squid": level_points + points}})

    # update the numbers of successfully obfuscated queries
    mongo.db.users.update_one({'_id': user_id},
                              {'$set': {'queries.' + category + '.' + original_query + '.' +
                                        str(index): 1}})

    num_successful_queries = user['queries'][category]['num_successful_queries'][index]
    mongo.db.users.update_one({'_id': user_id},
                              {'$set': {'queries.' + category + '.num_successful_queries.' +
                                        str(index): num_successful_queries + 1}})

    # The number of solved queries is only updated if the user did not quit the game and therefore achieved
    # zero points
    if points != 0:
        queries = user['statistics'][today]['queries_total']
        mongo.db.users.update_one({'_id': user_id},
                                  {'$set': {'statistics.' + today + '.queries_total': queries + 1}})
        if level == "chameleon":
            queries = user['statistics'][today]['queries_chameleon']
            mongo.db.users.update_one({'_id': user_id},
                                      {'$set': {'statistics.' + today + '.queries_chameleon': queries + 1}})
        else:
            queries = user['statistics'][today]['queries_squid']
            mongo.db.users.update_one({'_id': user_id},
                                      {'$set': {'statistics.' + today + '.queries_squid': queries + 1}})

        # update the value of second_level that indicates if the second level should be playable or not
        second_level = user['second_level']
        if second_level < 5:
            mongo.db.users.update_one({'_id': user_id}, {'$set': {'second_level': second_level + 1}})
        if (second_level + 1) == 5:
            mongo.db.users.update_one({'_id': user_id}, {'$set': {'introduction_second_level': True}})

    result = {'Success': 1}
    return jsonify(result)


@app.route(URL_PREFIX + '/game/<category>/<level>/', methods=['GET', 'POST'])
def game_start(category, level):
    """
    This function loads and prepares all the necessary data to start a new round of the game.
    @param category: The category in which the game is played
    @type category: String
    @param level: The level selected by the user
    @type level: String
    @return: The html file of the game containing data for the template
    @rtype: object
    """

    # Get the data of the playing user
    user_id = request.cookies.get('user_id')
    user = mongo.db.users.find_one({'_id': user_id})
    # If the user does not exist yet, then create one
    user_id = setup_user(user_id, user)
    user = mongo.db.users.find_one({'_id': user_id})

    # Load the needed data for the game
    game_round = user['game_round']
    total_points = user['total_points_game']
    query = request.args.get('query')
    file_name = QUERY_DATA[category][query]['file_name']
    keywords = QUERY_DATA[category][query]['keywords']
    forbidden_words = QUERY_DATA[category][query]['forbidden_words']

    # log the user data and the current query they are playing
    logging.info(json.dumps({'_id': user_id, 'username': user['user_name'], 'category': category, 'original query': query,
                 'level': level, 'timestamp': time.asctime(time.localtime())}))

    # Check if an introduction should be played or not
    intro = mongo.db.users.find_one({'_id': user_id}, {'introduction': 1, '_id': 0})
    provide_introduction = intro['introduction']

    resp = make_response(render_template('game-index.html', query=query, file_name=file_name, keywords=keywords,
                                         forbidden_words=forbidden_words, category=category, game_round=game_round,
                                         points=total_points, level=level, url_prefix=URL_PREFIX,
                                         introduction=provide_introduction))
    resp.set_cookie('user_id', user_id, samesite='Lax', max_age=1095 * 60 * 60 * 24)

    return resp


@app.route(URL_PREFIX + '/game', methods=['GET', 'POST'])
def query_round():
    """
    This function selects a random query the user has not solved yet.
    It is requested before the game starts and provides the data needed to start a
    new game round.
    @return: Jsonified dict that contains the selected category and a random query
    @rtype: object
    """
    category = request.get_json('selectedCategory')
    category = category['selectedCategory']
    level = request.get_json('selectedLevel')
    level = level['selectedLevel']
    user_id = request.cookies.get('user_id')

    unfinished_queries = []
    finished_queries = []
    user = mongo.db.users.find_one({'_id': user_id})
    game_round = user['game_round']
    # update the number of round the user has played
    mongo.db.users.update_one({'_id': user_id}, {'$set': {'game_round': game_round + 1}})

    index = 0
    if level == "chameleon":
        index = 1

    # get all queries which were not yet played in the specific level
    for query in user['queries'][category]:
        if query != 'num_successful_queries':
            if user['queries'][category][query][index] == 0:
                unfinished_queries.append(query)
            else:
                finished_queries.append(query)

    if len(unfinished_queries) != 0:
        random_query = random.choice(unfinished_queries)
    else:
        random_query = random.choice(finished_queries)

    result = {'query': random_query, 'category': category, 'level': level}
    return jsonify(result)


@app.route(URL_PREFIX + '/')
def introduction():
    """
    This function renders the intro layout of the game.
    @return: html template for the display of the introduction
    @rtype: object
    """
    user_id = request.cookies.get('user_id')
    user = mongo.db.users.find_one({'_id': user_id})
    user_id = setup_user(user_id, user)

    # Get the data of the playing user
    user_id = request.cookies.get('user_id')
    user = mongo.db.users.find_one({'_id': user_id})
    # If the user does not exist yet, then create one
    user_id = setup_user(user_id, user)
    user = mongo.db.users.find_one({'_id': user_id})

    tmp = mongo.db.users.find_one({'_id': user_id}, {'introduction': 1, '_id': 0})
    # Decide whether to show an option to play the intro or not
    provide_introduction = tmp['introduction']

    resp = make_response(render_template('introduction.html', url_prefix=URL_PREFIX,
                                         provide_introduction=provide_introduction))
    resp.set_cookie('user_id', user_id, samesite='Lax', max_age=1095 * 60 * 60 * 24)
    return resp


@app.route(URL_PREFIX + '/city')
def city_index():
    """
    The function renders the index of the game
    @return: html file that shows the index
    @rtype: object
    """
    user_id = request.cookies.get('user_id')
    user = mongo.db.users.find_one({'_id': user_id})
    second_level = False
    user_id = setup_user(user_id, user)

    user = mongo.db.users.find_one({'_id': user_id})
    # Decide if the option to select a level should be provided or not
    if user['second_level'] >= 5:
        second_level = True

    played_games_data = query_statistics(user_id, mongo.db.users, QUERY_LIST)

    # Decide whether the introduction should be played or not
    intro = mongo.db.users.find_one({'_id': user_id}, {'introduction': 1, '_id': 0})
    provide_introduction = intro['introduction']

    # Decide if the introduction for the second level should be played
    level_intro = mongo.db.users.find_one({'_id': user_id}, {'introduction_second_level': 1, '_id': 0})
    level_intro = level_intro['introduction_second_level']
    level_intro_was_played = mongo.db.users.find_one({'_id': user_id},
                                                     {'introduction_second_level_was_played': 1, '_id': 0})
    level_intro_was_played = level_intro_was_played['introduction_second_level_was_played']
    if level_intro is True and level_intro_was_played is False:
        play_level_intro = True
    else:
        play_level_intro = False

    resp = make_response(render_template('city-map.html', url_prefix=URL_PREFIX,
                                         played_games_data=played_games_data, second_level=second_level,
                                         introduction=provide_introduction, level_introduction=play_level_intro))
    resp.set_cookie('user_id', user_id, samesite='Lax', max_age=1095 * 60 * 60 * 24)
    return resp


@app.route(URL_PREFIX + '/search', methods=['POST'])
def search():
    """
    The function computes all the values to compute the points of a query the user entered
    @return: If provided document was found or not, if so then computed points are returned
    @rtype: object
    """
    # Get the query that the user just entered in the search form
    query = request.get_json('searchQuery')
    query = query['searchQuery']
    # get the original query which the user should obscure
    original_query = request.get_json('originalQuery')
    original_query = original_query['originalQuery']
    category = request.get_json('queryCategory')
    category = category['queryCategory']
    level = request.get_json('selectedLevel')
    level = level['selectedLevel']
    # uuid of the document for the original query
    query_id = QUERY_DATA[category][original_query]['uuid']

    # get the cookie to identify the user
    user_id = request.cookies.get('user_id')

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

    user = mongo.db.users.find_one({'_id': user_id})
    # log user data
    logging.info(json.dumps({'_id': user_id, 'username': user['user_name'], 'category': category, 'original query': original_query,
                            'user query': query, 'level': level,
                             'timestamp': time.asctime(time.localtime())}))

    # All the loops that compute the related documents etc. are only necessary when the document was found
    # If the document was not found, we can safe the run time of the following loops
    if found_document:
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

        result = {'document_position': document_pos_points, 'number_related_documents': num_related_docs_points,
                  'average_position_related_documents': avg_pos_related_docs_points, 'query_length': query_length_points,
                  'total_points_round': total_points, 'found_document': found_document}
        return jsonify(result)

    result = {'found_document': found_document}
    return jsonify(result)


@app.route(URL_PREFIX + "/leaderboards", methods=['GET'])
def display_leaderboards():
    """
    Loads the data of the points from all users
    @return: html file of the leaderboards
    @rtype: object
    """
    # Get the data of the playing user
    user_id = request.cookies.get('user_id')
    user = mongo.db.users.find_one({'_id': user_id})
    # If the user does not exist yet, then create one
    user_id = setup_user(user_id, user)

    data_total_points = list(mongo.db.users.find({}, {'_id': 1, 'user_name': 1, 'total_points': 1}))
    data_points_squid = list(mongo.db.users.find({}, {'_id': 1, 'user_name': 1, 'total_points_level_one': 1}))
    data_points_chameleon = list(mongo.db.users.find({}, {'_id': 1, 'user_name': 1, 'total_points_level_two': 1}))

    data_total_points = sorted(data_total_points, key=itemgetter('total_points'), reverse=True)
    data_points_squid = sorted(data_points_squid, key=itemgetter('total_points_level_one'), reverse=True)
    data_points_chameleon = sorted(data_points_chameleon, key=itemgetter('total_points_level_two'), reverse=True)

    resp = make_response(render_template('leaderboards.html', data_total_points=data_total_points,
                                         data_points_squid=data_points_squid,
                                         data_points_chameleon=data_points_chameleon, num_users=len(data_total_points),
                                         url_prefix=URL_PREFIX))
    resp.set_cookie('user_id', user_id, samesite='Lax', max_age=1095 * 60 * 60 * 24)

    return resp


@app.route(URL_PREFIX + "/settings", methods=['GET'])
def user_settings():
    """
    Renders the html file that allows people to change their username
    @return: html file
    @rtype: object
    """

    # Get the data of the playing user
    user_id = request.cookies.get('user_id')
    user = mongo.db.users.find_one({'_id': user_id})
    # If the user does not exist yet, then create one
    user_id = setup_user(user_id, user)
    user = mongo.db.users.find_one({'_id': user_id})
    username = user['user_name']

    resp = make_response(render_template('username.html', username=username, url_prefix=URL_PREFIX))
    resp.set_cookie('user_id', user_id, samesite='Lax', max_age=1095 * 60 * 60 * 24)
    return resp


@app.route(URL_PREFIX + "/changeUsername", methods=['POST', 'GET'])
def change_username():
    """
    Function is used to change the username of a user
    @return:
    @rtype: object
    """
    user_id = request.cookies.get('user_id')
    username = request.get_json('newName')
    username = username['newName']

    # check if the entered username is already taken
    usernames = list(mongo.db.users.find({}, {'user_name': 1, '_id': 0}))
    for x in usernames:
        if x['user_name'] == username:
            return jsonify({'success': False})

    mongo.db.users.update_one({'_id': user_id}, {'$set': {'user_name': username}})
    return jsonify({'success': True})


@app.route(URL_PREFIX + '/changeIntroData', methods=['POST'])
def change_intro_data():
    """
    This function defines that the introduction should not be played anymore
    @return:
    @rtype: object
    """
    user_id = request.cookies.get('user_id')
    data = request.get_json('intro')
    data = data['intro']

    mongo.db.users.update_one({'_id': user_id}, {'$set': {'introduction': data}})
    return jsonify({'success': True})


@app.route(URL_PREFIX + "/statistics", methods=['GET'])
def show_statistics():
    """
    This function loads the data to show the user specific statistics for the users
    @return: html response
    @rtype: object
    """
    # Get the data of the playing user
    user_id = request.cookies.get('user_id')
    user = mongo.db.users.find_one({'_id': user_id})
    # If the user does not exist yet, then create one
    user_id = setup_user(user_id, user)
    user = mongo.db.users.find_one({'_id': user_id})
    today = datetime.datetime.now()
    data_points = []
    data_queries = []
    smaller_date_exists = True
    # The statistics are empty at this point therefore there is an error here!!!
    smallest_date = next(iter(user['statistics']))
    counter = 0
    entries = 0

    # Load the data for the last seven dates where the user played
    while smaller_date_exists is True and entries <= 7:
        current_date = today - datetime.timedelta(days=counter)
        current_date = current_date.strftime("%d/%m/%Y")
        if current_date >= smallest_date:
            if current_date in user['statistics']:
                data_points.insert(0, {'date': current_date, 'Total Points': user['statistics'][current_date]['points_total'],
                                                  'Points Level Chameleon': user['statistics'][current_date]['points_chameleon'],
                                                'Points Level Squid': user['statistics'][current_date]['points_squid']})
                data_queries.insert(0, {'date': current_date, 'Total Number of Queries':
                    user['statistics'][current_date]['queries_total'],
                                                  'Queries Level Chameleon': user['statistics'][current_date]['queries_chameleon'],
                                     'Queries Level Squid': user['statistics'][current_date]['queries_squid']})
                entries = entries + 1
        else:
            smaller_date_exists = False
        counter = counter + 1

    json.dumps(data_points)
    json.dumps(data_queries)
    played_games_data = query_statistics(user_id, mongo.db.users, QUERY_LIST)

    resp = make_response(render_template('statistics.html', url_prefix=URL_PREFIX, data_points=data_points,
                                         data_queries=data_queries, played_games_data=played_games_data))
    resp.set_cookie('user_id', user_id, samesite='Lax', max_age=1095 * 60 * 60 * 24)

    return resp


@app.before_first_request
def load_query_data():
    global QUERY_DATA
    global QUERY_LIST
    site_root = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(site_root, "static/data/query_data", "query_complete_data.json")
    data = json.load(open(json_url))
    QUERY_DATA = data
    json_url = os.path.join(site_root, "static/data/query_data", "query_listing_data.json")
    data = json.load(open(json_url))
    QUERY_LIST = data


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
