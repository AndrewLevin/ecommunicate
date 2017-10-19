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

from viewemail import ViewEmail

from viewchat import ViewChat

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

import html_strings

class View(object):

    email = ViewEmail()

    chat = ViewChat()

    @cherrypy.expose
    def index(self):

        issessionauthenticated=is_session_authenticated()

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
"""

            html_string = html_string+"<center><h1>Ecommunicate</h1>"
            html_string = html_string+"<h3>A free online communication service</h3>"
            html_string = html_string+html_strings.not_authenticated_menubar_html_string+"""
<h4>View</h4>
</center>
"""
            html_string = html_string+"      Ecommunicate is a free online communication service in which all communication is viewable by anyone on the open internet instead of being private. E-mail to other ecommunicate.ch e-mail addresses and text messaging (like Google Hangouts or WeChat) are implemented already, and we hope to eventually add audio and video calling (like Skype). You can chat or e-mail yourself (after registering and logging in) or you can view other people's chat conversations or e-mail inboxes (see below). This website is experimental at this point. You should expect bugs, unexpected downtime, etc. Please contact ecommunicate.feedback@gmail.com for comments, feature requests, etc.<br>"

            html_string=html_string+"<br>"

            html_string = html_string + "<table>"

            html_string = html_string + "<tr><th>Chat Conversations</th><th>E-mail Boxes</th></tr>"

            html_string = html_string + "<tr>\n"

            html_string = html_string + "<td valign=\"top\">\n"

            html_string=html_string+"<ol>\n"

            secrets_file=open("/home/ec2-user/secrets.txt")

            passwords=secrets_file.read().rstrip('\n')

            db_password = passwords.split('\n')[0]

            dbname = "ecommunicate"

            conn = MySQLdb.connect(host='ecommunicate-production.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='browser', passwd=db_password, port=3306)

            curs = conn.cursor()

            curs.execute("use "+dbname+";")

            curs.execute("select DISTINCT username1,username2 from messages;")

            conversations = curs.fetchall()

            colnames = [desc[0] for desc in curs.description]

            for conversation in conversations:

                conversation_dict=dict(zip(colnames, conversation))
            
                html_string=html_string+"<li><a href=\"/view/chat/?username1=%22"+conversation_dict["username1"]+"%22&username2=%22"+conversation_dict["username2"]+"%22\">"+conversation_dict["username1"]+" and "+conversation_dict["username2"]+"</a><br></li>\n"

            html_string=html_string+"</ol>\n"

            html_string = html_string +"</td>\n"

            html_string = html_string +"<td valign=\"top\">\n"

            curs.execute("select username from user_info;")

            colnames = [desc[0] for desc in curs.description]

            usernames = curs.fetchall()

            html_string=html_string+"<ol>\n"

            for username in usernames:

                username_dict=dict(zip(colnames, username))

                html_string=html_string+"<li><a href=\"/view/email?username=%22"+username_dict["username"]+"%22\">"+username_dict["username"]+"</a><br></li>\n"

            html_string=html_string+"</ol>\n"

            html_string = html_string +"</td>\n"

            html_string = html_string + "</tr>\n"

            html_string = html_string + "</table>"


            html_string = html_string+"""
</body>
</html>
"""
            conn.close()

            return html_string

        elif issessionauthenticated:


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
"""

            html_string = html_string+"<center><h1>Ecommunicate</h1>"
            html_string = html_string+"<h3>A free online communication service</h3>"
            html_string = html_string+html_strings.authenticated_menubar_html_string+"""
<h4>View</h4>
</center>
"""

            html_string = html_string+"      Ecommunicate is a free online communication service in which all communication is viewable by anyone on the open internet instead of being private. E-mail to other ecommunicate.ch e-mail addresses and text messaging (like Google Hangouts or WeChat) are implemented already, and we hope to eventually add audio and video calling (like Skype). You can chat or e-mail yourself (after registering and logging in) or you can view other people's chat conversations or e-mail inboxes (see below). This website is experimental at this point. You should expect bugs, unexpected downtime, etc. Please contact ecommunicate.feedback@gmail.com for comments, feature requests, etc.<br>"

            html_string=html_string+"<br>"

            html_string = html_string + "<table>"

            html_string = html_string + "<tr><th>Chat Conversations</th><th>E-mail Boxes</th></tr>"

            html_string = html_string + "<tr>\n"

            html_string = html_string + "<td valign=\"top\">\n"

            html_string=html_string+"<ol>\n"

            secrets_file=open("/home/ec2-user/secrets.txt")

            passwords=secrets_file.read().rstrip('\n')

            db_password = passwords.split('\n')[0]

            dbname = "ecommunicate"

            conn = MySQLdb.connect(host='ecommunicate-production.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='browser', passwd=db_password, port=3306)

            curs = conn.cursor()

            curs.execute("use "+dbname+";")

            curs.execute("select DISTINCT username1,username2 from messages;")

            conversations = curs.fetchall()

            colnames = [desc[0] for desc in curs.description]

            for conversation in conversations:

                conversation_dict=dict(zip(colnames, conversation))
            
                html_string=html_string+"<li><a href=\"/view/chat/?username1=%22"+conversation_dict["username1"]+"%22&username2=%22"+conversation_dict["username2"]+"%22\">"+conversation_dict["username1"]+" and "+conversation_dict["username2"]+"</a><br></li>\n"

            html_string=html_string+"</ol>\n"

            html_string = html_string +"</td>\n"

            html_string = html_string +"<td valign=\"top\">\n"

            curs.execute("select username from user_info;")

            colnames = [desc[0] for desc in curs.description]

            usernames = curs.fetchall()

            html_string=html_string+"<ol>\n"

            for username in usernames:

                username_dict=dict(zip(colnames, username))

                html_string=html_string+"<li><a href=\"/view/email?username=%22"+username_dict["username"]+"%22\">"+username_dict["username"]+"</a><br></li>\n"

            html_string=html_string+"</ol>\n"

            html_string = html_string +"</td>\n"

            html_string = html_string + "</tr>\n"

            html_string = html_string + "</table>"

            html_string = html_string+"""
</body>
</html>
"""
            conn.close()

            return html_string
