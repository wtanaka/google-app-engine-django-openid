# vim:ts=2:sw=2:expandtab
import os
import logging
import datetime

import django.core.urlresolvers
import django.http

from openid.consumer.consumer import Consumer
from openid.consumer import discover
import openid.consumer.consumer
import openidgae
import store

def initOpenId():
  # installFetcher
  from openid import fetchers
  import openidgae.fetcher
  fetchers.setDefaultFetcher(openidgae.fetcher.UrlfetchFetcher())
  # Switch logger to use logging package instead of stderr
  from openid import oidutil
  def myLoggingFunction(message, level=0):
    import logging
    logging.info(message)
  oidutil.log = myLoggingFunction

DIRNAME = os.path.dirname(__file__)
def render(template_name, request, response, extra_values={}):
  values = {
    'lip': openidgae.get_current_person(request, response)
    }

  values.update(extra_values)
  #path = os.path.join(DIRNAME, 'templates', template_name)
  #return template.render(path, values)

  import django.template
  import django.template.loader
  t = django.template.loader.get_template(template_name)
  return t.render(django.template.Context(values))

def get_full_path(request):
  full_path = ('http', ('', 's')[request.is_secure()], '://',
      request.META['HTTP_HOST'], request.path)
  return ''.join(full_path)

def get_store():
  return store.DatastoreStore()

def args_to_dict(querydict):
  return dict([(arg, values[0]) for arg, values in querydict.lists()])

def show_main_page(request, error_msg=None):
  """Do an internal (non-302) redirect to the front page.

  Preserves the user agent's requested URL.
  """
  request.method='GET'
  return MainPage(request, error_msg)


############## Handlers #################
def MainPage(request, error_msg):
  initOpenId()
  response = django.http.HttpResponse()
  if request.method == 'GET':
    template_values = {
      'error_msg': error_msg,
      }

    response['X-XRDS-Location'] = 'http://'+request.META['HTTP_HOST']+'/rpxrds/'
    response.write(render('openidgae-main.html', request, response, template_values))
    return response


def PersonPage(request):
  initOpenId()
  response = django.http.HttpResponse()
  if request.method == 'GET':
    openid = request.GET.get('openid', '')

    import models
    persons = models.Person.gql("WHERE openid = :1",openid)
    try:
      p = persons[0]
    except IndexError:
      return show_main_page(request, 'Unknown user')


    lip = openidgae.get_current_person(request, response)

    response.write(render('openidgae-person.html',request,response,
          {'person':p,
          'lip_is_person': lip and lip.openid == p.openid }))
    return response

def HomePage(request):
  initOpenId()
  response = django.http.HttpResponse()
  if request.method == 'GET':
    if openidgae.get_current_person(request, response):
      response.write(render('openidgae-home.html',request,response,{}))
      return response
    else:
      return django.http.HttpResponseRedirect('/')

def LoginPage(request):
  initOpenId()
  response = django.http.HttpResponse()
  if request.method == 'GET':
    continueUrl = request.GET.get('continue', '/')
    # Sanitize
    if continueUrl.find('//') >= 0 or not continueUrl.startswith('/'):
      continueUrl = '/'
    import urllib
    template_values = {
      'continueUrl': urllib.quote_plus(continueUrl),
    }
    response.write(render('openidgae-login.html',request,response,template_values))
    return response

def OpenIDStartSubmit(request):
  initOpenId()
  response = django.http.HttpResponse()
  if request.method == 'POST':
    openid = request.POST.get('openid_identifier', '')
    if not openid:
      return show_main_page(request)

    c = Consumer({},get_store())
    try:
      auth_request = c.begin(openid)
    except discover.DiscoveryFailure, e:
      logging.error('OpenID discovery error with begin on %s: %s'
          % (openid, str(e)))
      return show_main_page(request, 'An error occured determining your server information.  Please try again.')

    from openid.extensions import sreg
    sreg_request = sreg.SRegRequest(
        optional=['dob', 'gender', 'postcode'],
        required=['email', 'nickname', 'fullname', 'country', 'language', 'timezone'])
    auth_request.addExtension(sreg_request)

    from openid.extensions import ax
    ax_req = ax.FetchRequest()
    ax_req.add(ax.AttrInfo('http://schema.openid.net/contact/email',
          alias='email',required=True))
    ax_req.add(ax.AttrInfo('http://axschema.org/namePerson/first',
          alias='firstname',required=True))
    ax_req.add(ax.AttrInfo('http://axschema.org/namePerson/last',
          alias='lastname',required=True))
    ax_req.add(ax.AttrInfo('http://axschema.org/pref/language',
          alias='language',required=True))
    ax_req.add(ax.AttrInfo('http://axschema.org/contact/country/home',
          alias='country',required=True))
    auth_request.addExtension(ax_req)

    import urlparse
    parts = list(urlparse.urlparse(get_full_path(request)))
    # finish URL with the leading "/" character removed
    parts[2] = django.core.urlresolvers.reverse('openidgae.views.OpenIDFinish')[1:]

    continueUrl = request.GET.get('continue', '/')
    # Sanitize
    if continueUrl.find('//') >= 0 or not continueUrl.startswith('/'):
      continueUrl = '/'
    import urllib
    parts[4] = 'continue=%s' % urllib.quote_plus(continueUrl)
    parts[5] = ''
    return_to = urlparse.urlunparse(parts)

    realm = urlparse.urlunparse(parts[0:2] + [''] * 4)

    # save the session stuff
    session = openidgae.get_session(request, response)
    import pickle
    session.openid_stuff = pickle.dumps(c.session)
    session.put()

    # send the redirect!  we use a meta because appengine bombs out
    # sometimes with long redirect urls
    redirect_url = auth_request.redirectURL(realm, return_to)
    response.write(
        "<html><head><meta http-equiv=\"refresh\" content=\"0;url=%s\"></head><body></body></html>"
        % (redirect_url,))
    return response


