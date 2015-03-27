import concurrent.futures
from functools import wraps
from geopy.geocoders import Nominatim
from os.path import exists
import os
import pandas as pd
import numpy as np
import requests
from time import sleep
from types import FunctionType

import pylab as plt
from mpl_toolkits import basemap


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


def get_dfs(npages=927):
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


def retry(ntimes, delay=2):
    if ntimes < 0:
        raise Exception("ntimes must be >= 0")
    def _retry_decorator(func):
        @wraps(func)
        def _func(*args, **kwargs):
            for x in range(ntimes + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as err:
                    sleep(delay)
                    print("retry func due to error:", func, err)
            raise err
        return _func
    return _retry_decorator



def receives_future(expand_args=True, raise_on_error=True):
    """Wraps a function such that, instead of calling the function(...)
    directly, expect to receive a Future and then pass the future.result()
    to the function.

    `expand_args` - If False, the wrapped function expects to receive a Future.
        If True, expect that the future.result() contains
        parameters for the wrapped function in one of these forms:

        args_tuple  -->  (1,2)
        kwargs_dict  -->  {'arg1': 1}
    """
    def _receives_future(func):
        @wraps(func)
        def _receives_future_decorator(future):
            rv = future.result()
            if isinstance(rv, Exception):
                if raise_on_error:
                    raise rv
                else:
                    print(rv)
            elif not expand_args:
                return func(rv)
            elif isinstance(rv, dict):
                return func(**rv)
            elif isinstance(rv, tuple):
                return func(*rv)
            else:
                return func(rv)
        return _receives_future_decorator
    return _receives_future


def get_lat_lon(df, fp='./data/zipcode.csv.gz'):
    print("get city lat and long")
    col = 'City, State/Country'
    df2 = pd.read_csv(fp, compression=fp.endswith('.gz') and 'gzip' or None)\
        .groupby(['city', 'state'])\
        .agg({'latitude': np.mean, 'longitude': np.mean})\
        .reset_index()
    df2[col] = df2['city'] + ', ' + df2['state']
    df2.drop(['city', 'state'], inplace=True, axis=1)
    missing_locations = np.setdiff1d(df[col].values, df2[col].values)
    # df3 = get_lat_lon_from_arcGIS(missing_locations)
    df3 = pd.DataFrame()  # TODO: enable arcGIS
    df4 = pd.concat([df2, df3])

    # finally, merge all three sets together
    res = pd.merge(df, df4, on=col, how='left')
    return res


def get_lat_lon_from_arcGIS(cities, nworkers=20):
    """
    get latitude and longitude of each city for given fram
    """
    print("get city lat and long from arcGIS")
    # if len(cities) > 1000:
        # raise Exception(
            # "Can only fetch up to 1000 lat/long per day from arcGIS")
    nominatum = Nominatim()

    @retry(5)
    def geocoder(nominatum, city):
        notfound = {
            'City, State/Country': city, 'latitude': None, 'longitude': None}
        loc = nominatum.geocode(city)
        if not loc:
            print("SKIPPING %s due to %s" % (city, "it being unrecognized"))
            return notfound
        elif isinstance(loc, Exception):
            print("SKIPPING %s due to %s" % (city, loc))
            return notfound
        else:
            return {'City, State/Country': city,
                    'latitude': loc[1][0],
                    'longitude': loc[1][1]}

    _lat_lon = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=nworkers) as executor:
        for city in cities:
            executor\
                .submit(geocoder, nominatum, city)\
                .add_done_callback(receives_future(False)(_lat_lon.append))

    lat_lon = pd.DataFrame(_lat_lon)
    return lat_lon


def plots(df):
    print("plot things")

    plt.ion()

    # total giving vs total assets
    # df.dropna().plot(kind='scatter', x='Total Assets.log', y='Total Giving.log')
    # plt.figure()

    # plot each city on a map
    agg_by_city = df\
        .groupby(['City, State/Country', 'latitude', 'longitude'])\
        ['Total Giving']\
        .agg(
            {'Total Giving ($)': lambda x: x.sum(),
             'Total Giving (num grants)': lambda x: x.count()})
    usmap_plot(agg_by_city['Total Giving ($)'])


def usmap_plot(series):
    print("plotting points on map")
    usmap = basemap.Basemap(
        llcrnrlon=-130, llcrnrlat=24, urcrnrlon=-64, urcrnrlat=50)
    usmap.drawcountries(color='gray', linewidth='.6')
    usmap.drawcoastlines(color='gray')
    usmap.drawstates()

    def get_markersize(x, min_, max_):
        return np.log((x - min_) / (max_ - min_) * (np.e ** 10) + np.e ** 1)
    mmin, mmax = series.quantile(.001), series.quantile(.999)
    for idx, row in series.reset_index().iterrows():
        plt.plot(
            row['longitude'], row['latitude'], 'bo',
            markersize=get_markersize(row[series.name], mmin, mmax))


if __name__ == "__main__":
    df = c(
        927,  # 930
        get_dfs,
        get_lat_lon
    )
    plots(df)
    input('hit enter...')
