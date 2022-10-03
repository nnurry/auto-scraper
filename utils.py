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
