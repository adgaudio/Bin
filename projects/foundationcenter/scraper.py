import concurrent
from functools import wraps
from geopy.geocoders import Nominatim
from os.path import exists
import os
import pandas as pd
import requests
from time import sleep


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


def retry(ntimes, func, *args, **kwargs):
    for x in range(ntimes):
        try:
            return func(*args, **kwargs)
        except Exception as err:
            sleep(2)
            print("retry", err)


def get_lat_lon2(df, fp='./data/city_lat_long2.csv'):
    col = 'City, State/Country'
    df2 = pd.read_csv(fp)\
        .groupby(['city', 'state'])\
        .agg({'latitude': np.mean, 'longitude': np.mean})\
        .reset_index()
    df2[col] = df2['city'] + ', ' + df2['state']
    df2.drop(['city', 'state'], inplace=True, axis=1)

    missing_locations = df[col].DIFFERENCE(df2[col])  # TODO
    # TODO: look up these locations using geopy
    df3 = pd.DataFrame()
    # finally, merge all three sets together
    df = pd.merge(df, df2, on=col, how='left')
    df = pd.merge(df, df3, on=col, how='left')
    return df
    # df[df['latitude'].isnull()].groupby('City, State/Country').count().max()
    # (1).order()


def get_lat_lon(df, fp='./data/city_lat_long.csv'):
    """
    get latitude and longitude of each city for given fram
    """
    print("get city lat and long")
    if exists(fp):
        return pd.read_csv(fp, index_col=0)
    print("... this may take some time")
    geolocator = Nominatim()
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        fs = (
            executor.submit(lambda: (city, retry(5, geolocator.geocode, city)))
            for city in df['City, State/Country'].unique())
        _lat_lon = {}
        for fut in concurrent.futures.as_completed(fs):
            try:
                city, loc = fut.result()
            except Exception as err:
                print("SKIPPING", fut, err)
                continue
            if not loc:
                print("SKIPPING % due to %s" % (city, "it being unrecognized"))
                continue
            if isinstance(loc, Exception):
                print("SKIPPING % due to %s" % (city, loc))
                continue
            _lat_lon[city] = loc[1]
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


# df = get_dfs(927)  # 930
# plots(df)
# input('hit enter...')
