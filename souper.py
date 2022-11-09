from json import dumps, load
from operator import index
from bs4 import BeautifulSoup, Tag
from utils import write_file, format_, deep_split, generate_url
from functools import reduce


def inquire(search_key, loccation):
    if not search_key and not loccation:
        question = input("What is your query? ")
        if not question:
            raise Exception("Please don't leave the query empty, try again")
        area = input("Where do you want to search? ")
        if not area:
            raise Exception("Please don't leave the location empty, try again")

        url = generate_url(question, area)
        return url
    else:
        url = generate_url(question=search_key, area=loccation)
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
    local_class = [
        "M8OgIe",
        "Qq3Lb"
    ]

    organic_body = content.find("div", class_="s6JM6d")
    for class_ in local_class:
        local_body = content.find("div", class_=class_)
        if local_body is not None:
            break

    return organic_body, local_body


def extract_organic(organic_body: Tag):
    organic = organic_body.find("div", id="search")
    related = organic_body.find("div", id="botstuff")
    organic_results = []
    related_results = []

    for organic_ in organic.find_all("div", class_="MjjYud"):
        if organic_.cite and organic_.h3:
            organic_result = {
                "title": format_(organic_.h3),
                "link": organic_.cite.text.split(" \u203a ")[0],
            }
            organic_results.append(organic_result)

    organic_results = [
        {"position": index + 1, **organic_result}
        for index, organic_result in enumerate(organic_results)
    ]

    for related_ in related.find_all("div", jsname="Cpkphb"):
        question = format_(related_.span)
        answer_title = format_(related_.find("div", attrs={"data-tts": "answers"}))
        answer_body = format_(related_.find("div", role="heading"))
        # NOTE: in answer_body there might be 2 div with role = heading -> handle this later
        article_link = related_.find("a", href=True)["href"]
        article_link = format_(article_link, False)
        article_header = format_(related_.find("h3"))
        related_result = {
            "question": question,
            "snippet": " - ".join([answer_title, answer_body])
            if answer_title
            else answer_body,
            "title": article_header,
            "link": article_link,
        }
        related_results.append(related_result)

    return organic_results, related_results


def extract_local(local_body: Tag):
    def filter_website(url: str):
        return (
            True
            if ("http" in url or "https" in url) and ("google" not in url)
            else False
        )

    def convert_to_base_10(num_string: str):
        def get_base_10(times: int):
            return f'1{times * "0"}'

        kws = ["K", "M", "B"]
        for i, kw in enumerate(kws):
            if kw in num_string:
                num_string += get_base_10((i + 1) * 3)
                kws = num_string.split(kw)
                break

        if len(kws) == 2:
            kws = list(map(lambda x: float(x), kws))
            num_string = reduce(lambda acc, ele: acc * ele, kws, 1)

        return int(num_string)

    def get_local_data(local_ad):
        local_data = []
        for local_ in local_ad.contents:
            local_content = get_local_content(local_)
            if local_content:
                local_data = [*local_data, local_content]
        return local_data

    def get_local_content(local_ad_content):
        local_ad_content = deep_split(format_(local_ad_content))
        local_ad_content = list(filter(lambda x: '"' not in x, local_ad_content))
        return local_ad_content

    def get_local_dict(local_ad):
        def process_contact(data):
            output = {}
            indexes = []
            for i, contact_ in enumerate(data):
                if str.isdigit(
                    contact_.replace("+", "").replace("-", " ").replace(" ", "")
                ):
                    output["phone"] = data[i].replace("-", " ").replace(" ", "")
                    indexes.append(i)
                if "in business" in contact_:
                    output["years_in_business"] = data[i]
                    indexes.append(i)

            for index, _ in enumerate(data):
                if index not in indexes:
                    output["service_area"] = data[index]
            return output

        def process_schedule(data: list):
            output = {"hours": ", ".join(data)}
            return output

        def process_service_type(data: list):
            output = {"service_type": ", ".join(data)}
            return output

        def check_deep_type(data):
            for phrase in data:
                if str.isdigit(
                    phrase.replace("+", "").replace("-", " ").replace(" ", "")
                ):
                    return "contact"
                if "in business" in phrase:
                    return "contact"
                if "," in phrase:
                    return "contact"
                if "Close" in phrase:
                    return "schedule"
                if "Open" in phrase:
                    return "schedule"
                if "on-site" in phrase.lower() or "online" in phrase.lower():
                    return "service_type"
                return "miscel"

        def generate_dict(local_data):
            itr = 0
            data = {}
            processed = []
            while len(local_data) > 0:
                if itr == 0:
                    title_line = local_data.pop(0)
                    title_data = {"title": title_line[0]}
                    data.update(title_data)
                    processed.append("title")
                elif itr == 1:
                    popular_line = local_data.pop(0)
                    popular_data = {
                        "rating": float(popular_line[0][:3].replace(",", ".")),
                        "rating_count": convert_to_base_10(popular_line[0][4:-1]),
                        "type": popular_line[-1],
                    }
                    data.update(popular_data)
                    processed.append("popular")
                else:
                    line_data = local_data.pop(0)
                    line_type = check_deep_type(line_data)
                    if line_type == "contact":
                        data.update(process_contact(line_data))
                        processed.append("contact")
                    if line_type == "schedule":
                        data.update(process_schedule(line_data))
                        processed.append("schedule")
                    if line_type == "service_type":
                        data.update(process_service_type(line_data))
                        processed.append("service_type")
                    if line_type == "miscel":
                        if "contact" not in processed:
                            data.update({"service_area": ", ".join(line_data)})
                            processed.append("contact")
                        else:
                            data.update(dict(miscel=line_data))
                            processed.append("miscel")
                itr += 1
            return data

        schema = set(
            [
                "title",
                "rating",
                "rating_count",
                "type",
                "phone",
                "years_in_business",
                "service_area",
                "service_type",
                "hours",
                "badge",
            ]
        )
        local_data = get_local_data(local_ad)
        local_dict = generate_dict(local_data)
        missing_keys = schema.difference(set(local_dict.keys()))
        for missing_key in missing_keys:
            local_dict[missing_key] = None
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
