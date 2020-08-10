# Imse 0.0.1

# Standard modules
import sys
import time
import requests
from requests.compat import urljoin
# from requests.compat import urlparse
import http.client
from bs4 import BeautifulSoup
import math
from functools import reduce
import traceback
import operator
import pprint
import threading
from threading import Thread

def getVersion():
    version_major = 0
    version_minor = 0
    version_patch = 1
    return f'{version_major}.{version_minor}.{version_patch}'

def getName():
    name = "Imse"
    return name

def getBanner():
    return f'{getName()} Version {getVersion()}'

def getUsage():
    usage = "Usage: python spider.py <url> [<max-depth> <fetch-timeout> <only-unique> <use-colors> <number-of-threads>]"
    return usage

def checkArgs():
    if len(sys.argv) < 2:
        print (f'\n{getUsage()}\n')
        sys.exit(-1)

# Versions and arg check
print (f'{getBanner()} running on Python {sys.version}')
checkArgs()


# Project modules
import log
import util

    

class Result:
    threadId = None
    parentUrl = None
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
        link = f'{util.getPath(self.url)}{"?"if util.getQuery(self.url) else ""}{util.getQuery(self.url)}'
        if self.message is None:
            self.message = ""



        str = util.space(self.stepsFromRoot * 2) + f'{util.httpscrp(self.httpCode):<20}{self.length:7d} {self.fetchTime: 9.2f}s [d:{self.depth: 2d}][l:{len(self.subLinks): 4d}] [ {link} ]   {self.message}  <---  Linked from {self.parentUrl} [By thread {self.threadId}]'
        if self.httpCode == 200:
            return log.ansi_esc(log.Style.GREEN, str)
        elif self.httpCode == 404:
            return log.ansi_esc(log.Style.RED, str)
        elif self.httpCode > 499:
            return log.ansi_esc(log.bg(log.Style.RED), str)
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
        # Use set() to only return the unique links
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
        log.error(f'URL that caused this: {url}')
        result.message = str(e)

    # log.info( f'{result.httpStatus()} - {getPath(url)}{getQuery(url)}' )
    
    return result


class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        # print(type(self._target))
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self, *args):
        Thread.join(self, *args)
        return self._return



# Fetches the links in the doc provided by url recursivly and the optimal amount of threads depending on the machine
def threadedFetcher (baseUrl, depth, urls, stepsFromRoot, timeout=1, only_never_seen_urls=True, threadCount=2, parentUrl=None):
    log.note(f'Start-point {baseUrl}, max-depth {depth}, fetch-timeout {timeout}s, only unique {only_never_seen_urls}')
    log.note(f'Domain to be considered {log.ansi_esc(log.Style.GREEN, util.getHost(baseUrl))}')
    log.note(f'Using a least {threadCount} threads')

    r = urlTest(baseUrl, timeout)
    log.info( f'{r.httpStatus()} - {baseUrl}' )
    urls.add(baseUrl)
    r.depth = depth
    r.stepsFromRoot = stepsFromRoot
    r.isRoot = True
    r.parentUrl = parentUrl
    r.threadId = threadId=f'{threading.currentThread().getName()}'
    resultSet = set()
    resultSet.add(r)



    if threadCount < 2:
        log.info("Sequential execution...")
        resultSet = sequentialListFecther(baseUrl, r.subLinks, depth, resultSet, urls, 1, timeout, only_never_seen_urls)

    else:
        log.info("Parallel execution...")

        # Calculate taskSize, dependant on threadCount
        taskSize = math.floor(len(r.subLinks) / threadCount)
        taskList = list(util.chunks(list(r.subLinks), taskSize))

        # pprint.pprint(taskList)
        log.note(f'A total of {len(r.subLinks)} links in {baseUrl} will be handled')
        log.note(f'{len(taskList)} thread(s) will recursively handle a least {taskSize} urls')

        threads = []

        for subList in taskList:
            funcArgs = [baseUrl, subList, depth, resultSet, urls, stepsFromRoot, timeout, only_never_seen_urls]
            t = ThreadWithReturnValue(target=sequentialListFecther, args=funcArgs)
            t.start()
            threads.append(t)
            # log.info(f'Thread: {t.getName()} with id {t.ident} got {len(subList)} links to test')


        for t in threads:
            resultSet.update(t.join())


    return resultSet




