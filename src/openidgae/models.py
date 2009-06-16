# vim:ts=2:sw=2:expandtab
import hashlib

from google.appengine.ext import db

class Association(db.Model):
  """An association with another OpenID server, either a consumer or a provider.
  """
  url = db.LinkProperty()
  handle = db.StringProperty()
  association = db.TextProperty()

class Nonce(db.Model):
  """An OpenID nonce.
  """
  nonce = db.StringProperty()
  timestamp = db.IntegerProperty()

class Person(db.Model):
  openid = db.StringProperty()
  date = db.DateTimeProperty(auto_now_add=True)
  # Pickled Simple Registration Response
  sreg = db.BlobProperty()
  # Pickled Attribute Exchange Response
  ax = db.BlobProperty()

  def get_depickled_version(self, property):
    if not property:
      return {}
    else:
      import pickle
      return pickle.loads(property)

  def get_sreg_dict(self):
    return self.get_depickled_version(self.sreg)

  def get_ax_dict(self):
    return self.get_depickled_version(self.ax)

  def openidURI(self):
    from openid.yadis import xri
    if xri.identifierScheme(self.openid) == "XRI":
      return "http://xri.net/%s" % self.openid
    return self.openid

  def pretty_openid(self):
    return self.openid.replace('http://','').replace('https://','').rstrip('/').split('#')[0]

  def person_name(self):
    ax_dict = self.get_ax_dict()
    sreg_dict = self.get_sreg_dict()
    if ax_dict.get('firstname', False) and \
        ax_dict.get('lastname', False):
      firstname = ax_dict['firstname']
      if isinstance(firstname, list):
        firstname = firstname[0]
      lastname = ax_dict['lastname']
      if isinstance(lastname, list):
        lastname = lastname[0]
      return "%s %s" % (firstname, lastname)
    elif sreg_dict.get('fullname', False):
      return sreg_dict['fullname']
    else:
      return self.pretty_openid()

class Session(db.Expando):
  # the logged in person
  person = db.ReferenceProperty(Person)

  # OpenID library session stuff
  openid_stuff = db.TextProperty()

  def __init__(self, parent=None, key_name=None, **kw):
    """if key_name is None, generate a random key_name so that
       session_id cookies are not guessable
    """
    if key_name is None:
      import uuid
      key_name = uuid.uuid4()
      import binascii
      key_name = binascii.unhexlify(key_name.hex)
      import base64
      key_name = "S" + base64.urlsafe_b64encode(key_name).rstrip('=')
    super(db.Expando, self).__init__(parent=parent, key_name=key_name, **kw)
