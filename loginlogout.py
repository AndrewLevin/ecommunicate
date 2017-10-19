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

class LogInLogOut(object):

    def login_html(self,  message="", from_page="/"):

        login_html_string = """
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
</style
</head>   
<body>
<center><h1>Ecommunicate</h1>
<h3>A free online communication service</h3>
"""+html_strings.not_authenticated_menubar_html_string+"""
<h4>Login</h4>
</center>
"""

        login_html_string = login_html_string+"<center>"
        login_html_string = login_html_string+"<form method=\"post\" action=\"/loginlogout/login\">"
        login_html_string = login_html_string+"<input type=\"hidden\" name=\"from_page\" value=\""+from_page+"\" />"
        login_html_string = login_html_string+"username: <br><br>"
        login_html_string = login_html_string+"<input type=\"text\" id=\"username\" name=\"username\" size=\"18\" /><br><br>"
        login_html_string = login_html_string+"password: <br><br>"
        login_html_string = login_html_string+"<input type=\"password\" id=\"password\" name=\"password\" size=\"18\" /> <br><br>"
        login_html_string = login_html_string+"<button type=\"submit\">"
        login_html_string = login_html_string+"Login"
        login_html_string = login_html_string+"</button>"
        if message != "":
            login_html_string = login_html_string+"<br><br>"
            login_html_string = login_html_string+message
        login_html_string = login_html_string+"</center>"
        login_html_string = login_html_string+"</body>"
        login_html_string = login_html_string+"</html>"

        return login_html_string    
        
        
    @cherrypy.expose
    def login(self, username=None, password=None, from_page="/"):

        if username is None or password is None:
            return self.login_html(from_page=from_page)
        
        [pass_password_check,error_msg] = is_right_password(username, password)
        if not pass_password_check:
            return self.login_html(error_msg, from_page)
        else:

            cherrypy.request.login = username

            cherrypy.session.acquire_lock() 

            cherrypy.session['_cp_username'] = username

            cherrypy.session.release_lock()

            raise cherrypy.HTTPRedirect(from_page)
    
    @cherrypy.expose
    def logout(self, from_page="/"):

        cherrypy.session.acquire_lock()

        cherrypy.session['_cp_username'] = None

        cherrypy.session.release_lock()

        cherrypy.request.login = None
        raise cherrypy.HTTPRedirect(from_page)
