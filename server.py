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

from view import View

from chat import Chat

from loginlogout import LogInLogOut

from register import Register

from about import About

from emails import Email

from compose import Compose

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

class Root(object):

    _cp_config = {
        'tools.sessions.on': True,
        'tools.auth.on': True,
        'tools.sessions.locking': 'explicit' #this and the acquire_lock and the release_lock statements in the login and logout functions are necessary so that multiple ajax requests can be processed in parallel in a single session
    }

    view = View()

    chat = Chat()

    loginlogout = LogInLogOut()

    register = Register()

    about = About()

    email = Email()

#    @cherrypy.expose
#    def default(self,*args):
#        return static.serve_file("/home/ec2-user/server/google_verification_file.html");        

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

"""

            html_string = html_string+"<center><h1>Ecommunicate</h1>"
            html_string = html_string+"<h3>A free online communication service</h3>"
            html_string = html_string+not_authenticated_menubar_html_string+"""

</center>

"""
            html_string = html_string+"Ecommunicate is a free online communication service in which all communication is viewable by anyone on the open internet instead of being private. E-mail to other ecommunicate.ch e-mail addresses and text messaging (like Google Hangouts or WeChat) are implemented already, and we hope to eventually add audio and video calling (like Skype). You can chat or e-mail yourself (after registering and logging in) or you can view other people's chat conversations or e-mail inboxes (see below). This website is experimental at this point. You should expect bugs, unexpected downtime, etc. Please contact ecommunicate.feedback@gmail.com for comments, feature requests, etc.<br>"

            html_string=html_string+"<br>"

            html_string = html_string + "<table>"

            html_string = html_string + "<tr><th>Chat Conversations</th><th>E-mail Boxes</th><td valign = \"top\" style=\"padding-left:100px\"><a href=\"https://play.google.com/store/apps/details?id=ch.ecommunicate.amlevin.chat\">Android Chat App<a></td></tr>"

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

            html_string = html_string + """

</body>
</html>

"""
            conn.close()

        else: #authenticated    
            html_string="""


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
            html_string = html_string+authenticated_menubar_html_string+"""
</center>

"""
            html_string = html_string+"Ecommunicate is a free online communication service in which all communication is viewable by anyone on the open internet instead of being private. E-mail to other ecommunicate.ch e-mail addresses and text messaging (like Google Hangouts or WeChat) are implemented already, and we hope to eventually add audio and video calling (like Skype). You can chat or e-mail yourself (after registering and logging in) or you can view other people's chat conversations or e-mail inboxes (see below). This website is experimental at this point. You should expect bugs, unexpected downtime, etc. Please contact ecommunicate.feedback@gmail.com for comments, feature requests, etc.<br>"

            html_string=html_string+"<br>"

            html_string = html_string + "<table>"

            html_string = html_string + "<tr><th>Chat Conversations</th><th>E-mail Boxes</th><td valign = \"top\" style=\"padding-left:100px\"><a href=\"https://play.google.com/store/apps/details?id=ch.ecommunicate.amlevin.chat\">Android Chat App<a></td></tr>"

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

def is_right_password(username, password):

    secrets_file=open("/home/ec2-user/secrets.txt")

    passwords=secrets_file.read().rstrip('\n')

    db_password = passwords.split('\n')[0]

    dbname = "ecommunicate"

    conn = MySQLdb.connect(host='ecommunicate-production.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='browser', passwd=db_password, port=3306)

    curs = conn.cursor()

    curs.execute("use "+dbname+";")

    curs.execute("select * from user_info where username = \""+username+"\";")

    colnames = [desc[0] for desc in curs.description]

    user_infos=curs.fetchall()

    if len(user_infos) == 0:
        return [False,"Login failed. The username that you entered was not found."]
    else:
        assert(len(user_infos) == 1)

    user_info=user_infos[0]

    user_info_dict=dict(zip(colnames, user_info))

    hashed_password = user_info_dict["hashed_password"]

    h = hashlib.sha256()

    h.update(password)

    conn.close()

    if h.hexdigest() == hashed_password:
        return [True,""]
    else:
        return [False,"Login failed. The password that you entered is not the one associated with the username that you entered."]

if __name__ == '__main__':
    cherrypy.config.update({'server.socket_port': 443}) #port 443 for https or port 80 for http
#    cherrypy.config.update({'server.socket_port': 80})
    cherrypy.config.update({'server.socket_host': 'ec2-35-163-111-83.us-west-2.compute.amazonaws.com'})
    

    #cherrypy.tree.mount(Root())
    cherrypy.tree.mount(Root(),'/',{ '/favicon.ico': { 'tools.staticfile.on': True, 'tools.staticfile.filename': '/home/ec2-user/server/favicon.ico' } })

    cherrypy.server.ssl_module = 'builtin'
    cherrypy.server.ssl_certificate = "/etc/letsencrypt/live/ecommunicate.ch/fullchain.pem"
    cherrypy.server.ssl_private_key = "/etc/letsencrypt/live/ecommunicate.ch/privkey.pem"
    cherrypy.server.ssl_certificate_chain = "/etc/letsencrypt/live/ecommunicate.ch/fullchain.pem"
    cherrypy.server.thread_pool = 50


    cherrypy.engine.start()
    cherrypy.engine.block()

