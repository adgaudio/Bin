import requests
import pandas as pd
import os
from os.path import exists
from functools import wraps


def c(*args):
    """Pipeline funcs together like this:

        c(1, lambda x: x + 1, lambda x: x**2)
    """
    it = iter(args)
    rv = next(it)
    for f in it:
        rv = f(rv)
    return rv


def closure(func):
    """
    Decorate a function and convert it into a partial closure.
    where you must call it twice, and can pass in args both times
    """
    @wraps(func)
    def f(*args, **kwargs):
        def f2(*args2, **kwargs2):
            kws = dict()
            kws.update(kwargs)
            kws.update(kwargs2)
            return func(*(x for y in [args2, args] for x in y), **kws)
        return f2
    return f


def get_page(num):
    print("getting page %s" % num)
    url = 'https://fdo.foundationcenter.org/search/results'
    params = dict(
        collection='grantmakers',
        activity='pagination',  # pagination
        page=num,
        _new_search='1',
        name='',
        ein='',
        location='',
        country='',
        state='',
        county='',
        city='',
        metro_area='',
        congressional_district='',
        zip_code='',
        type_of_grantmaker='',
        range='total_giving',
        range_start='0',
        range_stop='9999999',
        # range='year',  # doesn't seem to work
        # range_start='2011',
        # range_stop='2012',
        sort_by='sort_name',
        sort_order='0',
    )

    resp = requests.get(url, params=params)
    return resp


@closure
def parse_html_table(resp, pagenum, fp):
    df = pd.read_html(resp.text, 'Total Giving')[0]
    df.columns = [x.strip() for x in df.columns]
    df.drop('Unnamed: 0', axis=1, inplace=True)
    df.set_index('Grantmaker Name', inplace=True)
    for col in ['Total Assets', 'Total Giving']:
        df[col] = df[col].str.replace(r'[$,]', '').astype('float')
        df[col + '.log'] = df[col].apply(pd.np.log)
    df['page'] = pagenum
    df.to_csv(fp)
    return df


# fetch all pages
# currently between 925 and 930 pages of foundations on the site
def get_dfs(npages):
    try:
        os.makedirs('./data')
    except FileExistsError:
        pass

    def fp(pagenum): return './data/%s.csv' % pagenum

    dfs = (c(
        pagenum,
        get_page,
        parse_html_table(pagenum, fp(pagenum)),
    ) if not exists(fp(pagenum)) else pd.read_csv(fp(pagenum))
        for pagenum in range(1, npages)
    )

    df = pd.concat(dfs)
    return df

df = get_dfs(930)  # 930
df.dropna().plot(kind='scatter', x='Total Assets.log', y='Total Giving.log')
