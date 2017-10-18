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

from compose import Compose

from readone import ReadOne

from reply import Reply

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

class Email(object):

    compose = Compose()

    readone = ReadOne()

    reply = Reply()

    @cherrypy.expose
    @require()
    def index(self,sent="False"):

        if sent == "False":
            sent_bool = False
        else:
            sent_bool = True

        secrets_file=open("/home/ec2-user/secrets.txt")

        passwords=secrets_file.read().rstrip('\n')

        db_password = passwords.split('\n')[0]

        dbname = "ecommunicate"

        conn = MySQLdb.connect(host='ecommunicate-production.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='browser', passwd=db_password, port=3306)

        curs = conn.cursor()

        curs.execute("use "+dbname+";")

        if sent_bool == False:
            curs.execute("select * from received_emails where username = \""+cherrypy.session.get('_cp_username')+"\" order by received_time desc;")
        else:
            curs.execute("select * from sent_emails where username = \""+cherrypy.session.get('_cp_username')+"\" order by sent_time desc;")

        colnames = [desc[0] for desc in curs.description]

        emails=curs.fetchall()

        if sent_bool == False:
            #use the message factory so that you get MaildirMessages instead of rfc822.Messages
            
            try:
                emailbox = mailbox.Maildir('/var/mail/vhosts/ecommunicate.ch/'+cherrypy.session.get('_cp_username')+'/', factory=mailbox.MaildirMessage,create=False)
            except mailbox.NoSuchMailboxError:
                pass
                
        else: 
            emailbox = mailbox.Maildir('/var/mail/vhosts/ecommunicate.ch-sent/'+cherrypy.session.get('_cp_username')+'/', factory=mailbox.MaildirMessage)

        email_javascript_string = ""

        email_string = ""

        if "emails" in vars():

            for i,msg in  enumerate(emails):

                msg_dict=dict(zip(colnames, msg))

                em = emailbox.get_message(msg_dict["id"])

                email_javascript_string = email_javascript_string +"var email"+str(i)+" = document.getElementById('email"+str(i)+"');\n"

                email_javascript_string = email_javascript_string +"email"+str(i)+".addEventListener('mouseover',function(e) { $('#email"+str(i)+"').css('background-color','WhiteSmoke');  } ,  false);\n"

                if not sent_bool:
                    if msg_dict["is_read"]:
                        email_javascript_string = email_javascript_string +"email"+str(i)+".addEventListener('mouseout',function(e) { $('#email"+str(i)+"').css('background-color','White');  } ,  false);\n"
                    else:
                        email_javascript_string = email_javascript_string +"email"+str(i)+".addEventListener('mouseout',function(e) { $('#email"+str(i)+"').css('background-color','Gold');  } ,  false);\n"
                else:
                    email_javascript_string = email_javascript_string +"email"+str(i)+".addEventListener('mouseout',function(e) { $('#email"+str(i)+"').css('background-color','White');  } ,  false);\n"


                if sent_bool == False:
                    email_javascript_string = email_javascript_string +"email"+str(i)+".addEventListener('click',function(e) { window.open('/email/readone/?message_id="+msg_dict["id"]+"','_self')  } ,  false);\n"
                else:    
                    email_javascript_string = email_javascript_string +"email"+str(i)+".addEventListener('click',function(e) { window.open('/email/readone/?sent=True&&message_id="+msg_dict["id"]+"','_self')  } ,  false);\n"



                if email_string == "":
                    email_string = email_string+"<table border = \"1\" width = \"100%\" id=\"emaillist\" style=\"table-layout:fixed\" >"

                if msg_dict["is_read"]:
                    email_string = email_string + "<tr id=\"email"+str(i)+"\" style=\"background-color:white\">"
                else:
                    email_string = email_string + "<tr id=\"email"+str(i)+"\" style=\"background-color:gold\">"

                if sent_bool:
                    if 'To' in em:
                        if email.utils.parseaddr(em['To'])[0]:
                            email_string = email_string + "<td style=\"overflow:hidden;max-width:25%;width:25%;white-space:nowrap\"><b>"+email.utils.parseaddr(em[1]['To'])[0]+"</b></td>"
                        else:    
                            email_string = email_string + "<td style=\"overflow:hidden;max-width:25%;width:25%;white-space:nowrap\"><b>"+email.utils.parseaddr(em['To'])[1]+"</b></td>"
                    #email_string = email_string + email.utils.parseaddr(em[1]['From'])[1]+"<br>"            
                else:
                    if 'From' in em:
                        if email.utils.parseaddr(em['From'])[0]:
                            email_string = email_string + "<td style=\"overflow:hidden;max-width:25%;width:25%;white-space:nowrap\"><b>"+email.utils.parseaddr(em['From'])[0]+"</b></td>"
                        else:
                            email_string = email_string + "<td style=\"overflow:hidden;max-width:25%;width:25%;white-space:nowrap\"><b>"+email.utils.parseaddr(em['From'])[1]+"</b></td>"

                if 'Subject' in em:    
                    email_string = email_string + "<td style=\"overflow:hidden;max-width:30%;width:30%;white-space:nowrap\"><i>"+em['Subject']+"</i></td>"

                if em.is_multipart():
                    if em.get_payload()[0].is_multipart():
                        email_string = email_string + "<td style=\"overflow:hidden;max-width:35%;width:35%;white-space:nowrap\">"+em.get_payload()[0].get_payload()[0].get_payload()+"</td>"
                    else:
                
                        if em.get_payload()[0].get_payload().rstrip('\n'):
                            email_string = email_string + "<td style=\"overflow:hidden;max-width:35%;width:35%;white-space:nowrap\">"+em.get_payload()[0].get_payload().rstrip('\n')+"</td>"
                        else:
                            email_string = email_string + "<td style=\"overflow:hidden;max-width:35%;width:35%;white-space:nowrap\"></td>"
                else:
                    email_string = email_string + "<td style=\"overflow:hidden;max-width:35%;width:35%;white-space:nowrap\">"+em.get_payload()+"</td>"

                if 'Date' in em:
                    email_string = email_string + "<td id=\"table_divide\" style=\"overflow:hidden;max-width:10%;width:10%;white-space:nowrap\" >"+time.strftime("%d %b %H:%M",email.utils.parsedate(em['Date']))+"</td>"


                email_string = email_string + "</tr>"


            if email_string != "":    
                email_string = email_string+"</table>"

        curs.close()

        conn.close()
                

        return """<html>
<head>
<style>
a.button {
    -webkit-appearance: button;
    -moz-appearance: button;
    appearance: button;
    padding: 7px;    
    text-decoration: none;
    color: initial;
}
.terminal {
border: none; 
}
li.menubar {
        display: inline;
        padding: 20px;
}
</style>
<title>Ecommunicate</title>
</head>
<body>
<center><h1>Ecommunicate</h1>
<h3>A free online communication service</h3>
"""+authenticated_menubar_html_string+"""
<h4>Email</h4>
</center>
<br><br>
<table>
<tr>
<td width="150">
<a href="/email/compose/" class="button">Compose</a>
</td>
<td width="150">
<a href="/email/">Received</a>
</td>
<td width="150">
<a href="/email/?sent=True">Sent</a>
</td>
</tr>
</table>
<br><br>
"""+email_string+"""
</body>
<script type="text/javascript" src="https://code.jquery.com/jquery-3.1.0.js"></script> 
<script>
"""+email_javascript_string+"""
</script>
        </html>"""
