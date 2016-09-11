import MySQLdb
import sys
import datetime
import sys,os
import cherrypy
import hashlib

import smtplib
import email

from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate

import subprocess

import time

from HTMLParser import HTMLParser

class Register(object):
    @cherrypy.expose
    def index(self):
        return """<html>
<head>

<style>

.terminal {

border: none; 

}
</style>

<title>open</title>


</head>
<body>

   <form id="register" target="console_iframe" method="post" action="register">

   username: <br><br>
   <input type="text" id="username" name="username" size="18" /><br><br>
   password: <br><br>
   <input type="password" id="password" name="password" size="18" /> <br><br>

  <button id="register" type="submit">
  Register
  </button>

  </form>

  <iframe name="console_iframe" class="terminal" />

  
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
    def register(self, username, password):

#        $( "iframe" ).clear()
        def register_function():

            secrets_file=open("/home/ec2-user/secrets.txt")

            passwords=secrets_file.read().rstrip('\n')

            db_password = passwords.split('\n')[0]

            dbname = "open"

            h = hashlib.sha256()

            h.update(password)

            conn = MySQLdb.connect(host='tutorial-db-instance.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='open', passwd=db_password, port=3306)

            curs = conn.cursor()

            curs.execute("use "+dbname+";")

            curs.execute("select * from user_info where username = \""+username+"\"")

            user_infos = curs.fetchall()

            if len(user_infos) > 0:
                yield "That username is already taken."
                return
            
            if len(password) < 6:
                yield "Please choose a password that is at least 6 characters."
                return
            
            curs.execute("insert into user_info set username = \""+username+"\", hashed_password = \""+h.hexdigest()+"\"")

            conn.commit()

            yield "Your registration was succesful. Please remember your password, as there is no way to access the account if you forget."

        return register_function()


class ShowMessages(object):
    @cherrypy.expose
    def index(self):
        return """<html>

<style>

.terminal {

border: none; 
width: 100%; 
height: 30em;


}
</style>

<head><title>open</title>

<script type="text/javascript" src="https://code.jquery.com/jquery-3.1.0.js"></script> 

<script>

function get_messages(){
   $.ajax({
      type: "GET",
      url: "get_messages",
      success: function(arg1){
//         setTimeout('get_messages()',15000);
        document.write(arg1)
      },
      error: function(arg1, arg2, arg3){
         alert("There was an error. Some information about it is: "+arg2+" "+arg3)
      }

   });
}


//$(document).ready(function(){
//    get_messages();
//});

</script>

</head>

<body>

<center>

<form id="ping_form" target="console_iframe" method="post" action="get_messages">
  username1: <br><br>
  <input type="text" id="username1" name="username1" size="18" /><br><br>
  username2: <br><br>
  <input type="text" id="username2" name="username2" size="18" /> <br><br>
  <button id="ping" class="fg-button ui-state-default ui-corner-all" type="submit">
  Display Messages
  </button>
  </form>

<iframe name="console_iframe" class="terminal" />

</center>

</body>

        </html>"""


    @cherrypy.expose
    def get_messages(self,username1,username2):
        #dn=cherrypy.request.headers['Cms-Authn-Dn']



        sorted_usernames= sorted([username1,username2])

        username1=sorted_usernames[0]
        username2=sorted_usernames[1]

        secrets_file=open("/home/ec2-user/secrets.txt")

        passwords=secrets_file.read().rstrip('\n')

        db_password = passwords.split('\n')[0]

        dbname = "open"

        conn = MySQLdb.connect(host='tutorial-db-instance.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='open', passwd=db_password, port=3306)

        curs = conn.cursor()

        curs.execute("use "+dbname+";")

        curs.execute("select * from messages where username1 = \""+username1+"\" and username2 = \""+username2+"\" order by time;")

        colnames = [desc[0] for desc in curs.description]

        messages=curs.fetchall()

        return_string=""

        for message in messages:

            message_dict=dict(zip(colnames, message))

            if message_dict["forward"] == 1:
                return_string=return_string+str(message_dict["username1"] +": " + message_dict["message"]+"<br>");
            elif message_dict["forward"] == 0:
                return_string=return_string+str(message_dict["username2"] + ": " + message_dict["message"]+"<br>");

        return return_string

    #get_messages._cp_config = {'response.stream': True}     

class Main(object):
    @cherrypy.expose
    def index(self):

        return """<html>
