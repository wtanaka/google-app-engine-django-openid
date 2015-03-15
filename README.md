OpenID Consumer/Relying Party (RP) for [Google App Engine Django](http://code.google.com/p/google-app-engine-django/) projects implemented as a Django app. 

Derived by [Wesley Tanaka](http://wtanaka.com/) from Brian Ellin's WSGI
[demand.openid.net OpenID consumer](http://code.google.com/p/demand/).

Patches/suggestions appreciated.

Join the [discussion group](http://groups.google.com/group/google-app-engine-django-openid)

To install with a new Google App Engine project:

  1. Get the [Google App Engine Helper for Django](http://code.google.com/p/google-app-engine-django/). You will need a [version which works with the Django bundled with the latest version of the App Engine SDK](http://github.com/wtanaka/google-app-engine-helper-for-django/tree/django096_compatible). 
  2. Get the google-app-engine-django-openid source (using the Source tab above) and copy it into the same directory, overwriting urls.py from the App Engine Helper distribution 
  3. add 'openidgae' to INSTALLED_APPS in settings.py 
  4. add 'openidgae.middleware.OpenIDMiddleware' to MIDDLEWARE_CLASSES in settings.py 

To install with an existing Google App Engine project:

  1. get the openid and openidgae directories from the subversion respository and put them in your main application directory 
  2. Modify your urls.py using [this urls.py](http://code.google.com/p/google-app-engine-django-openid/source/browse/trunk/src/urls.py) as an example 
  3. add 'openidgae' to INSTALLED_APPS in settings.py 
  4. add 'openidgae.middleware.OpenIDMiddleware' to MIDDLEWARE_CLASSES in settings.py 
