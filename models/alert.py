import re
import logging

from datetime import datetime
from utils.external.BeautifulSoup import BeautifulStoneSoup

from utils.external.pytz import timezone
import utils.external.pytz
from models import place
import models
from utils.api import weather

class Alert:
  NAME_RE = re.compile("[.,:]")
  FORMAT  = "%Y-%m-%d %H:%M:%S %Z"

  def __init__(self, **kwargs):
    kwlist = {
        'place': None,
        'event': None,
        'effective': None,
        'expires': None,
        'severity': None
    }
    kwlist.update(kwargs)
    self.place = kwlist['place']
    self.event = kwlist['event']
    self.effective = self._adjust_for_tz(kwlist['effective'])
    self.expires = self._adjust_for_tz(kwlist['expires'])
    self.severity = self._severity_for(self.event)

  def _severity_for(self, event):
    """ Return a severity (for sorting) between 0 (lowest) and 10 (highest).

    Anything (other than a short-term forecast) besides those listed here is assumed
    to be of a lower importance. Short-term forecasts are not considered severe.
    """
    try:
      return {
          "tornado warning": 10,
          "warning": 9,
          "watch": 8,
          "advisory": 7,
          "statement": 6,
          "short term forecast": 0,
          }[event.lower()]
    except KeyError:
      return 1

  def _adjust_for_tz(self, utc_datetime):
    tz = timezone(self.place.timezone or 'UTC')
    date, time = utc_datetime.split('T')
    y,m,d,h,mi,s = [int(n) for n in date.split('-') + time.split(':')]
    datetime_utc = datetime(y, m, d, h, mi, s, 0, tzinfo=utils.external.pytz.utc)
    datetime_tz  = datetime_utc.astimezone(tz)
    return datetime_tz.strftime(self.FORMAT)
  
  def __str__(self):
    return "Alert %s Eff %s Exp %s Sev %d" % (self.event,self.effective,self.expires,self.severity)

  @classmethod
  def alerts_for(cls, place):
    """ Find all of the Alerts for a given Place.

    """
    if not place.county:
      raise models.InvalidPlace(place)
    logging.debug("Finding alerts for %s" % place)
    alerts = []
    doc = BeautifulStoneSoup(weather.cap_for_state(place.state_abbreviation))
    for info in doc.findAll("cap:info"):
      area = info.find("cap:area")
      if area:
        area_desc = area.find("cap:areadesc").string
        if cls.names_match(area_desc, place):
          alert = Alert(
              place=place,
              event=info.find("cap:event").string,
              effective=info.find("cap:effective").string,
              expires=info.find("cap:expires").string
          )
          alerts.append(alert)
    return alerts

  @classmethod
  def names_match(cls, area, place):
    """ Compare the NOAA's name for an area with Yahoo! Geo's name for a Place.

    """
    def n(name):
      """ Normalize a name by removing punctuation. """
      return cls.NAME_RE.sub('', name)

    area = n(area)
    return re.match(r"%s\s*(County)?\s*\(%s\)" % (n(place.county), n(place.state)), area, re.IGNORECASE)


if __name__ == '__main__':
  import sys
  p = place.Place(" ".join(sys.argv[1:]))
  print("Checking alerts for %s" % p)
  for alert in Alert.alerts_for(p):
    print("\tAlert %s Eff %s Exp %s Sev %d" % (alert.event,alert.effective,alert.expires,alert.severity))


