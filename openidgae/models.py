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
  hashedkey = db.StringProperty()

  def pretty_openid(self):
    return self.openid.replace('http://','').replace('https://','').rstrip('/').split('#')[0]

  def put(self):
    if self.hashedkey is None:
      if self.is_saved():
        key = self.key()
      else:
        key = db.Model.put(self)

      self.hashedkey = hashlib.sha1(str(key)).hexdigest()

    assert self.hashedkey
    return db.Model.put(self)


class Session(db.Expando):
  # the logged in person
  person = db.ReferenceProperty(Person)

  # OpenID library session stuff
  openid_stuff = db.TextProperty()

  # when someone tries to demand a site and they aren't logged in,
  # we store it here
  url = db.StringProperty()

  # this goes in the cookie
  session_id = db.StringProperty()

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

  def put(self):
    if self.session_id is None:

      if self.is_saved():
        key = self.key() 
      else:
        key = db.Expando.put(self)

      self.session_id = hashlib.sha1(str(key)).hexdigest()
    else:
      key = self.key()

    assert self.session_id
    db.Expando.put(self)
    return key
