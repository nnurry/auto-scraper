from json import dumps, load
from os import system
from bs4 import BeautifulSoup, Tag
from models import Supabase, init_selenium
from utils import write_file, generate_url
from sys import argv
from const import URL
import yake

NUM_OF_PAGES = 3

url = URL

print("URL = {}".format(url))

def aggregate(directory_path, destination='./data/aggregated.json'):
    PARAMS = dict(mode='r', encoding='utf-8')
    child_files = [
        'organic_links', 
        'local_results', 
        'local_ads', 
        'keywords',
        'questions',
    ]
    def open_files(directory_path, filenames):
        return [open(f'{directory_path}/{filename}.json', **PARAMS) for filename in filenames]
    def close_files(files):
        for file in files:
            file.close()
    files = open_files(directory_path, child_files)
    data = {field: {} for field in child_files}
    for i, file in enumerate(files):
        data[child_files[i]] = load(file)
    write_file(dumps(data), destination, encoding=PARAMS['encoding'])
    close_files(files)
    return data

def read_and_make_soup(params: dict):
    with open(**params) as fp:
        soup = BeautifulSoup(fp)
    return soup


def get_content(main_div: Tag):
    main_res = main_div.find(class_='GyAeWb')
    if main_res:
        return main_res
    main_res = main_div.find(id='rcnt')
    if main_res:
        return main_res
    return None


def extract_content(soup: BeautifulSoup):
    html = soup.html
    body = html.body
    main = body.find(name='div', class_='main')
    return get_content(main)


def extract_segment(content: Tag):
    organic_body = content.find('div', class_='s6JM6d')
    local_body = content.find('div', class_='M8OgIe')
    return organic_body, local_body


def trim(string: str, get_text=True):
    if string:
        if get_text:
            string = string.text
        string = ' '.join(
            filter(lambda x: x != '', string.strip().replace('\n', '').split(' ')))
        return string
    return ''


def deep_split(string: str):
    if string.find('·'):
        first = list(filter(lambda x: x != '', string.split("·")))
        later = list(map(lambda x: x.strip(), first))
        return later
    else:
        return [string]


def extract_organic(organic_body: Tag):
    organic = organic_body.find('div', id='search')
    related = organic_body.find('div', id='botstuff')
    organic_results = []
    related_results = []

    for organic_result in organic.find_all('div', class_='MjjYud'):
        if organic_result.cite and organic_result.h3:
            organic_results.append({'title': trim(organic_result.h3),
                                    'link': trim(organic_result.cite)})
    organic_results = [{'position': index + 1, **organic_result}
                       for index, organic_result in enumerate(organic_results)]

    for related_result in related.find_all('div', jsname='Cpkphb'):
        question = trim(related_result.span)
        answer_title = trim(related_result.find(
            'div', attrs={"data-tts": "answers"}))
        answer_body = trim(related_result.find('div', role='heading'))
        # NOTE: in answer_body there might be 2 div with role = heading -> handle this later
        article_link = trim(related_result.find('a', href=True)['href'], False)
        article_header = trim(related_result.find('h3'))
        related_results.append({
            'question': question,
            'snippet': ' - '.join([answer_title, answer_body]) if answer_title else answer_body,
            'title': article_header,
            'link': article_link
        })

    return organic_results, related_results


def extract_local(local_body: Tag):

    def filter_website(url):
        return True if ("http" in url or "https" in url) and ("google" not in url) else False

    local_websites = list(
        map(lambda url: url['href'], local_body.find_all('a', href=True)))

    local_websites = list(filter(filter_website, local_websites))

    local_ads = local_body.find_all('div', class_='rllt__details')
    local_dicts = []
    for local_ad in local_ads:
        # print(local_ad.a)
        local_data = []
        for local_ in local_ad.contents:
            local_ = deep_split(trim(local_))
            local_data = [*local_data, *local_]
        service_area = local_data.pop(4) if len(local_data) > 7 else None
        local_dict = {
            'title': local_data[0],
            'rating': local_data[1][:3],
            'rating_count': local_data[1][4:-1],
            'type': local_data[2],
            'years_in_business': local_data[3],
            'phone': local_data[4],
            'hours': local_data[5],
            'service_type': local_data[6],
            'service_area': service_area
        }
        local_dicts.append(local_dict)

    local_ads = list(
        map(lambda x: x['data-cid'], local_body.find_all('a', attrs={'data-cid': True})))

    more_location_link = local_body.find('g-more-link')
    more_location_link = more_location_link.find('a', href=True)['href']
    for i, local_dict in enumerate(local_dicts):
        local_dicts[i] = {'position': i + 1,
                          'place_id': local_ads[i],
                          'website': local_websites[i],
                          **local_dict}
    local_dicts = {'more_location_link': more_location_link,
                   'places': local_dicts}

    # TODO: MISSING badge, service_area
    return local_dicts


