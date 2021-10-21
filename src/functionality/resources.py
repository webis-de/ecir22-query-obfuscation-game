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
import urllib
import urllib.parse as urlparse
from urllib.parse import parse_qs
from urllib.request import urlopen


# API_KEY = '265b2795-b7d2-42c6-a0a9-79fce26b3d44'
url = 'https://www.chatnoir.eu/cache?uuid=ca562721-447e-525a-801a-12cc5d4d689d&index=cw09&raw'
ELASTIC_SEARCH_INFO = 'http://betaweb023.medien.uni-weimar.de:9200/webis_warc_clueweb09_003/' \
                      'warcrecord/'


# def fix_html(html):
#    return html


def retrieve_wayback_url():
    # Get the timestamp and the original url of the crawl from the elasticsearch representation
    parsed = urlparse.urlparse(url)
    uuid = parse_qs(parsed.query)['uuid'][0]

    elastic_data = requests.get(ELASTIC_SEARCH_INFO + uuid)
    elastic_data = elastic_data.json()
    crawl_date = elastic_data['_source']['date']
    original_uri = elastic_data['_source']['warc_target_uri']

    # convert the timestamp in the needed format
    crawl_date = crawl_date.replace('-', '')
    crawl_date = crawl_date[:8]

    # Check if the url exists in the web archive and retrieve its url
    # If there is no time stamp defined in this function,
    # the most recent available capture is returned
    wayback_url = requests.get('http://archive.org/wayback/available?url=' + original_uri + '&timestamp=' + crawl_date)
    # convert response object into json object to get url of the wayback machine
    wayback_url = wayback_url.json()
    wayback_url = wayback_url['archived_snapshots']['closest']['url']

    return wayback_url


def change_stylesheet_resources(soup, chatnoir_soup):

    wayback_stylesheets = soup.findAll('link', attrs={'type': 'text/css', 'rel': 'stylesheet'})
    wayback_stylesheet_links = []

    # change the realtive path to absolute paths
    for i in wayback_stylesheets:
        wayback_stylesheet_links.append('http://web.archive.org' + i['href'])

    chatnoir_stylesheets = chatnoir_soup.findAll('link',
                                                 attrs={'type': 'text/css', 'rel': 'stylesheet'})

    counter = 0

    # change the links inside the stylesheets to the resources from the wayback machine
    for links in chatnoir_stylesheets:
        links['href'] = wayback_stylesheet_links[counter]
        counter = counter + 1


def change_image_resources(soup, chatnoir_soup):
    # find all the images in chatnoir
    chatnoir_images = chatnoir_soup.findAll('img')

    # find all the corresponding images inside the wayback machine
    wayback_images = soup.findAll('img')
    wayback_image_links = []

    # change the relative path to absolute paths
    for i in wayback_images:
        wayback_image_links.append('https://web.archive.org' + i['src'])

    counter = 0
    # change the links inside the images to the resources from the wayback machine
    for image in chatnoir_images:
        image['src'] = wayback_image_links[counter]
        counter = counter + 1


def main():
    wayback_url = retrieve_wayback_url()

    # get all the stylesheets from the wayback machine
    wayback_website = requests.get(wayback_url)
    soup = BeautifulSoup(wayback_website.content, 'html.parser')

    chatnoir_website = requests.get(url)
    chatnoir_soup = BeautifulSoup(chatnoir_website.content, 'html.parser')

    change_stylesheet_resources(soup, chatnoir_soup)
    change_image_resources(soup, chatnoir_soup)

    f = open("wayback.html", "w")
    f.write(str(chatnoir_soup))
    f.close()


if __name__ == '__main__':
    main()
