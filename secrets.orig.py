import os
#Copy this file to secrets.py and edit it's values
#> cp secrets.orig.py secrets.py
#(git rm --cached secrets.py)

## settings for inquiring articles from newsapi.org
#  Get API Key: https://newsapi.org/register &  https://newsapi.org/account
os.environ['NEWSAPI_KEY'] = '1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7'

## setting for inquring data from geonames
# Get API Key here: http://www.geonames.org/export/web-services.html
os.environ['GEONAMES_KEY'] = '1a2b3c4d5'

