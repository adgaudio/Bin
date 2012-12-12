"""Scrape theday.com for dad's articles
Put all those articles into a pdf book ready to be bound
(christmas present)"""
import BeautifulSoup
import datetime
import gevent.pool
import gevent.monkey
import hashlib
import jinja2
import pickle
import re
import requests
import os

gevent.monkey.patch_all(thread=False)


def get_article(url):
    print ('starting')
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
            print("Not more than %s articles for category %s" % (
                pager_index, category))
            break
        pager_index += 25
        urls.extend(_urls)
    return urls


def scrape(fp, fp2, overwrite=False):
    if not os.path.exists(fp2) or overwrite:
        with open(fp2, 'w') as urlswriter:
            print('getting article links')
            urls = []
            for category in ('DAYARC', 'ENT'):
                urls.extend(search(category))
            pickle.dump(urls, urlswriter)
    if not os.path.exists(fp) or overwrite:
        with open(fp, 'w') as writer:
            print('async getting data from articles')
            pool = gevent.pool.Pool(20)
            jobs = [pool.spawn(get_article, url)
                    for url in urls]  # TODO
            gevent.joinall(jobs, raise_error=True)
            pickle.dump([j.get() for j in jobs], writer)


def soupify(var):
    return BeautifulSoup.BeautifulSoup(var)


def _extract_datetime(var):
    var = soupify(var).text.split()[1].encode('utf-8')
    var = datetime.datetime.strptime(var, "%m/%d/%Y")
    return var.strftime('%s')


def clean_content(content):
    content = re.sub(
        '[\x80\xe2\x9d]', '"', content)  # clean retarded chars
    soup = soupify(content)
    c = lambda pattern: re.compile(pattern)
    patterns = (
        c('(?i)(Dr\.* *)?Joh*n Gaudio is a( New London-based)? cardiologist(.* New London)?.*'),
        c("Article UID=.*"),
        c('(?i)jcgaudio@pol.net.*'),
        c('(?i)This is the opinion of (Dr. )?Joh*n Gaudio\.*'),
    )
    for pattern in patterns:
        res = soup.find(text=pattern)
        if not res:
            continue
        for parent in res.parentGenerator():
            if parent.name == 'p':
                parent.extract()
                break
    [x.extract() for x in soup.findAll(['br'])]  # odd line spacing
    return soup.prettify().strip()


def make_html_book(fp, fp2, jinja_template_fp, jinja_toc_template_fp,
                   bad_titles, out_fp):
    articles = pickle.load(open(fp, 'r'))
    titles = {}  # store article title:unique id for that title
    templates = []  # for toc
    articles = sorted(articles, key=lambda x: _extract_datetime(x[1][0]))
    for (title, (published_at, updated_at), content) in articles:
        title_text = soupify(title).text
        if title_text in bad_titles or title_text in titles:
            continue
        title_hash = hashlib.sha1(title_text).hexdigest()[:4]
        titles[title_text] = title_hash
        published_at = soupify(published_at).text.split()[1].encode('utf-8')
        published_at = datetime.datetime.strptime(
            published_at, "%m/%d/%Y").strftime("%B %d, %Y")
        content = clean_content(content)
        template = jinja2.Template(open(jinja_template_fp, 'r').read())
        html = template.render(**locals())
        templates.append(html)
    book_template = jinja2.Template(open(jinja_toc_template_fp, 'r').read())
    book_html = book_template.render(titles=sorted(titles.items()),
                                     templates=templates)
    with open(out_fp, 'w') as f:
        f.write(book_html)


if __name__ == '__main__':
    from os.path import dirname, abspath, join
    # Big fat ass list of junk and relevant works we're excluding
    bad_titles = ("Honor Rolls",
                  'Lyme/Old Lyme Middle School',
                  'Lyme-Old Lyme Middle School',
                  'Fitch Senior High School',
                  "Vikings Tie For ECC Large Title",
                  "Ledyard Girls Hand Vikes Their First Loss Of Season",
                  "Stonington Sweeps New London",
                  'Woodstock Boys Clinch Share Of Large Crown',
                  "Tennis",
                  "Business Leaders Revive NL&#39;s Sailfest Road Race",
                  "It&#39;s The Lifestyle, Stupid",
                  "Reporters face off against five of the world's hottest peppers, and live (barely)",
                  "A Night To Remember",
                  'Of Women and Mothers',  # ABOUT MOM! Really cool
                  #'The Art of Femininity', # ABOUT MOM, but same as above

                  #'Let Elderly Take A Test To Assess Driving Skills', # An editorial about dad's article
                  #'Sex education must be comprehensive',  # Another editorial review, but not so great
                  #'History's smoke screen', # A great article from one of dad's patients.
                  #'Cover To Cover', # A patient's article about dad + others
                  'Salazar Heart Attack Should Serve As Warning To Runners Of All Abilities',  # ..
                  #'When Docs Made House Calls' #..
                  #'No joke, red wine is good for you' # ..
                  # introduces dad, kinda, but not cutting it
                  "Do You Really Have A Shot At Getting A Flu Shot?"
                  )
    cwd = dirname(abspath(__file__))
    fp = join(cwd, 'dads_articles.pickle')
    fp2 = join(cwd, 'dads_urls')
    jinja_template_fp = join(cwd, 'dads_jinja.html')
    jinja_toc_template_fp = join(cwd, 'dads_jinja_toc.html')
    out_fp = join(cwd, 'dads_book.html')

    scrape(fp, fp2)
    make_html_book(fp, fp2, jinja_template_fp, jinja_toc_template_fp,
                   bad_titles, out_fp)
    cmd = "prince %s -o %s" % (out_fp, out_fp.replace('html', 'pdf'))
    os.system(cmd)
