#!/usr/bin/env/python3

# ------------------------------------------------------------------------------------------------
# @authors       Nicola Lea Libera (117073)
#
# ------------------------------------------------------------------------------------------------
# Description: Testing the functionality of loading the missing resources.
#
# ------------------------------------------------------------------------------------------------

import requests
from bs4 import BeautifulSoup
import csv
import sys


API_KEY = '265b2795-b7d2-42c6-a0a9-79fce26b3d44'
ELASTIC_SEARCH_INFO = 'http://betaweb023.medien.uni-weimar.de:9200/webis_warc_clueweb09_003/' \
                      'warcrecord/'


def change_stylesheet_resources(soup, chatnoir_soup):
    try:
        wayback_stylesheets = soup.findAll('link', attrs={'type': 'text/css', 'rel': 'stylesheet'})
        wayback_stylesheet_links = []

        # change the realtive path to absolute paths
        # version 1: Here every stylesheets gets into the list
        """for i in wayback_stylesheets:
            if i['href'].startswith('https://web.archive.org'):
                wayback_stylesheet_links.append(i['href'])
            else:
                wayback_stylesheet_links.append('http://web.archive.org' + i['href'])"""

        #version 2: Here the static css files of the wayback machine are ignored
        for i in wayback_stylesheets:
            if not i['href'].startswith('/_static/'):
                if i['href'].startswith('http://web.archive.org'):
                    wayback_stylesheet_links.append(i['href'])
                else:
                    wayback_stylesheet_links.append('http://web.archive.org' + i['href'])

        chatnoir_stylesheets = chatnoir_soup.findAll('link',
                                                     attrs={'type': 'text/css', 'rel': 'stylesheet'})

        counter = 0

        # change the links inside the stylesheets to the resources from the wayback machine
        for links in chatnoir_stylesheets:
            links['href'] = wayback_stylesheet_links[counter]
            counter = counter + 1
        return 0, 0
    except:
        print("Unexpected error in stylesheets:", sys.exc_info()[0], sys.exc_info()[1])
        return 'ERROR', sys.exc_info()


def change_image_resources(soup, chatnoir_soup):
    try:
        # find all the images in chatnoir
        chatnoir_images = chatnoir_soup.findAll('img')
        #print("chatnoir images: " + str(chatnoir_images))

        # find all the corresponding images inside the wayback machine
        wayback_images = soup.findAll('img')
        #print("wayback images: " + str(wayback_images))
        wayback_image_links = []

        # change the relative path to absolute paths
        """for i in wayback_images:
            if i['src'].startswith('https://web.archive.org'):
                wayback_image_links.append(i['src'])
            else:
                wayback_image_links.append('https://web.archive.org' + i['src'])"""
        #print("wayback images: ", wayback_images)
        for i in wayback_images:
            wayback_image_links.append('https://web.archive.org' + i['src'])

        print(wayback_image_links)
        counter = 0
        # change the links inside the images to the resources from the wayback machine
        for image in chatnoir_images:
            image['src'] = wayback_image_links[counter]
            counter = counter + 1
        return 0, 0
    except:
        print("Unexpected error in images:", sys.exc_info()[0], sys.exc_info()[1])
        return 'ERROR', sys.exc_info()


def check_wayback_url(entry):
    uuid = entry['uuid']
    #print(uuid)
    elastic_data = requests.get(ELASTIC_SEARCH_INFO + uuid)
    elastic_data = elastic_data.json()
    #print(elastic_data)
    crawl_date = elastic_data['_source']['date']
    original_uri = elastic_data['_source']['warc_target_uri']

    # convert the timestamp in the needed format
    crawl_date = crawl_date.replace('-', '')
    crawl_date = crawl_date[:8]

    # create the corresponding chatnoir url that is needed to load its content later on
    chatnoir_url = 'https://www.chatnoir.eu/cache?uuid=' + uuid + '&index=cw09&raw'

    # Check if the url exists in the web archive and retrieve its url
    # If there is no time stamp defined in this function,
    # the most recent available capture is returned
    wayback_url = requests.get(
        'http://archive.org/wayback/available?url=' + original_uri + '&timestamp=' + crawl_date)
    # convert response object into json object to get url of the wayback machine
    wayback_url = wayback_url.json()
    #print(wayback_url)
    if 'archived_snapshots' not in wayback_url or len(wayback_url['archived_snapshots']) == 0:
        return 'ERROR', 0

    wayback_url = wayback_url['archived_snapshots']['closest']['url']

    return wayback_url, chatnoir_url


def find_existing_entry_in_wayback_machine(request, query):
    result_index = 0  # This is the index that keeps track which of the 3 results from the chatnoir search is taken for further processing

    for entry in request['results']:
        # print(entry)
        wayback_url, chatnoir_url = check_wayback_url(entry)
        if wayback_url != 'ERROR':
            query.append(wayback_url)
            #print("result index: " + str(result_index))
            wayback_website = requests.get(wayback_url)
            soup = BeautifulSoup(wayback_website.content, 'html.parser')

            chatnoir_website = requests.get(chatnoir_url)
            chatnoir_soup = BeautifulSoup(chatnoir_website.content, 'html.parser')

            success_status_stylesheets, possible_error_message_stylesheets = change_stylesheet_resources(
                soup, chatnoir_soup)
            success_status_images, possible_error_message_images = change_image_resources(soup,
                                                                                          chatnoir_soup)
            print("This is a test for error handling: " + str(success_status_images))
            if success_status_images == 'ERROR' or success_status_stylesheets == 'ERROR':
                #print("Test query 1: ", query)
                del query[1]
                #print("Test query 2: ", query)
                if len(request['results']) == 1:
                    if success_status_images == 'ERROR':
                        query.append(possible_error_message_stylesheets)
                    if success_status_stylesheets == 'ERROR':
                        query.append(possible_error_message_images)

                    return 0
                else:
                    del request['results'][result_index]
                    find_existing_entry_in_wayback_machine(request, query)
            else:
                return chatnoir_soup

        if wayback_url == 'ERROR' and entry == request['results'][2]:
            query.append('ERROR: Could not find entry in wayback machine')
            return 0

        result_index = result_index + 1
    return chatnoir_soup


def create_csv(csv_list) -> int:
    """
    This function writes the related querys and their distances into a csv file.
    :return: 0
    """
    f = open('queries_with_wayback_url_and_html_file_missing_resources_2.csv', 'w')
    with f:
        writer = csv.writer(f)
        for row in csv_list:
            writer.writerow(row)
    return 0


def main():
    with open('queries.csv', newline='') as f:
        reader = csv.reader(f)
        queries = list(reader)

    query_counter = 0
    for query in queries:
        query_counter = query_counter + 1
        print(query)
        #print(query_counter)
        request = requests.get('https://www.chatnoir.eu/api/v1/_search',
                               params={'apikey': API_KEY, 'query': query, 'size': 3,
                                       'index': 'cw09', 'raw': True})
        request = request.json()

        chatnoir_soup = find_existing_entry_in_wayback_machine(request, query)

        if chatnoir_soup != 0:
            html_file_name = 'html_file_' + str(query_counter) + '.html'
            f = open(html_file_name, 'w')
            f.write(str(chatnoir_soup))
            f.close()
            query.append(html_file_name)

        print(queries)
    create_csv(queries)


if __name__ == '__main__':
    main()
