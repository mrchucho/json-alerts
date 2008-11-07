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

