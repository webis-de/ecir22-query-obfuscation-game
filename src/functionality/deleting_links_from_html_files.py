#!/usr/bin/env/python3

# ------------------------------------------------------------------------------------------------
# @authors       Nicola Lea Libera (117073)
#
# ------------------------------------------------------------------------------------------------
# Description: This script deletes all the href attributes inside the <a> tags of the html files
#              for the game.
#
# ------------------------------------------------------------------------------------------------

import requests
from bs4 import BeautifulSoup
import csv
import sys
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import os

PATH_TO_FILES = '/home/nicola/Desktop/thesis-libera/src/data/good-websites/'


def delete_links():
    arr = os.listdir(PATH_TO_FILES)
    # chatnoir_website = requests.get(chatnoir_url)

    for file in arr:
        print("I was called: " + str(file))
        with open(PATH_TO_FILES + file) as f:
            soup = BeautifulSoup(f, 'html', from_encoding='utf-8')
            # print(str(soup))
            for a in soup.findAll('a'):
                del a['href']

            # html_file_name = str(file)
            f = open(PATH_TO_FILES + file, 'w')
            f.write(str(soup))
            f.close()
            print("I was written: " + str(file))


def rename_html_files():
    arr = os.listdir(PATH_TO_FILES)
    # chatnoir_website = requests.get(chatnoir_url)

    for file in arr:
        new_file_name = file.split('.')
        new_file_name = str(new_file_name[0][:-2]) + '.' + new_file_name[1]
        print(str(new_file_name))
        os.rename(PATH_TO_FILES + file, new_file_name)


def main():
    # delete_links()
    rename_html_files()


if __name__ == '__main__':
    main()