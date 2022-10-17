from json import dumps, load
from bs4 import BeautifulSoup, Tag
from utils import write_file, format_, deep_split, generate_url


def inquire():
    question = input("What is your query? ")
    if not question:
        raise Exception("Please don't leave the query empty, try again")
    area = input("Where do you want to search? ")
    if not area:
        raise Exception("Please don't leave the location empty, try again")

    url = generate_url(question, area)
    return url


def read_and_make_soup(params: dict):
    with open(**params) as fp:
        soup = BeautifulSoup(fp, features="html.parser")
    return soup


def aggregate(directory_path: str, destination: str = "./data/aggregated.json"):
    def open_multiple_files(directory_path, filenames):
        return [
            open(f"{directory_path}/{filename}.json", **PARAMS)
            for filename in filenames
        ]

    def close_multiple_files(files):
        for file in files:
            file.close()

    PARAMS = dict(mode="r", encoding="utf-8")
    child_files = [
        "organic_links",
        "local_results",
        "local_ads",
        "keywords",
        "questions",
    ]

    files = open_multiple_files(directory_path, child_files)
    data = {field: {} for field in child_files}
    for i, file in enumerate(files):
        data[child_files[i]] = load(file)
    write_file(dumps(data), destination, encoding=PARAMS["encoding"])
    close_multiple_files(files)
    return data


def get_content(main_div: Tag):
    main_res = main_div.find(class_="GyAeWb")
    if main_res:
        return main_res
    main_res = main_div.find(id="rcnt")
    if main_res:
        return main_res
    return None


def extract_content(soup: BeautifulSoup):
    html = soup.html
    body = html.body
    main = body.find(name="div", class_="main")
    return get_content(main)


def extract_segment(content: Tag):
    organic_body = content.find("div", class_="s6JM6d")
    local_body = content.find("div", class_="M8OgIe")
    return organic_body, local_body


def extract_organic(organic_body: Tag):
    organic = organic_body.find("div", id="search")
    related = organic_body.find("div", id="botstuff")
    organic_results = []
    related_results = []

    for organic_result in organic.find_all("div", class_="MjjYud"):
        if organic_result.cite and organic_result.h3:
            organic_results.append(
                {
                    "title": format_(organic_result.h3),
                    "link": format_(organic_result.cite),
                }
            )

    organic_results = [
        {"position": index + 1, **organic_result}
        for index, organic_result in enumerate(organic_results)
    ]

    for related_result in related.find_all("div", jsname="Cpkphb"):
        question = format_(related_result.span)
        answer_title = format_(
            related_result.find("div", attrs={"data-tts": "answers"})
        )
        answer_body = format_(related_result.find("div", role="heading"))
        # NOTE: in answer_body there might be 2 div with role = heading -> handle this later
        article_link = format_(related_result.find("a", href=True)["href"], False)
        article_header = format_(related_result.find("h3"))
        related_results.append(
            {
                "question": question,
                "snippet": " - ".join([answer_title, answer_body])
                if answer_title
                else answer_body,
                "title": article_header,
                "link": article_link,
            }
        )

    return organic_results, related_results


def extract_local(local_body: Tag):
    def filter_website(url: str):
        return (
            True
            if ("http" in url or "https" in url) and ("google" not in url)
            else False
        )

    def get_local_data(local_ad):
        local_data = []
        for local_ in local_ad.contents:
            local_ = deep_split(format_(local_))
            local_data = [*local_data, *local_]
        return local_data

    def get_local_dict(local_ad):
        local_data = get_local_data(local_ad)
        service_area = local_data.pop(4) if len(local_data) > 7 else None
        local_dict = {
            "title": local_data[0],
            "rating": local_data[1][:3],
            "rating_count": local_data[1][4:-1],
            "type": local_data[2],
            "years_in_business": local_data[3],
            "phone": local_data[4],
            "hours": local_data[5],
            "service_type": local_data[6],
            "service_area": service_area,
        }
        return local_dict

    local_results = local_body.find_all("div", class_="VkpGBb")

    more_location_link = local_body.find("g-more-link")
    more_location_link = more_location_link.find("a", href=True)["href"]

    local_dicts = {"more_location_link": more_location_link, "places": []}

    for i, local_result in enumerate(local_results):

        place_id = local_result.find(attrs={"data-cid": True})
        place_id = "" if not place_id else place_id["data-cid"]

        local_websites = list(
            map(lambda url: url["href"], local_result.find_all("a", href=True))
        )

        local_websites = list(filter(filter_website, local_websites))
        local_website = "" if not len(local_websites) else local_websites[0]

        local_ad = local_result.find("div", class_="rllt__details")
        local_dict = {
            "position": i + 1,
            "place_id": place_id,
            "website": local_website,
            **get_local_dict(local_ad),
        }

        local_dicts["places"].append(local_dict)

    # TODO: MISSING badge
    return local_dicts
