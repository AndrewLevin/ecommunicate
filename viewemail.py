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

from viewreadone import ViewReadOne

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

class ViewEmail(object):

    readone = ViewReadOne()

    @cherrypy.expose
    def index(self,username,sent=False):

        username = username.strip('"')

        secrets_file=open("/home/ec2-user/secrets.txt")

        passwords=secrets_file.read().rstrip('\n')

        db_password = passwords.split('\n')[0]

        dbname = "ecommunicate"

        conn = MySQLdb.connect(host='ecommunicate-production.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='browser', passwd=db_password, port=3306)

        curs = conn.cursor()

        curs.execute("use "+dbname+";")

        if sent == False:
            curs.execute("select * from received_emails where username = \""+username+"\" order by received_time desc;")
        else:
            curs.execute("select * from sent_emails where username = \""+username+"\" order by sent_time desc;")

        colnames = [desc[0] for desc in curs.description]

        emails=curs.fetchall()

        username = username.strip('"')

        if sent == False:
            #use the message factory so that you get MaildirMessages instead of rfc822.Messages
            
            try:
                emailbox = mailbox.Maildir('/var/mail/vhosts/ecommunicate.ch/'+username+'/', factory=mailbox.MaildirMessage,create=False)
            except mailbox.NoSuchMailboxError:
                pass
                
        else: 
            emailbox = mailbox.Maildir('/var/mail/vhosts/ecommunicate.ch-sent/'+username+'/', factory=mailbox.MaildirMessage)

        email_javascript_string = ""

        email_string = ""

        if "emails" in vars():

            for i,msg in  enumerate(emails):

                msg_dict=dict(zip(colnames, msg))

                em = emailbox.get_message(msg_dict["id"])
                
                email_javascript_string = email_javascript_string +"var email"+str(i)+" = document.getElementById('email"+str(i)+"');\n"

                email_javascript_string = email_javascript_string +"email"+str(i)+".addEventListener('mouseover',function(e) { $('#email"+str(i)+"').css('background-color','WhiteSmoke');  } ,  false);\n"
                email_javascript_string = email_javascript_string +"email"+str(i)+".addEventListener('mouseout',function(e) { $('#email"+str(i)+"').css('background-color','White');  } ,  false);\n"
                if sent == False:
                    email_javascript_string = email_javascript_string +"email"+str(i)+".addEventListener('click',function(e) { window.open('/view/email/readone/?username=\""+username+"\"&&message_id="+msg_dict["id"]+"','_self')  } ,  false);\n"
                else:    
                    email_javascript_string = email_javascript_string +"email"+str(i)+".addEventListener('click',function(e) { window.open('/view/email/readone/?username=\""+username+"\"&&sent=True&&message_id="+msg_dict["id"]+"','_self')  } ,  false);\n"

                if email_string == "":
                    email_string = email_string+"<table border = \"1\" width = \"100%\" id=\"emaillist\" style=\"table-layout:fixed\" >"

                email_string = email_string + "<tr id=\"email"+str(i)+"\">"

                if sent:
                    if 'To' in em:
                        if email.utils.parseaddr(em['To'])[0]:
                            email_string = email_string + "<td style=\"overflow:hidden;max-width:25%;width:25%;white-space:nowrap\"><b>"+email.utils.parseaddr(em['To'])[0]+"</b></td>"
                        else:    
                            email_string = email_string + "<td style=\"overflow:hidden;max-width:25%;width:25%;white-space:nowrap\"><b>"+email.utils.parseaddr(em['To'])[1]+"</b></td>"
                    #email_string = email_string + email.utils.parseaddr(em[1]['From'])[1]+"<br>"            
                else:
                    if 'From' in em:
                        if email.utils.parseaddr(em['From'])[0]:
                            email_string = email_string + "<td style=\"overflow:hidden;max-width:25%;width:25%;white-space:nowrap\"><b>"+email.utils.parseaddr(em['From'])[0]+"</b></td>"
                        else:
                            email_string = email_string + "<td style=\"overflow:hidden;max-width:25%;width:25%;white-space:nowrap\"><b>"+email.utils.parseaddr(em['From'])[1]+"</b></td>"
                    #email_string = email_string + email.utils.parseaddr(em[1]['From'])[1]+"<br>"
                if 'Subject' in em:    
                    email_string = email_string + "<td style =\"overflow:hidden;max-width:30%;width:30%;white-space:nowrap\"><i>"+em['Subject']+"</i></td>"

            #return em[1].get_payload()[1].get_payload()
            
            #print type(em[1].get_payload())

                if em.is_multipart():
                    if em.get_payload()[0].is_multipart():
                        email_string = email_string + "<td style =\"overflow:hidden;max-width:35%;width:35%;white-space:nowrap\">"+em.get_payload()[0].get_payload()[0].get_payload()+"</td>"
                    else:
                
                        if em.get_payload()[0].get_payload().rstrip('\n'):
                            email_string = email_string + "<td style =\"overflow:hidden;max-width:35%;width:35%;white-space:nowrap\">"+em.get_payload()[0].get_payload().rstrip('\n')+"</td>"
                        else:
                            email_string = email_string + "<td style =\"overflow:hidden;max-width:35%;width:35%;white-space:nowrap\"></td>"
                else:
                    email_string = email_string + "<td style =\"overflow:hidden;max-width:35%;width:35%;white-space:nowrap\">"+em.get_payload()+"</td>"
                if 'Date' in em:
                    email_string = email_string + "<td id=\"table_divide\" style=\"overflow:hidden;max-width:10%;width:10%;white-space:nowrap\">"+time.strftime("%d %b %H:%M",email.utils.parsedate(em['Date']))+"</td>"


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
"""+(html_strings.authenticated_menubar_html_string if is_session_authenticated() else html_strings.not_authenticated_menubar_html_string)+"""
<h4>Email</h4>
</center>
<br><br>
<table>
<tr>
<td width="150">
</td>
<td width="150">
<a href="/view/email/?username=%22"""+username+"""%22">Received</a>
</td>
<td width="150">
<a href="/view/email/?username=%22"""+username+"""%22&&sent=True">Sent</a>
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
