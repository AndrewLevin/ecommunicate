import MySQLdb
import cherrypy

from cherrypy.lib import static

from viewemail import ViewEmail

from viewchat import ViewChat

import html_strings

import utils

class View(object):

    _cp_config = {
        'tools.sessions.on': True,
        'tools.auth.on': True,
        'tools.sessions.locking': 'explicit' #this and the acquire_lock and the release_lock statements in the login and logout functions are necessary so that multiple ajax requests can be processed in parallel in a single session
    }

    email = ViewEmail()

    chat = ViewChat()

#    @cherrypy.expose
#    def default(self,*args):
#        return static.serve_file("/home/ec2-user/server/google_verification_file.html");        

    @cherrypy.expose
    def index(self):

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

        curs.execute("select username from received_emails;")

        email_usernames = curs.fetchall()

        curs.execute("select username from sent_emails;")

        email_usernames += curs.fetchall()

        conn.close()

        is_mobile = False

        if "User-Agent" in cherrypy.request.headers and ("Android" in cherrypy.request.headers['User-Agent'] or "iPhone" in cherrypy.request.headers['User-Agent'] or "iPad" in cherrypy.request.headers['User-Agent']):
            is_mobile = True

        if is_mobile:

            html_string = """
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">

"""+html_strings.google_adsense_conversion_tracking_global_site_tag+"""

<title>
Ecommunicate
</title>
<style>

nav a, button {
    min-width: 48px;
    min-height: 48px;
}

html, body {
    height: 100%;
    width: 100%;
    margin-top:0;
    margin-left:0;
    margin-right:0;
}

a#menu svg {
    width: 40px;
    fill: #000;
}

main {
    width: 100%;
    height: 100%;
}

nav {
    width: 250px;
    height: 100%;
    position: fixed;
    transform: translate(-250px, 0);
    transition: transform 0.3s ease;
}

nav.open {
    transform: translate(0, 0);
}

.header {
float : right
}

.content {
padding-left:1em;
padding-right:1em;
}


</style>
</head>
<body>

<nav id="drawer" style="background-color:LightGrey">
<center><h2 style="margin-top:0">Ecommunicate</h2></center>"""+(html_strings.authenticated_mobile_navigation_menu if utils.is_session_authenticated() else html_strings.not_authenticated_mobile_navigation_menu)+"""
</nav>

<main>
<div style = "width:100%;top:0;left:0;">
<a id="menu">
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
    <path d="M2 6h20v3H2zm0 5h20v3H2zm0 5h20v3H2z" />
  </svg>
</a>
<div class = "header">
<h1 style="margin-top:0;margin-bottom:0">Ecommunicate</h1>
</div>
</div>

<div class = "content">
<center><h2>View</h2></center>"""

            html_string += "<center><h3>Chat Conversations</h3></center>"

            html_string += "<ul style=\"list-style:none;\">"

            for conversation in conversations:
                
                conversation_dict=dict(zip(colnames, conversation))
            
                if conversation_dict["username1"] == conversation_dict["username2"]:
                    html_string += "<li><a href=\"/view/chat/?username1=%22"+conversation_dict["username1"]+"%22&username2=%22"+conversation_dict["username2"]+"%22\">"+conversation_dict["username1"]+" with self</a><br></li>\n"
                else:
                    html_string += "<li><a href=\"/view/chat/?username1=%22"+conversation_dict["username1"]+"%22&username2=%22"+conversation_dict["username2"]+"%22\">"+conversation_dict["username1"]+" and "+conversation_dict["username2"]+"</a><br></li>\n"

            html_string += "</ul>"

            html_string += "<center><h3>E-mail Boxes</h3></center>"

            already_listed_usernames = []

            html_string += "<ul style=\"list-style:none;\">"

            for username in email_usernames:

                if username not in already_listed_usernames:

                    html_string+= "<li><a href=\"/view/email?username=%22"+username[0]+"%22\">"+username[0]+"</a><br></li>\n"

                    already_listed_usernames.append(username)

            html_string += "</ul>"

            html_string += "</div></main>"

            html_string += """<script type="text/javascript" src="https://code.jquery.com/jquery-3.1.0.js"></script>

<script type="text/javascript">

var menu = document.querySelector('#menu');

var main = document.querySelector('main');

var drawer = document.querySelector('#drawer');

menu.addEventListener('click', function(e) {
    drawer.classList.toggle('open');
    e.stopPropagation();
});

main.addEventListener('click', function() {
    drawer.classList.remove('open');
});

main.addEventListener('touchstart', function() {
    drawer.classList.remove('open');
});

</script>        



</body></html>"""

            return html_string;

        else:
        
            html_string = """
<html>
<head>

"""+html_strings.google_adsense_conversion_tracking_global_site_tag+"""

<title>
Ecommunicate
</title>
<style>

.nonheader { width:960px; margin: 80px auto 0px auto;  }

"""+html_strings.header_style+"""
</style>
</head>
<body>
"""+(html_strings.authenticated_header if utils.is_session_authenticated() else html_strings.not_authenticated_header)

            html_string += "<div class=\"nonheader\">"

            html_string += "<center><h2>View</h2></center>"

            html_string += "<table>"

            html_string += "<tr><th>Chat Conversations</th><th style=\"padding-left:100px\">E-mail Boxes</th></tr>"

            html_string += "<tr>\n"
        
            html_string += "<td valign=\"top\">\n"
        
            html_string += "<ol>\n"

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
            
            html_string +=  """
            </body>
            </html>
"""

        return html_string

