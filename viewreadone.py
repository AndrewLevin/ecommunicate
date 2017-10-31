import cherrypy

import email

import mailbox

import time

from viewattachment import ViewAttachment

import html_strings

import utils

class ViewReadOne(object):

    attachment = ViewAttachment()

    @cherrypy.expose
    def index(self,username,message_id,sent=False):

        username = username.strip('"')

        #the default message factory is the rfc822.Message for historical reasons (see https://docs.python.org/2/library/mailbox.html#maildir)
        if sent == False:
            try:
                emails = mailbox.Maildir('/efsemail/mail/vhosts/ecommunicate.ch/'+username+'/',factory=mailbox.MaildirMessage,create=False)
            except mailbox.NoSuchMailboxError:
                raise Exception
        else:
            emails = mailbox.Maildir('/efsemail/mail/vhosts/ecommunicate.ch-sent/'+username+'/',factory=mailbox.MaildirMessage)

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

                        attachment_string = attachment_string + '<tr><td><a href="/view/email/readone/attachment/?username='+username+'&&message_id='+message_id+'&&attachment_id='+payload["X-Attachment-Id"]+'">'+payload["Content-Description"]+'</a></tr></td>'

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
"""+(html_strings.authenticated_menubar_html_string if utils.is_session_authenticated() else html_strings.not_authenticated_menubar_html_string)+"""
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
