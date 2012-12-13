"""Scrape theday.com for dad's articles
Put all those articles into a pdf book ready to be bound
(christmas present)"""
import BeautifulSoup
from collections import defaultdict, OrderedDict
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


def capitalize_index(title_text, start):
    """Capitalize first letter after given index"""
    title_text = list(title_text)
    offset = 1
    while not title_text[start + offset].isalpha():
        offset += 1
        if start + offset >= len(title_text) - 1:
            offset = len(title_text) - start - 1
            break
    title_text[start + offset] = title_text[start + offset].capitalize()
    title_text = ''.join(title_text)
    if offset > 2:
        print 'WARNING: capitalizing at index %s: %s' % (start + offset, title_text)
    return title_text


def make_article_html(articles_fp, jinja_env):
    get_title_hash = lambda txt: hashlib.sha1(txt).hexdigest()[:4]
    articles = pickle.load(open(articles_fp, 'r'))
    titles = OrderedDict()  # store article title:unique id for that title
    templates = []  # for toc
    articles = sorted(articles, key=lambda x: _extract_datetime(x[1][0]))
    for (title, (published_at, updated_at), content) in articles:
        title_text = soupify(title).text
        if title_text in bad_titles or title_text in titles:
            continue
        title_text = reduce(capitalize_index,
                            [w.start()
                                for w in re.finditer("( '|-| |[^ ]\.)", title_text)],
                            capitalize_index(title_text, -1))
        title_hash = get_title_hash(title_text)
        published_at = soupify(published_at).text.split()[1].encode('utf-8')
        published_at = datetime.datetime.strptime(published_at, "%m/%d/%Y")
        year = published_at.year
        published_at = published_at.strftime("%B %d, %Y")
        titles[title_text] = (title_hash, year)

        if title_text == "Do You Really Have A Shot At Getting A Flu Shot?":
            title = title.replace(title_text, "Introduction")
            titles.pop(title_text)
            title_text = "Introduction"
            title_hash = get_title_hash(title_text)
            titles[title_text] = (title_hash, year)
            content = jinja_env.get_template("dads_jinja_introduction.html").render()
        else:
            content = clean_content(content)
        template = jinja_env.get_template(jinja_template_fp)
        html = template.render(**locals())
        templates.append(html)
    titles_by_year = defaultdict(list)
    for title_text, (title_hash, year) in titles.items():
        titles_by_year[year].append((title_text, title_hash))
    return templates, titles_by_year


def make_html_book(articles_fp, jinja_template_fname, jinja_toc_template_fname,
                   jinja_template_dir, bad_titles, out_fp):
    env = jinja2.Environment()
    env.loader = jinja2.FileSystemLoader(jinja_template_dir)
    templates, titles_by_year = make_article_html(articles_fp, env)
    book_template = env.get_template(jinja_toc_template_fp)
    book_html = book_template.render(titles_by_year=titles_by_year.items(),
                                     templates=templates)
    assert all([title_text not in bad_titles
                for title_text in (tup[0] for titles in titles_by_year.values()
                                   for tup in titles)])
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
                  'Salazar Heart Attack Should Serve As Warning To Runners Of All Abilities',  # ..
                  #"Do You Really Have A Shot At Getting A Flu Shot?",  # introduces dad, kinda, but not cutting it
                  "A Night To Remember",
                  'Of Women and Mothers',  # ABOUT MOM! Really cool
                  'The Art of Femininity',  # ABOUT MOM, but same as above

                  'Let Elderly Take A Test To Assess Driving Skills',
                  # An editorial about dad's article
                  'Sex education must be comprehensive',
                  # Another editorial review, but not so great
                  "History's smoke screen",
                  # A great article from one of dad's patients.
                  'Cover To Cover',  # A patient's article about dad + others
                  'When Docs Made House Calls',  # ..
                  'No joke, red wine is good for you',  # ..
                  )
    cwd = dirname(abspath(__file__))
    fp = join(cwd, 'dads_articles.pickle')
    fp2 = join(cwd, 'dads_urls.pickle')
    jinja_template_fp = 'dads_jinja.html'
    jinja_toc_template_fp = 'dads_jinja_toc.html'
    jinja_template_dir = cwd
    out_fp2 = join(cwd, 'dads_book.pdf')

    scrape(fp, fp2)
    make_html_book(fp, jinja_template_fp, jinja_toc_template_fp,
                   jinja_template_dir, bad_titles, out_fp2.replace('pdf', 'html'))
    cmd = "prince %s -o %s" % (out_fp2.replace('pdf', 'html'), out_fp2)
    os.system(cmd)
    out_fp1 = join(cwd, 'pre_toc.pdf')
    cmd = "prince %s -o %s" % (out_fp1.replace('pdf', 'html'), out_fp1)
    os.system(cmd)
    out_fp3 = "richter_gaudio_book_block.pdf"
    cmd = ("gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite"
           " -sOutputFile={out_fp3} {out_fp1} {out_fp2}").format(**locals())
    os.system(cmd)
