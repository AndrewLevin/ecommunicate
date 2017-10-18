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

chat_menubar_html_string = """

<div id="header">

<div id="nav">

<ul class="menubar">
<li class="menubar"><a href="/">Home</a></li>
<li class="menubar"><a href="/view/">View</a></li>
<li class="menubar"><a href="/email/">Email</a></li>
<li class="menubar">

<ul class = "submenubar">
<li class = "submenubar">

<ul class = "subsubmenubar">
<li class = "subsubmenubarleftmost"><a href="/chat">Chat</a></li>
<li class = "subsubmenubar"><a href="/loginlogout/logout">Logout</a></li>
<li class = "subsubmenubarrightmost"><a href="/about/">About</a></li>
</ul>

</li>

<li class = "submenubar" ><a href="/chat/makecontactrequests">Make Contact Requests</a></li>
<li class = "submenubar"><a href="/chat/respondtocontactrequests">Respond to Contact Requests</a></li>
</ul>
</ul>

</div>

</div>

"""

chat_menubar_style_html_string = """

ul.subsubmenubar {

text-align: left;
padding: 0;

}

li.subsubmenubarleftmost {
display: inline;
padding-left: 0px;
padding-right: 20px;
}

li.subsubmenubarrightmost {
display: inline;
padding-left: 20px;
padding-right: 0px;
}

li.subsubmenubar {
display: inline;
padding: 20px;

}

ul.submenubar {

list-style-type:none;
display: inline-block;
vertical-align:top;
text-align: left;
padding: 0;

}

li.submenubar {

display: block;

}


ul.menubar {

text-align: center;

}

li.menubar {
        display: inline;
        padding: 20px;
}

"""


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

"""+not_authenticated_menubar_html_string+"""

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
    cherrypy.config.update({'server.socket_port': 8443}) #port 443 for https or port 80 for http
#    cherrypy.config.update({'server.socket_port': 80})
    cherrypy.config.update({'server.socket_host': 'ec2-35-163-111-83.us-west-2.compute.amazonaws.com'})
    

    #cherrypy.tree.mount(Root())
    cherrypy.tree.mount(Root(),'/',{ '/favicon.ico': { 'tools.staticfile.on': True, 'tools.staticfile.filename': '/home/ec2-user/server/favicon.ico' } })

    cherrypy.server.ssl_module = 'builtin'
    cherrypy.server.ssl_certificate = "/etc/letsencrypt/live/ecommunicate.ch/fullchain.pem"
    cherrypy.server.ssl_private_key = "/etc/letsencrypt/live/ecommunicate.ch/privkey.pem"
    cherrypy.server.ssl_certificate_chain = "/etc/letsencrypt/live/ecommunicate.ch/fullchain.pem"


    cherrypy.engine.start()
    cherrypy.engine.block()

