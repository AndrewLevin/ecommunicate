import MySQLdb
import cherrypy

from view import View

from chat import Chat

from loginlogout import LogInLogOut

from register import Register

from about import About

from emails import Email

from compose import Compose

from cherrypy.lib import static

import html_strings

import utils

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


        html_string = """
<html>
<head>
<title>
Ecommunicate
</title>
<style>

.nonheader { width:960px; margin: 140px auto 0px auto;  }

"""+html_strings.not_authenticated_header_style+"""
</style>
</head>
<body>
"""+html_strings.not_authenticated_header
    
        html_string += "<div class=\"nonheader\">"

        html_string += "Ecommunicate is a free online communication service in which all communication is viewable by anyone on the open internet instead of being private. Text messaging (like Google Hangouts or WeChat) and e-mail (to other ecommunicate.ch e-mail addresses) are implemented already, and we hope to eventually add audio and video calling (like Skype). You can chat or e-mail yourself (after registering and logging in) or you can view other people's chat conversations or e-mail inboxes (see below). This website is experimental at this point. You should expect bugs, unexpected downtime, etc. Please contact ecommunicate.feedback@gmail.com for comments, feature requests, etc.<br>"

        html_string += "<br>"

        html_string += "<table>"

        html_string += "<tr><th>Chat Conversations</th><th>E-mail Boxes</th><td valign = \"top\" style=\"padding-left:100px\"><a href=\"https://play.google.com/store/apps/details?id=ch.ecommunicate.chat\">Android Chat App <a></td><td valign = \"top\" style=\"padding-left:100px\"><a href=\"https://play.google.com/store/apps/details?id=ch.ecommunicate.email\">Android Email App <a></td></tr>"

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
    
        curs.execute("select DISTINCT username1,username2 from messages;")
    
        conversations = curs.fetchall()

        colnames = [desc[0] for desc in curs.description]

        for conversation in conversations:

            conversation_dict=dict(zip(colnames, conversation))
            
            html_string += "<li><a href=\"/view/chat/?username1=%22"+conversation_dict["username1"]+"%22&username2=%22"+conversation_dict["username2"]+"%22\">"+conversation_dict["username1"]+" and "+conversation_dict["username2"]+"</a><br></li>\n"

        html_string += "</ol>\n"
            
        html_string += "</td>\n"

        html_string += "<td valign=\"top\">\n"

        curs.execute("select username from user_info;")

        colnames = [desc[0] for desc in curs.description]
            
        usernames = curs.fetchall()

        html_string+= "<ol>\n"

        for username in usernames:

            username_dict=dict(zip(colnames, username))
            
            html_string+= "<li><a href=\"/view/email?username=%22"+username_dict["username"]+"%22\">"+username_dict["username"]+"</a><br></li>\n"

        html_string += "</ol>\n"

        html_string += "</td>\n"

        html_string += "</tr>\n"

        html_string += "</table>"

        html_string += "</div>"

        html_string +=  """
</body>
</html>
"""
        conn.close()


        return html_string

