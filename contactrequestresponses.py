import MySQLdb
import datetime
import cherrypy

import html_strings

from require import require

import utils

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

        contact_requests += curs.fetchall()

        contact_request_string = "<form action=\"contact_request_responses\" method=\"post\" id =\"contact_request_responses\" target=\"console_iframe4\">\n"

        for contact_request in contact_requests:

            colnames = [desc[0] for desc in curs.description]

            contact_request_dict=dict(zip(colnames, contact_request))

            if contact_request_dict["username2"] == cherrypy.session.get('_cp_username'):
                username = contact_request_dict["username1"]
            else:
                assert(contact_request_dict["username1"] == cherrypy.session.get('_cp_username'))
                username = contact_request_dict["username2"]


            contact_request_string += username+": <select name=\""+username+"\">\n<option value=\"Wait\"></option>\n<option value=\"Accept\">Accept</option>\n<option value=\"Reject\">Reject</option></select>\n<br><br>"

        contact_request_string += "<br><button type=\"submit\" id = \"contact_request_responses\">Respond to contact requests</button>\n</form>"

        conn.close()

        return """<html>
<head><title>Ecommunicate</title>
<style>
.nonheader { width:960px; margin: 80px auto 0px auto;  }
"""+html_strings.header_style+"""
.messageerrorbox {
    width: 100%;
    height: 5em;
    border: none;
}
</style>
</head>
<body>
"""+(html_strings.authenticated_header if utils.is_session_authenticated() else html_strings.not_authenticated_header)+"""

<div class = "nonheader">

<h2>

Respond to Contact Requests

</h2>

""" + contact_request_string + """
  <iframe name="console_iframe4" class="messageerrorbox" />  </iframe>

</div>

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
