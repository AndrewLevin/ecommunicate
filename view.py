import MySQLdb

import cherrypy

from cherrypy.lib import static

from viewemail import ViewEmail

from viewchat import ViewChat

import utils

import html_strings

class View(object):

    email = ViewEmail()

    chat = ViewChat()

    @cherrypy.expose
    def index(self):

        html_string = """
<html>
<head>
<title>
Ecommunicate
</title>
<style>
"""+html_strings.header_style+"""

.nonheader { width:960px; margin: 80px auto 0px auto;  }

</style>
</head>
<body>
"""
        
        html_string += (html_strings.authenticated_header if utils.is_session_authenticated() else html_strings.not_authenticated_header)

        html_string += "<div class=\"nonheader\">"

        html_string += """
<center>
<h2>View</h2>
</center>
"""
        html_string += "      Ecommunicate is a free online communication service in which all communication is viewable by anyone on the open internet instead of being private. E-mail to other ecommunicate.ch e-mail addresses and text messaging (like Google Hangouts or WeChat) are implemented already, and we hope to eventually add audio and video calling (like Skype). You can chat or e-mail yourself (after registering and logging in) or you can view other people's chat conversations or e-mail inboxes (see below). This website is experimental at this point. You should expect bugs, unexpected downtime, etc. Please contact ecommunicate.feedback@gmail.com for comments, feature requests, etc.<br>"

        html_string += "<br>"
        
        html_string += "<table>"
    
        html_string += "<tr><th>Chat Conversations</th><th style=\"padding-left:100px\">E-mail Boxes</th></tr>"
    
        html_string += "<tr>\n"

        html_string += "<td valign=\"top\">\n"

        html_string += "<ol>\n"

        secrets_file=open("/home/ec2-user/secrets.txt")

        passwords=secrets_file.read().rstrip('\n')

        db_password = passwords.split('\n')[0]

        dbname = "ecommunicate"

        conn = MySQLdb.connect(host='ecommunicate-production.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='browser', passwd=db_password, port=3306)

        curs = conn.cursor()

        curs.execute("use "+dbname+";")

        curs.execute("select DISTINCT username1,username2,max(time) from messages group by username1,username2 order by max(time) desc;")

        conversations = curs.fetchall()

        colnames = [desc[0] for desc in curs.description]

        for conversation in conversations:

            conversation_dict=dict(zip(colnames, conversation))
            
            if conversation_dict["username1"] == conversation_dict["username2"]:
                html_string += "<li><a href=\"/view/chat/?username1=%22"+conversation_dict["username1"]+"%22&username2=%22"+conversation_dict["username2"]+"%22\">"+conversation_dict["username1"]+" with self</a><br></li>\n"
            else:
                html_string += "<li><a href=\"/view/chat/?username1=%22"+conversation_dict["username1"]+"%22&username2=%22"+conversation_dict["username2"]+"%22\">"+conversation_dict["username1"]+" and "+conversation_dict["username2"]+"</a><br></li>\n"
                
        html_string += "</ol>\n"

        html_string += "</td>\n"
        
        html_string += "<td valign=\"top\" style=\"padding-left:100px\">\n"

        html_string+= "<ol>\n"

        curs.execute("select username from received_emails;")

        email_usernames = curs.fetchall()

        curs.execute("select username from sent_emails;")

        email_usernames += curs.fetchall()

        already_listed_usernames = []

        for username in email_usernames:

            if username not in already_listed_usernames:
                
                html_string+= "<li><a href=\"/view/email?username=%22"+username[0]+"%22\">"+username[0]+"</a><br></li>\n"

                already_listed_usernames.append(username)

        html_string += "</ol>\n"

        html_string += "</td>\n"

        html_string += "</tr>\n"
            
        html_string += "</table>"

        html_string += "</div>"

        html_string += """
</body>
</html>
"""
        conn.close()

        return html_string
