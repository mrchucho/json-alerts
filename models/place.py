import re

from utils.external.BeautifulSoup import BeautifulStoneSoup

import models
from utils.api import geo

class Place:
  TZ_CODE = "31"
  STATE_ABBREV_RE = re.compile("^US\s*-?\s*",re.IGNORECASE)

  def __init__(self, place_name):
    self.named    = place_name
    self.place    = None
    self.county   = None
    self.state    = None
    self.abbrev   = None
    self.woeid    = None
    self.timezone = None

    self._find_place()
    self._find_timezone()

  @property
  def state_abbreviation(self):
    return Place.STATE_ABBREV_RE.sub('',self.abbrev or '')

  def _find_place(self):
    doc = BeautifulStoneSoup(geo.place_for_search_term(self.named))
    for place in doc.places:
      self.place = place
      for types in place.findAll(type=["County","State"]):
        if types['type'] == "County":
          self.county = types.string
        else:
          self.state  = types.string
          self.abbrev = types['code']
      for woeid in place.woeid:
        self.woeid = woeid

  def _find_timezone(self):
    woeid = self.woeid
    timezone = None
    tries = 0
    while not timezone and tries < 5:
      timezone = self._find_timezone_for_woeid(woeid)
      if not timezone:
        woeid = self._find_parent_woeid(woeid)
      tries += 1
    self.timezone = timezone

  def _find_timezone_for_woeid(self,woeid):
    try:
      doc = BeautifulStoneSoup(geo.children_of_place(woeid,type=Place.TZ_CODE))
      for place in doc.places:
        if len(place.findAll("placetypename",code=Place.TZ_CODE)) > 0:
          return place.findAll("name")[0].string
      return None
    except models.GeoError:
      return None

  def _find_parent_woeid(self,woeid):
    try:
      doc = BeautifulStoneSoup(geo.parent_of_place(woeid))
      for woeid in doc.woeid:
        return woeid
      return None
    except models.GeoError:
      return None

  def __str__(self):
    return ("County: %s State: %s (%s) Abbrev: %s WOEID: %s Timezone: %s" %
        (self.county, self.state, self.state_abbreviation, self.abbrev, self.woeid, self.timezone))



if __name__ == '__main__':
  p = Place("St Louis, MO")
  print("County: %s State: %s (%s) Abbreviation: %s WOEID: %s Timezone: %s" %
      (p.county, p.state, p.state_abbreviation, p.abbrev, p.woeid, p.timezone))
