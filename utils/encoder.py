from django.utils import simplejson as json

class AlertEncoder(json.JSONEncoder):

  def default(self, o):
    return {
        'place': {
          'name': o.place.named,
          'county': o.place.county,
          'state': o.place.state, 
          'timezone': o.place.timezone
        },
        'event': o.event,
        'effective': o.effective,
        'expires': o.expires,
        'severity': o.severity 
    }


class PlaceEncoder(json.JSONEncoder):
  
  def default(self, o):
    return {
        'place': o.named,
        'county': o.county,
        'state': o.state,
        'timezone': o.timezone,
        'alerts': [ {'event': alert.event, 'effective': alert.effective, 'expires': alert.expires, 'severity': alert.severity} for alert in o.alerts ]
    }
