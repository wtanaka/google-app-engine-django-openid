from django.conf import settings

COOKIE_NAME='openidgae_sess'
if hasattr(settings, 'OPENIDGAE_COOKIE_NAME'):
  COOKIE_NAME = settings.OPENIDGAE_COOKIE_NAME

def get_session_id_from_cookie(request):
  if request.COOKIES.has_key(COOKIE_NAME):
    return request.COOKIES[COOKIE_NAME]

  return None

def write_session_id_cookie(response, session_id):
  expires = datetime.datetime.now() + datetime.timedelta(weeks=2)
  expires_rfc822 = expires.strftime('%a, %d %b %Y %H:%M:%S +0000')
  response.set_cookie(COOKIE_NAME, session_id, expires=expires_rfc822)

def get_session(request, response, create=True):
  if hasattr(request, 'openidgae_session'):
    return request.openidgae_session

  # get existing session
  session_id = get_session_id_from_cookie(request)
  if session_id:
    import models
    session = models.Session.get_by_key_name(session_id)
    if session is not None:
      request.openidgae_session = session
      return request.openidgae_session

  if create:
    import models
    request.openidgae_session = models.Session()
    request.openidgae_session.put()
    write_session_id_cookie(response, request.openidgae_session.key().name())
    return request.openidgae_session

  return None

def create_login_url():
  import django.core.urlresolvers
  return django.core.urlresolvers.reverse('openidgae.views.LoginPage')

def create_logout_url():
  import django.core.urlresolvers
  return django.core.urlresolvers.reverse('openidgae.views.LogoutSubmit')

def get_current_person(request, response):
  if hasattr(request, 'openidgae_logged_in_person'):
    return request.openidgae_logged_in_person

  s = get_session(request, response, create=False)
  if s and s.person:
    request.openidgae_logged_in_person = s.person
    return request.openidgae_logged_in_person

  return None
