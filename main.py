from json import dumps, load
from os import system
from models import Supabase, init_selenium
from utils import write_file, generate_url, make_dir
from sys import argv
from const import URL
from souper import (
    format_, 
    read_and_make_soup, 
    extract_content, 
    extract_local, 
    extract_organic, 
    extract_segment, 
    aggregate,
)
import yake

NUM_OF_PAGES = 3

def step_1(url, run_selenium: bool):
    """Extract organic urls, local data and related questions into .json files"""
    # init
    make_dir('./data')
    make_dir('./html')
    params = dict(file="./html/page-1.html", mode="r", encoding="utf-8")
    if run_selenium:
        init_selenium(url, destination=params['file'])
    soup = read_and_make_soup(params)
    # execute
    content_div = extract_content(soup)
    if not content_div:
        raise Exception('Invalid HTML')

    organic_body, local_body = extract_segment(content_div)
    organic_results, related_results = extract_organic(organic_body)
    local_results = {}
    local_ads = []
    
    if local_body:
        local_dicts = extract_local(local_body)
        local_results = {
            'more_location_link': local_dicts['more_location_link'], 
            'places': []
        }

        for local_dict in local_dicts['places']:

            local_result = {
                'title': local_dict['title'],
                'place_id': local_dict['place_id']
            }
            
            local_ad = {
                'rating': float(local_dict['rating'].replace(',', '.')),
                'rating_count': int(local_dict['rating_count']),
                'badge': None,
                'service_area': local_dict['service_area'],
                'hours': local_dict['hours'],
                'years_in_business': local_dict['years_in_business'],
                'phone': local_dict['phone'].replace('-', '').replace(' ', '')
            }

            if local_dict.get('website'): # empty string or non-existent at all -> False -> dont't add website
                local_result['website'] = local_dict['website']
                local_ad['link'] = local_dict['website']

            local_results['places'].append(local_result)
            local_ads.append(local_ad)

    write_file(dumps(organic_results), './data/organic_links.json', 'w')
    write_file(dumps(local_results), './data/local_results.json', 'w')
    write_file(dumps(local_ads), './data/local_ads.json', 'w')
    write_file(dumps(related_results), './data/questions.json', 'w')


def step_2(url, run_selenium: bool):
    """Extracting h1, h2, h3, h4 and p in search pages"""
    make_dir('./data')
    make_dir('./html')
    step_2_data = dict()
    for i in range(0, NUM_OF_PAGES):
        # init
        filepath = f'./html/page-{i + 1}.html'
        params = dict(file=filepath, mode="r", encoding="utf-8")
        if run_selenium:
            init_selenium(url, page=i + 1, destination=filepath)
        soup = read_and_make_soup(params)

        h1s = soup.find_all('h1')
        h2s = soup.find_all('h2')
        h3s = soup.find_all('h3')
        h4s = soup.find_all('h4')
        ps = soup.find_all('p')

        h1s = [format_(h1) for h1 in h1s]
        h2s = [format_(h2) for h2 in h2s]
        h3s = [format_(h3) for h3 in h3s]
        h4s = [format_(h4) for h4 in h4s]
        ps = [format_(p.span) for p in ps]

        data = dict(h1=h1s, h2=h2s, h3=h3s, h4=h4s, p=ps)

        step_2_data[f'page {i + 1}'] = data

    write_file(dumps(step_2_data), './data/header.json', 'w')


def step_3():
    """Extract n-grams keywords into .json with descending ranking"""
    def get_field(data, key, field):
        return ' . '.join(data[key][field])

    kw_extractor = yake.KeywordExtractor(top=3, stopwords=None)
    with open('./data/header.json', 'r', encoding='utf-8') as fp:
        step_2_data = load(fp)

    h3s = []
    ps = []
    for key in step_2_data:
        h3s.append(get_field(step_2_data, key, 'h3'))
        ps.append(get_field(step_2_data, key, 'p'))
    h3s = ' . '.join(h3s)
    ps = ' . '.join(ps)

    keywords = kw_extractor.extract_keywords(' . '.join([h3s, ps]))
    write_file(
        dumps([{'rank': i + 1, 'keyword': packaged[0], 'score': packaged[1]}
               for i, (packaged) in enumerate(keywords[::-1])]),
        './data/keywords.json',
        'w',
        'utf-8'
    )


def step_4():
    """Aggregate and pipeline extracted data into Supabase (pending)"""
    aggregate('./data')

def run():
    system("cls")
    fns = [
        step_1, 
        step_2, 
        step_3, 
        step_4
    ]
    
    cmts = [
        "Extract organic urls, local data and related questions into .json files",
        "Extracting h1, h2, h3, h4 and p in search pages",
        "Extract n-grams keywords into .json with descending ranking",
        "Aggregate and pipeline extracted data"
    ]

    if len(argv) > 1:
        index = int(argv[1])
        if index > 4 or index < 1:
            raise Exception('Wrong parameter (must be int from 1 -> 4)')
        print('Executing step {}: {}\n\n'.format(index, cmts[index - 1]))

        if index == 1 or index == 2:
            if len(argv) < 3:
                raise Exception('Not enough parameters ("true" or "false" required)')

            param = argv[2].lower()

            if param in ['true', 't', 'yes', 'y']:
                param = True
            elif param in ['false', 'f', 'no', 'n']:
                param = False
            else:
                raise Exception('Invalid parameter ("true" or "false" required)')

            if param:
                question = input('What is your query? ')
                if not question:
                    raise Exception('Please don\'t leave the query empty, try again')
                area = input('Where do you want to search? ')
                if not area:
                    raise Exception('Please don\'t leave the location empty, try again')

                url = generate_url(question, area)
                print("\n- - - Scraping {} - - -\n".format(url))
            else:
                url = URL

            fns[index - 1](url, param)
        else:
            fns[index - 1]()

        print("Finished execution\n")

    else:
        raise Exception('Not enough parameters')
    
if __name__ == "__main__":
    run()