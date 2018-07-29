#!/usr/bin/env python
"""MAIN script for nasa-rose-datastore API connecting to Earth Engine using App Engine."""



# Works in the local development environment and when deployed.
# If successful, shows a single web page with the SRTM DEM
# displayed in a Google Map.  See accompanying README file for
# instructions on how to set up authentication.

import config

import httplib2
import json
import logging
import os


import ee
from google.appengine.api import urlfetch
from google.appengine.api import users
import jinja2
import webapp2

import ee_methods
import template_methods
import jinja_filters





# SET STATICS
urlfetch.set_default_fetch_deadline(180000)
httplib2.Http(timeout=180000)


# Set the JINJA_ENVIRONMENT
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
JINJA_ENVIRONMENT = jinja2.Environment(
    autoescape=True,
    loader=jinja2.FileSystemLoader(template_dir),
    extensions=['jinja2.ext.with_'])

# Register custom filters
JINJA_ENVIRONMENT.filters['is_in'] = jinja_filters.is_in
JINJA_ENVIRONMENT.filters['not_in'] = jinja_filters.not_in
JINJA_ENVIRONMENT.filters['make_string_range'] = jinja_filters.make_string_range
JINJA_ENVIRONMENT.filters['make_int_range'] = jinja_filters.make_int_range
JINJA_ENVIRONMENT.filters['divisibleby'] = jinja_filters.divisibleby


#####################################################
#   RUN APP - RUNS THE APPLICATION AND SETS WEBPAGE
####################################################
def runApp(self, app_name, method):
    '''
    :param self: webapp2.RequestHandler)
    :param app_name:
    :param method: PAGELOAD, POST or API
    :return: tv dictionary of template values
    '''
    try:
        tv = template_methods.set_template_values(
            self, app_name, method)
    except Exception as e:
        # This will trigger a hard 500 error
        # We can't set error and load the default page
        raise
    return tv




class defaultApplication(webapp2.RequestHandler):
    '''
    defaultApplication, defines:
        - get and post responses
        - error handling
        - logging
    tv: template_variables
    '''
    ee.Initialize(config.EE_CREDENTIALS)
    ee.data.setDeadline(180000)

    """Loading the main page or a sharelink will trigger a GET"""
    def get(self):
        if not self.request.arguments():
            # Initial page load
            tv = runApp(self, self.app_name, 'PAGELOAD')
            self.tv_logging(tv)
            return_vars = tv
            template = JINJA_ENVIRONMENT.get_template(self.appHTML)
            self.response.out.write(template.render(return_vars))
        else:
            try:
                tv = runApp(self, self.app_name, 'API')
                # Only return the query data
                return_vars = tv['query_data']
                self.response.out.write(json.dumps(return_vars))
            except Exception as e:
                tv = runApp(self, self.app_name, 'PAGELOAD')
                tv['error'] = str(e)
                tv['method'] = 'API'
                return_vars = tv
                template = JINJA_ENVIRONMENT.get_template(self.appHTML)
                self.response.out.write(template.render(return_vars))

    def post(self):
        tv = runApp(self, self.app_name, 'POST')
        self.tv_logging(tv)
        self.generateResponse(tv)

    def generateResponse(self, tv):
        """
        POST calls are executed via ajax calls
        Extract the return variables associated with each application
        If instead an error was set in the template_values, generate an error response
        """
        return_vars = {}
        if ('error' in tv.keys() and tv['error']):
            return_vars['error'] = tv['error']
            return_vars['method'] = tv['method']
        else:
            for var in config.statics['response_vars'][self.app_name]:
                try:
                    return_vars[var] = tv[var]
                except KeyError:
                    return_vars[var] = []
        self.response.out.write(json.dumps(return_vars))

    def handle_exception(self, exception, debug):
        """
        This catches unhandled Python exceptions in GET requests
        """
        logging.exception(exception)
        app_name = self.app_name
        tv = runApp(self, app_name, 'GET')
        tv['error'] = str(exception)
        self.generateResponse(tv)

    def tv_logging(self, tv):
        """
        Log important template values
        These values are will be written to the appEngine logger
        so that we can tracks what page requests are being made
        """
        # Skip form values and maxDates
        log_values = {
            k: v for k, v in tv.items()
            if not k.startswith('form') and
            not k.startswith('etdata')
        }
        # Log all values at once
        logging.info('{}'.format(log_values))

class AdminPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            if users.is_current_user_admin():
                self.response.write('You are an administrator.')
            else:
                self.response.write('You are not an administrator.')
        else:
            self.response.write('You are not logged in.')

class LogInPage(webapp2.RequestHandler):
    def get(self):
        # [START user_details]
        user = users.get_current_user()
        if user:
            nickname = user.nickname()
            logout_url = users.create_logout_url('/')
            greeting = 'Welcome, {}! (<a href="{}">sign out</a>)'.format(
                nickname, logout_url)
        else:
            login_url = users.create_login_url('/')
            greeting = '<a href="{}">Sign in</a>'.format(login_url)
        # [END user_details]
        self.response.write(
            '<html><body>{}</body></html>'.format(greeting))


# SET THE APPLICATIONS
class home(defaultApplication):
    app_name = 'home'
    appHTML = 'home.html'

class populate_db(defaultApplication):
    app_name = 'populate_db'
    appHTML = 'populate.html'

class depopulate_db(defaultApplication):
    app_name = 'depopulate_db'
    appHTML = 'populate.html'

class query_db(defaultApplication):
    app_name = 'query_db'
    appHTML = 'query_db.html'

app = webapp2.WSGIApplication([
    ('/', NASA_ROSES),
    ('/admin', AdminPage),
    ('/login', LogInPage),
    ('/databaseTasks', databaseTasks)
], debug=True)
