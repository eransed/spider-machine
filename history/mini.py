
import sys
import time
import requests
from requests.compat import urljoin
import http.client
from bs4 import BeautifulSoup

def recursiveFetcher(baseUrl, goDownSteps, resultsList):
    if goDownSteps < 0:
        print (f'Reached final level')
        return resultsList
    else:
        pass
    # print (f'Testing urls in {baseUrl}')

    start_time = time.time()

    # Fetch resource from url
    fetchTime = time.time()
    r = requests.get(baseUrl)
    fetchTime = time.time() - fetchTime
    baseStatus = r.status_code
    baseStatusMsg = http.client.responses[baseStatus]

    # Parse the document
    pageTitle = "__ERROR__"
    try:
        parsed = BeautifulSoup(r.content, 'html.parser')
        pageTitle = parsed.title.string
    except Exception as e:
        pageTitle = repr(e)
        # pageTitle = str(e)

    # print (f'Base url: "{baseUrl}" {baseStatus} {baseStatusMsg} {pageTitle}')
    # resultsList.append (f'Base url: "{baseUrl}" {baseStatus} {baseStatusMsg} {pageTitle}')

    length = -1
    try:
        length = len(r.content)
    except:
        pass

    resultsList.append (f'{baseStatus} {baseStatusMsg} {len(r.content): 9d} {fetchTime: 9.2f}s\t\t[ {baseUrl} ] ( {pageTitle} )')

    linkList = parsed("a")
    imgList = parsed('img')
    scriptList = parsed('script')
    styleList = parsed('link')

    # print (f'hrefs: {len(linkList)}')
    # print (f'imgs: {len(imgList)}')
    # print (f'styles: {len(styleList)}')
    # print (f'scripts: {len(scriptList)}')

    linkList = set(map (lambda l: l.get('href'), linkList))
    imgList = set(map (lambda l: l.get('src'), imgList))
    scriptList = set(map (lambda l: l.get('src'), scriptList))
    styleList = set(map (lambda l: l.get('href'), styleList))


    # print (f'hrefs (unique): {len(linkList)}')
    # print (f'imgs (unique): {len(imgList)}')
    # print (f'styles (unique): {len(styleList)}')
    # print (f'scripts (unique): {len(scriptList)}')



    # print ("\n\n\n")

    # Create one set with all links
    allLinks = set()
    allLinks.update(linkList)
    # allLinks.update(imgList)
    # allLinks.update(scriptList)
    # allLinks.update(styleList)
    
    # Filter the None value if present
    allLinks = list(set(filter(lambda n: n is not None, allLinks)))

    return set(allLinks)

    loopStart = time.time()

    # print (f'Testing {len(allLinks)} links:\n')
    # print ("-----------------------------------------------------")
    sys.stdout.flush()
    for link in allLinks:
        if link is None:
            continue

        tag = "map-rec"
        url = urljoin(baseUrl, link)
        if baseUrl not in url:
            resultsList.append (f'[Skipping {url}]')
            continue
        try:

            fetchTime = time.time()
            resultsList = recursiveFetcher(url, goDownSteps - 1, resultsList)
            fetchTime = time.time() - fetchTime

            # code = res.status_code
            # msg = http.client.responses[code]
            # # print (f'{code} {msg} {len(res.content): 9d} {fetchTime: 9.2f}s\t\t[ {link} ] ( {tag} )')
            # resultsList.append (f'{code} {msg} {len(res.content): 9d} {fetchTime: 9.2f}s\t\t[ {link} ] ( {tag} )')

        except:
            # print (f'[{link} could not be fetched]')
            resultsList.append (f'[{link} could not be fetched]')
        # sys.stdout.flush()
    
    return resultsList

    

    # print ("-----------------------------------------------------")

    # print(f'\nLoop ended in {time.time() - loopStart:.2f} seconds')
    # print (f'\n\nTests performed in a total of {time.time() - start_time:.2f} seconds')
    # print ("\n\n\n")


results = recursiveFetcher(sys.argv[1], 2, {} )
print (f'{len(results)} links was tested:')
print ("-----------------------------------------------------")
print ( "\n".join( results ) )
print ("-----------------------------------------------------")

x=30
print ("\n".join(list(map(lambda x: str(x), [1, f'this is a test {x}', 3, 4]))))

test = {"1", "två", 3}
print (test)

test.add(4)
print (test)

test.add("1")
print (test)

test.add(5)
print (test)

test.add("två")
print (test)
