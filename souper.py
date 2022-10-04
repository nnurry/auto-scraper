from json import dumps, load
from bs4 import BeautifulSoup, Tag
from utils import write_file

def read_and_make_soup(params: dict):
    with open(**params) as fp:
        soup = BeautifulSoup(fp)
    return soup

def aggregate(directory_path: str, destination: str ='./data/aggregated.json'):
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

def format_(string: str, get_text: bool =True):
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
            organic_results.append({
                'title': format_(organic_result.h3),
                'link': format_(organic_result.cite)
            })

    organic_results = [
        {'position': index + 1, **organic_result}
        for index, organic_result in enumerate(organic_results)
    ]

    for related_result in related.find_all('div', jsname='Cpkphb'):
        question = format_(related_result.span)
        answer_title = format_(related_result.find(
            'div', 
            attrs={"data-tts": "answers"}
        ))
        answer_body = format_(related_result.find('div', role='heading'))
        # NOTE: in answer_body there might be 2 div with role = heading -> handle this later
        article_link = format_(related_result.find('a', href=True)['href'], False)
        article_header = format_(related_result.find('h3'))
        related_results.append({
            'question': question,
            'snippet': ' - '.join([answer_title, answer_body]) if answer_title else answer_body,
            'title': article_header,
            'link': article_link
        })

    return organic_results, related_results

def extract_local(local_body: Tag):
    def filter_website(url: str):
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
            local_ = deep_split(format_(local_))
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
