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

import html_strings

from require import require

class About(object):

    @cherrypy.expose
    def index(self):

        issessionauthenticated = utils.is_session_authenticated()

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
"""+html_strings.not_authenticated_menubar_html_string+"""
<h4>About This Website</h4>
</center>
"""+html_strings.about_html_string+"""
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
"""+html_strings.authenticated_menubar_html_string+"""
<h4>About This Website</h4>
</center>
"""+html_strings.about_html_string+"""
</body>
</html>
"""

        return html_string
