from functools import wraps, lru_cache
from geopy.geocoders import Nominatim
from os.path import exists
import os
import pandas as pd
import requests


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


def get_dfs(npages):
    """
    fetch all pages
    currently between 925 and 930 pages of foundations on the site
    """
    print("loading data")
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


def get_lat_lon(df, fp='./data/city_lat_long.csv'):
    """
    get latitude and longitude of each city for given fram
    """
    print("get city lat and long")
    if exists(fp):
        return pd.read_csv(fp, index_col=0)
    print("... this may take some time")
    geolocator = Nominatim()
    _lat_lon = {}
    for city in df['City, State/Country'].unique():
        l = geolocator.geocode(city)
        if not l:
            print("... SKIP", city)
            continue
        _lat_lon[city] = l[1]
    lat_lon = pd.DataFrame.from_dict(_lat_lon, orient='index')
    lat_lon.columns = ['lat', 'lon']
    lat_lon.index.name = 'City, State/Country'
    lat_lon.to_csv(fp)
    return lat_lon


def plots(df):
    import pylab as plt
    from mpl_toolkits import basemap

    print("plot things")

    plt.ion()

    # total giving vs total assets
    df.dropna().plot(kind='scatter', x='Total Assets.log', y='Total Giving.log')
    plt.figure()

    # plot each city on a map
    usmap = basemap.Basemap(
        llcrnrlon=-130, llcrnrlat=24, urcrnrlon=-64, urcrnrlat=50)
    usmap.drawcountries(color='gray', linewidth='.6')
    usmap.drawcoastlines(color='gray')
    usmap.drawstates()
    agg_by_city = get_lat_lon(df).join(
        df.groupby('City, State/Country')['Total Giving'].agg(
            {'Total Giving ($)': lambda x: x.sum(),
             'Total Giving (num grants)': lambda x: x.count()}))

    def get_markersize(x, min, max):
        l = pd.np.log
        return (l(x) - l(min)) / (l(max) - l(min)) * (20-5) + 5
    min, max = agg_by_city.min(), agg_by_city.max()
    for row in agg_by_city.itertuples():
        t = 'Total Giving ($)'
        # t = 'Total Giving (num grants)'
        usmap.plot(
            row[2], row[1], 'bo',
            markersize=get_markersize(row[3], min.ix[t], max.ix[t]))


df = get_dfs(927)  # 930
plots(df)
input('hit enter...')
