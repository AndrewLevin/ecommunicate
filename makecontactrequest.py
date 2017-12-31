import MySQLdb
import datetime
import cherrypy

import html_strings

from require import require

import utils

import json

class MakeContactRequest(object):

    _cp_config = {
        'tools.sessions.on': True,
        'tools.auth.on': True
    }

    @cherrypy.expose
    @require()
    def index(self):

        is_mobile = False

        if "Android" in cherrypy.request.headers['User-Agent'] or "iPhone" in cherrypy.request.headers['User-Agent'] or "iPad" in cherrypy.request.headers['User-Agent']:
            is_mobile = True

        if is_mobile:

            html_string = """
<head>
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
<h2>Make a contact request </h2>
<form id="contact_request_form" target="console_iframe3" method="post" action="contact_request">
<div style = "font-size:120%">username:</div><br>
  <input type="text" id="username2" name="username2" size="18" style="border:2px solid black;font-size: 120%;outline: none;"/> <br><br>
<div style = "font-size:120%">message:</div><br>
  <input type="text" id="message" name="message" style="width:100%;border:2px solid black;font-size: 120%;outline: none;"/> <br><br>
  <button id="contact_request" class="fg-button ui-state-default ui-corner-all" type="submit">
  Submit
  </button>
  </form>
  <iframe name="console_iframe3" class="messageerrorbox" /> </iframe>

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

$('#contact_request_form').submit(function(event) {

   event.preventDefault();

   var $this = $(this);

   $.ajax({

      url: $this.attr('action'),

      type: 'POST',

      data: $this.serialize(),

      success: function(data){

        json_object = JSON.parse(data)

        if (json_object["success"]) {

            $('#contact_request_form').hide();

            var console_iframe3 = document.getElementById('console_iframe3');

            console_iframe3.contentWindow.document.open();

            console_iframe3.contentWindow.document.close();

            console_iframe3.contentWindow.document.write('<center style="color:blue;font-size:20px;font-weight:bold">'+"E-mail sent succesfully."+'</center>');

        }

        else {

            var console_iframe3 = document.getElementById('console_iframe3');

            console_iframe3.contentWindow.document.open();

            console_iframe3.contentWindow.document.close();

            console_iframe3.contentWindow.document.write('<center style="color:red;font-size:20px;font-weight:bold">'+json_object["errors"]+'</center>');

        }

      },

      error : function (data) {

        var console_iframe3 = document.getElementById('console_iframe3');

        console_iframe3.write("Error. E-mail not sent succesfully.");

        //alert(JSON.stringify(data))

      }

   });

});

</script>

</body>

</html>

"""
        else:

            html_string = """<html>
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
"""+(html_strings.authenticated_header if utils.is_session_authenticated() else html_strings.not_authenticated_header) +"""

<div class = "nonheader">

<center>
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

</div>

<script>

$('#contact_request_form').submit(function(event) {

   event.preventDefault();

   var $this = $(this);

   $.ajax({

      url: $this.attr('action'),

      type: 'POST',

      data: $this.serialize(),

      success: function(data){

        json_object = JSON.parse(data)

        if (json_object["success"]) {

            $('#contact_request_form').hide();

            var console_iframe3 = document.getElementById('console_iframe3');

            console_iframe3.contentWindow.document.open();

            console_iframe3.contentWindow.document.close();

            console_iframe3.contentWindow.document.write('<center style="color:blue;font-size:20px;font-weight:bold">'+"E-mail sent succesfully."+'</center>');

        }

        else {

            var console_iframe3 = document.getElementById('console_iframe3');

            console_iframe3.contentWindow.document.open();

            console_iframe3.contentWindow.document.close();

            console_iframe3.contentWindow.document.write('<center style="color:red;font-size:20px;font-weight:bold">'+json_object["errors"]+'</center>');

        }

      },

      error : function (data) {

        var console_iframe3 = document.getElementById('console_iframe3');

        console_iframe3.write("Error. E-mail not sent succesfully.");

        //alert(JSON.stringify(data))

      }

   });

});



</script>

</body>
        </html>"""


        return html_string


    @cherrypy.expose
    def contact_request(self, username2, message):

        print username2

        print message

        json_object = {}

        json_object["success"] = True

        json_object["errors"] = []

        username2 = username2.strip().lower()

        if username2 == cherrypy.session.get('_cp_username').lower():
            json_object["success"] = False
            json_object["errors"].append("You cannot make a contact request for yourself.")
            print json.dumps(json_object)
            return json.dumps(json_object)

        secrets_file=open("/home/ec2-user/secrets.txt")

        passwords=secrets_file.read().rstrip('\n')

        db_password = passwords.split('\n')[0]

        dbname = "ecommunicate"

        conn = MySQLdb.connect(host='ecommunicate-production.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='browser', passwd=db_password, port=3306)

        curs = conn.cursor()

        curs.execute("use "+dbname+";")
            
        curs.execute("select * from user_info where username = \""+username2+"\";")

        if len(curs.fetchall()) == 0:
            json_object["success"] = False
            json_object["errors"].append("Username "+username2+" does not exist.")
            print json.dumps(json_object)
            return json.dumps(json_object)


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
            json_object["success"] = False
            json_object["errors"].append("Contact request already made between these two users")
            print json.dumps(json_object)
            return json.dumps(json_object)

        curs.execute("select * from contacts where username1 = \""+username1+"\" and username2 = \""+username2+"\";")

        contacts = curs.fetchall()

        if len(contacts) > 0:
            json_object["success"] = False
            json_object["errors"].append("This user is already your contact.")
            print json.dumps(json_object)
            return json.dumps(json_object)

        curs.execute("insert into contact_requests set username1 = \""+username1+"\", username2 = \""+username2+"\", message = \""+message+"\", forward="+forward+", request_time = now(6);")

        conn.commit()

        conn.close()

        print json.dumps(json_object)
        return json.dumps(json_object)