def OpenIDFinish(request):
  initOpenId()
  response = django.http.HttpResponse()
  if request.method == 'GET':
    args = args_to_dict(request.GET)
    url = 'http://'+request.META['HTTP_HOST']+django.core.urlresolvers.reverse('openidgae.views.OpenIDFinish')
    session = openidgae.get_session(request, response)
    s = {}
    if session.openid_stuff:
      try:
        import pickle
        s = pickle.loads(str(session.openid_stuff))
      except:
        session.openid_stuff = None

    session.put()

    c = Consumer(s, get_store())
    auth_response = c.complete(args, url)

    sreg_response = {}
    ax_items = {}
    if auth_response.status == openid.consumer.consumer.SUCCESS:
      from openid.extensions import sreg
      sreg_response = sreg.SRegResponse.fromSuccessResponse(auth_response)
      sreg_response = dict(sreg_response.iteritems())
      logging.debug("sreg_response: %r" % sreg_response)

      from openid.extensions import ax
      ax_response = ax.FetchResponse.fromSuccessResponse(auth_response)
      logging.debug("ax_response: %r" % ax_response)
      if ax_response:
        ax_items = {
          'email': ax_response.get(
              'http://schema.openid.net/contact/email'),
          'firstname': ax_response.get(
              'http://axschema.org/namePerson/first'),
          'lastname': ax_response.get(
              'http://axschema.org/namePerson/last'),
          'language': ax_response.get(
              'http://axschema.org/pref/language'),
          'country': ax_response.get(
              'http://axschema.org/contact/country/home'),
        }
        logging.debug("ax_items: %r" % ax_items)

      openid_url = auth_response.getDisplayIdentifier()

      import models
      persons = models.Person.gql('WHERE openid = :1', openid_url)
      if persons.count() == 0:
        p = models.Person()
        p.openid = openid_url
        import pickle
        p.ax = pickle.dumps(ax_items, pickle.HIGHEST_PROTOCOL)
        p.sreg = pickle.dumps(sreg_response, pickle.HIGHEST_PROTOCOL)
        p.put()
      else:
        p = persons[0]
        if p.get_sreg_dict() != sreg_response or \
            p.get_ax_dict() != ax_items:
          p.ax = pickle.dumps(ax_items, pickle.HIGHEST_PROTOCOL)
          p.sreg = pickle.dumps(sreg_response, pickle.HIGHEST_PROTOCOL)
          p.put()

      s = openidgae.get_session(request, response)
      s.person = p.key()
      request.openidgae_logged_in_person = p

      s.put()

      continueUrl = request.GET.get('continue', '/')
      # Sanitize
      if continueUrl.find('//') >= 0 or not continueUrl.startswith('/'):
        continueUrl = '/'

      return django.http.HttpResponseRedirect(continueUrl)

    else:
      return show_main_page(request, 'OpenID verification failed :(')

def LogoutSubmit(request):
  initOpenId()
  response = django.http.HttpResponse()
  if request.method == 'GET':
    s = openidgae.get_session(request, response)
    if s:
      s.person = None
      s.put()

    continueUrl = request.GET.get('continue', '/')
    # Sanitize
    if continueUrl.find('//') >= 0 or not continueUrl.startswith('/'):
      continueUrl = '/'

    return django.http.HttpResponseRedirect(continueUrl)

def RelyingPartyXRDS(request):
  initOpenId()
  response = django.http.HttpResponse()
  if request.method == 'GET':
    xrds = """
<?xml version='1.0' encoding='UTF-8'?>
<xrds:XRDS
  xmlns:xrds='xri://$xrds'
  xmlns:openid='http://openid.net/xmlns/1.0'
  xmlns='xri://$xrd*($v*2.0)'>                                                                          
  <XRD>
    <Service>
      <Type>http://specs.openid.net/auth/2.0/return_to</Type>
      <URI>http://%s%s</URI>
    </Service>
</XRD>
</xrds:XRDS>      
""" % (request.META['HTTP_HOST'],django.core.urlresolvers.reverse('openidgae.views.OpenIDFinish'),)
    

    response['Content-Type'] = 'application/xrds+xml'
    response.write(xrds)
    return response