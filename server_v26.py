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
            Ecommunicate is intended to meet the need for electronic communication that is the opposite of private. Making online communication public instead of private could lead to increased levels of honesty, transparency, cooperation and decreased levels of deception, misunderstanding between people, and duplicative work. It is not clear whether this concept will catch on, but it is worth a try.<br><br>

          E-mail to other ecommunicate.ch e-mail addresses and text messaging (like Google Hangouts or WeChat) are implemented already, and we hope to eventually add audio and video calling (like Skype). You can chat or e-mail yourself (after registering and logging in) or you can view other people's chat conversations or e-mail inboxes (see below). This website is experimental at this point. You should expect bugs, unexpected downtime, etc. Please contact ecommunicate.feedback@gmail.com for comments, feature requests, etc. <br><br>

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

class Register(object):
    @cherrypy.expose
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

"""+not_authenticated_menubar_html_string+"""

<h4>Registration</h4>

</center>

      Ecommunicate is a free online communication service in which all communication is viewable by anyone on the open internet instead of being private. E-mail to other ecommunicate.ch e-mail addresses and text messaging (like Google Hangouts or WeChat) are implemented already, and we hope to eventually add audio and video calling (like Skype). You can chat or e-mail yourself (after registering and logging in) or you can view other people's chat conversations or e-mail inboxes. This website is experimental at this point. You should expect bugs, unexpected downtime, etc. Please contact ecommunicate.feedback@gmail.com for comments, feature requests, etc.<br> <br>

      Register here for your free account. Please remember your username and password, as there is no way to recover them at this time.

<br><br>

<center>

   <form id="register" target="console_iframe" method="post" action="register">

   username: <br><br>
   <input type="text" id="username" name="username" size="18" /><br><br>
   password: <br><br>
   <input type="password" id="password" name="password" size="18" /> <br><br>
   name: <br><br>
   <input type="text" id="name" name="name" size="18" /><br><br>


  <button id="register" type="submit">
  Register
  </button>

  </form>

  <iframe name="console_iframe" class="terminal" />

</center>
  
<script type="text/javascript" src="https://code.jquery.com/jquery-3.1.0.js"></script>

  <script type="text/javascript">

  $( document ).ready(function() {

    $( "button" ).click(function( event ) {


 $("iframe").attr('src', '');


    });

  });

  </script>        



  
  <br>
  <br>

  </center>

