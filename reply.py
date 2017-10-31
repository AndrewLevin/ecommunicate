import cherrypy

import smtplib
import email

import mailbox

from email.MIMEMultipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate

import time

import re

import html_strings

from require import require

import utils

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
                emails = mailbox.Maildir('/efsemail/mail/vhosts/ecommunicate.ch/'+cherrypy.session.get('_cp_username')+'/',factory=mailbox.MaildirMessage,create=False)
            except mailbox.NoSuchMailboxError:
                raise Exception

        else:
            emails = mailbox.Maildir('/efsemail/mail/vhosts/ecommunicate.ch-sent/'+cherrypy.session.get('_cp_username')+'/',factory=mailbox.MaildirMessage)

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
                if email.utils.parseaddr(em['From'])[0]:
                    body = body+email.utils.parseaddr(em['From'])[0]+" wrote:\n"
                else:
                    body = body+email.utils.parseaddr(em['From'])[1]+" wrote:\n"
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
"""+html_strings.authenticated_menubar_html_string+"""
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

            mime_applications = []

            l = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','0','1','2','3','4','5','6','7','8','9']

            if len(attachments) > 36:
                raise Exception

            for i,attachment in enumerate(attachments):
                if attachment.file != None and attachment.filename != "":
                    tmp_filename=os.popen("mktemp").read().rstrip('\n')
                    open(tmp_filename,'wb').write(attachment.file.read());
                    
                    if str(attachment.content_type) == "application/pdf":
                        mime_application = MIMEApplication(open(tmp_filename,'rb').read(),"pdf")
                        mime_application['Content-Disposition'] = 'attachment; filename="'+str(attachment.filename)+'"'
                        mime_application['Content-Description'] = str(attachment.filename)
                        mime_application['X-Attachment-Id'] = str("f_")+l[random.randint(0,35)]+l[random.randint(0,35)]+l[random.randint(0,35)]+l[random.randint(0,35)]+l[i]+l[random.randint(0,35)]+l[random.randint(0,35)]+l[random.randint(0,35)]+l[random.randint(0,35)]
                        mime_applications.append(mime_application)

            try:
                msg.attach(MIMEText(body))

                for mime_application in mime_applications:
                    msg.attach(mime_application)

                smtpObj = smtplib.SMTP(port=25)

                smtpObj.connect()

                smtpObj.sendmail(send_from, send_to+send_cc, msg.as_string())
                
                smtpObj.close()


            except Exception as e:
                print "Error: unable to send email", e.__class__
              
        return reply_function()
