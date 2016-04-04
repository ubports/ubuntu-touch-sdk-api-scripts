def remove_leading_and_trailing_slash(url):
    if url.startswith('/'):
        url = url[1:]
    if url.endswith('/'):
        url = url[:-1]
    return url


def remove_trailing_slash(url):
    if url.endswith('/'):
        url = url[:-1]
    return url
