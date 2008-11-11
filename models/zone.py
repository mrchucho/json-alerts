from google.appengine.ext import db
from google.appengine.ext import bulkload
from google.appengine.api import datastore_types
from google.appengine.ext import search

import logging

class Zone(db.Model):
  state     = db.StringProperty() # 2
  zone      = db.StringProperty() # 3
  cwa       = db.StringProperty() # 3 'County Warning Area'
  name      = db.StringProperty() # 254
  state_zone= db.StringProperty() # 5
  county    = db.StringProperty() # 24
  fips      = db.StringProperty() # 5
  time_zone = db.StringProperty() # 2
  fe_area   = db.StringProperty() # 2
  latitude  = db.FloatProperty() # 9,5
  longitude = db.FloatProperty() # 10,5

  @classmethod
  def fips_for_county(cls, county=None, state=None):
    zone = cls.all().filter("county =", county).filter("state =", state).get()
    if zone:
      return zone.fips
    else:
      return ""


class ZoneLoader(bulkload.Loader):
  def __init__(self):
    bulkload.Loader.__init__(self, 'Zone',
        [
          ('state', str), 
          ('zone' , str), 
          ('cwa'  , str), 
          ('name' , str), 
          ('state_zone', str), 
          ('county', str),
          ('fips' , str), 
          ('time_zone', str),
          ('fe_area', str),
          ('latitude', float),
          ('longitude', float)
          ])

  """ Not Implemented """
  def _HandleEntity(self, entity):
    logging.debug(entity)
    return None


if __name__ == '__main__':
  bulkload.main(ZoneLoader())

