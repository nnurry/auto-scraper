from json import dumps
from os import system
from bs4 import BeautifulSoup, PageElement, Tag
from models import Execute
from utils import write_file

def read_and_make_soup(params):

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
        return ' '.join(filter(lambda x: x != '', string.strip().replace('\n', '').split(' ')))
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
    """
    """
    
    def filter_website(url):
        return True if ("http" in url or "https" in url) and ("google" not in url) else False
    
    local_websites = list(
        map(lambda url: url['href'], local_body.find_all('a', href=True)))
    local_websites = list(filter(filter_website, local_websites))

    local_ads = local_body.find_all('div', class_='rllt__details')
    local_dicts = []
    for local_ad in local_ads:
        local_data = []
        for local_ in local_ad.contents:
            local_ = deep_split(trim(local_))
            local_data = [*local_data, *local_]

        local_dict = {
            'title': local_data[0],
            'rating': local_data[1][:3],
            'rating_count': local_data[1][4:-1],
            'type': local_data[2],
            'years_in_business': local_data[3],
            'phone': local_data[4],
            'hours': local_data[5],
            'service_type': local_data[6]
        }
        local_dicts.append(local_dict)

    local_ads = list(
        map(lambda x: x['data-cid'], local_body.find_all('a', attrs={'data-cid': True})))
    for i, local_dict in enumerate(local_dicts):
        local_dicts[i] = {'position': i + 1,
                          'place_id': local_ads[i], 
                          'more_info': local_websites[i],
                          **local_dict}
    # TODO: MISSING badge, service_area
    return local_dicts

def run():
    system("cls")
    # Execute.init_selenium()
    """STEP 1"""
    params = dict(file="./content.html", mode="r", encoding="utf-8")
    # soup = read_and_make_soup(params)
    # content_div = extract_content(soup)
    # if not content_div:
    #     raise Exception('Invalid HTML')

    # organic_body, local_body = extract_segment(content_div)
    # organic_results, related_results = extract_organic(organic_body)
    # local_dicts = extract_local(local_body)
    # print(local_dicts)
    # write_file(dumps(organic_results), './data/organic.json', 'w')
    # write_file(dumps(related_results), './data/related.json', 'w')
    # write_file(dumps(local_dicts), './data/local-data.json', 'w')
    # extract_local(local_body)
    """STEP 2"""
    for i in range(0, 4):
        filepath = f'./data-step-2/content-page-{i + 1}.html'
        # Execute.init_selenium(True, i + 1, filepath)
        params['file'] = filepath
        soup = read_and_make_soup(params)
        # get h1-h2-h3-h4-p
        h1s = soup.find_all('h1')
        h2s = soup.find_all('h2')
        h3s = soup.find_all('h3')
        h4s = soup.find_all('h4')
        ps = soup.find_all('p')
        
        h1s = [trim(h1) for h1 in h1s]
        h2s = [trim(h2) for h2 in h2s]
        h3s = [trim(h3) for h3 in h3s]
        h4s = [trim(h4) for h4 in h4s]
        ps = [trim(p) for p in ps]
        
        step_2_data = dict(h1=h1s, h2=h2s, h3=h3s, h4=h4s, p=ps)

        # write_file(dumps(step_2_data), './data/step-2.json', 'w')
if __name__ == "__main__":
    run()