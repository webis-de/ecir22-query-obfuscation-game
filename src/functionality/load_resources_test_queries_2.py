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
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


API_KEY = '265b2795-b7d2-42c6-a0a9-79fce26b3d44'
ELASTIC_SEARCH_INFO = 'http://betaweb024.medien.uni-weimar.de:9200/webis_warc_clueweb12_011/' \
                      'warcrecord/'


def change_stylesheet_resources(soup, chatnoir_soup):
    try:
        wayback_stylesheets = soup.findAll('link', attrs={'type': 'text/css', 'rel': 'stylesheet'})
        wayback_stylesheet_links = []

        # change the realtive path to absolute paths
        #version 2: Here the static css files of the wayback machine are ignored
        for i in wayback_stylesheets:
            if not i['href'].startswith('/_static/'):
                if i['href'].startswith('http://web.archive.org'):
                    wayback_stylesheet_links.append(i['href'])
                else:
                    wayback_stylesheet_links.append('http://web.archive.org' + i['href'])

        chatnoir_stylesheets = chatnoir_soup.findAll('link',
                                                     attrs={'type': 'text/css', 'rel': 'stylesheet'})

        #print("wayback stylesheets: ", wayback_stylesheets)
        #print("wayback stylesheet links: ", wayback_stylesheet_links)
        #print("chatnoir stylesheets: ", chatnoir_stylesheets)

        for link in chatnoir_stylesheets:
            tmp = link['href'].replace("https://", "")
            # print("Call 1: ", tmp)
            for i in range(0, len(wayback_stylesheet_links)):
                if tmp in wayback_stylesheet_links[i]:
                    # print("Call 2: ", tmp)
                    # print("Call 3: ", wayback_stylesheet_links[i])
                    link['href'] = wayback_stylesheet_links[i]

        #print("New Stylesheets: ", chatnoir_stylesheets)

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

        for i in wayback_images:
            if not i['src'].startswith('/_static/'):
                if i['src'].startswith('http://web.archive.org'):
                    wayback_image_links.append(i['src'])
                else:
                    wayback_image_links.append('http://web.archive.org' + i['src'])

        #print("wayback images: ", wayback_images)
        #print("wayback image links: ", wayback_image_links)
        #print("chatnoir images: ", chatnoir_images)

        for image in chatnoir_images:
            tmp = image['src'].replace("https://", "")
            # print("Call 1: ", tmp)
            for i in range(0, len(wayback_image_links)):
                if tmp in wayback_image_links[i]:
                    # print("Call 2: ", tmp)
                    # print("Call 3: ", wayback_stylesheet_links[i])
                    image['src'] = wayback_image_links[i]
        #print("New Image Links: ", chatnoir_images)
        return 0, 0
    except:
        print("Unexpected error in images:", sys.exc_info()[0], sys.exc_info()[1])
        return 'ERROR', sys.exc_info()


def check_wayback_url(entry):
    uuid = entry['uuid']
    # print(uuid)
    elastic_data = requests.get(ELASTIC_SEARCH_INFO + uuid)
    elastic_data = elastic_data.json()
    # print(elastic_data)
    crawl_date = elastic_data['_source']['date']
    original_uri = elastic_data['_source']['warc_target_uri']

    # convert the timestamp in the needed format
    crawl_date = crawl_date.replace('-', '')
    crawl_date = crawl_date[:8]

    # create the corresponding chatnoir url that is needed to load its content later on
    chatnoir_url = 'https://www.chatnoir.eu/cache?uuid=' + uuid + '&index=cw12&raw'

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


def create_csv(csv_list) -> int:
    """
    This function writes the related querys and their distances into a csv file.
    :return: 0
    """
    f = open('query_list_files.csv', 'w')
    with f:
        writer = csv.writer(f)
        for row in csv_list:
            writer.writerow(row)
    return 0


def main():
    retry_strategy = Retry(
        total=5,
        backoff_factor=15,
        status_forcelist=[429, 500, 502, 503, 504],
        method_whitelist=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("https://", adapter)
    http.mount("http://", adapter)

    with open('queries.csv', newline='') as f:
        reader = csv.reader(f)
        queries = list(reader)

    #query_counter = 0
    for query in queries:
        query_counter = 0
        print(query)
        #query_counter = query_counter + 1

        request = http.get('https://www.chatnoir.eu/api/v1/_search',
                           params={'apikey': API_KEY, 'query': query, 'size': 3,
                                   'index': 'cw12', 'raw': True})
        request = request.json()
        #print("Requests: " + str(request))

        for entry in request['results']:
            wayback_url, chatnoir_url = check_wayback_url(entry)
            #print(entry)
            #print(wayback_url)
            #print(chatnoir_url)

            if wayback_url != 'ERROR':
                query.append(wayback_url)
                query.append(chatnoir_url)
                # get all the stylesheets from the wayback machine
                wayback_website = requests.get(wayback_url)
                soup = BeautifulSoup(wayback_website.content, 'html.parser')

                chatnoir_website = requests.get(chatnoir_url)
                chatnoir_soup = BeautifulSoup(chatnoir_website.content, 'html.parser')

                success_status_stylesheets, possible_error_message_stylesheets = change_stylesheet_resources(
                    soup, chatnoir_soup)
                success_status_images, possible_error_message_images = change_image_resources(soup, chatnoir_soup)

                # html_file_name = 'html_file_' + str(query_counter) + '.html'
                html_file_name = str(query[0]) + '_' + str(query_counter) + '.html'
                print("File name: " + str(html_file_name))
                f = open(html_file_name, 'w')
                f.write(str(chatnoir_soup))
                f.close()
                query.append(html_file_name)

            else:
                print("Could not find wayback url")
                query.append('ERROR could not find matching wayback url')
                query.append('No matching html file')
            print(queries)
            query_counter = query_counter + 1
    create_csv(queries)
    print(queries)


if __name__ == '__main__':
    main()
