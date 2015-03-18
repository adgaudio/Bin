import requests
import pandas as pd


def c(*args):
    """Pipeline funcs together like this:

        c(1, lambda x: x + 1, lambda x: x**2)
    """
    it = iter(args)
    rv = next(it)
    for f in it:
        rv = f(rv)
    return rv


def get_page(num):
    url = 'https://fdo.foundationcenter.org/search/results'
    params = dict(
        collection='grantmakers',
        activity='pagination',  # pagination
        page=1,
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


def parse_html_table(resp):
    df = pd.read_html(resp.text, 'Total Giving')[0]
    df.columns = [x.strip() for x in df.columns]
    df.drop('Unnamed: 0', axis=1, inplace=True)
    for col in ['Total Assets', 'Total Giving']:
        df[col] = df[col].str.replace(r'[$,]', '').astype('float')
        df[col + '.log'] = df[col].apply(pd.np.log)
    return df


df = c(
    1,
    get_page,
    parse_html_table
)
df.dropna().plot(kind='scatter', x='Total Assets.log', y='Total Giving.log')
