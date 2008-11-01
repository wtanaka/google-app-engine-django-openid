import django.http

def exampleMain(request):
   response = django.http.HttpResponse()
   response.write('<a href="/openid-login">Login</a>')
   return response