<head><title>open</title>

<style>
    .fg-button {
    outline: 0;
    clear: left;
    margin:0 4px 0 0;
    padding: .1em .5em;
    text-decoration:none !important;
    cursor:pointer;
    position: relative;
    text-align: center;
    zoom: 1;
    }
    .fg-button .ui-icon {
    position: absolute;
    top: 50%;
    margin-top: -8px;
    left: 50%;
    margin-left: -8px;
    }
    a.fg-button { float:left;  }
    .terminal {
    position: relative;
    top: 0;
    left: 0;
    display: block;
    font-family: monospace;
    white-space: pre;
    width: 100%; height: 30em;
    border: none;
    }
</style>

</head>
<body>

<nav>
<ul>
<li><a href="/chat">Chat</a></li>
<li><a href="/make_contact_request">Make Contact Requests</a></li>
<li><a href="/respond_to_contact_requests">Respond to Contact Requests</a></li>
</ul>
</nav>


</body>
        </html>"""

class Chat(object):
    @cherrypy.expose
    def index(self):

        return """<html>
<head><title>open</title>

<style>
    .contact {
        color : black;
        background-color: green;
        list-style-type: none;
        height: 50px;
        font-size: 24px;
        border-top: 2px solid black;
        border-bottom: 2px solid black;
        font-size: 24px;
        width: 100px;
        padding-left: 20px;
        padding-top: 20px;
        margin-top: 2px;
        font-family: Verdana;
        font-weight: bold;
        cursor: default;

    }
    .terminal {
    width: 100%;
    height: 30em;

}
</style>

</head>
<body>

<nav>
<ul>
<li><a href="/chat">Chat</a></li>
<li><a href="/make_contact_requests">Make Contact Requests</a></li>
<li><a href="/respond_to_contact_requests">Respond to Contact Requests</a></li>
</ul>
</nav>



  <table border=2>
  <tr>
  <td><ul>
<li id="kevin" name="kevin" class="contact">kevin</li>
<li id="katie" name="katie" class="contact">katie</li>
</ul></td>
  <td><iframe id="console_iframe2" name="console_iframe2" class="terminal" />  </iframe></td>
  </tr>
  </table>

</body>

<script type="text/javascript" src="https://code.jquery.com/jquery-3.1.0.js"></script> 

<script>

function chat(e){

   $.ajax({
      type: "GET",
      url: "get_messages?username2="+e.target.id,
      success: function(arg1){
//         setTimeout('get_messages()',15000);

var console_iframe2 = document.getElementById('console_iframe2');


//clear the iframe
console_iframe2.contentWindow.document.open();
console_iframe2.contentWindow.document.close();

console_iframe2.contentWindow.document.write(arg1);

      },
      error: function(arg1, arg2, arg3){
         alert("There was an error. Some information about it is: "+arg2+" "+arg3)
      }

   });

}


function contact_mouseover(e){

var target = e.target;

$('#'+target.id).css('background-color','orange');

}

function contact_mouseout(e){

var target = e.target;

$('#'+target.id).css('background-color','green');

}


var katie = document.getElementById('katie')

katie.addEventListener('click', function(e) { chat(e); } , false )

katie.addEventListener('mouseover',function(e) {contact_mouseover(e); } ,  false)

katie.addEventListener('mouseout',function(e) {contact_mouseout(e); } ,  false)

var kevin = document.getElementById('kevin')

kevin.addEventListener('click', function(e) { chat(e); } , false )

kevin.addEventListener('mouseover',function(e) { contact_mouseover(e); } ,  false)

