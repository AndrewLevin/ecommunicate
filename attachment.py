import cherrypy

import os

import email

import mailbox

from cherrypy.lib import static

class Attachment(object):

    @cherrypy.expose
    def index(self,message_id,attachment_id,sent=False):

        if sent == False:
            #use the message factory so that you get MaildirMessages instead of rfc822.Messages
            try:
                emails = mailbox.Maildir('/efsemail/mail/vhosts/ecommunicate.ch/'+cherrypy.session.get('_cp_username')+'/', factory=mailbox.MaildirMessage)
            except mailbox.NoSuchMailboxError:
                raise Exception
        else: 
            emails = mailbox.Maildir('/efsemail/mail/vhosts/ecommunicate.ch-sent/'+cherrypy.session.get('_cp_username')+'/', factory=mailbox.MaildirMessage)

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
