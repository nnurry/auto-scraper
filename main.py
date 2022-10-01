from scraper import get_data_by_html, get_data_by_url
from sys import argv
from os import system

if len(argv) > 1:
    system('cls')
    if argv[1] == 'html':
        get_data_by_html()
    elif argv[1] == 'url':
        get_data_by_url()
    else:
        raise Exception('wrong parameter')