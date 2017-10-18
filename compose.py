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

def msgfactory(fp):
    try:
        return email.message_from_file(fp)
    except email.Errors.MessageParseError:
        # Don't return None since that will
        # stop the mailbox iterator
        return ''

class Compose(object):
    @cherrypy.expose
    @require()
    def index(self):
        return """<html>
<head>
<style>
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
<h4>Compose</h4>
</center>
<br><br>
<center>
   <form id="compose_email" target="console_iframe" method="post" action="send" enctype="multipart/form-data">
   to: <br><br>
   <input type="text" id="to" name="to" size="100" /><br><br>
   cc: <br><br>
   <input type="text" id="cc" name="cc" size="100" /><br><br>
   subject: <br><br>
   <input type="text" id="subject" name="subject" size="100" /><br><br>
   attachments: <br><br>
   <input type="file" id="attachment1" name="attachment1"/>
   <input type="file" id="attachment2" name="attachment2" style="display:none;"/>
   <input type="file" id="attachment3" name="attachment3" style="display:none;"/>
   <input type="file" id="attachment4" name="attachment4" style="display:none;"/>
   <input type="file" id="attachment5" name="attachment5" style="display:none;"/>
   <input type="file" id="attachment6" name="attachment6" style="display:none;"/>
   <input type="file" id="attachment7" name="attachment7" style="display:none;"/>
   <input type="file" id="attachment8" name="attachment8" style="display:none;"/>
   <input type="file" id="attachment9" name="attachment9" style="display:none;"/>
   <input type="file" id="attachment10" name="attachment10" style="display:none;"/>
   <br><br>
   body: <br><br>
   <textarea name="body" rows="50" cols="200"></textarea> <br><br>
  <button id="send" type="submit">
  Send
  </button>
  </form>
  <iframe name="console_iframe" class="terminal" /></iframe>
</center>
</body>
<script type="text/javascript" src="https://code.jquery.com/jquery-3.1.0.js"></script>
<script type="text/javascript">
$('#attachment1').click(function(event) { $('#attachment2').css('display','block')  });
$('#attachment2').click(function(event) { $('#attachment3').css('display','block')  });
$('#attachment3').click(function(event) { $('#attachment4').css('display','block')  });
$('#attachment4').click(function(event) { $('#attachment5').css('display','block')  });
$('#attachment5').click(function(event) { $('#attachment6').css('display','block')  });
$('#attachment6').click(function(event) { $('#attachment7').css('display','block')  });
$('#attachment7').click(function(event) { $('#attachment8').css('display','block')  });
$('#attachment8').click(function(event) { $('#attachment9').css('display','block')  });
$('#attachment9').click(function(event) { $('#attachment10').css('display','block')  });
  </script>        
        </html>"""
    @cherrypy.expose
    def send(self, to, cc, subject, attachment1, attachment2, attachment3, attachment4, attachment5, attachment6, attachment7, attachment8, attachment9, attachment10, body):

        attachments = [attachment1, attachment2, attachment3, attachment4, attachment5, attachment6, attachment7, attachment8, attachment9, attachment10]

        def send_function():
            msg = MIMEMultipart()
            send_from = cherrypy.session.get('_cp_username')+"@ecommunicate.ch"
            #msg['From'] = 
            send_to = re.findall(r'[^\;\,\s]+',to)
            send_cc = re.findall(r'[^\;\,\s]+',cc)

            for email_address in (send_to + send_cc):
                if email_address.split("@")[1] != "ecommunicate.ch":
                    return "Can only send emails to ecommunicate.ch e-mail addresses."

            msg['To'] = COMMASPACE.join(send_to)
            msg['CC'] = COMMASPACE.join(send_cc)
            msg['Date'] = formatdate(localtime=True)
            msg['Subject'] = subject
            msg['Message-ID'] = email.Utils.make_msgid()

            mime_applications = []

            for attachment in attachments:
                if attachment.file != None and attachment.filename != "":
                    tmp_filename=os.popen("mktemp").read().rstrip('\n')
                    open(tmp_filename,'wb').write(attachment.file.read());
                    
                    if str(attachment.content_type) == "application/pdf":
                        mime_application = MIMEApplication(open(tmp_filename,'rb').read(),"pdf")
                        mime_application['Content-Disposition'] = 'attachment; filename="'+str(attachment.filename)+'"'
                        mime_applications.append(mime_application)

            try:
                print "andrew debug 0"

                msg.attach(MIMEText(body))

                print "andrew debug 1"

                for mime_application in mime_applications:
                    msg.attach(mime_application)

                print "andrew debug 2"

                smtpObj = smtplib.SMTP(port=25)

                print "andrew debug 3"

                smtpObj.connect()

                print "andrew debug 4"

                smtpObj.sendmail(send_from, send_to+send_cc, msg.as_string())
                
                print "andrew debug 5"

                smtpObj.close()

                print "andrew debug 6"

                sent_emails = mailbox.Maildir('/var/mail/vhosts/ecommunicate.ch-sent/'+cherrypy.session.get('_cp_username')+'/', msgfactory)

                print "andrew debug 7"

                add_return_value=sent_emails.add(email.message_from_string(msg.as_string()));
                
                print "andrew debug 8"

                dbname="ecommunicate"

                print "andrew debug 9"

                secrets_file=open("/home/ec2-user/secrets.txt")

                print "andrew debug 10"
                
                passwords=secrets_file.read().rstrip('\n')

                print "andrew debug 11"
            
                db_password = passwords.split('\n')[0]

                print "andrew debug 12"

                conn = MySQLdb.connect(host='ecommunicate-production.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='browser', passwd=db_password, port=3306)

                print "andrew debug 13"

                curs = conn.cursor()

                print "andrew debug 14"

                curs.execute("use "+dbname+";")

                print "andrew debug 15"

                curs.execute("insert into sent_emails set username = \""+cherrypy.session.get('_cp_username')+"\", id=\""+add_return_value+"\", sent_time=\""+time.strftime('%Y-%m-%d %H:%M:%S',email.utils.parsedate(msg['Date']))+"\";")

                print "andrew debug 16"
                
                curs.close()

                print "andrew debug 17"

                conn.commit()

                print "andrew debug 18"

                conn.close()

                print "andrew debug 19"

            except Exception as e:
                print "Error: unable to send email", e.__class__
              
        return send_function()
