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

        is_mobile = False

        if "Android" in cherrypy.request.headers['User-Agent'] or "iPhone" in cherrypy.request.headers['User-Agent'] or "iPad" in cherrypy.request.headers['User-Agent']:
            is_mobile = True

        if is_mobile:

            html_string = """

<head>

"""+html_strings.google_adsense_conversion_tracking_global_site_tag+"""

<meta name="viewport" content="width=device-width, initial-scale=1.0">

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

.messageerrorbox {
    width: 100%;
    height: 5em;
    border: none;
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

<center>
<h2>
Respond to Contact Requests
</h2>
</center>

<center>
""" + contact_request_string + """
  <iframe name="console_iframe4" class="messageerrorbox" />  </iframe>
</center>

</div>

</main>

<script type="text/javascript" src="https://code.jquery.com/jquery-3.1.0.js"></script> 

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

</body>
</html

"""
        else:

            html_string = """<html>

"""+html_strings.google_adsense_conversion_tracking_global_site_tag+"""

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
<center>
<h2>

Respond to Contact Requests

</h2>
</center>

<center>
""" + contact_request_string + """
  <iframe name="console_iframe4" class="messageerrorbox" />  </iframe>
</center>


</div>

</body>
        </html>"""
 
        return html_string


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
