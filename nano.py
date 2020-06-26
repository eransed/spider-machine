
import sys
import time
import requests
from requests.compat import urljoin
from requests.compat import urlparse
import http.client
from bs4 import BeautifulSoup
# from urllib.parse import urlparse

class Result:
    url = None
    httpCode = -1
    httpMessage = "__NONE__"
    length = -1
    fetchTime = -1
    message = "__NONE__"
    depth = -1

    def __str__(self):
        return f'{self.httpCode: 4d} {http.client.responses[self.httpCode]:<3}\t\t\t{self.length: 7d} {self.fetchTime: 9.2f}s [d:{self.depth: 2d}]\t[ {self.url} ] ( {self.message} )'



def getHost(url):
    url_parsed = urlparse(url)
    host = "{uri.scheme}://{uri.netloc}/".format(uri=url_parsed)
    return host

def removeNewlineAndTrim(string):
    string = string.replace('\n', '')
    string = string.replace('\r', '')
    string = string.strip()
    return string

# (url, depth, results) ?
def recursiveFetcher(baseUrl, goDownSteps, resultsList):

    sys.stdout.flush()

    # BASE CASE
    if goDownSteps < 1:
        # print (f'Reached final level')
        return resultsList

    # Fetch resource from url
    fetchTime = time.time()

    # THE TEST OF THE URL
    r = requests.get(baseUrl)
    result = Result()
    result.fetchTime = time.time() - fetchTime
    result.httpCode = r.status_code

    # Parse the document
    pageTitle = "__ERROR__"
    length = -1

    try:
        parsed = BeautifulSoup(r.content, 'html.parser')

        if parsed is not None:
            pageTitle = parsed.title.string

            if pageTitle is not None:
                pageTitle = removeNewlineAndTrim(pageTitle)
            else:
                pageTitle = "__NO_TITLE__"
        else:
            pageTitle = "Could not html-parse the resource"
        
        try:
            result.length = len(r.content)

        except:
            pass

        result.message = pageTitle
        # THE RESULT IS ADDED TO THE RESULTS-LIST
        resultsList.append(result)

    except Exception as e:
        # pageTitle = repr(e)
        # pageTitle = str(e)
        result.message = str(e)
        resultsList.append(result)
        return resultsList

    # Get any links if the url points at an html page
    linkList = parsed("a")
    imgList = parsed('img')
    scriptList = parsed('script')
    styleList = parsed('link')

    linkList = set(map (lambda l: l.get('href'), linkList))
    imgList = set(map (lambda l: l.get('src'), imgList))
    scriptList = set(map (lambda l: l.get('src'), scriptList))
    styleList = set(map (lambda l: l.get('href'), styleList))

    # Create one set with all links
    allLinks = set()
    allLinks.update(linkList)
    # allLinks.update(imgList)
    # allLinks.update(scriptList)
    # allLinks.update(styleList)
    
    # Filter the None value if present
    allLinks = list(set(filter(lambda n: n is not None, allLinks)))

    for link in allLinks:

        if link is None:
            continue

        url = urljoin(baseUrl, link)

        if getHost(baseUrl) not in getHost(url):
            # resultsList.append (f'[{getHost(baseUrl)} not in {getHost(url)}]')
            continue

        try:
            # RECURSIVE CALL
            resultsList = recursiveFetcher(url, goDownSteps - 1, resultsList)

        except Exception as e:
            resultsList.append (f'[{url} could not be fetched: {str(e)}]')

    return resultsList


totalTime = time.time()
results = recursiveFetcher(sys.argv[1], int(sys.argv[2]), [] )
print (f'{len(results)} links was tested in {time.time() - totalTime:.2f} seconds:')
print ("-----------------------------------------------------")
print ( "\n".join( list(map(lambda r: str(r), results ) ) ) )
print ("-----------------------------------------------------")