</body>
        </html>"""
    @cherrypy.expose
    def register(self, username, password,name):

#        $( "iframe" ).clear()
        def register_function():

            if len(username) > 30:
                yield "Username is too long."
                return
                
            for c in username:
                if c != 'a' and c != 'b' and c != 'c' and c != 'd' and c != 'e' and c != 'f' and c != 'g' and c != 'h' and c != 'i' and c != 'j' and c != 'k' and c != 'l' and c != 'm' and c != 'n' and c != 'o' and c != 'p' and c != 'q' and c != 'r' and c != 's' and c != 't' and c != 'u' and c != 'v' and c != 'w' and c != 'x' and c != 'y' and c != 'z' and c != 'A' and c != 'B' and c != 'C' and c != 'D' and c != 'E' and c != 'F' and c != 'G' and c != 'H' and c != 'I' and c != 'J' and c != 'K' and c != 'L' and c != 'M' and c != 'N' and c != 'O' and c != 'P' and c != 'Q' and c != 'R' and c != 'S' and c != 'T' and c != 'U' and c != 'V' and c != 'W' and c != 'X' and c != 'Y' and c != 'Z' and c != '0' and c != '1' and c != '2' and c != '3' and c != '4' and c != '5' and c != '6' and c != '7' and c != '8' and c != '9' and c != '_' and c != '-' and c != '.':
                    yield "The username contains a character that is not allowed."
                    return

            #only allow one person to register at a time
            ret=os.system("if [ -f /home/ec2-user/registering_someone ]; then exit 0; else exit 1; fi");

            if ret == 0:
                yield "Registration was not succesful. Please try again later."
                return

            os.system("touch /home/ec2-user/registering_someone");

            secrets_file=open("/home/ec2-user/secrets.txt")

            passwords=secrets_file.read().rstrip('\n')

            db_password = passwords.split('\n')[0]

            dbname = "ecommunicate"

            h = hashlib.sha256()

            h.update(password)

            conn = MySQLdb.connect(host='ecommunicate-production.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='browser', passwd=db_password, port=3306)

            curs = conn.cursor()

            curs.execute("use "+dbname+";")

            curs.execute("select * from user_info where username = \""+username+"\"")

            user_infos = curs.fetchall()

            if len(user_infos) > 0:
                yield "That username is already taken."
                return
            
            if len(password) < 6:
                yield "Please choose a password that is at least 6 characters."
                return
            
            curs.execute("insert into user_info set username = \""+username+"\", hashed_password = \""+h.hexdigest()+"\", name = \""+name+"\", registration_time = now(6)")

            conn.commit()

            os.system("echo \""+username+"@ecommunicate.ch ecommunicate.ch/"+username +"/\" >> /etc/postfix/vmailbox")

            os.system("postmap /etc/postfix/vmailbox")

            os.system("rm /home/ec2-user/registering_someone");

            yield "Your registration was succesful. Please remember your username and password, as there is no way to recover them at this time."

            conn.close()

        return register_function()



#from https://docs.python.org/2/library/mailbox.html
def msgfactory(fp):
    try:
        return email.message_from_file(fp)
    except email.Errors.MessageParseError:
        # Don't return None since that will
        # stop the mailbox iterator
        return ''

class Reply(object):
    @cherrypy.expose
    @require()
    def index(self,message_id,sent="False"):

        if sent == "False":
            sent_bool = False
        else:
            sent_bool = True
        
        #the default message factory is the rfc822.Message for historical reasons (see https://docs.python.org/2/library/mailbox.html#maildir)
        if sent_bool == False:

            try:
                emails = mailbox.Maildir('/var/mail/vhosts/ecommunicate.ch/'+cherrypy.session.get('_cp_username')+'/',factory=mailbox.MaildirMessage,create=False)
            except mailbox.NoSuchMailboxError:
                raise Exception

        else:
            emails = mailbox.Maildir('/var/mail/vhosts/ecommunicate.ch-sent/'+cherrypy.session.get('_cp_username')+'/',factory=mailbox.MaildirMessage)

        em = emails.get_message(message_id)

        subject = ""

        body = "\n\n"

        to = ""
        CC = ""
        

        if 'Date' in em:
            body = body +"On "+time.strftime("%d %b %H:%M",email.utils.parsedate(em['Date']))+", "

        if sent_bool:
            if 'To' in em:
                if email.utils.parseaddr(em['To'])[0]:
                    body = body+email.utils.parseaddr(em['To'])[0]+" wrote:\n\n"
                else:    
                    body = body+email.utils.parseaddr(em['To'])[1]+" wrote:\n\n"
        else:
            if 'From' in em:
                body = body+email.utils.parseaddr(em['From'])[0]+" wrote:\n"
                to = "\""+email.utils.parseaddr(em['From'])[1]+"\""

        if email.utils.getaddresses([em['CC']]) != []:
            for address_pair in email.utils.getaddresses([em['CC']]):
                if CC != "":
                    CC = CC + COMMASPACE + address_pair[0]
                else:
                    CC = CC + address_pair[0]

        if 'Subject' in em:  
            subject = subject+"\"Re: "+em['Subject']+"\""
            

        if em.is_multipart():
            if em.get_payload()[0].get_payload().rstrip('\n'):
                for line in em.get_payload()[0].get_payload().rstrip('\n').split('\n'):
                    body = body + ">"+line+"\n"
                
        else:
            for line in em.get_payload().split('\n'):
                body = body + ">"+line+"\n"

            

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

<h4>Reply</h4>

</center>

<br><br>

<center>

   <form id="compose_email" target="console_iframe" method="post" action="reply">

   to: <br><br>
   <input type="text" id="to" name="to" size="100" value="""+to+"""/><br><br>
   cc: <br><br>
   <input type="text" id="cc" name="cc" size="100" value='"""+CC+"""'/><br><br>
   subject: <br><br>
   <input type="text" id="subject" name="subject" size="100" value="""+subject+"""/><br><br>
   body: <br><br>
   <textarea name="body" rows="50" cols="200">"""+body+"""</textarea> <br><br>


  <button id="send" type="submit">
  Send
  </button>

  </form>

  <iframe name="console_iframe" class="terminal" />

</center>
  
<script type="text/javascript" src="https://code.jquery.com/jquery-3.1.0.js"></script>

  <script type="text/javascript">

  $( document ).ready(function() {

    $( "button" ).click(function( event ) {


 $("iframe").attr('src', '');


    });

  });

  </script>        



  
  <br>
  <br>

  </center>

</body>
        </html>"""
    @cherrypy.expose
    def reply(self, to, cc, subject, body):

        def reply_function():
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
            try:
                msg.attach(MIMEText(body))
                smtpObj = smtplib.SMTP(port=25)
                smtpObj.connect()
                smtpObj.sendmail(send_from, send_to+send_cc, msg.as_string())
                smtpObj.close()

                sent_emails = mailbox.Maildir('/var/mail/vhosts/ecommunicate.ch-sent/'+cherrypy.session.get('_cp_username')+'/', msgfactory)

                sent_emails.add(email.message_from_string(msg.as_string()));

            except Exception as e:
                print "Error: unable to send email", e.__class__
              
        return reply_function()

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
                msg.attach(MIMEText(body))
                for mime_application in mime_applications:
                    msg.attach(mime_application)

                smtpObj = smtplib.SMTP(port=25)
                smtpObj.connect()
                smtpObj.sendmail(send_from, send_to+send_cc, msg.as_string())
                smtpObj.close()

                sent_emails = mailbox.Maildir('/var/mail/vhosts/ecommunicate.ch-sent/'+cherrypy.session.get('_cp_username')+'/', msgfactory)

                add_return_value=sent_emails.add(email.message_from_string(msg.as_string()));

                dbname="ecommunicate"

                secrets_file=open("/home/ec2-user/secrets.txt")
                
                passwords=secrets_file.read().rstrip('\n')
            
                db_password = passwords.split('\n')[0]

                conn = MySQLdb.connect(host='ecommunicate-production.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='browser', passwd=db_password, port=3306)

                curs = conn.cursor()

                curs.execute("use "+dbname+";")

                curs.execute("insert into sent_emails set username = \""+cherrypy.session.get('_cp_username')+"\", id=\""+add_return_value+"\", sent_time=\""+time.strftime('%Y-%m-%d %H:%M:%S',email.utils.parsedate(msg['Date']))+"\";")

                curs.close()

                conn.commit()

                conn.close()

            except Exception as e:
                print "Error: unable to send email", e.__class__
              
        return send_function()


class Attachment(object):

    @cherrypy.expose
    def index(self,message_id,attachment_id,sent=False):

        if sent == False:
            #use the message factory so that you get MaildirMessages instead of rfc822.Messages
            try:
                emails = mailbox.Maildir('/var/mail/vhosts/ecommunicate.ch/'+cherrypy.session.get('_cp_username')+'/', factory=mailbox.MaildirMessage)
            except mailbox.NoSuchMailboxError:
                raise Exception
        else: 
            emails = mailbox.Maildir('/var/mail/vhosts/ecommunicate.ch-sent/'+cherrypy.session.get('_cp_username')+'/', factory=mailbox.MaildirMessage)

        em = emails.get_message(message_id)

        if not em.is_multipart():
            raise Exception

        for payload in em.get_payload():
            if payload.is_multipart():
                continue
            if 'X-Attachment-Id' in payload and payload["X-Attachment-Id"] == attachment_id:

                tmp_filename=os.popen("mktemp").read().rstrip('\n')

                open(tmp_filename,'wb').write(payload.get_payload(decode=True))

                #stringio = StringIO.StringIO()
                #stringio.write(payload.get_payload(decode=True))

                return static.serve_file(tmp_filename, "application/x-download", "attachment", payload['Content-Description'])        

class ReadOne(object):

    attachment = Attachment()

    @cherrypy.expose
    @require()
    def index(self,message_id,sent=False):

        #the default message factory is the rfc822.Message for historical reasons (see https://docs.python.org/2/library/mailbox.html#maildir)
        if sent == False:
            emails = mailbox.Maildir('/var/mail/vhosts/ecommunicate.ch/'+cherrypy.session.get('_cp_username')+'/',factory=mailbox.MaildirMessage,create=False)
        else:
            emails = mailbox.Maildir('/var/mail/vhosts/ecommunicate.ch-sent/'+cherrypy.session.get('_cp_username')+'/',factory=mailbox.MaildirMessage)

        em = emails.get_message(message_id)

        email_string = ""

        email_string = email_string+"<table border = \"1\" width = \"100%\"  >"

        if sent:
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

"""+(authenticated_menubar_html_string if is_session_authenticated() else not_authenticated_menubar_html_string)+"""

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


class Email(object):

    compose = Compose()

    readone = ReadOne()

    reply = Reply()

    @cherrypy.expose
    @require()
    def index(self,sent=False):

        if sent == False:
            #use the message factory so that you get MaildirMessages instead of rfc822.Messages
            try:
                emails = mailbox.Maildir('/var/mail/vhosts/ecommunicate.ch/'+cherrypy.session.get('_cp_username')+'/', factory=mailbox.MaildirMessage,create=False)
            except mailbox.NoSuchMailboxError:
                pass
            
        else: 
            emails = mailbox.Maildir('/var/mail/vhosts/ecommunicate.ch-sent/'+cherrypy.session.get('_cp_username')+'/', factory=mailbox.MaildirMessage)

        email_javascript_string = ""

        email_string = ""

        if "emails" in vars():

            for i,em in enumerate(sorted(emails.items(), key = lambda tup : email.utils.parsedate(tup[1]['Date']), reverse = True)):

                email_javascript_string = email_javascript_string +"var email"+str(i)+" = document.getElementById('email"+str(i)+"');\n"
                
                email_javascript_string = email_javascript_string +"email"+str(i)+".addEventListener('mouseover',function(e) { $('#email"+str(i)+"').css('background-color','WhiteSmoke');  } ,  false);\n"
                email_javascript_string = email_javascript_string +"email"+str(i)+".addEventListener('mouseout',function(e) { $('#email"+str(i)+"').css('background-color','White');  } ,  false);\n"
                if sent == False:
                    email_javascript_string = email_javascript_string +"email"+str(i)+".addEventListener('click',function(e) { window.open('/email/readone/?message_id="+em[0]+"','_self')  } ,  false);\n"
                else:    
                    email_javascript_string = email_javascript_string +"email"+str(i)+".addEventListener('click',function(e) { window.open('/email/readone/?sent=True&&message_id="+em[0]+"','_self')  } ,  false);\n"



                if email_string == "":
                    email_string = email_string+"<table border = \"1\" width = \"100%\" id=\"emaillist\" style=\"table-layout:fixed\" >"

                email_string = email_string + "<tr id=\"email"+str(i)+"\">"

                if sent:
                    if 'To' in em[1]:
                        if email.utils.parseaddr(em[1]['To'])[0]:
                            email_string = email_string + "<td style=\"overflow:hidden;max-width:25%;width:25%;white-space:nowrap\"><b>"+email.utils.parseaddr(em[1]['To'])[0]+"</b></td>"
                        else:    
                            email_string = email_string + "<td style=\"overflow:hidden;max-width:25%;width:25%;white-space:nowrap\"><b>"+email.utils.parseaddr(em[1]['To'])[1]+"</b></td>"
                    #email_string = email_string + email.utils.parseaddr(em[1]['From'])[1]+"<br>"            
                else:
                    if 'From' in em[1]:
                        if email.utils.parseaddr(em[1]['From'])[0]:
                            email_string = email_string + "<td style=\"overflow:hidden;max-width:25%;width:25%;white-space:nowrap\"><b>"+email.utils.parseaddr(em[1]['From'])[0]+"</b></td>"
                        else:
                            email_string = email_string + "<td style=\"overflow:hidden;max-width:25%;width:25%;white-space:nowrap\"><b>"+email.utils.parseaddr(em[1]['From'])[1]+"</b></td>"

                if 'Subject' in em[1]:    
                    email_string = email_string + "<td style=\"overflow:hidden;max-width:30%;width:30%;white-space:nowrap\"><i>"+em[1]['Subject']+"</i></td>"

                if em[1].is_multipart():
                    if em[1].get_payload()[0].is_multipart():
                        email_string = email_string + "<td style=\"overflow:hidden;max-width:35%;width:35%;white-space:nowrap\">"+em[1].get_payload()[0].get_payload()[0].get_payload()+"</td>"
                    else:
                
                        if em[1].get_payload()[0].get_payload().rstrip('\n'):
                            email_string = email_string + "<td style=\"overflow:hidden;max-width:35%;width:35%;white-space:nowrap\">"+em[1].get_payload()[0].get_payload().rstrip('\n')+"</td>"
                        else:
                            email_string = email_string + "<td style=\"overflow:hidden;max-width:35%;width:35%;white-space:nowrap\"></td>"
                else:
                    email_string = email_string + "<td style=\"overflow:hidden;max-width:35%;width:35%;white-space:nowrap\">"+em[1].get_payload()+"</td>"

                if 'Date' in em[1]:
                    email_string = email_string + "<td id=\"table_divide\" style=\"overflow:hidden;max-width:10%;width:10%;white-space:nowrap\" >"+time.strftime("%d %b %H:%M",email.utils.parsedate(em[1]['Date']))+"</td>"


                email_string = email_string + "</tr>"


            if email_string != "":    
                email_string = email_string+"</table>"


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

class ViewAttachment(object):

    @cherrypy.expose
    def index(self,username,message_id,attachment_id,sent=False):

        username = username.strip('"')

        if sent == False:
            #use the message factory so that you get MaildirMessages instead of rfc822.Messages
            try:
                emails = mailbox.Maildir('/var/mail/vhosts/ecommunicate.ch/'+username+'/', factory=mailbox.MaildirMessage,create=False)
            except mailbox.NoSuchMailboxError:
                raise Exception
        else: 
            emails = mailbox.Maildir('/var/mail/vhosts/ecommunicate.ch-sent/'+username+'/', factory=mailbox.MaildirMessage)

        em = emails.get_message(message_id)

        if not em.is_multipart():
            raise Exception

        for payload in em.get_payload():
            if payload.is_multipart():
                continue
            if 'X-Attachment-Id' in payload and payload["X-Attachment-Id"] == attachment_id:

                tmp_filename=os.popen("mktemp").read().rstrip('\n')

                open(tmp_filename,'wb').write(payload.get_payload(decode=True))

                #stringio = StringIO.StringIO()
                #stringio.write(payload.get_payload(decode=True))

                return static.serve_file(tmp_filename, "application/x-download", "attachment", payload['Content-Description'])        

class ViewReadOne(object):

    attachment = ViewAttachment()

    @cherrypy.expose
    def index(self,username,message_id,sent=False):

        username = username.strip('"')

        #the default message factory is the rfc822.Message for historical reasons (see https://docs.python.org/2/library/mailbox.html#maildir)
        if sent == False:
            try:
                emails = mailbox.Maildir('/var/mail/vhosts/ecommunicate.ch/'+username+'/',factory=mailbox.MaildirMessage,create=False)
            except mailbox.NoSuchMailboxError:
                raise Exception
        else:
            emails = mailbox.Maildir('/var/mail/vhosts/ecommunicate.ch-sent/'+username+'/',factory=mailbox.MaildirMessage)

        em = emails.get_message(message_id)

        email_string = ""

        email_string = email_string+"<table border = \"1\" width = \"100%\"  >"

        if sent:
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

                        attachment_string = attachment_string + '<tr><td><a href="/view/email/readone/attachment/?username='+username+'message_id='+message_id+'&&attachment_id='+payload["X-Attachment-Id"]+'">'+payload["Content-Description"]+'</a></tr></td>'

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

"""+(authenticated_menubar_html_string if is_session_authenticated() else not_authenticated_menubar_html_string)+"""

</center>

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



class ViewEmail(object):

    readone = ViewReadOne()

    @cherrypy.expose
    def index(self,username,sent=False):

        username = username.strip('"')

        if sent == False:
            #use the message factory so that you get MaildirMessages instead of rfc822.Messages
            
            try:
                emails = mailbox.Maildir('/var/mail/vhosts/ecommunicate.ch/'+username+'/', factory=mailbox.MaildirMessage,create=False)
            except mailbox.NoSuchMailboxError:
                pass
                
        else: 
            emails = mailbox.Maildir('/var/mail/vhosts/ecommunicate.ch-sent/'+username+'/', factory=mailbox.MaildirMessage)

        email_javascript_string = ""

        email_string = ""

        if "emails" in vars():

            for i,em in enumerate(sorted(emails.items(), key = lambda tup : email.utils.parsedate(tup[1]['Date']), reverse = True)):

                email_javascript_string = email_javascript_string +"var email"+str(i)+" = document.getElementById('email"+str(i)+"');\n"

                email_javascript_string = email_javascript_string +"email"+str(i)+".addEventListener('mouseover',function(e) { $('#email"+str(i)+"').css('background-color','WhiteSmoke');  } ,  false);\n"
                email_javascript_string = email_javascript_string +"email"+str(i)+".addEventListener('mouseout',function(e) { $('#email"+str(i)+"').css('background-color','White');  } ,  false);\n"
                if sent == False:
                    email_javascript_string = email_javascript_string +"email"+str(i)+".addEventListener('click',function(e) { window.open('/view/email/readone/?username=\""+username+"\"&&message_id="+em[0]+"','_self')  } ,  false);\n"
                else:    
                    email_javascript_string = email_javascript_string +"email"+str(i)+".addEventListener('click',function(e) { window.open('/view/email/readone/?username=\""+username+"\"&&sent=True&&message_id="+em[0]+"','_self')  } ,  false);\n"

                if email_string == "":
                    email_string = email_string+"<table border = \"1\" width = \"100%\" id=\"emaillist\" style=\"table-layout:fixed\" >"

                email_string = email_string + "<tr id=\"email"+str(i)+"\">"

                if sent:
                    if 'To' in em[1]:
                        if email.utils.parseaddr(em[1]['To'])[0]:
                            email_string = email_string + "<td style=\"overflow:hidden;max-width:25%;width:25%;white-space:nowrap\"><b>"+email.utils.parseaddr(em[1]['To'])[0]+"</b></td>"
                        else:    
                            email_string = email_string + "<td style=\"overflow:hidden;max-width:25%;width:25%;white-space:nowrap\"><b>"+email.utils.parseaddr(em[1]['To'])[1]+"</b></td>"
                    #email_string = email_string + email.utils.parseaddr(em[1]['From'])[1]+"<br>"            
                else:
                    if 'From' in em[1]:
                        if email.utils.parseaddr(em[1]['From'])[0]:
                            email_string = email_string + "<td style=\"overflow:hidden;max-width:25%;width:25%;white-space:nowrap\"><b>"+email.utils.parseaddr(em[1]['From'])[0]+"</b></td>"
                        else:
                            email_string = email_string + "<td style=\"overflow:hidden;max-width:25%;width:25%;white-space:nowrap\"><b>"+email.utils.parseaddr(em[1]['From'])[1]+"</b></td>"
                    #email_string = email_string + email.utils.parseaddr(em[1]['From'])[1]+"<br>"
                if 'Subject' in em[1]:    
                    email_string = email_string + "<td style =\"overflow:hidden;max-width:30%;width:30%;white-space:nowrap\"><i>"+em[1]['Subject']+"</i></td>"

            #return em[1].get_payload()[1].get_payload()
            
            #print type(em[1].get_payload())

                if em[1].is_multipart():
                    if em[1].get_payload()[0].is_multipart():
                        email_string = email_string + "<td style =\"overflow:hidden;max-width:35%;width:35%;white-space:nowrap\">"+em[1].get_payload()[0].get_payload()[0].get_payload()+"</td>"
                    else:
                
                        if em[1].get_payload()[0].get_payload().rstrip('\n'):
                            email_string = email_string + "<td style =\"overflow:hidden;max-width:35%;width:35%;white-space:nowrap\">"+em[1].get_payload()[0].get_payload().rstrip('\n')+"</td>"
                        else:
                            email_string = email_string + "<td style =\"overflow:hidden;max-width:35%;width:35%;white-space:nowrap\"></td>"
                else:
                    email_string = email_string + "<td style =\"overflow:hidden;max-width:35%;width:35%;white-space:nowrap\">"+em[1].get_payload()+"</td>"
                if 'Date' in em[1]:
                    email_string = email_string + "<td id=\"table_divide\" style=\"overflow:hidden;max-width:10%;width:10%;white-space:nowrap\">"+time.strftime("%d %b %H:%M",email.utils.parsedate(em[1]['Date']))+"</td>"


                email_string = email_string + "</tr>"


            if email_string != "":    
                email_string = email_string+"</table>"


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

"""+(authenticated_menubar_html_string if is_session_authenticated() else not_authenticated_menubar_html_string)+"""

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


class ViewChat(object):
    @cherrypy.expose
    def index(self,username1=None,username2=None):

        if username1 != None and username2 != None:    

            html_string_usernames="username1="+username1+"\n"
            html_string_usernames=html_string_usernames+"username2="+username2

            return """<html>
<head><title>open</title>

<style>

ul.menubar {

text-align: center;

}

li.menubar {
        display: inline;
        padding: 20px;
}

ul {
    list-style:none;
    padding-left:0;
}

    .terminal {
    width: 100%;
    height: 30em;
    border: none;

}
    .messageerrorbox {
    width: 100%;
    height: 1em;
    border: none;

}
</style>

</head>
<body>

</body>

<center><h1>Ecommunicate</h1>

<h3>A free online communication service</h3>

"""+(authenticated_menubar_html_string if is_session_authenticated() else not_authenticated_menubar_html_string)+"""


<h4>View</h4>

</center>

<iframe id="console_iframe2" name="console_iframe2" class="terminal" /></iframe>


<script type="text/javascript" src="https://code.jquery.com/jquery-3.1.0.js"></script> 

<script>

messages_list = "";
messages_list_old = "";
"""+html_string_usernames+"""
max_time = ""

function update_messages(){

    if (messages_list != "") {

            var console_iframe2 = document.getElementById('console_iframe2');

            //clear the iframe
            console_iframe2.contentWindow.document.open();
            console_iframe2.contentWindow.document.close();

            for ( var i = 0, l = messages_list.length; i < l; i++ ) {
                console_iframe2.contentWindow.document.write(messages_list[i][0]+": "+messages_list[i][1]);
                console_iframe2.contentWindow.document.write("<br>");
            }

            var console_iframe2_contentWindow_document = console_iframe2.contentWindow.document;

            //this will "over-scroll", but it works i.e. it moves to the bottom    

            $(console_iframe2_contentWindow_document).scrollTop($(console_iframe2_contentWindow_document).height());  
       
    }

}

function view_recursive() {

get_messages_url = "get_messages?username1="+username1+"&username2="+username2+"&upon_update=True&client_max_time="+max_time;

   $.ajax({
      url: get_messages_url,
      type: 'GET',
      dataType: 'html',
      success: function(data) {

         parsed_data = JSON.parse(data);
         messages_list = parsed_data[0];
         max_time = parsed_data[1];

         messages_list_old = messages_list;

         update_messages();  

         view_recursive();
      }
   });

}

function view_initial() {

get_messages_url = 'get_messages?username1='+username1+'&username2='+username2;

   $.ajax({
      url: get_messages_url,
      type: 'GET',
      dataType: 'html',
      success: function(data) {

         parsed_data = JSON.parse(data);

         messages_list = parsed_data[0];

         max_time=parsed_data[1]; 

         messages_list_old = messages_list;

         update_messages(); 

         view_recursive();

      }
   });

}

$(document).ready(function() {

   view_initial();

});


</script>

        </html>"""


    @cherrypy.expose
    def get_messages(self,username1,username2,upon_update=False,client_max_time=""):

        sorted_usernames= sorted([username1,username2])

        username1=sorted_usernames[0]

        username2=sorted_usernames[1]

        secrets_file=open("/home/ec2-user/secrets.txt")

        passwords=secrets_file.read().rstrip('\n')

        db_password = passwords.split('\n')[0]

        dbname = "ecommunicate"

        conn = MySQLdb.connect(host='ecommunicate-production.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='browser', passwd=db_password, port=3306)

        if upon_update:

            #the connection will timeout eventually
            for i in range(0,1000):

                conn.commit()
                
                curs = conn.cursor()

                curs.execute("use "+dbname+";")

                curs.execute("select MAX(time) from messages where username1=\""+username1+"\" and username2=\""+username2+"\";")

                server_max_time = curs.fetchall()[0][0]

                if server_max_time != None and server_max_time > datetime.datetime.strptime(client_max_time,"%Y-%m-%d %H:%M:%S.%f"):
                    break

                time.sleep(0.1)


        #conn = MySQLdb.connect(host='tutorial-db-instance.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='open', passwd=db_password, port=3306)

        curs = conn.cursor()

        curs.execute("use "+dbname+";")

        messages_list = []

        curs.execute("select * from messages where username1 = \""+username1+"\" and username2 = \""+username2+"\" order by time;")

        colnames = [desc[0] for desc in curs.description]

        messages=curs.fetchall()

        return_string=""

        if len(messages) > 0:

            for message in messages:

                message_dict=dict(zip(colnames, message))

                if message_dict["forward"] == 1:
                    return_string=return_string+str(message_dict["username1"] +": " + message_dict["message"]+"<br>");
                    messages_list.append([message_dict["username1"], message_dict["message"]])
                elif message_dict["forward"] == 0:
                    return_string=return_string+str(message_dict["username2"] + ": " + message_dict["message"]+"<br>");
                    messages_list.append([message_dict["username2"], message_dict["message"]])

        #return str(messages_json)

        curs.execute("select MAX(time) from messages where username1 = \""+username1+"\" and username2 = \""+username2+"\";")

        max_time = str(curs.fetchall()[0][0])

        curs.close()

        conn.close()

        return json.dumps([messages_list,max_time])


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
            html_string = html_string+not_authenticated_menubar_html_string+"""
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
            html_string = html_string+authenticated_menubar_html_string+"""

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

class MakeContactRequest(object):

    _cp_config = {
        'tools.sessions.on': True,
        'tools.auth.on': True
    }

    @cherrypy.expose
    @require()
    def index(self):

        return """<html>
<head><title>Ecommunicate</title>

<style>

"""+chat_menubar_style_html_string+"""

.messageerrorbox {
    width: 100%;
    height: 5em;
    border: none;
}

</style>

</head>
<body>

<center><h1>Ecommunicate</h1>

<h3>A free online communication service</h3>

"""+chat_menubar_html_string +"""



</center>

<h2>Make a contact request </h2>

<form id="contact_request_form" target="console_iframe3" method="post" action="contact_request">
  Username: <br><br>
  <input type="text" id="username2" name="username2" size="18" /> <br><br>

Message: <br><br>
  <input type="text" id="message" name="message" size="100" /> <br><br>
  <button id="contact_request" class="fg-button ui-state-default ui-corner-all" type="submit">
  Submit
  </button>
  </form>

  <iframe name="console_iframe3" class="messageerrorbox" /> </iframe>

</body>
        </html>"""


    @cherrypy.expose
    def contact_request(self, username2, message):

        if username2 == cherrypy.session.get('_cp_username'):
            return "You cannot make a contact request for yourself."
        
        secrets_file=open("/home/ec2-user/secrets.txt")

        passwords=secrets_file.read().rstrip('\n')

        db_password = passwords.split('\n')[0]

        dbname = "ecommunicate"

        conn = MySQLdb.connect(host='ecommunicate-production.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='browser', passwd=db_password, port=3306)

        curs = conn.cursor()

        curs.execute("use "+dbname+";")
            
        curs.execute("select * from user_info where username = \""+username2+"\";")

        if len(curs.fetchall()) == 0:
            return "Username "+username2+" does not exist."

        username1=cherrypy.session.get('_cp_username')

        sorted_usernames= sorted([username1,username2])

        if sorted_usernames == [username1,username2]:
            forward=str(1)
        else:
            forward=str(0)

        original_username2 = username2    

        username1 = sorted_usernames[0]
    
        username2 = sorted_usernames[1]    

        curs.execute("select * from contact_requests where username1 = \""+username1+"\" and username2 = \""+username2+"\";")

        contact_requests = curs.fetchall()

        if len(contact_requests) > 0:
            return "Contact request already made between these two users."

        curs.execute("select * from contacts where username1 = \""+username1+"\" and username2 = \""+username2+"\";")

        contacts = curs.fetchall()

        if len(contacts) > 0:
            return "Contact request already made between these two users."

        curs.execute("insert into contact_requests set username1 = \""+username1+"\", username2 = \""+username2+"\", message = \""+message+"\", forward="+forward+", request_time = now(6);")

        conn.commit()

        conn.close()

        return "A contact request has been sent to user "+original_username2+"."

class ContactRequestResponses(object):
    @cherrypy.expose
    @require()
    def index(self):

        secrets_file=open("/home/ec2-user/secrets.txt")

        passwords=secrets_file.read().rstrip('\n')

        db_password = passwords.split('\n')[0]

        dbname = "ecommunicate"

        conn = MySQLdb.connect(host='ecommunicate-production.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='browser', passwd=db_password, port=3306)

        curs = conn.cursor()

        curs.execute("use "+dbname+";")

        curs.execute("select * from contact_requests where username1 = \""+cherrypy.session.get('_cp_username')+"\" and forward=0;")

        contact_requests = curs.fetchall()

        curs.execute("select * from contact_requests where username2 = \""+cherrypy.session.get('_cp_username')+"\" and forward=1;")

        contact_requests = contact_requests+curs.fetchall()

        contact_request_string = "<form action=\"contact_request_responses\" method=\"post\" id =\"contact_request_responses\" target=\"console_iframe4\">\n"

        for contact_request in contact_requests:

            colnames = [desc[0] for desc in curs.description]

            contact_request_dict=dict(zip(colnames, contact_request))

            if contact_request_dict["username2"] == cherrypy.session.get('_cp_username'):
                username = contact_request_dict["username1"]
            else:
                assert(contact_request_dict["username1"] == cherrypy.session.get('_cp_username'))
                username = contact_request_dict["username2"]


            contact_request_string = contact_request_string+username+": <select name=\""+username+"\">\n<option value=\"Wait\"></option>\n<option value=\"Accept\">Accept</option>\n<option value=\"Reject\">Reject</option></select>\n<br><br>"

        contact_request_string=contact_request_string+"<br><button type=\"submit\" id = \"contact_request_responses\">Respond to contact requests</button>\n</form>"

        conn.close()

        return """<html>
<head><title>open</title>

<style>

"""+chat_menubar_style_html_string+"""

    .messageerrorbox {
    width: 100%;
    height: 5em;
    border: none;
}

</style>

</head>
<body>


<center><h1>Ecommunicate</h1>

<h3>A free online communication service</h3>

"""+chat_menubar_html_string+"""

</center>


""" + contact_request_string + """

  <iframe name="console_iframe4" class="messageerrorbox" />  </iframe>

</body>
        </html>"""

    @cherrypy.expose
    def contact_request_responses(self,**responses):

        secrets_file=open("/home/ec2-user/secrets.txt")

        passwords=secrets_file.read().rstrip('\n')

        db_password = passwords.split('\n')[0]

        dbname = "ecommunicate"

        conn = MySQLdb.connect(host='ecommunicate-production.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='browser', passwd=db_password, port=3306)

        curs = conn.cursor()

        curs.execute("use "+dbname+";")

        for username in responses.keys():
            if responses[username] == "Wait":
                continue
            elif responses[username] == "Reject":

                curs.execute("delete from contact_requests where username1 = \""+username+"\" and username2 = \""+cherrypy.session.get('_cp_username')+"\";")
                curs.execute("delete from contact_requests where username2 = \""+username+"\" and username1 = \""+cherrypy.session.get('_cp_username')+"\";")
            elif responses[username] == "Accept":

                curs.execute("select * from contacts where username1 = \""+cherrypy.session.get('_cp_username')+"\" and username2 = \""+username+"\";")

                contacts_tuple1=curs.fetchall()
                
                curs.execute("select * from contacts where username1 = \""+username+"\" and username2 = \""+cherrypy.session.get('_cp_username')+"\";")

                contacts_tuple2=curs.fetchall()

                contacts_tuple = contacts_tuple1+contacts_tuple2

                if len(contacts_tuple) > 0:
                    continue

                curs.execute("delete from contact_requests where username1 = \""+username+"\" and username2 = \""+cherrypy.session.get('_cp_username')+"\";")
                curs.execute("delete from contact_requests where username2 = \""+username+"\" and username1 = \""+cherrypy.session.get('_cp_username')+"\";")
                
                sorted_usernames= sorted([cherrypy.session.get('_cp_username'),username])

                username1=sorted_usernames[0]
                username2=sorted_usernames[1]

                curs.execute("insert into contacts set username1 = \""+username1+"\", username2 = \""+username2+"\", new_message_username1 = 0, new_message_username2 = 0, accept_time = now(6);")
            
        conn.commit()

        conn.close()

        return "Your responses have been registered."


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


class Chat(object):

    makecontactrequests=MakeContactRequest()

    respondtocontactrequests=ContactRequestResponses()

    @cherrypy.expose
    @require()
    def index(self):

        secrets_file=open("/home/ec2-user/secrets.txt")

        passwords=secrets_file.read().rstrip('\n')

        db_password = passwords.split('\n')[0]

        dbname = "ecommunicate"

        conn = MySQLdb.connect(host='ecommunicate-production.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='browser', passwd=db_password, port=3306)

        curs = conn.cursor()

        curs.execute("use "+dbname+";")

        curs.execute("select * from contacts where username1 = \""+cherrypy.session.get('_cp_username')+"\"")

        contacts = curs.fetchall()

        curs.execute("select * from contacts where username2 = \""+cherrypy.session.get('_cp_username')+"\"")

        contacts = contacts+curs.fetchall()

        contacts_string = "<td><ul class=\"contactlistclass\" id=\"contactslist\">\n"

        contacts_string = contacts_string+"<li id=\""+cherrypy.session.get('_cp_username')+"\" name=\""+cherrypy.session.get('_cp_username')+"\" class=\"contact\">"+cherrypy.session.get('_cp_username')+"</li>\n"

        iframes_string = "";

        iframes_string = iframes_string+ "<iframe id=\"console_"+cherrypy.session.get('_cp_username')+"\" name=\"console_"+cherrypy.session.get('_cp_username')+"\" class=\"terminal\" />  </iframe>\n"

        iframes_hide_string = "";

        iframes_hide_string = iframes_hide_string+iframes_hide_string+"$(\'#console_" + cherrypy.session.get('_cp_username') + "\').hide();\n"

        for contact in contacts:

            colnames = [desc[0] for desc in curs.description]

            contact_dict=dict(zip(colnames, contact))

            if contact_dict["username2"] == cherrypy.session.get('_cp_username'):
                username = contact_dict["username1"]
            else:
                assert(contact_dict["username1"] == cherrypy.session.get('_cp_username'))
                username = contact_dict["username2"]

            contacts_string = contacts_string+"<li id=\""+username+"\" name=\""+username+"\" class=\"contact\">"+username+"</li>\n" 

            iframes_string = iframes_string+ "<iframe id=\"console_"+username+"\" name=\"console_"+username+"\" class=\"terminal\" />  </iframe>\n"

            iframes_hide_string = iframes_hide_string+"$(\'#console_" + username + "\').hide();\n"

        contacts_string=contacts_string+"</ul></td>\n</td>"

        click_on_self_string = "$(\'#"+cherrypy.session.get('_cp_username')+"\').click();"

        conn.close()

        return """<html>
<head><title>Ecommunicate</title>

<style>

"""+chat_menubar_style_html_string+"""

ul.contactlistclass {

    list-style:none;
    padding-left:0;


}

    .contact {
        color : black;
        background-color: green;
        height: 50px;
        font-size: 24px;
        font-size: 24px;
        width: 98.5%;
//        padding-left: 20px;
        padding-top: 20px;
        margin-top: 2px;
        font-family: Verdana;
        font-weight: bold;
        cursor: default;
        border-top: 2px solid black;
        border-bottom: 2px solid black;
    }
    .terminal {
    width: 100%;
    height: 30em;
    border: none;
}
    .messageerrorbox {
    width: 100%;
    height: 1em;
    border: none;
}


</style>

</head>
<body>

<center><h1>Ecommunicate</h1>
<h3>A free online communication service</h3>

"""+chat_menubar_html_string+"""

<h4>Chat</h4>

</center>


<center>

  <table border=2>
  <tr>
""" + contacts_string + """ 
  <td>
"""+ iframes_string + """
<form id="add_message_form" name = "add_messages_form" target="console_iframe1" method="POST" action="add_message">
 <input type="text" id="add_message_text" name="add_message_text" size="100" /> <br> <br>
 <input type="hidden" id="username2" name="username2"/>
 </form>
 <iframe id="console_iframe1" name="console_iframe1" class="messageerrorbox" />  </iframe>
</td>
  </tr>
  </table>

</center>


</body>
<script type="text/javascript" src="https://code.jquery.com/jquery-3.1.0.js"></script> 
<script>
messages_json = "";
messages_json_old = "";
username2  = "";
max_time = ""
function show_messages(e){
   var target = e.target;
   if( target.id != "contactslist"){
    var console_iframe2 = document.getElementById('console_'+e.target.id);
    if (username2 != ""){
    
        $('#console_'+username2).hide();
    }
//    console_iframe2.slideDown('slow');
 
    username2=e.target.id;
    $('#console_'+username2).show();
   }
}
function update_messages(){

    if (messages_json != "") {

        for (var item in messages_json) {  
            var console_iframe2 = document.getElementById('console_'+item);
            //clear the iframe
            console_iframe2.contentWindow.document.open();
            console_iframe2.contentWindow.document.close();
            for ( var i = 0, l = messages_json[item].length; i < l; i++ ) {
                console_iframe2.contentWindow.document.write(messages_json[item][i][0]+": "+messages_json[item][i][1]);
                console_iframe2.contentWindow.document.write("<br>");
            }
            var console_iframe2_contentWindow_document = console_iframe2.contentWindow.document;
            //this will "over-scroll", but it works i.e. it moves to the bottom    
            $(console_iframe2_contentWindow_document).scrollTop($(console_iframe2_contentWindow_document).height());  
        }
    }
}
function chat_initial() {
   $.ajax({
      url: 'get_messages',
      type: 'GET',
      dataType: 'html',
      success: function(data) {
         parsed_data = JSON.parse(data);
         messages_json = parsed_data[0];
         max_time=parsed_data[1]; 
         messages_json_old = messages_json;
         update_messages(); 
         chat_recursive();
      }
   });
}
function chat_recursive() {
get_messages_url = 'get_messages?upon_update=True&client_max_time='+max_time;
   $.ajax({
      url: get_messages_url,
      type: 'GET',
      dataType: 'html',
      success: function(data) {

         parsed_data = JSON.parse(data);
         //alert(parsed_data["phone8"]);
         messages_json = parsed_data[0];

         max_time = parsed_data[1];
         if (messages_json_old != ""){
             for (var item in messages_json) {
                 if (item in messages_json_old){
                    if ( messages_json[item].length > messages_json_old[item].length ) {
                        for ( var i = messages_json_old[item].length, l = messages_json[item].length; i < l; i++ ) { 
                            if (messages_json[item][i][0] == item){
                                $('#'+item).css('background-color','blue');
                            }
                        }  
                     }
                 } else {
                    for ( var i = 0, l = messages_json[item].length; i < l; i++ ) { 
                        if (messages_json[item][i][0] == item){
                                $('#'+item).css('background-color','blue');
                        }
                    }  

                 }
             }
         }
         messages_json_old = messages_json;
         update_messages();  
         chat_recursive();
      }
   });
}
$('#add_message_form').submit(function(event) {
   event.preventDefault();
   $('input[name="username2"]',this).val(username2);
   var $this = $(this);
   //$.get($this.attr('action'),$this.serialize());
   //alert($this.serialize());
   $.ajax({
      url: $this.attr('action'),
      type: 'POST',
      dataType: 'html',
      data: $this.serialize()
   
   });
   add_message_form.reset();
});
//$('#add_message_text')
//.keyup(function(event) {
//if (event.keyCode == 13){
//alert(event.keyCode);
//}
//});
function contact_mouseover(e){
var target = e.target;
if( target.id != "contactslist"){
    $('#'+target.id).css('background-color','orange');
}
}
function contact_mouseout(e){
var target = e.target;
if( target.id != "contactslist"){
    $('#'+target.id).css('background-color','green');
}
}
console_iframe1=document.getElementById('console_iframe1')
//var add_message_form = document.getElementById('add_message_form')
//var message = document.getElementById('message')
//add_message_form.addEventListener('submit', function (e) { 
//e.preventDefault();
//add_message_form.submit();
//}, false)
//console_iframe1.addEventListener('load', function(e) {
//add_message_form.reset();
//}, false)
var contactslist = document.getElementById('contactslist')
contactslist.addEventListener('touchstart', function(e) { show_messages(e); } , false )
contactslist.addEventListener('click', function(e) { 
    show_messages(e); 
} , false )
contactslist.addEventListener('mouseover',function(e) {contact_mouseover(e); } ,  false)
contactslist.addEventListener('mouseout',function(e) {contact_mouseout(e); } ,  false)

$(document).ready(function() {
"""+iframes_hide_string+"""
   chat_initial();

"""+click_on_self_string+"""

});


</script>
        </html>"""

    @cherrypy.expose
    @require()
    def get_messages(self,upon_update=False,client_max_time=None):

        if client_max_time == "null":
            client_max_time = None

        #dn=cherrypy.request.headers['Cms-Authn-Dn']

        #client_max_time="2017-06-30 08:01:06.562369";

        username1=cherrypy.session.get('_cp_username')

        secrets_file=open("/home/ec2-user/secrets.txt")

        passwords=secrets_file.read().rstrip('\n')

        db_password = passwords.split('\n')[0]

        dbname = "ecommunicate"

        conn = MySQLdb.connect(host='ecommunicate-production.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='browser', passwd=db_password, port=3306)

        if upon_update:

            #the connection will timeout eventually
            for i in range(0,1000):

                conn.commit()
                
                curs = conn.cursor()

                curs.execute("use "+dbname+";")

                curs.execute("select MAX(time) from messages where username1=\""+username1+"\";")

                #tmp = curs.fetchall()

                server_max_time = curs.fetchall()[0][0]

                if server_max_time != None and client_max_time == None:
                    break

                if server_max_time != None and server_max_time > datetime.datetime.strptime(client_max_time,"%Y-%m-%d %H:%M:%S.%f"):
                    break

                curs.execute("select MAX(time) from messages where username2=\""+username1+"\";")

                server_max_time = curs.fetchall()[0][0]

                if server_max_time != None and client_max_time == None:
                    break

                if server_max_time != None and server_max_time > datetime.datetime.strptime(client_max_time,"%Y-%m-%d %H:%M:%S.%f"):
                    break

                curs.close()    
                
                time.sleep(0.1)


        #conn = MySQLdb.connect(host='tutorial-db-instance.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='open', passwd=db_password, port=3306)

        curs = conn.cursor()

        curs.execute("use "+dbname+";")

        curs.execute("select * from contacts where username1 = \""+cherrypy.session.get('_cp_username')+"\"")

        contacts = curs.fetchall()

        curs.execute("select * from contacts where username2 = \""+cherrypy.session.get('_cp_username')+"\"")

        contacts = contacts+curs.fetchall()

        colnames_contacts = [desc[0] for desc in curs.description]

        messages_json = {}


        for contact in contacts:

            contact_dict=dict(zip(colnames_contacts, contact))

            if contact_dict["username2"] == cherrypy.session.get('_cp_username'):
                username = contact_dict["username1"]
                curs.execute("select * from messages where username1 = \""+username+"\" and username2 = \""+username1+"\" order by time;")
            else:
                assert(contact_dict["username1"] == cherrypy.session.get('_cp_username'))
                username = contact_dict["username2"]
                curs.execute("select * from messages where username1 = \""+username1+"\" and username2 = \""+username+"\" order by time;")

            colnames = [desc[0] for desc in curs.description]

            messages=curs.fetchall()

            if len(messages) > 0:

                messages_json[username] = []

                for message in messages:

                    message_dict=dict(zip(colnames, message))

                    if message_dict["forward"] == 1:
                        messages_json[username].append([message_dict["username1"], message_dict["message"]])
                    elif message_dict["forward"] == 0:
                        messages_json[username].append([message_dict["username2"], message_dict["message"]])

        curs.execute("select * from messages where username1 = \""+cherrypy.session.get('_cp_username')+"\" and username2 = \""+cherrypy.session.get('_cp_username')+"\" order by time;")

        colnames = [desc[0] for desc in curs.description]

        messages=curs.fetchall()

        if len(messages) > 0:
            messages_json[cherrypy.session.get('_cp_username')] = []
            for message in messages:
                message_dict=dict(zip(colnames, message))
                messages_json[cherrypy.session.get('_cp_username')].append([cherrypy.session.get('_cp_username'), message_dict["message"]])

        #return str(messages_json)

        curs.execute("select MAX(time) from messages where username1=\""+cherrypy.session.get('_cp_username')+"\";")

        max_time1 = curs.fetchall()[0][0]

        curs.execute("select MAX(time) from messages where username2=\""+cherrypy.session.get('_cp_username')+"\";")

        max_time2 = curs.fetchall()[0][0]

        curs.close()

        if max_time1 == None and max_time2 != None:
            max_time = str(max_time2)

        elif max_time2 == None and max_time1 != None:
            max_time = str(max_time1)

        elif max_time1 == None and max_time2 == None:
            max_time = None

        else:
            max_time = str(max(max_time1,max_time2))

        conn.close()

        return json.dumps([messages_json,max_time])

        #return '{"a1" : "b1"}'



    @cherrypy.expose
    @require()
    def add_message(self, add_message_text,username2):

        username1=cherrypy.session.get('_cp_username')
        
        sorted_usernames= sorted([username1,username2])

        if sorted_usernames == [username1,username2]:
            forward = "1"
        else:
            forward = "0"

        username1=sorted_usernames[0]

        username2=sorted_usernames[1]

        secrets_file=open("/home/ec2-user/secrets.txt")

        passwords=secrets_file.read().rstrip('\n')

        db_password = passwords.split('\n')[0]

        dbname = "ecommunicate"

        conn = MySQLdb.connect(host='ecommunicate-production.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='browser', passwd=db_password, port=3306)

        curs = conn.cursor()

        curs.execute("use "+dbname+";")

        curs.execute("insert into messages set username1 = \""+username1+"\", username2 = \""+username2+"\", forward="+forward+", time=now(6), message = \""+add_message_text+"\";")

        if forward == "1":
            curs.execute("update contacts set new_message_username2 = 1 where username1 = \""+username1+"\" and username2 = \""+username2+"\";")
        else: 
            curs.execute("update contacts set new_message_username1 = 1 where username1 = \""+username1+"\" and username2 = \""+username2+"\";")

        conn.commit()

        params_json = {'username1': username1, 'username2': username2}


        headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}

        http_conn  =  httplib.HTTPSConnection("android.ecommunicate.ch")
        http_conn.request('POST','/new_message_browser/', headers = headers, body = json.dumps(params_json))
        r=http_conn.getresponse()
        print r.status
        print r.reason

        conn.close()


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

