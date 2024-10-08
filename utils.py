from os import makedirs


def _path(name):
    return "./data/" + name


def outer(func):
    def inner(*args, **kwargs):
        fn_call = func(*args, **kwargs)
        print("Result of {}:\n{}\n\n\n\n".format(func.__name__, fn_call))
        return fn_call

    return inner


def write_file(content, filepath, mode="w", encoding=""):
    params = dict(file=filepath, mode=mode)
    if encoding:
        params.update(dict(encoding=encoding))
    with open(**params) as f:
        f.write(content)
    return content


def generate_url(question: str, area: str):
    def format(string: str):
        return string.lower().strip().replace(" ", "+")

    return (
        "https://www.google.com/search?" + f"q={format(question)}&near={format(area)}"
    )


def format_(string: str, get_text: bool = True):
    def pre_clean(string: str):
        f_pairs = [
            ("\n", ""),
            ("\u22c5", "|"),
            # ("\u203a", "/"),
        ]
        string = string.strip()
        for f_pair in f_pairs:
            string = string.replace(*f_pair)
        return string.split(" ")

    if string:
        if get_text:
            string = string.text
        f_pairs = ()
        string = " ".join(
            filter(
                lambda x: x != "",
                pre_clean(string),
            )
        )
        return string
    return ""


def deep_split(string: str):
    if string.find("·"):
        first = list(filter(lambda x: x != "", string.split("·")))
        later = list(map(lambda x: x.strip(), first))
        return later
    else:
        return [string]


def make_dir(filepath: str):
    try:
        makedirs(filepath)
        print(f"Created {filepath}")
    except FileExistsError:
        print(f"{filepath} already exists")
