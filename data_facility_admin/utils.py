def show_urls(urllist, depth=0):
    urls = []
    for entry in urllist:
        url = '%s%s' % ("  " * depth, entry.regex.pattern)
        urls.append(url)
        if hasattr(entry, 'url_patterns'):
            urls += (show_urls(entry.url_patterns, depth + 1))
    return urls
