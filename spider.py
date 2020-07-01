# STD
import sys
import time
import requests
from requests.compat import urljoin
from requests.compat import urlparse
import http.client
from bs4 import BeautifulSoup
import math
from functools import reduce
import traceback

# OWN
import log

def space(count):
    return charRepet(count, " ")

def charRepet(count, char):
    s = ""
    for _ in range(count):
        s = s + char

    return s


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


class Result:
    url = None
    httpCode = -1
    httpMessage = "__NONE__"
    length = -1
    fetchTime = -1
    message = None
    depth = -1
    subLinks = set()
    stepsFromRoot = -1
    isRoot = False

    def httpStatus(self):
        try:
            return f'{self.httpCode} {http.client.responses[self.httpCode]}'
        except Exception as e:
            log.error(f'{str(e)}')
            return f'{self.httpCode} {str(e)}'

    def __hash__(self):
        return hash(self.url)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented

        return self.url == other.url

    def __str__(self):
        # link = getHost(self.url) if self.isRoot else getPath(self.url) + getQuery(self.url)
        link = getPath(self.url) + getQuery(self.url)
        if self.message is None:
            self.message = ""

        str = space(self.stepsFromRoot * 2) + f'{self.httpCode:3d} {http.client.responses[self.httpCode]:<20}{self.length:7d} {self.fetchTime: 9.2f}s [d:{self.depth: 2d}][l:{len(self.subLinks): 4d}] [ {link} ]   {self.message}'
        if self.httpCode == 200:
            return log.ansi_esc(log.Style.GREEN, str)
        elif self.httpCode > 499 or self.httpCode == 404:
            return log.ansi_esc(log.Style.RED, str)
        else:
            return log.ansi_esc(log.Style.YELLOW, str)


# Takes a html-doc and returns a set of the included links
def linkSetParser(soup):
    try:
        # Get any links if the url points at an html page
        linkList = soup("a")
        imgList = soup('img')
        scriptList = soup('script')
        styleList = soup('link')

        linkList = set(map (lambda l: l.get('href'), linkList))
        styleList = set(map (lambda l: l.get('href'), styleList))
        imgList = set(map (lambda l: l.get('src'), imgList))
        scriptList = set(map (lambda l: l.get('src'), scriptList))

        # Create one set with all links
        allLinks = set()
        allLinks.update(linkList)
        allLinks.update(imgList)
        allLinks.update(scriptList)
        allLinks.update(styleList)
        
        # Filter the None value if present
        allLinks = set(filter(lambda n: n is not None, allLinks))

        return allLinks

    except Exception as e:
        log.error(str(e))
        return set()

def urlTest(url, _timeout=1):

    result = Result()
    result.url = url

    try:
        # Fetch resource from url
        fetchTime = time.time()

        # THE TEST OF THE URL
        r = requests.get(url, timeout = _timeout)

        # result.depth = goDownSteps
        result.fetchTime = time.time() - fetchTime
        result.httpCode = r.status_code

        # log.good(r.headers['Content-Type'])

        if "html" in r.headers['Content-Type']:

            soup = BeautifulSoup(r.content, 'html.parser')
            result.subLinks = linkSetParser(soup)

            try:
                result.message = soup.title.text
            except Exception as e:
                result.message = str(e)

        else:
            log.warn(f'Skipping img...')

        result.length = len(r.content)
    except Exception as e:
        log.error(str(e))
        result.message = str(e)

    # log.info( f'{result.httpStatus()} - {getPath(url)}{getQuery(url)}' )
    
    return result



