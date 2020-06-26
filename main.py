
# > pip list:
# Package        Version
# -------------- ---------
# beautifulsoup4 4.9.1
# certifi        2020.6.20
# chardet        3.0.4
# idna           2.9
# pip            20.1.1
# requests       2.24.0
# setuptools     41.2.0
# soupsieve      2.0.1
# urllib3        1.25.9

# Python meta data
# print (f'Python version {sys.version}')
# print (f'__doc__ = {__doc__}')
# print (f'__file__ = {__file__}')
# print (f'__name__ = {__name__}')
# print (f'__package__ = {__package__}')


import sys
import time
import requests
from requests.compat import urljoin
import http.client
from bs4 import BeautifulSoup

# print ("world")

# take arg -urlLinks for printing one url per newline?
# <img class="someClass" src="/relative/path/file.png" alt="text-if-not-found">
# <script src="/script.js"></script>

def recursiveFetcher(baseUrl, goDownSteps):
    if goDownSteps < 0:
        print (f'Reached final level')
        return None
    else:
        # Fetch resource from url
        fetchTimeBase = time.time()
        r = requests.get(baseUrl)
        fetchTimeBase = time.time() - fetchTimeBase
        baseStatus = r.status_code
        baseStatusMsg = http.client.responses[baseStatus]

        # Parse the document
        pageTitle = ""
        try:
            parsed = BeautifulSoup(r.content, 'html.parser')
            pageTitle = parsed.title.string
        except:
            pass

        print (f'Base url: "{baseUrl}" {baseStatus} {baseStatusMsg} "{pageTitle}" Fetch time: {fetchTimeBase:.2f} seconds')

        # Find and fetch all links in document, depth first

        linkList = parsed("a")
        print (linkList)

        for l in parsed("a"):

            try:
                tag = l.string
                # print (type(tag))
                tag = tag.replace('\n', '')
                tag = tag.replace('\r', '')
                tag = tag.strip()
            except:
                pass

            link = l.get('href')
            url = urljoin(baseUrl, link)

            if url not is None:

                if baseUrl not in url:
                    print (f'[Skipping {url}]')
                    continue
                try:
                    fetchTime = time.time()
                    res = recursiveFetcher(url, goDownSteps - 1)
                    fetchTime = time.time() - fetchTime

                    code = res.status_code
                    msg = http.client.responses[code]
                    print (f'{code} {msg} {len(res.content): 9d} {fetchTime: 9.2f}s\t\t[ {link} ] ( {tag} )')
                except:
                    print (f'[{link} could not be fetched]')

            else:
                print (f'Error joining url and path')
        return r

def simpleTest(baseUrl):
    print (f'Testing urls in {baseUrl}')

    start_time = time.time()

    # Fetch resource from url

    r = requests.get(baseUrl)
    baseStatus = r.status_code
    baseStatusMsg = http.client.responses[baseStatus]

    # Parse the document
    pageTitle = ""
    try:
        parsed = BeautifulSoup(r.content, 'html.parser')
        pageTitle = parsed.title.string
    except:
        pass

    print (f'Base url: "{baseUrl}" {baseStatus} {baseStatusMsg} {pageTitle}')

    linkList = parsed("a")
    imgList = parsed('img')
    scriptList = parsed('script')
    styleList = parsed('link')


    print("\n")

    print (f'hrefs: {len(linkList)}')
    print (f'imgs: {len(imgList)}')
    print (f'styles: {len(styleList)}')
    print (f'scripts: {len(scriptList)}')

    print ("\n\n\n")

    linkList = set(map (lambda l: l.get('href'), linkList))
    imgList = set(map (lambda l: l.get('src'), imgList))
    scriptList = set(map (lambda l: l.get('src'), scriptList))
    styleList = set(map (lambda l: l.get('href'), styleList))


    print (f'hrefs (unique): {len(linkList)}')
    print (f'imgs (unique): {len(imgList)}')
    print (f'styles (unique): {len(styleList)}')
    print (f'scripts (unique): {len(scriptList)}')



    print ("\n\n\n")

    # Create one set with all links
    allLinks = set()
    allLinks.update(linkList)
    allLinks.update(imgList)
    allLinks.update(scriptList)
    allLinks.update(styleList)
    
    # Filter the None value if present
    allLinks = list(set(filter(lambda n: n is not None, allLinks)))


    loopStart = time.time()

    print (f'Testing {len(allLinks)} links:\n')
    print ("-----------------------------------------------------")
    sys.stdout.flush()
    for l in allLinks:
        if l is None:
            continue

        tag = "map"
        # try:
        #     tag = l.string
        #     # print (type(tag))
        #     tag = tag.replace('\n', '')
        #     tag = tag.replace('\r', '')
        #     tag = tag.strip()
        # except:
        #     pass

        # link = l.get('href')
        link = l
        url = urljoin(baseUrl, link)
        if baseUrl not in url:
            print (f'[Skipping {url}]')
            continue

        try:

            fetchTime = time.time()
            res = requests.get(url)
            fetchTime = time.time() - fetchTime

            code = res.status_code
            msg = http.client.responses[code]
            print (f'{code} {msg} {len(res.content): 9d} {fetchTime: 9.2f}s\t\t[ {link} ] ( {tag} )')

        except:
            print (f'[{link} could not be fetched]')
        sys.stdout.flush()

    

    print ("-----------------------------------------------------")

    print(f'\nLoop ended in {time.time() - loopStart:.2f} seconds')
    print (f'\n\nTests performed in a total of {time.time() - start_time:.2f} seconds')
    print ("\n\n\n")

print ("Call to simpleTest...")
simpleTest(sys.argv[1])