def sequentialListFecther(baseUrl, linkList, depth, resultSet, urls, stepsFromRoot, timeout=1, only_never_seen_urls=True):
    log.blue (f'Got {len(linkList)} links to test')
    for link in linkList:
        if link is None:
            continue

        if link in urls and only_never_seen_urls:
            continue

        url = urljoin(baseUrl, link)

        if util.getHost(baseUrl) not in util.getHost(url) and baseUrl != url:
            # resultsList.append (f'[{getHost(baseUrl)} not in {getHost(url)}]')
            # log.warn(f'[{getHost(baseUrl)} not in {getHost(url)}]')
            continue

        # log.good(f'Fetching sublinks for {url}')
        resultSet = recursiveFetcher(url, depth - 1, resultSet, urls, 1, timeout, only_never_seen_urls, parentUrl=baseUrl, threadId=f'{threading.currentThread().getName()}')
    
    return resultSet




def recursiveFetcher(baseUrl, goDownSteps, resultsSet, urls, stepsFromRoot, timeout=1, only_never_seen_urls=True, parentUrl=None, threadId=None):

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
    r.parentUrl = parentUrl
    r.threadId = threadId
    # log.info(str(r))

    for link in r.subLinks:

        if link is None:
            continue

        if link in urls and only_never_seen_urls:
            continue

        url = urljoin(baseUrl, link)

        if util.getHost(baseUrl) not in util.getHost(url) and baseUrl != url:
            # resultsList.append (f'[{getHost(baseUrl)} not in {getHost(url)}]')
            log.warn(f'[{util.getHost(baseUrl)} not in {util.getHost(url)}]')
            continue

        try:

            # RECURSIVE CALL
            # log.info(f'Fetching sublinks at depth {goDownSteps} for {url}')
            resultsSet = recursiveFetcher(url, goDownSteps - 1, resultsSet, urls, stepsFromRoot + 1, timeout, parentUrl=baseUrl, threadId=threadId)
            
        except Exception as e:
            log.error(str(e))
            r.message = f'[Could not be fetched: {str(e)}]'

    resultsSet.add(r)

    return resultsSet



def httpCodeCountPrinter(results, code, style, operator):
    count = len(list(filter(lambda r: operator(r.httpCode, code), results)))
    if count > 0:
        log.info (log.ansi_esc(style or util.httpCodeColor(code), f' Number of {util.httpscrp(code)}: {count} ({count/len(results)*100:.1f}%) '))


def main():

    try:

        # Timer
        totalTime = time.time()

        # Args
        depth = log.parseIntArg(sys.argv, 2, 1)
        timeout = log.parseIntArg(sys.argv, 3, 1)
        only_unique = log.parseIntArg(sys.argv, 4, 1) == 1
        if log.parseIntArg(sys.argv, 5, 1) < 1: log.ansi_colors = False
        threads = log.parseIntArg(sys.argv, 6, 1)

        # Fetcher
        results = threadedFetcher( sys.argv[1], depth, set(), 0, timeout, only_unique, threads)

        # Results
        divider = util.charRepeat(60, "-")
        print (divider)
        resSort = list(results)
        resSort.sort(key=lambda x: x.depth, reverse=True)
        toShow = list (filter (lambda x: x.httpCode != 200, resSort))
        print ( "\n".join( list( map( lambda r: str( r ), toShow ) ) ) )
        print (divider)
        elapsed = time.time() - totalTime
        log.info (f'{len(resSort)}{" " if only_unique==False else " unique "}link(s) was tested in {elapsed:.2f} seconds ({elapsed/60:.1f}m):')
        average = sum(r.fetchTime for r in results) / len (results)
        log.info (f'Average fetch time {average:.2f} seconds')

        print (divider)
        for httpCode in range(600):
            httpCodeCountPrinter(results, httpCode, None, operator.eq)

        print (divider)

    except Exception as e:

        # Error handling
        print (str(e))
        traceback.print_exc()
        print (getUsage())
        exit(1)

# Entry point
if __name__ == '__main__':
    main()