kevin.addEventListener('mouseout',function(e) { contact_mouseout(e); } ,  false)

</script>

        </html>"""

    @cherrypy.expose
    def chat(self, username2):

        username1=cherrypy.request.login

        sorted_usernames= sorted([username1,username2])

        if sorted_usernames == [username1,username2]:
            forward=str(1)
        else:
            forward=str(0)

        username1 = sorted_usernames[0]
        username2 = sorted_usernames[1]

        cherrypy.session['username1'] = username1
        cherrypy.session['username2'] = username2
        cherrypy.session['forward'] = forward

        cherrypy.session.save()

        #dn=cherrypy.request.headers['Cms-Authn-Dn']

        secrets_file=open("/home/ec2-user/secrets.txt")

        passwords=secrets_file.read().rstrip('\n')

        db_password = passwords.split('\n')[0]

        dbname = "open"

        #conn = MySQLdb.connect(host=' tutorial-db-instance.cphov5mfizlt.us-west-2.rds.amazonaws.com:3306', user='open', passwd="openserver")

        def print_messages():

            #for some reason, if there no messages inserted already, without this yield statement, the session does not get saved
            yield "<br>"

            conn = MySQLdb.connect(host='tutorial-db-instance.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='open', passwd=db_password, port=3306)

            curs = conn.cursor()

            curs.execute("use "+dbname+";")

            #curs.execute("select * from messages order by time where username1 = \""+username1+"\" and username2 = \""+username2+"\";")

            current_time=datetime.datetime.now()

            curs.execute("select * from messages where username1 = \""+username1+"\" and username2 = \""+username2+"\" order by time;")

            colnames = [desc[0] for desc in curs.description]

            messages=curs.fetchall()

            for message in messages:

                message_dict=dict(zip(colnames, message))

                if message_dict["forward"] == 1:
                    yield str(message_dict["username1"] +": " + message_dict["message"]+"<br>")
                elif message_dict["forward"] == 0:
                    yield str(message_dict["username2"] + ": " + message_dict["message"]+"<br>")

            while True:


                time.sleep(1)

                conn = MySQLdb.connect(host='tutorial-db-instance.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='open', passwd=db_password, port=3306)

                curs = conn.cursor()

                curs.execute("use "+dbname+";")

                current_time_old=current_time
                current_time=datetime.datetime.now()

                print current_time_old.strftime("%y:%m:%d %H:%M:%S.%f")

                #curs.execute("select * from messages where username1 = \""+username1+"\" and username2 = \""+username2+"\" order by time;")
                curs.execute("select * from messages where username1 = \""+username1+"\" and username2 = \""+username2+"\" and time > \""+current_time_old.strftime("%y:%m:%d %H:%M:%S.%f")+"\" order by time;")

                colnames = [desc[0] for desc in curs.description]

                messages=curs.fetchall()

                #current_time=datetime.datetime.now()

                #if len(messages) > 0:
                #    current_time=datetime.datetime.now()

                for message in messages:

                    message_dict=dict(zip(colnames, message))

                    print message_dict["time"]

                    if message_dict["forward"] == 1:
                        yield str(message_dict["username1"] +": " + message_dict["message"]+"<br>");
                    elif message_dict["forward"] == 0:
                        yield str(message_dict["username2"] + ": " + message_dict["message"]+"<br>");

        #return

        return print_messages()

    @cherrypy.expose
    def get_messages(self,username2):
        #dn=cherrypy.request.headers['Cms-Authn-Dn']

        username1=cherrypy.request.login

        sorted_usernames= sorted([username1,username2])

        username1=sorted_usernames[0]
        username2=sorted_usernames[1]

        secrets_file=open("/home/ec2-user/secrets.txt")

        passwords=secrets_file.read().rstrip('\n')

        db_password = passwords.split('\n')[0]

        dbname = "open"

        conn = MySQLdb.connect(host='tutorial-db-instance.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='open', passwd=db_password, port=3306)

        curs = conn.cursor()

        curs.execute("use "+dbname+";")

        curs.execute("select * from messages where username1 = \""+username1+"\" and username2 = \""+username2+"\" order by time;")

        colnames = [desc[0] for desc in curs.description]

        messages=curs.fetchall()

        return_string=""

        for message in messages:

            message_dict=dict(zip(colnames, message))

            if message_dict["forward"] == 1:
                return_string=return_string+str(message_dict["username1"] +": " + message_dict["message"]+"<br>");
            elif message_dict["forward"] == 0:
                return_string=return_string+str(message_dict["username2"] + ": " + message_dict["message"]+"<br>");

        return return_string

    @cherrypy.expose
    def add_message(self, message):

        username1=cherrypy.request.login
        
        username2 = cherrypy.session.get("username2")
        forward= cherrypy.session.get("forward")

        secrets_file=open("/home/ec2-user/secrets.txt")

        passwords=secrets_file.read().rstrip('\n')

        db_password = passwords.split('\n')[0]

        dbname = "open"

        conn = MySQLdb.connect(host='tutorial-db-instance.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='open', passwd=db_password, port=3306)

        curs = conn.cursor()

        curs.execute("use "+dbname+";")
            
        curs.execute("insert into messages set username1 = \""+username1+"\", username2 = \""+username2+"\", forward="+forward+", time=now(6), message = \""+message+"\";")

        conn.commit()

    chat._cp_config = {'response.stream': True}

class MakeContactRequest(object):
    @cherrypy.expose
    def index(self):

        return """<html>
