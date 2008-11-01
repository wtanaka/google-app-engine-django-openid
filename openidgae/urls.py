from django.conf.urls.defaults import *

urlpatterns = patterns('',
  (r'^openid-home/$', 'openidgae.views.HomePage'),
  (r'^openid-user/$', 'openidgae.views.PersonPage'),
  (r'^openid-login/$', 'openidgae.views.LoginPage'),
  (r'^openid-logout/$', 'openidgae.views.LogoutSubmit'),
  (r'^openid-start/$', 'openidgae.views.OpenIDStartSubmit'),
  (r'^openid-finish/$', 'openidgae.views.OpenIDFinish'),
  (r'^rpxrds/$', 'openidgae.views.RelyingPartyXRDS'),
)
