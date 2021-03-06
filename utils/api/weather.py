from google.appengine.api import urlfetch
from models import CAPError

from models import CAPError

def cap_for_state(state):
  try:
    result = urlfetch.fetch("http://alerts.weather.gov/cap/%s.atom" % state.lower())
    if result.status_code != 200:
      raise CAPError(result.status_code)
    else:
      return result.content
  except urlfetch.DownloadError:
    raise CAPError