<head><title>open</title>

<style>
    .fg-button {
    outline: 0;
    clear: left;
    margin:0 4px 0 0;
    padding: .1em .5em;
    text-decoration:none !important;
    cursor:pointer;
    position: relative;
    text-align: center;
    zoom: 1;
    }
    .fg-button .ui-icon {
    position: absolute;
    top: 50%;
    margin-top: -8px;
    left: 50%;
    margin-left: -8px;
    }
    a.fg-button { float:left;  }
    .terminal {
    position: relative;
    top: 0;
    left: 0;
    display: block;
    font-family: monospace;
    white-space: pre;
    width: 100%; height: 30em;
    border: none;
    }
</style>

</head>
<body>

<nav>
<ul>
<li><a href="/chat">Chat</a></li>
<li><a href="/make_contact_requests">Make Contact Requests</a></li>
<li><a href="/respond_to_contact_requests">Respond to Contact Requests</a></li>
</ul>
</nav>

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

  <iframe name="console_iframe2" class="terminal" /> </iframe>

</body>
        </html>"""


    @cherrypy.expose
    def contact_request(self, username2, message):

        if username2 == cherrypy.request.login:
            return "You cannot make a contact request for yourself."
        
        secrets_file=open("/home/ec2-user/secrets.txt")

        passwords=secrets_file.read().rstrip('\n')

        db_password = passwords.split('\n')[0]

        dbname = "open"

        conn = MySQLdb.connect(host='tutorial-db-instance.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='open', passwd=db_password, port=3306)

        curs = conn.cursor()

        curs.execute("use "+dbname+";")
            
        curs.execute("select * from user_info where username = \""+username2+"\";")

        if len(curs.fetchall()) == 0:
            return "Username "+username2+" does not exist."

        username1=cherrypy.request.login

        sorted_usernames= sorted([username1,username2])

        if sorted_usernames == [username1,username2]:
            forward=str(1)
        else:
            forward=str(0)

        curs.execute("select * from contact_requests where username1 = \""+username1+"\" and username2 = \""+username2+"\";")

        contact_requests = curs.fetchall()

        if len(contact_requests) > 0:
            return "Contact request already made between these two users."

        curs.execute("select * from contacts where username1 = \""+username1+"\" and username2 = \""+username2+"\";")

        contacts = curs.fetchall()

        if len(contacts) > 0:
            return "Contact request already made between these two users."

        curs.execute("insert into contact_requests set username1 = \""+username1+"\", username2 = \""+username2+"\", message = \""+message+"\", forward="+forward+";")

        conn.commit()

        return "A contact request has been sent to user "+username2+"."

class Root(object):
    @cherrypy.expose
    def index(self):
        return ""

class ContactRequestResponses(object):
    @cherrypy.expose
    def index(self):

        secrets_file=open("/home/ec2-user/secrets.txt")

        passwords=secrets_file.read().rstrip('\n')

        db_password = passwords.split('\n')[0]

        dbname = "open"

        conn = MySQLdb.connect(host='tutorial-db-instance.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='open', passwd=db_password, port=3306)

        curs = conn.cursor()

        curs.execute("use "+dbname+";")

        curs.execute("select * from contact_requests where username1 = \""+cherrypy.request.login+"\" and forward=0;")

        contact_requests = curs.fetchall()

        curs.execute("select * from contact_requests where username2 = \""+cherrypy.request.login+"\" and forward=1;")

        contact_requests = contact_requests+curs.fetchall()

        contact_request_string = "<form action=\"contact_request_responses\" method=\"post\" id =\"contact_request_responses\" target=\"console_iframe4\">\n"

        for contact_request in contact_requests:

            colnames = [desc[0] for desc in curs.description]

            contact_request_dict=dict(zip(colnames, contact_request))

            if contact_request_dict["username2"] == cherrypy.request.login:
                username = contact_request_dict["username1"]
            else:
                assert(contact_request_dict["username1"] == cherrypy.request.login)
                username = contact_request_dict["username2"]


            contact_request_string = contact_request_string+username+": <select name=\""+username+"\">\n<option value=\"Wait\"></option>\n<option value=\"Accept\">Accept</option>\n<option value=\"Reject\">Reject</option></select>\n<br><br>"

        contact_request_string=contact_request_string+"<br><button type=\"submit\" id = \"contact_request_responses\">Respond to contact requests</button>\n</form>"


        return """<html>
