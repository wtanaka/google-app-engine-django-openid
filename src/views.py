import django.http
import openidgae

def exampleMain(request):
   response = django.http.HttpResponse()
   response.write('<a href="%s">Login</a>' % openidgae.create_login_url('/'))
   return response
