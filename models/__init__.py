class GeoError(Exception):
  """ An error occurred while accessing the Yahoo! Geo API. """
  def __init__(self, code=500):
    self.code = code
    self.msg = "An error occurred while fetching location information."

  def __str__(self):
    return repr(self.msg)


class CAPError(Exception):
  """ An error occurred while accessing the NOAA's CAP feed. """
  def __init__(self, code=500):
    self.code = code
    self.msg = "An error occurred while fetching alerts."

  def __str__(self):
    return repr(self.msg)


class InvalidPlace(Exception):
  """ An error occurred while attempting to use an invalid or incomplete Place. """
  def __init__(self, place):
    self.code = 400 # or 404 or 417 ?
    self.msg = "[%s] is not a valid place." % place

  def __str__(self):
    return repr(self.msg)
     