<head><title>open</title>

<style>
    .fg-button {
    outline: 0;
    clear: left;
    margin:0 4px 0 0;
    padding: .1em .5em;
    text-decoration:none !important;
    cursor:pointer;
    position: relative;
    text-align: center;
    zoom: 1;
    }
    .fg-button .ui-icon {
    position: absolute;
    top: 50%;
    margin-top: -8px;
    left: 50%;
    margin-left: -8px;
    }
    a.fg-button { float:left;  }
    .terminal {
    position: relative;
    top: 0;
    left: 0;
    display: block;
    font-family: monospace;
    white-space: pre;
    width: 100%; height: 30em;
    border: none;
    }
</style>

</head>
<body>

<nav>
<ul>
<li><a href="/chat">Chat</a></li>
<li><a href="/contact_request_responses">Make Contact Requests</a></li>
<li><a href="/contact_requests">Respond to Contact Requests</a></li>
</ul>
</nav>

""" + contact_request_string + """

  <iframe name="console_iframe4" class="terminal" />  </iframe>

</body>
        </html>"""

    @cherrypy.expose
    def contact_request_responses(self,**responses):

        secrets_file=open("/home/ec2-user/secrets.txt")

        passwords=secrets_file.read().rstrip('\n')

        db_password = passwords.split('\n')[0]

        dbname = "open"

        conn = MySQLdb.connect(host='tutorial-db-instance.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='open', passwd=db_password, port=3306)

        curs = conn.cursor()

        curs.execute("use "+dbname+";")

        for username in responses.keys():
            if responses[username] == "Wait":
                continue
            elif responses[username] == "Reject":

                curs.execute("delete from contact_requests where username1 = \""+username+"\" and username2 = \""+cherrypy.request.login+"\";")
                curs.execute("delete from contact_requests where username2 = \""+username+"\" and username1 = \""+cherrypy.request.login+"\";")
            elif responses[username] == "Accept":

                curs.execute("select * from contacts where username1 = \""+cherrypy.request.login+"\" and username2 = \""+username+"\";")

                contacts_tuple1=curs.fetchall()
                
                curs.execute("select * from contacts where username1 = \""+username+"\" and username2 = \""+cherrypy.request.login+"\";")

                contacts_tuple2=curs.fetchall()

                contacts_tuple = contacts_tuple1+contacts_tuple2

                if len(contacts_tuple) > 0:
                    continue

                curs.execute("delete from contact_requests where username1 = \""+username+"\" and username2 = \""+cherrypy.request.login+"\";")
                curs.execute("delete from contact_requests where username2 = \""+username+"\" and username1 = \""+cherrypy.request.login+"\";")
                
                sorted_usernames= sorted([cherrypy.request.login,username])

                username1=sorted_usernames[0]
                username2=sorted_usernames[1]

                curs.execute("insert into contacts set username1 = \""+username1+"\", username2 = \""+username2+"\";")
            
        conn.commit()

        return "Your responses have been registered."

USERS = {'jon': 'secret'}

def validate_password(realm, username, password):

    secrets_file=open("/home/ec2-user/secrets.txt")

    passwords=secrets_file.read().rstrip('\n')

    db_password = passwords.split('\n')[0]

    dbname = "open"

    conn = MySQLdb.connect(host='tutorial-db-instance.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='open', passwd=db_password, port=3306)

    curs = conn.cursor()

    curs.execute("use "+dbname+";")

    curs.execute("select * from user_info where username = \""+username+"\";")

    colnames = [desc[0] for desc in curs.description]

    user_infos=curs.fetchall()

    if len(user_infos) == 0:
        return False
    else:
        assert(len(user_infos) == 1)

    user_info=user_infos[0]

    user_info_dict=dict(zip(colnames, user_info))

    hashed_password = user_info_dict["hashed_password"]

    h = hashlib.sha256()

    h.update(password)

    if h.hexdigest() == hashed_password:
        return True
    else:
        return False

if __name__ == '__main__':
    cherrypy.config.update({'server.socket_port': 8080})
    cherrypy.config.update({'server.socket_host': 'ec2-52-42-148-78.us-west-2.compute.amazonaws.com'})
    cherrypy.config.update({'tools.sessions.on': True})

    cherrypy.tree.mount(ShowMessages(),'/show_messages')
    cherrypy.tree.mount(Chat(),'/chat',{ '/': {
       'tools.auth_basic.on': True,
       'tools.auth_basic.realm': 'localhost',
       'tools.auth_basic.checkpassword': validate_password
    } }  )
    cherrypy.tree.mount(MakeContactRequest(),'/make_contact_requests',{ '/': {
       'tools.auth_basic.on': True,
       'tools.auth_basic.realm': 'localhost',
       'tools.auth_basic.checkpassword': validate_password
    } }  )
    cherrypy.tree.mount(ContactRequestResponses(),'/respond_to_contact_requests',{ '/': {
       'tools.auth_basic.on': True,
       'tools.auth_basic.realm': 'localhost',
       'tools.auth_basic.checkpassword': validate_password
    } }  )
    cherrypy.tree.mount(Main(),'/main',{ '/': {
       'tools.auth_basic.on': True,
       'tools.auth_basic.realm': 'localhost',
       'tools.auth_basic.checkpassword': validate_password
    }} )
    cherrypy.tree.mount(Main(),'/',{ 
    '/style.css' : {
       'tools.staticfile.on': True,
       'tools.staticfile.filename' : "/home/ec2-user/server/style.css"
 } } )
    cherrypy.tree.mount(Register(),'/register')
    #cherrypy.quickstart(Open())

    cherrypy.server.ssl_module = 'builtin'

    cherrypy.server.ssl_certificate = "cert.pem"
    cherrypy.server.ssl_private_key = "privkey.pem"
    #cherrypy.server.ssl_certificate_chain = "/etc/pki/tls/certs/ca-bundle.crt"

    cherrypy.engine.start()
    cherrypy.engine.block()

