import MySQLdb
import sys
import datetime
import sys,os
import cherrypy
import hashlib

import smtplib
import email

import mailbox

from email.MIMEMultipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate

import subprocess

import time

from HTMLParser import HTMLParser

import json

import urllib

import httplib

import re

import StringIO

from cherrypy.lib import static

def redirect_if_authentication_is_required_and_session_is_not_authenticated(*args, **kwargs):

    conditions = cherrypy.request.config.get('auth.require', None)
    if conditions is not None:
        username = cherrypy.session.get('_cp_username')
        if not username:
            raise cherrypy.HTTPRedirect("/loginlogout/login")

def is_session_authenticated(*args, **kwargs):

    username = cherrypy.session.get('_cp_username')
    if username:
        return True
    else:
        return False

cherrypy.tools.auth = cherrypy.Tool('before_handler', redirect_if_authentication_is_required_and_session_is_not_authenticated)

def require(*conditions):
    """A decorator that appends conditions to the auth.require config
    variable."""
    def decorate(f):
        if not hasattr(f, '_cp_config'):
            f._cp_config = dict()
        if 'auth.require' not in f._cp_config:
            f._cp_config['auth.require'] = []
        f._cp_config['auth.require'].extend(conditions)
        return f
    return decorate

about_html_string = """
            Ecommunicate is intended to meet the need for electronic communication that is the opposite of private. All of the communication that takes place on this website is purposefully released to the public. Anyone, with or without an Ecommunicate account, can view the communication starting immediately when it is created and continuing indefinitely, similar to an online forum.   <br><br>
          
Text messaging (like Google Hangouts or WeChat) and e-mail (to other ecommunicate.ch e-mail addresses) are implemented already, and we hope to eventually add audio and video calling (like Skype). You can chat or e-mail yourself (after registering and logging in) or you can view other people's chat conversations or e-mail inboxes (see below). This website is experimental at this point. You should expect bugs, unexpected downtime, etc. Please contact ecommunicate.feedback@gmail.com for comments, feature requests, etc. <br><br>
  Below is a list of all of the services that we would like to provide. The ones that are operational are in bold.
<ol>
<li>Chat
<ol>
<li>Create
<ol>
<li><b>Browser</b>
<li><b>Android</b>
<li>iOS
</ol>
<li>View
<ol>
<li><b>Browser</b>
</ol>
</ol>
<li>E-mail
<ol>
<li>Create
<ol>
<li><b>Browser</b>
<li>Android
<li>iOS
</ol>
<li>View
<ol>
<li><b>Browser</b>
</ol>
</ol>
<li>Audio/Video Call
<ol>
<li>Create
<ol>
<li>Windows
<li>MacOS
<li>Android
<li>iOS
</ol>
<li>View/Listen
<ol>
<li>Browser
</ol>
</ol>
</ol>
"""

not_authenticated_menubar_html_string = """
<div id="header">
<div id="nav">
<ul class="menubar">
<li class="menubar"><a href="/">Home</a></li>
<li class="menubar"><a href="/view/">View</a></li>
<li class="menubar"><a href="/register/">Register</a></li>
<li class="menubar"><a href="/loginlogout/login/">Login</a></li>
<li class="menubar"><a href="/about">About</a></li>
</ul>
</div>
</div>
"""

authenticated_menubar_html_string = """
<div id="header">
<div id="nav">
<ul class="menubar">
<li class="menubar"><a href="/">Home</a></li>
<li class="menubar"><a href="/view/">View</a></li>
<li class="menubar"><a href="/email/">Email</a></li>
<li class="menubar"><a href="/chat/">Chat</a></li>
<li class="menubar"><a href="/loginlogout/logout/">Logout</a></li>
<li class="menubar"><a href="/about">About</a></li>
</ul>
</div>
</div>
"""

class About(object):

    @cherrypy.expose
    def index(self):

        issessionauthenticated = is_session_authenticated()

        if not issessionauthenticated:

            html_string = """
<html>
<head>
<title>
Ecommunicate
</title>
<style>
li.menubar {
        display: inline;
        padding: 20px;
}
</style>
</head>
<body>
<center><h1>Ecommunicate</h1>
<h3>A free online communication service</h3>
"""+not_authenticated_menubar_html_string+"""
<h4>About This Website</h4>
</center>
"""+about_html_string+"""
</body>
</html>
"""

        else:

            html_string = """
<html>
<head>
<title>
Ecommunicate
</title>
<style>
li.menubar {
        display: inline;
        padding: 20px;
}
</style>
</head>
<body>
<center><h1>Ecommunicate</h1>
<h3>A free online communication service</h3>
"""+authenticated_menubar_html_string+"""
<h4>About This Website</h4>
</center>
"""+about_html_string+"""
</body>
</html>
"""

        return html_string
