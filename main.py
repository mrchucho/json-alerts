#!/usr/bin/env python

import wsgiref.handlers
import urllib2
import logging
import os
import sys
import traceback

from google.appengine.ext import webapp
from google.appengine.api import memcache
from google.appengine.ext.webapp import template

from django.utils import simplejson as json

# pytz imports itself, so this is necessary
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'utils', 'external')))

from models.alert import Alert
from models.place import Place
from models import InvalidPlace
from utils.encoder import PlaceEncoder

class AlertHandler(webapp.RequestHandler):
  PLACE_KEY = "/%s/place/"
  ALERT_KEY = "/%s/alert/"

  def get(self):
    place_name = self.request.get("p", None)
    callback = self.request.get("callback", None)

    if not place_name:
      raise InvalidPlace(" ")
    elif place_name == "favicon.ico":
      """ This happens so often, it's annoying. """
      self.response.set_status(204)
    else:
      place_name = urllib2.unquote(place_name)
      p = memcache.get(self.PLACE_KEY % place_name)
      if not p:
        p = Place(place_name)
        memcache.set(self.PLACE_KEY % place_name, p) # cache indefinitely

      alerts = memcache.get(self.ALERT_KEY % place_name)
      if not alerts:
        alerts = Alert.alerts_for(p)
        try:
          memcache.set(self.ALERT_KEY % place_name, alerts, time=10) # cache a SHORT time
        except:
          logging.error('Error setting memcache.')
          logging.error(''.join(traceback.format_exception(*sys.exc_info())))

      p.alerts = alerts
      javascript = json.dumps(p, sort_keys=True, indent=2, cls=PlaceEncoder)

      self.response.headers['Content-Type'] = 'text/javascript'
      self.response.out.write("%s(%s)" % (callback, javascript) if callback else javascript)


  def handle_exception(self, exception, debug_mode=False):
    logging.error(''.join(traceback.format_exception(*sys.exc_info())))
    if hasattr(exception, "code"):
      status = exception.code
      message = exception.msg
    else:
      status = 500
      message = "An Unknown Error Occurred."

    self.response.set_status(status)
    self.response.headers['Content-Type'] = 'text/javascript'
    self.response.out.write(json.dumps({'error': message}))


class MainHandler(webapp.RequestHandler):

  def get(self):
    index = os.path.join(os.path.dirname(__file__), 'views', 'index.html')
    self.response.out.write(template.render(index, {}))


def main():
  application = webapp.WSGIApplication([('/alerts.json', AlertHandler), ('/', MainHandler)],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
