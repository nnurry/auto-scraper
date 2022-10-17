from json import dumps, load
import json
import os.path
from os import system
from models import Supabase, init_selenium
from utils import write_file, make_dir
from sys import argv
from const import URL,SUPEBASE_TABLE
from souper import (
    format_,
    read_and_make_soup,
    extract_content,
    extract_local,
    extract_organic,
    extract_segment,
    aggregate,
    inquire,
)
import yake

NUM_OF_PAGES = 3


def step_1(**kwargs):
    """Extract organic urls, local data and related questions into .json files"""
    # init
    url = kwargs.get("url")
    run_selenium = kwargs.get("run_selenium")
    if None in [url, run_selenium]:
        raise Exception("Missing argument")
    make_dir("./data")
    make_dir("./html")
    params = dict(file="./html/page-1.html", mode="r", encoding="utf-8")
    if run_selenium:
        init_selenium(url, destination=params["file"])
    soup = read_and_make_soup(params)
    # execute
    content_div = extract_content(soup)
    if not content_div:
        raise Exception("Invalid HTML")

    organic_body, local_body = extract_segment(content_div)
    organic_results, related_results = extract_organic(organic_body)
    local_results = {}
    local_ads = []

    if local_body:
        local_dicts = extract_local(local_body)
        local_results = {
            "more_location_link": local_dicts["more_location_link"],
            "places": [],
        }

        local_result_schema = [
            "rating",
            "rating_count",
            "badge",
            "service_area",
            "hours",
            "years_in_business",
            "phone",
        ]

        for local_dict in local_dicts["places"]:

            local_result = {
                "title": local_dict["title"],
                "place_id": local_dict["place_id"],
            }

            local_ad = {key: local_dict[key] for key in local_result_schema}

            if local_dict.get(
                "website"
            ):  # empty string or non-existent at all -> False -> dont't add website
                local_result["website"] = local_dict["website"]
                local_ad["link"] = local_dict["website"]

            local_results["places"].append(local_result)
            local_ads.append(local_ad)

    write_file(dumps(organic_results), "./data/organic_links.json", "w")
    write_file(dumps(local_results), "./data/local_results.json", "w")
    write_file(dumps(local_ads), "./data/local_ads.json", "w")
    write_file(dumps(related_results), "./data/questions.json", "w")


def step_2(**kwargs):
    """Extracting h1, h2, h3, h4 and p in search pages"""
    url = kwargs.get("url")
    run_selenium = kwargs.get("run_selenium")
    if None in [url, run_selenium]:
        raise Exception("Missing argument")
    make_dir("./data")
    make_dir("./html")
    step_2_data = dict()
    for i in range(0, NUM_OF_PAGES):
        # init
        filepath = f"./html/page-{i + 1}.html"
        params = dict(file=filepath, mode="r", encoding="utf-8")
        if run_selenium:
            init_selenium(url, page=i + 1, destination=filepath)
        soup = read_and_make_soup(params)

        h1s = soup.find_all("h1")
        h2s = soup.find_all("h2")
        h3s = soup.find_all("h3")
        h4s = soup.find_all("h4")
        ps = soup.find_all("p")

        h1s = [format_(h1) for h1 in h1s]
        h2s = [format_(h2) for h2 in h2s]
        h3s = [format_(h3) for h3 in h3s]
        h4s = [format_(h4) for h4 in h4s]
        ps = [format_(p.span) for p in ps]

        data = dict(h1=h1s, h2=h2s, h3=h3s, h4=h4s, p=ps)

        step_2_data[f"page {i + 1}"] = data

    write_file(dumps(step_2_data), "./data/header.json", "w")


def step_3(**kwargs):
    """Extract n-grams keywords into .json with descending ranking"""

    def get_field(data, key, field):
        return " . ".join(data[key][field])

    kw_extractor = yake.KeywordExtractor(top=3, stopwords=None)
    with open("./data/header.json", "r", encoding="utf-8") as fp:
        step_2_data = load(fp)

    h3s = []
    ps = []
    for key in step_2_data:
        h3s.append(get_field(step_2_data, key, "h3"))
        ps.append(get_field(step_2_data, key, "p"))
    h3s = " . ".join(h3s)
    ps = " . ".join(ps)

    keywords = kw_extractor.extract_keywords(" . ".join([h3s, ps]))
    write_file(
        dumps(
            [
                {"rank": i + 1, "keyword": packaged[0], "score": packaged[1]}
                for i, (packaged) in enumerate(keywords[::-1])
            ]
        ),
        "./data/keywords.json",
        "w",
        "utf-8",
    )


def step_4(**kwargs):
    """Aggregate and pipeline extracted data into Supabase (pending)"""
    aggregate("./data")
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(my_path, "./data/aggregated.json")
    supabase = Supabase()
    try:
        f = open(path)
        data = json.load(f)
        f.close()
        supabase.insert(SUPEBASE_TABLE,key_value= json.dumps(data))
    except:
        print("Something went wrong when opening the file")


def run():
    def get_params(run_selenium: str):
        if run_selenium in [True, "true", "t", "yes", "y"]:
            run_selenium = True
        elif run_selenium in [False, "false", "f", "no", "n"]:
            run_selenium = False
        else:
            raise Exception('Invalid parameter ("true" or "false" required)')

        if run_selenium:
            url = inquire()
        else:
            url = URL
        return dict(url=url, run_selenium=run_selenium)

    def run_step(fns: list, cmts: list, step: int, **params):
        print("Executing step {}: {}\n\n".format(index, cmts[index - 1]))
        fns[step - 1](**params)

    system("cls")

    fns = [step_1, step_2, step_3, step_4]

    cmts = [
        "Extract organic urls, local data and related questions into .json files",
        "Extracting h1, h2, h3, h4 and p in search pages",
        "Extract n-grams keywords into .json with descending ranking",
        "Aggregate and pipeline extracted data",
    ]
    if len(argv) > 1:
        index = int(argv[1])
        param = str(argv[2]) if len(argv) >= 3 else ""
        if index not in [1, 2, 3, 4]:
            raise Exception("Wrong parameter (must be int from 1 -> 4)")
        params = get_params(param) if index in [1, 2] else {}
        run_step(fns, cmts, index, **params)

    else:
        print("Go through every step")
        params = get_params(True)
        for index in range(1, len(fns) + 1):
            run_step(fns, cmts, index, **params)

    print("Finished execution\n")


if __name__ == "__main__":
    run()
