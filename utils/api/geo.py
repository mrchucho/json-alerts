import urllib2

from google.appengine.api import urlfetch

APP_ID = "OSkXnanV34GmWWqcfpA2CsbB18xDtJF6_mfp7Su.HpqXelHWX.ipRGVAe.dw1j8-"

def fetch(url):
  result = urlfetch.fetch(url, method=urlfetch.GET, headers={"Accept": "application/xml"})
  if result.status_code != 200:
    raise models.GeoError(result.status_code)
  else:
    return result.content

def place_for_search_term(search_term):
  search_term = urllib2.quote("'%s'" % search_term)
  return fetch("http://where.yahooapis.com/v1/places.q(%s)?appid=%s" % (search_term, APP_ID))

def parent_of_place(place):
  return fetch("http://where.yahooapis.com/v1/place/%s/parent?appid=%s" % (place, APP_ID))

def children_of_place(place, **kwargs):
  kwlist = {'type': -1}
  kwlist.update(kwargs)
  type = kwlist['type']
  return fetch("http://where.yahooapis.com/v1/place/%s/belongtos.type(%s)?appid=%s" % (place, type, APP_ID))

