# vim:ts=2:sw=2:et
#
# Google App Engine OpenID Consumer Django App
# http://code.google.com/p/google-app-engine-django-openid/
#
# Copyright (C) 2009 Wesley Tanaka <http://wtanaka.com/>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

class OpenIDMiddleware(object):
  """This middleware initializes some settings to make the
  python-openid library compatible with Google App Engine
  """
  def process_view(self, request, view_func, view_args, view_kwargs):
    from openid import fetchers
    import openidgae.fetcher
    fetchers.setDefaultFetcher(openidgae.fetcher.UrlfetchFetcher())

    # Switch logger to use logging package instead of stderr
    from openid import oidutil
    def myLoggingFunction(message, level=0):
      import logging
      logging.info(message)
    oidutil.log = myLoggingFunction
