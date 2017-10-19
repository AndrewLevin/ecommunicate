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

from attachment import Attachment

import html_strings

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

class ReadOne(object):

    attachment = Attachment()

    @cherrypy.expose
    @require()
    def index(self,message_id,sent="False"):

        if sent == "False":
            sent_bool = False
        else:
            sent_bool = True

        #the default message factory is the rfc822.Message for historical reasons (see https://docs.python.org/2/library/mailbox.html#maildir)
        if sent_bool == False:
            emails = mailbox.Maildir('/var/mail/vhosts/ecommunicate.ch/'+cherrypy.session.get('_cp_username')+'/',factory=mailbox.MaildirMessage,create=False)
        else:
            emails = mailbox.Maildir('/var/mail/vhosts/ecommunicate.ch-sent/'+cherrypy.session.get('_cp_username')+'/',factory=mailbox.MaildirMessage)

        em = emails.get_message(message_id)

        email_string = ""

        email_string = email_string+"<table border = \"1\" width = \"100%\"  >"

        if sent_bool:
            if 'To' in em:
                if email.utils.parseaddr(em['To'])[0]:
                    email_string = email_string + "<tr><td><b>To: </b>"+email.utils.parseaddr(em['To'])[0]+"</td></tr>"
                else:    
                    email_string = email_string + "<tr><td><b>To: </b>"+email.utils.parseaddr(em['To'])[1]+"</td></tr>"
            #email_string = email_string + email.utils.parseaddr(em[1]['From'])[1]+"<br>"            
        else:
            if 'From' in em:
                if email.utils.parseaddr(em['From'])[0]:
                    email_string = email_string + "<tr><td><b>From: </b>"+email.utils.parseaddr(em['From'])[0]+"</td></tr>"
                else:
                    email_string = email_string + "<tr><td><b>From: </b>"+email.utils.parseaddr(em['From'])[1]+"</td></tr>"
                #email_string = email_string + email.utils.parseaddr(em[1]['From'])[1]+"<br>"
        if 'Subject' in em:    
            email_string = email_string + "<tr><td><b>Subject: </b>"+em['Subject']+"</td></tr>"
        if 'Date' in em:
            email_string = email_string + "<tr><td><b>Date: </b>"+time.strftime("%d %b %H:%M",email.utils.parsedate(em['Date']))+"</td></tr>"

        attachment_string = ""

        body_string = ""

        if em.is_multipart():

            for payload in em.get_payload():
                if not payload.is_multipart():

                    if 'X-Attachment-Id' in payload and "Content-Description" in payload:

                        attachment_string = attachment_string + '<tr><td><a href="/email/readone/attachment/?message_id='+message_id+'&&attachment_id='+payload["X-Attachment-Id"]+'">'+payload["Content-Description"]+'</a></tr></td>'

                    else:
                        if 'Content-Type' in payload and ('text/plain' in payload['Content-Type'] or 'message/delivery-status' in payload['Content-Type'] or 'message/rfc822' in payload['Content-Type']):
                            body_string = body_string + "<tr><td>"+payload.get_payload()+"</td></tr>"
                else:
                    for subpayload in payload.get_payload():
                        if not subpayload.is_multipart():
                            if 'Content-Type' in subpayload and ('text/plain' in subpayload['Content-Type'] or 'message/delivery-status' in subpayload['Content-Type'] or 'message/rfc822' in subpayload['Content-Type']):
                                body_string = body_string + "<tr><td>"+subpayload.get_payload()+"</td></tr>"
                        else:
                            for subsubpayload in subpayload.get_payload():
                                if not subsubpayload.is_multipart():
                                    if 'Content-Type' in subsubpayload and ('text/plain' in subsubpayload['Content-Type'] or 'message/delivery-status' in subsubpayload['Content-Type'] or 'message/rfc822' in subsubpayload['Content-Type']):
                                        body_string = body_string + "<tr><td>"+subsubpayload.get_payload()+"</td></tr>"
                                else:
                                    pass
        else:

            body_string = body_string + "<tr><td>"+em.get_payload()+"</td></tr>"

        email_string = email_string+attachment_string

        email_string = email_string+body_string

        email_string = email_string+"</table>"
        
        secrets_file=open("/home/ec2-user/secrets.txt")

        passwords=secrets_file.read().rstrip('\n')

        db_password = passwords.split('\n')[0]

        dbname = "ecommunicate"

        conn = MySQLdb.connect(host='ecommunicate-production.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='browser', passwd=db_password, port=3306)

        curs = conn.cursor()

        curs.execute("use "+dbname+";")

        if not sent_bool:
            curs.execute("update received_emails set is_read=1 where username=\""+cherrypy.session.get('_cp_username')+"\" and id=\""+message_id+"\";");

        curs.close()

        conn.commit()

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
"""+(html_strings.authenticated_menubar_html_string if is_session_authenticated() else html_strings.not_authenticated_menubar_html_string)+"""
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
<td width="150">
<a href="/email/reply/?sent="""+str(sent)+"""&&message_id="""+message_id+"""" class="button">Reply</a>
</td>
</tr>
</table>
<br><br>
<center>
"""+email_string+"""
</center>
  
  
  <br>
  <br>
  </center>
</body>
<script>
</script>
        </html>"""
