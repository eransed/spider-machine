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

# OWN
import log

class Result:
    url = None
    httpCode = -1
    httpMessage = "__NONE__"
    length = -1
    fetchTime = -1
    message = "__NONE__"
    depth = -1
    subLinks = set()

    # def __hash__(self):
    #     return hash( tuple(self.url, self.httpCode, self.httpMessage, self.urlengthl, self.fetchTime, self.message, self.depth) )

    def __hash__(self):
        return hash(self.url)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented

        return self.url == other.url


    def __str__(self):
        return f'{self.httpCode: 4d} {http.client.responses[self.httpCode]:<20}{self.length: 7d} {self.fetchTime: 9.2f}s [d:{self.depth: 2d}][l:{len(self.subLinks): 4d}]\t[ {self.url} ] ( {self.message} )'


def getHost(url):
    url_parsed = urlparse(url)
    host = "{uri.scheme}://{uri.netloc}/".format(uri=url_parsed)
    return host


def removeNewlineAndTrim(string):
    string = string.replace('\n', '')
    string = string.replace('\r', '')
    string = string.strip()
    return string


# Takes a html-doc and returns a set of the included links
def linkSetParser(doc):

    try:
        parsed = BeautifulSoup(doc, 'html.parser')

        # Get any links if the url points at an html page
        linkList = parsed("a")
        imgList = parsed('img')
        scriptList = parsed('script')
        styleList = parsed('link')

        linkList = set(map (lambda l: l.get('href'), linkList))
        styleList = set(map (lambda l: l.get('href'), styleList))
        imgList = set(map (lambda l: l.get('src'), imgList))
        scriptList = set(map (lambda l: l.get('src'), scriptList))

        # Create one set with all links
        allLinks = set()
        allLinks.update(linkList)
        # allLinks.update(imgList)
        allLinks.update(scriptList)
        allLinks.update(styleList)
        
        # Filter the None value if present
        allLinks = set(filter(lambda n: n is not None, allLinks))

        return allLinks

    except Exception as e:
        log.error(str(e))
        return set()

def urlTest(url):

    result = Result()
    result.url = url

    try:
        # Fetch resource from url
        fetchTime = time.time()

        # THE TEST OF THE URL
        r = requests.get(url)

        # result.depth = goDownSteps
        result.fetchTime = time.time() - fetchTime
        result.httpCode = r.status_code
        result.subLinks = linkSetParser(r.content)
    except Exception as e:
        log.error(str(e))
        result.message = str(e)
    
    return result



# Fetches the links in the doc provided by url recursivly and the optimal amount of threads depending on the machine
def threadedFetcher (baseUrl, depth, urls):
    r = urlTest(baseUrl)
    urls.add(baseUrl)
    r.depth = depth
    resultSet = set()
    resultSet.add(r)
    for link in r.subLinks:
        if link is None:
            continue

        url = urljoin(baseUrl, link)

        if getHost(baseUrl) not in getHost(url) and baseUrl != url:
            # resultsList.append (f'[{getHost(baseUrl)} not in {getHost(url)}]')
            log.warn(f'[{getHost(baseUrl)} not in {getHost(url)}]')
            continue

        log.good(f'Fetching sublinks for {url}')
        resultSet = recursiveFetcher(url, depth - 1, resultSet, urls)

    return resultSet




def recursiveFetcher(baseUrl, goDownSteps, resultsSet, urls):

    # BASE CASE
    if goDownSteps < 1:
        log.info("Reached final depth")
        return resultsSet

    if baseUrl in urls:
        log.info(f'Already checked {baseUrl}')
        return resultsSet

    # THE TEST OF THE URL
    r = urlTest(baseUrl)

    urls.add(baseUrl)

    r.depth = goDownSteps

    for link in r.subLinks:

        if link is None:
            continue

        url = urljoin(baseUrl, link)

        if getHost(baseUrl) not in getHost(url) and baseUrl != url:
            # resultsList.append (f'[{getHost(baseUrl)} not in {getHost(url)}]')
            log.warn(f'[{getHost(baseUrl)} not in {getHost(url)}]')
            continue

        try:
            sys.stdout.flush()

            # RECURSIVE CALL
            log.info(f'Fetching sublinks at depth {goDownSteps} for {url}')
            resultsSet = recursiveFetcher(url, goDownSteps - 1, resultsSet, urls)
            
        except Exception as e:
            log.error(str(e))
            r.message = f'[Could not be fetched: {str(e)}]'

    resultsSet.add(r)

    return resultsSet



def main():

    try:
        totalTime = time.time()
        urls = set()
        results = threadedFetcher( sys.argv[1], int(sys.argv[2]), urls )
        # print (f'{len(results)} links was tested in {time.time() - totalTime:.2f} seconds:')
        print ("-----------------------------------------------------")
        print ( "\n".join( list( map( lambda r: str( r ), results ) ) ) )
        print ("-----------------------------------------------------")
        elapsed = time.time() - totalTime
        print (f'{len(results)} link(s) was tested in {elapsed:.2f} seconds ({elapsed/60:.1f}m):')

        average = sum(r.fetchTime for r in results) / len (results)
        print (f'{len(urls)} unique link(s)')
        print (f'Average fetch time {average:.2f} seconds')

    except Exception as e:
        print (str(e))
        print ("Usage: python spider.py <url> <max-depth>")
        exit(1)


if __name__ == '__main__':
    main()