def step_1(run_selenium):
    """DRIVER CODE STEP 1"""
    # init
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
            local_results['places'].append({
                'title': local_dict['title'],
                'website': local_dict['website'],
                'place_id': local_dict['place_id']
            })
            local_ads.append({
                'link': local_dict['website'],
                'rating': float(local_dict['rating'].replace(',', '.')),
                'rating_count': int(local_dict['rating_count']),
                'badge': None,
                'service_area': local_dict['service_area'],
                'hours': local_dict['hours'],
                'years_in_business': local_dict['years_in_business'],
                'phone': local_dict['phone'].replace('-', '').replace(' ', '')
            })

    write_file(dumps(organic_results), './data/organic_links.json', 'w')
    write_file(dumps(local_results), './data/local_results.json', 'w')
    write_file(dumps(local_ads), './data/local_ads.json', 'w')
    write_file(dumps(related_results), './data/questions.json', 'w')


def step_2(run_selenium):
    """DRIVER CODE STEP 2"""
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

        h1s = [trim(h1) for h1 in h1s]
        h2s = [trim(h2) for h2 in h2s]
        h3s = [trim(h3) for h3 in h3s]
        h4s = [trim(h4) for h4 in h4s]
        ps = [trim(p.span) for p in ps]

        data = dict(h1=h1s, h2=h2s, h3=h3s, h4=h4s, p=ps)

        step_2_data[f'page {i + 1}'] = data

    write_file(dumps(step_2_data), './data/header.json', 'w')


def step_3():
    """
    h1, h2 full of default keyword -> analyze h3, p
    h3 gives generic and badly categorized keywords -> ignore h3 also
    """
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
    aggregate('./data')

def run():
    # system("cls")
    fns = [step_1, step_2, step_3, step_4]
    if len(argv) > 1:
        index = int(argv[1])
        if index > 4 or index < 1:
            raise Exception('Wrong parameter (must be int from 1 -> 4)')
        if index == 1 or index == 2:
            if len(argv) < 3:
                raise Exception('Not enough parameters ("true" or "false" required)')

            param = argv[2].lower()
            if param == 'true':
                param = True
            elif param == 'false':
                param = False
            else:
                raise Exception('Invalid parameter ("true" or "false" required)')

            fns[int(argv[1]) - 1](param)
        else:
            fns[int(argv[1]) - 1]()

    else:
        raise Exception('Not enough parameters')    

def run_alternative():
    """
        If you want to query, please change parameters below
    """
    # system("cls")
    step = int(input('Select step (1 | 2 | 3 | 4): '))
    if step > 4 or step < 1:
        raise Exception('Step must be int from 1 to 4')
    question = input('What is your query? ')
    if not question:
        raise Exception('Please don\'t leave the query empty, try again')
    area = input('Choose the area: ')
    if not area:
        raise Exception('Please don\'t leave the location empty, try again')
    url = URL if (not question or not area) else generate_url(question, area)
    print("URL = {}".format(url))
    fns = [step_1, step_2, step_3, step_4]
    if step == 1 or step == 2:
        scrape = input('Do you want to scrape the web? ')
        param = scrape.lower()
        if param in ['true', 'yes', 'y', 't']:
            param = True
        elif param == ['false', 'no', 'n', 'f']:
            param = False
        else:
            raise Exception('Invalid parameter ("true" or "false" required)')
        fns[step - 1](param)
    else:
        fns[step - 1]()
    
if __name__ == "__main__":
    run()
