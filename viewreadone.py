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
    def index(self,username,message_id,sent="False"):

        sent = sent.strip('"')

        username = username.strip('"')

        message_id = message_id.strip('"')

        sent_bool = True

        if sent == "False":
            sent_bool = False

        #the default message factory is the rfc822.Message for historical reasons (see https://docs.python.org/2/library/mailbox.html#maildir)
        if sent_bool == False:
            try:
                emails = mailbox.Maildir('/efsemail/mail/vhosts/ecommunicate.ch/'+username+'/',factory=mailbox.MaildirMessage,create=False)
            except mailbox.NoSuchMailboxError:
                raise Exception
        else:
            emails = mailbox.Maildir('/efsemail/mail/vhosts/ecommunicate.ch-sent/'+username+'/',factory=mailbox.MaildirMessage)

        em = emails.get_message(message_id)

        email_string = ""

        email_string += "<table border = \"1\" width = \"100%\"  >"

        if sent_bool:
            if 'To' in em:
                if email.utils.parseaddr(em['To'])[0]:
                    email_string += "<tr><td><b>To: </b>"+email.utils.parseaddr(em['To'])[0]+"</td></tr>"
                else:    
                    email_string += "<tr><td><b>To: </b>"+email.utils.parseaddr(em['To'])[1]+"</td></tr>"
            #email_string = email_string + email.utils.parseaddr(em[1]['From'])[1]+"<br>"            
        else:
            if 'From' in em:
                if email.utils.parseaddr(em['From'])[0]:
                    email_string += "<tr><td><b>From: </b>"+email.utils.parseaddr(em['From'])[0]+"</td></tr>"
                else:
                    email_string += "<tr><td><b>From: </b>"+email.utils.parseaddr(em['From'])[1]+"</td></tr>"
                #email_string = email_string + email.utils.parseaddr(em[1]['From'])[1]+"<br>"
        if 'Subject' in em:    
            email_string += "<tr><td><b>Subject: </b>"+em['Subject']+"</td></tr>"
        if 'Date' in em:
            email_string += "<tr><td><b>Date: </b>"+time.strftime("%d %b %H:%M",email.utils.parsedate(em['Date']))+"</td></tr>"

        attachment_string = ""

        body_string = ""

        at_least_one_attachment = False

        if em.is_multipart():

            for payload in em.get_payload():
                if not payload.is_multipart():


                    if 'X-Attachment-Id' in payload and "Content-Description" in payload:


                        if not at_least_one_attachment:
                            at_least_one_attachment = True

                            attachment_string += '<tr><td style="white-space:pre-wrap">'

                            attachment_string += '<a href="/view/email/readone/attachment/?username=%22'+username+'%22&&sent=%22'+str(sent_bool)+'%22&&message_id=%22'+message_id+'%22&&attachment_id=%22'+payload["X-Attachment-Id"]+'%22">'+payload["Content-Description"]+'</a>'

                        else:

                            attachment_string += '   <a href="/view/email/readone/attachment/?username=%22'+username+'%22&&sent=%22'+str(sent_bool)+'%22&&message_id=%22'+message_id+'%22&&attachment_id=%22'+payload["X-Attachment-Id"]+'%22">'+payload["Content-Description"]+'</a>'

                    else:
                        if 'Content-Type' in payload and ('text/plain' in payload['Content-Type'] or 'message/delivery-status' in payload['Content-Type'] or 'message/rfc822' in payload['Content-Type']):
                            body_string += '<tr><td style="white-space:pre-line">'+payload.get_payload()+"</td></tr>"
                else:
                    for subpayload in payload.get_payload():
                        if not subpayload.is_multipart():
                            if 'Content-Type' in subpayload and ('text/plain' in subpayload['Content-Type'] or 'message/delivery-status' in subpayload['Content-Type'] or 'message/rfc822' in subpayload['Content-Type']):
                                body_string += '<tr><td style="white-space:pre-line">'+subpayload.get_payload()+"</td></tr>"
                        else:
                            for subsubpayload in subpayload.get_payload():
                                if not subsubpayload.is_multipart():
                                    if 'Content-Type' in subsubpayload and ('text/plain' in subsubpayload['Content-Type'] or 'message/delivery-status' in subsubpayload['Content-Type'] or 'message/rfc822' in subsubpayload['Content-Type']):
                                        body_string += '<tr><td style="white-space:pre-line">'+subsubpayload.get_payload()+"</td></tr>"
                                else:
                                    pass
        else:

            body_string += "<tr><td>"+em.get_payload()+"</td></tr>"

        if at_least_one_attachment:
            attachment_string += '</tr></td>'
        

        email_string += attachment_string

        email_string += body_string

        email_string += "</table>"
        
        return """<html>
<head>
<style>
.terminal {
border: none; 
}
.nonheader { width:960px; margin: 80px auto 0px auto;  }
"""+html_strings.header_style+"""   
</style>
<title>Ecommunicate</title>
</head>
<body>
"""+(html_strings.authenticated_header if utils.is_session_authenticated() else html_strings.not_authenticated_header)+"""

<div class="nonheader">

<br><br>
<center>
"""+email_string+"""
</center>
  
  
  <br>
  <br>
  </center>
</div>

</body>
<script>
</script>
        </html>"""
