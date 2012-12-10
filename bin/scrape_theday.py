"""Scrape theday.com for dad's articles (christmas present)"""
import requests
import BeautifulSoup
import gevent.pool
import gevent.monkey
import pickle
import os

gevent.monkey.patch_all(thread=False)


def get_article(url):
    print 'starting'
    resp2 = requests.get(url)
    soup2 = BeautifulSoup.BeautifulSoup(resp2.content)
    _res2 = soup2.findAll(id='readColumn')
    assert len(_res2) == 1
    _res2 = _res2[0]
    title = _res2.find('h1').prettify().strip()
    datestamps = [x.prettify().strip()
                  for x in _res2.findAll(attrs={'class': 'dateStamps'})]
    story = [x.prettify().strip()
             for x in _res2.findAll(attrs={'class': 'fullStory'})]
    assert len(story) == 1
    story = story[0]
    return (title, datestamps, story)


def get_article_links(url):
    resp = requests.get(url)

    soup = BeautifulSoup.BeautifulSoup(resp.content)
    _res = soup.findAll(id='searchresults')
    assert len(_res) == 1
    _res = _res[0]
    article_links = [_section.findAll('a') for _section in _res.findAll('h5')]
    assert all(len(x) == 1 for x in article_links)
    article_links = [y['href'] for x in article_links for y in x]
    return article_links


def search(category):
    """Search for dad's articles by category.  TheDay has terrible search
    capabilities"""
    urls = []
    pager_index = 0
    while True:
        url = ("http://www.theday.com/apps/pbcs.dll/search"
               "?Category=SEARCH&q=jon%20gaudio"
               "&SearchCategory={category}%25"
               "&Kat={category}%25&Simple=0"
               "&Max=100&Start={pager_index}").format(
                   category=category,
                   pager_index=pager_index)
        _urls = get_article_links(url)
        if not _urls:
            print "Not more than %s articles for category %s" % (
                pager_index, category)
            break
        pager_index += 25
        urls.extend(_urls)
    return urls


def scrape(fp='./dads_articles.pickle', fp2='./dads_urls'):
    if not os.path.exists(fp2):
        with open(fp2, 'w') as urlswriter:
            print 'getting article links'
            urls = []
            for category in ('DAYARC', 'ENT'):
                urls.extend(search(category))
            pickle.dump(urls, urlswriter)
    else:
        urls = pickle.load(open(fp2, 'r'))
    if not os.path.exists(fp):
        with open(fp, 'w') as writer:
            print 'async getting data from articles'
            pool = gevent.pool.Pool(20)
            jobs = [pool.spawn(get_article, url)
                    for url in urls]  # TODO
            gevent.joinall(jobs, raise_error=True)
            pickle.dump([j.get() for j in jobs], writer)
    else:
        articles = pickle.load(open(fp, 'r'))
        for title, datestamps, content in articles:
            pass
        import IPython ; IPython.embed()


if __name__ == '__main__':
    scrape()
