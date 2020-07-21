from requests.compat import urlparse
import http.client
import log


def space(count):
    return charRepeat(count, " ")


def charRepeat(count, char):
    s = ""
    for _ in range(count):
        s = s + char

    return s


def chunks(lst, n):
    # Yield successive n-sized chunks from lst.
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def getHost(url):
    url_parsed = urlparse(url)
    host = "{uri.scheme}://{uri.netloc}/".format(uri=url_parsed)
    return str(host)


def getPath(url):
    url_parsed = urlparse(url)
    path = "{uri.path}".format(uri=url_parsed)
    if str(path) == "":
        return "/"
    return str(path)


def getQuery(url):
    url_parsed = urlparse(url)
    q = "{uri.query}".format(uri=url_parsed)
    return str(q)


def removeNewlineAndTrim(string):
    string = string.replace('\n', '')
    string = string.replace('\r', '')
    string = string.strip()
    return string


def httpReasonPhrase(code):
    return http.client.responses[code]


def httpscrp(code):
    try:
        return f'{code} {http.client.responses[code]}'
    except Exception as e:
        return f'{code} {str(e)}'

def httpCodeColor(code):
    if code == 404: return log.Style.RED
    if code > 99 and code < 200: return log.Style.CYAN
    if code > 199 and code < 300: return log.Style.GREEN
    if code > 299 and code < 400: return log.Style.BLUE
    if code > 399 and code < 500: return log.Style.YELLOW
    if code > 499 and code < 600: return log.bg(log.Style.RED)
    return log.Style.INVERTED

