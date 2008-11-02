from django.conf.urls.defaults import patterns

urlpatterns = patterns('',
  (r'^home/$', 'openidgae.views.HomePage'),
  (r'^user/$', 'openidgae.views.PersonPage'),
  (r'^login/$', 'openidgae.views.LoginPage'),
  (r'^logout/$', 'openidgae.views.LogoutSubmit'),
  (r'^start/$', 'openidgae.views.OpenIDStartSubmit'),
  (r'^finish/$', 'openidgae.views.OpenIDFinish'),
  (r'^rpxrds/$', 'openidgae.views.RelyingPartyXRDS'),
)