# Fetches the links in the doc provided by url recursivly and the optimal amount of threads depending on the machine
def threadedFetcher (baseUrl, depth, urls, stepsFromRoot, timeout=1, only_never_seen_urls=True):
    log.note(f'Start-point {baseUrl}, max-depth {depth}, fetch-timeout {timeout}s, only unique {only_never_seen_urls}')
    log.note(f'Domain to be considered {log.ansi_esc(log.Style.GREEN, getHost(baseUrl))}')

    r = urlTest(baseUrl, timeout)
    log.info( f'{r.httpStatus()} - {baseUrl}' )
    urls.add(baseUrl)
    r.depth = depth
    r.stepsFromRoot = stepsFromRoot
    r.isRoot = True
    resultSet = set()
    resultSet.add(r)
    for link in r.subLinks:
        if link is None:
            continue

        if link in urls and only_never_seen_urls:
            continue

        url = urljoin(baseUrl, link)

        if getHost(baseUrl) not in getHost(url) and baseUrl != url:
            # resultsList.append (f'[{getHost(baseUrl)} not in {getHost(url)}]')
            # log.warn(f'[{getHost(baseUrl)} not in {getHost(url)}]')
            continue

        # log.good(f'Fetching sublinks for {url}')
        resultSet = recursiveFetcher(url, depth - 1, resultSet, urls, 1, timeout, only_never_seen_urls)

    return resultSet




def recursiveFetcher(baseUrl, goDownSteps, resultsSet, urls, stepsFromRoot, timeout=1, only_never_seen_urls=True):

    # BASE CASE
    if goDownSteps < 1:
        # log.info("Reached final depth")
        return resultsSet

    if baseUrl in urls and only_never_seen_urls:
        # log.info(f'Already checked {baseUrl}')
        return resultsSet

    # THE TEST OF THE URL
    r = urlTest(baseUrl, timeout)

    urls.add(baseUrl)

    r.stepsFromRoot = stepsFromRoot

    r.depth = goDownSteps

    for link in r.subLinks:

        if link is None:
            continue

        if link in urls and only_never_seen_urls:
            continue

        url = urljoin(baseUrl, link)

        if getHost(baseUrl) not in getHost(url) and baseUrl != url:
            # resultsList.append (f'[{getHost(baseUrl)} not in {getHost(url)}]')
            log.warn(f'[{getHost(baseUrl)} not in {getHost(url)}]')
            continue

        try:

            # RECURSIVE CALL
            # log.info(f'Fetching sublinks at depth {goDownSteps} for {url}')
            resultsSet = recursiveFetcher(url, goDownSteps - 1, resultsSet, urls, stepsFromRoot + 1, timeout)
            
        except Exception as e:
            log.error(str(e))
            r.message = f'[Could not be fetched: {str(e)}]'

    resultsSet.add(r)

    return resultsSet



def main():
    try:

        # Timer
        totalTime = time.time()

        # Args
        depth = log.parseIntArg(sys.argv, 2, 1)
        timeout = log.parseIntArg(sys.argv, 3, 1)
        only_unique = log.parseIntArg(sys.argv, 4, 1) == 1
        if log.parseIntArg(sys.argv, 5, 1) < 1: log.ansi_colors = False

        # Fetcher
        results = threadedFetcher( sys.argv[1], depth, set(), 0, timeout, only_unique)

        # Results
        print ("-----------------------------------------------------")
        resSort = list(results)
        resSort.sort(key=lambda x: x.depth, reverse=True)
        print ( "\n".join( list( map( lambda r: str( r ), resSort ) ) ) )
        print ("-----------------------------------------------------")
        elapsed = time.time() - totalTime
        log.info (f'{len(resSort)}{" " if only_unique==False else " unique "}link(s) was tested in {elapsed:.2f} seconds ({elapsed/60:.1f}m):')
        average = sum(r.fetchTime for r in results) / len (results)
        log.info (f'Average fetch time {average:.2f} seconds')

    except Exception as e:

        # Error handling
        print (str(e))
        traceback.print_exc()
        print ("Usage: python spider.py <url> <max-depth> <fetch-timeout> <only-unique> <use-colors>")
        exit(1)

# Entry point
if __name__ == '__main__':
    log.blue (f'Python {sys.version}')
    main()

