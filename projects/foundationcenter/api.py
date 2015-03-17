"""
Query Foundation Center api to get data on different foundations and non profits

# num grants by year in the arts
http://api.foundationcenter.org/research-dev/v1.0/FC1000/subjects/trends.json?key={API_KEY}&subject=arts&recipient_location=all
"""
from os import getenv
import json
import urllib
from pprint import pprint

# import pandas as pd
# import ggplots as gg
# import requests


url = (
    "https://apigee.com/foundation-stats/embed/console/qb"
    "?req=%7B%22resource%22%3A%22method10%22%2C%22params%22%3A%7B%22"
    "query%22%3A%7B%22"
    "key%22%3A%22{API_KEY}"
    "%22%2C%22year%22%3A%222012%22%2C%22subject%22%3A%22arts%22%2C%22"
    "population%22%3A%22all%22%2C%22recipient_location%22%3A%22all%22%7D%2C%22"
    "template%22%3A%7B%22format%22%3A%22json%22%7D%2C%22"
    "headers%22%3A%7B%7D%2C%22body%22%3A%7B%22attachmentFormat%22%3A%22"
    "mime%22%2C%22attachmentContentDisposition%22%3A%22"
    "form-data%22%7D%7D%2C%22verb%22%3A%22get%22%7D"
).format(API_KEY=getenv('FOUNDATION_API_KEY'))

purl = {
    u: [json.loads(vv) for vv in v]
    for u, v in urllib.parse.parse_qs(url).items()}

pprint(purl)
resp = urllib.request.urlopen(url)
