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

import json

def is_session_authenticated(*args, **kwargs):

    conditions = cherrypy.request.config.get('auth.require', None)
    if conditions is not None:

        username = cherrypy.session.get('_cp_username')

        if username:

            cherrypy.request.login = username

        else:
            raise cherrypy.HTTPRedirect("/loginlogout/login")

cherrypy.tools.auth = cherrypy.Tool('before_handler', is_session_authenticated)

def require(*conditions):
    """A decorator that appends conditions to the auth.require config
    variable."""
    def decorate(f):
        if not hasattr(f, '_cp_config'):
            f._cp_config = dict()
        if 'auth.require' not in f._cp_config:
            f._cp_config['auth.require'] = []
        f._cp_config['auth.require'].extend(conditions)
        return f
    return decorate

class LogInLogOut(object):

    def login_html(self,  message="", from_page="/"):

        login_html_string = "<html>"
        login_html_string = login_html_string+"<center>"
        login_html_string = login_html_string+"<form method=\"post\" action=\"/loginlogout/login\">"
        login_html_string = login_html_string+"<input type=\"hidden\" name=\"from_page\" value=\""+from_page+"\" />"
        login_html_string = login_html_string+"username: <br><br>"
        login_html_string = login_html_string+"<input type=\"text\" id=\"username\" name=\"username\" size=\"18\" /><br><br>"
        login_html_string = login_html_string+"password: <br><br>"
        login_html_string = login_html_string+"<input type=\"password\" id=\"password\" name=\"password\" size=\"18\" /> <br><br>"
        login_html_string = login_html_string+"<button type=\"submit\">"
        login_html_string = login_html_string+"Login"
        login_html_string = login_html_string+"</button>"
        if message != "":
            login_html_string = login_html_string+"<br><br>"
            login_html_string = login_html_string+message
        login_html_string = login_html_string+"</center>"
        return login_html_string    
        
        
    @cherrypy.expose
    def login(self, username=None, password=None, from_page="/"):

        if username is None or password is None:
            return self.login_html(from_page=from_page)
        
        [pass_password_check,error_msg] = is_right_password(username, password)
        if not pass_password_check:
            return self.login_html(error_msg, from_page)
        else:

            cherrypy.request.login = username

            cherrypy.session['_cp_username'] = username
            raise cherrypy.HTTPRedirect(from_page)
    
    @cherrypy.expose
    def logout(self, from_page="/"):
        cherrypy.session['_cp_username'] = None

        cherrypy.request.login = None
        raise cherrypy.HTTPRedirect(from_page)

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

   This is an <b>open chatting service</b>. It is similar to wechat or Google Hangouts, except that all conversations are viewable on the open internet. Register here for your free account. 

<br><br>

<center>

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

</center>
  
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


class View(object):
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

</head>

<body>

<center>



<form id="view_messages_form" target="console_iframe" method="post" action="view_messages">
  username1: <br><br>
  <input type="text" id="username1" name="username1" size="18" /><br><br>
  username2: <br><br>
  <input type="text" id="username2" name="username2" size="18" /> <br><br>
  <button id="ping" class="fg-button ui-state-default ui-corner-all" type="submit">
  View
  </button>
</form>

<iframe name="console_iframe" class="terminal" /> </iframe>

</center>

</body>

<script>

$('#view_messages_form').submit(function(event) {



   event.preventDefault(); 

   var $this = $(this);

   $.ajax({
      type: "POST",
      url: $this.attr('action'),
      dataType: 'html',
      data: $this.serialize(),
      success: function(data){


        parsed_data = JSON.parse(data);
        messages_list = parsed_data[0];
        for ( var i = 0, l = messages_list.length; i < l; i++ ) {
           document.write(messages_list[i][0]+": "+messages_list[i][1]);
           document.write("<br>");
        }

      },
      error: function(arg1, arg2, arg3){
         alert("There was an error. Some information about it is: "+arg2+" "+arg3)
      }

   });

});


</script>

</html>"""


    @cherrypy.expose
    def view_messages(self,username1,username2,upon_update=False,client_max_time=""):
        #dn=cherrypy.request.headers['Cms-Authn-Dn']

        #client_max_time="2017-06-30 08:01:06.562369";

        sorted_usernames= sorted([username1,username2])

        username1=sorted_usernames[0]

        username2=sorted_usernames[1]

        secrets_file=open("/home/ec2-user/secrets.txt")

        passwords=secrets_file.read().rstrip('\n')

        db_password = passwords.split('\n')[0]

        dbname = "open"

        conn = MySQLdb.connect(host='tutorial-db-instance.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='open', passwd=db_password, port=3306)

        if upon_update:

            while True:

                conn.commit()
                
                curs = conn.cursor()

                curs.execute("use "+dbname+";")

                curs.execute("select MAX(time) from messages where username1=\""+username1+"\";")

                server_max_time = curs.fetchall()[0][0]

                if server_max_time != None and server_max_time > datetime.datetime.strptime(client_max_time,"%Y-%m-%d %H:%M:%S.%f"):
                    break

                curs.execute("select MAX(time) from messages where username2=\""+username1+"\";")

                server_max_time = curs.fetchall()[0][0]

                if server_max_time != None and server_max_time > datetime.datetime.strptime(client_max_time,"%Y-%m-%d %H:%M:%S.%f"):
                    break

                curs.close()    
                
                time.sleep(0.1)


        #conn = MySQLdb.connect(host='tutorial-db-instance.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='open', passwd=db_password, port=3306)

        curs = conn.cursor()

        curs.execute("use "+dbname+";")

        messages_list = []

        curs.execute("select * from messages where username1 = \""+username1+"\" and username2 = \""+username2+"\" order by time;")

        colnames = [desc[0] for desc in curs.description]

        messages=curs.fetchall()

        return_string=""

        if len(messages) > 0:

            for message in messages:

                message_dict=dict(zip(colnames, message))

                if message_dict["forward"] == 1:
                    return_string=return_string+str(message_dict["username1"] +": " + message_dict["message"]+"<br>");
                    messages_list.append([message_dict["username1"], message_dict["message"]])
                elif message_dict["forward"] == 0:
                    return_string=return_string+str(message_dict["username2"] + ": " + message_dict["message"]+"<br>");
                    messages_list.append([message_dict["username2"], message_dict["message"]])


        #return str(messages_json)

        curs.execute("select MAX(time) from messages where username1 = \""+username1+"\" and username2 = \""+username2+"\";")

        max_time = str(curs.fetchall()[0][0])

        curs.close()

        return json.dumps([messages_list,max_time])

        #return '{"a1" : "b1"}'

class MakeContactRequest(object):

    _cp_config = {
        'tools.sessions.on': True,
        'tools.auth.on': True
    }

    @cherrypy.expose
    @require()
    def index(self):

        return """<html>
<head><title>open</title>

<style>

ul.menubar {

text-align: center;

}

li.menubar {
        display: inline;
        padding: 5px;
}

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
<ul class="menubar">
<li class="menubar"><a href="/chat">Chat</a></li>
<li class="menubar"><a href="/chat/makecontactrequests">Make Contact Requests</a></li>
<li class="menubar"><a href="/chat/respondtocontactrequests">Respond to Contact Requests</a></li>
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

  <iframe name="console_iframe3" class="terminal" /> </iframe>

</body>
        </html>"""


    @cherrypy.expose
    def contact_request(self, username2, message):

        if username2 == cherrypy.session.get('_cp_username'):
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

        original_username2 = username2    

        username1 = sorted_usernames[0]
    
        username2 = sorted_usernames[1]    

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

        return "A contact request has been sent to user "+original_username2+"."

class ContactRequestResponses(object):
    @cherrypy.expose
    @require()
    def index(self):

        secrets_file=open("/home/ec2-user/secrets.txt")

        passwords=secrets_file.read().rstrip('\n')

        db_password = passwords.split('\n')[0]

        dbname = "open"

        conn = MySQLdb.connect(host='tutorial-db-instance.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='open', passwd=db_password, port=3306)

        curs = conn.cursor()

        curs.execute("use "+dbname+";")

        curs.execute("select * from contact_requests where username1 = \""+cherrypy.session.get('_cp_username')+"\" and forward=0;")

        contact_requests = curs.fetchall()

        curs.execute("select * from contact_requests where username2 = \""+cherrypy.session.get('_cp_username')+"\" and forward=1;")

        contact_requests = contact_requests+curs.fetchall()

        contact_request_string = "<form action=\"contact_request_responses\" method=\"post\" id =\"contact_request_responses\" target=\"console_iframe4\">\n"

        for contact_request in contact_requests:

            colnames = [desc[0] for desc in curs.description]

            contact_request_dict=dict(zip(colnames, contact_request))

            if contact_request_dict["username2"] == cherrypy.session.get('_cp_username'):
                username = contact_request_dict["username1"]
            else:
                assert(contact_request_dict["username1"] == cherrypy.session.get('_cp_username'))
                username = contact_request_dict["username2"]


            contact_request_string = contact_request_string+username+": <select name=\""+username+"\">\n<option value=\"Wait\"></option>\n<option value=\"Accept\">Accept</option>\n<option value=\"Reject\">Reject</option></select>\n<br><br>"

        contact_request_string=contact_request_string+"<br><button type=\"submit\" id = \"contact_request_responses\">Respond to contact requests</button>\n</form>"


        return """<html>
<head><title>open</title>

<style>

ul.menubar {

text-align: center;

}

li.menubar {
        display: inline;
        padding: 5px;
}

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
<ul class="menubar">
<li class="menubar"><a href="/chat">Chat</a></li>
<li class="menubar"><a href="/chat/contact_request_responses">Make Contact Requests</a></li>
<li class="menubar"><a href="/chat/contact_requests">Respond to Contact Requests</a></li>
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

                curs.execute("delete from contact_requests where username1 = \""+username+"\" and username2 = \""+cherrypy.session.get('_cp_username')+"\";")
                curs.execute("delete from contact_requests where username2 = \""+username+"\" and username1 = \""+cherrypy.session.get('_cp_username')+"\";")
            elif responses[username] == "Accept":

                curs.execute("select * from contacts where username1 = \""+cherrypy.request.login+"\" and username2 = \""+username+"\";")

                contacts_tuple1=curs.fetchall()
                
                curs.execute("select * from contacts where username1 = \""+username+"\" and username2 = \""+cherrypy.session.get('_cp_username')+"\";")

                contacts_tuple2=curs.fetchall()

                contacts_tuple = contacts_tuple1+contacts_tuple2

                if len(contacts_tuple) > 0:
                    continue

                curs.execute("delete from contact_requests where username1 = \""+username+"\" and username2 = \""+cherrypy.session.get('_cp_username')+"\";")
                curs.execute("delete from contact_requests where username2 = \""+username+"\" and username1 = \""+cherrypy.session.get('_cp_username')+"\";")
                
                sorted_usernames= sorted([cherrypy.request.login,username])

                username1=sorted_usernames[0]
                username2=sorted_usernames[1]

                curs.execute("insert into contacts set username1 = \""+username1+"\", username2 = \""+username2+"\";")
            
        conn.commit()

        return "Your responses have been registered."




class Chat(object):


    register = Register()

    makecontactrequests=MakeContactRequest()

    respondtocontactrequests=ContactRequestResponses()

    @cherrypy.expose
    @require()
    def index(self):

        secrets_file=open("/home/ec2-user/secrets.txt")

        passwords=secrets_file.read().rstrip('\n')

        db_password = passwords.split('\n')[0]

        dbname = "open"

        conn = MySQLdb.connect(host='tutorial-db-instance.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='open', passwd=db_password, port=3306)

        curs = conn.cursor()

        curs.execute("use "+dbname+";")

        curs.execute("select * from contacts where username1 = \""+cherrypy.request.login+"\"")

        contacts = curs.fetchall()

        curs.execute("select * from contacts where username2 = \""+cherrypy.request.login+"\"")

        contacts = contacts+curs.fetchall()

        contacts_string = "<td><ul id=\"contactslist\">\n"

        iframes_string = "";

        iframes_hide_string = "";

        for contact in contacts:

            colnames = [desc[0] for desc in curs.description]

            contact_dict=dict(zip(colnames, contact))

            if contact_dict["username2"] == cherrypy.request.login:
                username = contact_dict["username1"]
            else:
                assert(contact_dict["username1"] == cherrypy.request.login)
                username = contact_dict["username2"]

            contacts_string = contacts_string+"<li id=\""+username+"\" name=\""+username+"\" class=\"contact\">"+username+"</li>\n" 

            iframes_string = iframes_string+ "<iframe id=\"console_"+username+"\" name=\"console_"+username+"\" class=\"terminal\" />  </iframe>\n"

            iframes_hide_string = iframes_hide_string+"$(\'#console_" + username + "\').hide();\n"

        contacts_string=contacts_string+"</ul></td>\n</td>"


        return """<html>
<head><title>open</title>

<style>

ul.menubar {

text-align: center;

}

li.menubar {
        display: inline;
        padding: 5px;
}

ul {
    list-style:none;
    padding-left:0;
}

    .contact {
        color : black;
        background-color: green;
        height: 50px;
        font-size: 24px;
        font-size: 24px;
        width: 98.5%;
//        padding-left: 20px;
        padding-top: 20px;
        margin-top: 2px;
        font-family: Verdana;
        font-weight: bold;
        cursor: default;
        border-top: 2px solid black;
        border-bottom: 2px solid black;

    }
    .terminal {
    width: 100%;
    height: 30em;
    border: none;

}
    .messageerrorbox {
    width: 100%;
    height: 1em;
    border: none;

}
</style>

</head>
<body>


<!--
<nav>
-->

<div id="header">

<div id="nav">

<ul class="menubar">
<li class="menubar"><a href="/chat/">Chat</a></li>
<li class="menubar"><a href="/chat/makecontactrequests/">Make Contact Requests</a></li>
<li class="menubar"><a href="/chat/respondtocontactrequests/">Respond to Contact Requests</a></li>
<li class="menubar"><a href="/loginlogout/logout/">Logout</a></li>
</ul>

</div>

</div>

<!--
</nav>
-->


  <table border=2>
  <tr>
""" + contacts_string + """ 
  <td>

"""+ iframes_string + """

<form id="add_message_form" name = "add_messages_form" target="console_iframe1" method="POST" action="add_message">

 <input type="text" id="add_message_text" name="add_message_text" size="100" /> <br> <br>

 <input type="hidden" id="username2" name="username2"/>

 </form>

 <iframe id="console_iframe1" name="console_iframe1" class="messageerrorbox" />  </iframe>

</td>
  </tr>
  </table>

</body>

<script type="text/javascript" src="https://code.jquery.com/jquery-3.1.0.js"></script> 

<script>

messages_json = "";
messages_json_old = "";
username2  = "";
max_time = ""

function show_messages(e){

   var target = e.target;

   if( target.id != "contactslist"){

    var console_iframe2 = document.getElementById('console_'+e.target.id);

    if (username2 != ""){
    
        $('#console_'+username2).hide();

    }


//    console_iframe2.slideDown('slow');

 

    username2=e.target.id;

    $('#console_'+username2).show();

   }
}

function update_messages(){

    if (messages_json != "") {



        for (var item in messages_json) {  

            var console_iframe2 = document.getElementById('console_'+item);

            //clear the iframe
            console_iframe2.contentWindow.document.open();
            console_iframe2.contentWindow.document.close();

            for ( var i = 0, l = messages_json[item].length; i < l; i++ ) {
                console_iframe2.contentWindow.document.write(messages_json[item][i][0]+": "+messages_json[item][i][1]);
                console_iframe2.contentWindow.document.write("<br>");
            }

            var console_iframe2_contentWindow_document = console_iframe2.contentWindow.document;


            //this will "over-scroll", but it works i.e. it moves to the bottom    

            $(console_iframe2_contentWindow_document).scrollTop($(console_iframe2_contentWindow_document).height());  


        }
    }

}


$(document).ready(function() {


"""+iframes_hide_string+"""

   chat_initial();

});


function chat_initial() {

   $.ajax({
      url: 'get_messages',
      type: 'GET',
      dataType: 'html',
      success: function(data) {
         parsed_data = JSON.parse(data);
         //alert(parsed_data["phone8"]);
         messages_json = parsed_data[0];
         max_time=parsed_data[1]; 

         messages_json_old = messages_json;

         update_messages(); 

         chat_recursive();

      }
   });




}

function chat_recursive() {

get_messages_url = 'get_messages?upon_update=True&client_max_time='+max_time;

   $.ajax({
      url: get_messages_url,
      type: 'GET',
      dataType: 'html',
      success: function(data) {

         parsed_data = JSON.parse(data);
         //alert(parsed_data["phone8"]);
         messages_json = parsed_data[0];
         max_time = parsed_data[1];

         if (messages_json_old != ""){
             for (var item in messages_json) {
                 if ( messages_json[item].length > messages_json_old[item].length ) {
                    for ( var i = messages_json_old[item].length, l = messages_json[item].length; i < l; i++ ) { 
                        if (messages_json[item][i][0] == item){
                            $('#'+item).css('background-color','blue');
                        }
                    }  

                 }
             }
         }
         messages_json_old = messages_json;

         update_messages();  

         chat_recursive();
      }
   });

}

$('#add_message_form').submit(function(event) {

   event.preventDefault();

   $('input[name="username2"]',this).val(username2);

   var $this = $(this);

   //$.get($this.attr('action'),$this.serialize());

   //alert($this.serialize());

   $.ajax({
      url: $this.attr('action'),
      type: 'POST',
      dataType: 'html',
      data: $this.serialize()
   
   });

  add_message_form.reset();

});


//$('#add_message_text')
//.keyup(function(event) {

//if (event.keyCode == 13){

//alert(event.keyCode);

//}

//});

function contact_mouseover(e){

var target = e.target;

if( target.id != "contactslist"){
    $('#'+target.id).css('background-color','orange');
}

}

function contact_mouseout(e){

var target = e.target;

if( target.id != "contactslist"){
    $('#'+target.id).css('background-color','green');
}


}

console_iframe1=document.getElementById('console_iframe1')

//var add_message_form = document.getElementById('add_message_form')
//var message = document.getElementById('message')

//add_message_form.addEventListener('submit', function (e) { 

//e.preventDefault();

//add_message_form.submit();

//}, false)

//console_iframe1.addEventListener('load', function(e) {

//add_message_form.reset();

//}, false)


var contactslist = document.getElementById('contactslist')

contactslist.addEventListener('touchstart', function(e) { show_messages(e); } , false )

contactslist.addEventListener('click', function(e) { 

    show_messages(e); 

} , false )

contactslist.addEventListener('mouseover',function(e) {contact_mouseover(e); } ,  false)

contactslist.addEventListener('mouseout',function(e) {contact_mouseout(e); } ,  false)

</script>

        </html>"""

    @cherrypy.expose
    def get_messages(self,upon_update=False,client_max_time=""):

        #dn=cherrypy.request.headers['Cms-Authn-Dn']

        #client_max_time="2017-06-30 08:01:06.562369";

        username1=cherrypy.session.get('_cp_username')

        secrets_file=open("/home/ec2-user/secrets.txt")

        passwords=secrets_file.read().rstrip('\n')

        db_password = passwords.split('\n')[0]

        dbname = "open"

        conn = MySQLdb.connect(host='tutorial-db-instance.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='open', passwd=db_password, port=3306)

        if upon_update:

            while True:

                conn.commit()
                
                curs = conn.cursor()

                curs.execute("use "+dbname+";")

                curs.execute("select MAX(time) from messages where username1=\""+username1+"\";")

                server_max_time = curs.fetchall()[0][0]

                if server_max_time != None and server_max_time > datetime.datetime.strptime(client_max_time,"%Y-%m-%d %H:%M:%S.%f"):
                    break

                curs.execute("select MAX(time) from messages where username2=\""+username1+"\";")

                server_max_time = curs.fetchall()[0][0]

                if server_max_time != None and server_max_time > datetime.datetime.strptime(client_max_time,"%Y-%m-%d %H:%M:%S.%f"):
                    break

                curs.close()    
                
                time.sleep(0.1)


        #conn = MySQLdb.connect(host='tutorial-db-instance.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='open', passwd=db_password, port=3306)

        curs = conn.cursor()

        curs.execute("use "+dbname+";")

        curs.execute("select * from contacts where username1 = \""+cherrypy.session.get('_cp_username')+"\"")

        contacts = curs.fetchall()

        curs.execute("select * from contacts where username2 = \""+cherrypy.session.get('_cp_username')+"\"")

        contacts = contacts+curs.fetchall()

        colnames_contacts = [desc[0] for desc in curs.description]

        messages_json = {}


        for contact in contacts:

            contact_dict=dict(zip(colnames_contacts, contact))

            if contact_dict["username2"] == cherrypy.session.get('_cp_username'):
                username = contact_dict["username1"]
                curs.execute("select * from messages where username1 = \""+username+"\" and username2 = \""+username1+"\" order by time;")
            else:
                assert(contact_dict["username1"] == cherrypy.session.get('_cp_username'))
                username = contact_dict["username2"]
                curs.execute("select * from messages where username1 = \""+username1+"\" and username2 = \""+username+"\" order by time;")

            colnames = [desc[0] for desc in curs.description]

            messages=curs.fetchall()

            return_string=""

            if len(messages) > 0:

                messages_json[username] = []

                for message in messages:

                    message_dict=dict(zip(colnames, message))

                    if message_dict["forward"] == 1:
                        return_string=return_string+str(message_dict["username1"] +": " + message_dict["message"]+"<br>");
                        messages_json[username].append([message_dict["username1"], message_dict["message"]])
                    elif message_dict["forward"] == 0:
                        return_string=return_string+str(message_dict["username2"] + ": " + message_dict["message"]+"<br>");
                        messages_json[username].append([message_dict["username2"], message_dict["message"]])


        #return str(messages_json)

        curs.execute("select MAX(time) from messages where username1=\""+username1+"\";")

        max_time1 = curs.fetchall()[0][0]

        curs.execute("select MAX(time) from messages where username2=\""+username1+"\";")

        max_time2 = curs.fetchall()[0][0]

        curs.close()

        if max_time1 == None and max_time2 != None:
            max_time = str(max_time2)

        elif max_time2 == None and max_time1 != None:
            max_time = str(max_time1)

        elif max_time1 == None and max_time2 == None:
            max_time = None

        else:
            max_time = str(max(max_time1,max_time2))

        return json.dumps([messages_json,max_time])

        #return '{"a1" : "b1"}'



    @cherrypy.expose
    def add_message(self, add_message_text,username2):

        username1=cherrypy.session.get('_cp_username')
        
        sorted_usernames= sorted([username1,username2])

        if sorted_usernames == [username1,username2]:
            forward = "1"
        else:
            forward = "0"

        username1=sorted_usernames[0]

        username2=sorted_usernames[1]

        secrets_file=open("/home/ec2-user/secrets.txt")

        passwords=secrets_file.read().rstrip('\n')

        db_password = passwords.split('\n')[0]

        dbname = "open"

        conn = MySQLdb.connect(host='tutorial-db-instance.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='open', passwd=db_password, port=3306)

        curs = conn.cursor()

        curs.execute("use "+dbname+";")

        curs.execute("insert into messages set username1 = \""+username1+"\", username2 = \""+username2+"\", forward="+forward+", time=now(6), message = \""+add_message_text+"\";")

        conn.commit()

class MakeContactRequest(object):

#    _cp_config = {
#        'tools.sessions.on': True,
#        'tools.auth.on': True
#    }

    @cherrypy.expose
    @require()
    def index(self):

        return """<html>
<head><title>open</title>

<style>

ul.menubar {

text-align: center;

}

li.menubar {
        display: inline;
        padding: 5px;
}

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
<ul class="menubar">
<li class="menubar"><a href="/chat">Chat</a></li>
<li class="menubar"><a href="/chat/makecontactrequests">Make Contact Requests</a></li>
<li class="menubar"><a href="/chat/respondtocontactrequests">Respond to Contact Requests</a></li>
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

  <iframe name="console_iframe3" class="terminal" /> </iframe>

</body>
        </html>"""


    @cherrypy.expose
    def contact_request(self, username2, message):

        if username2 == cherrypy.session.get('_cp_username'):
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

        original_username2 = username2    

        username1 = sorted_usernames[0]
    
        username2 = sorted_usernames[1]    

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

        return "A contact request has been sent to user "+original_username2+"."

class Root(object):

    _cp_config = {
        'tools.sessions.on': True,
        'tools.auth.on': True
    }

    view = View()

    chat = Chat()

    loginlogout = LogInLogOut()

    @cherrypy.expose
    def index(self):

        html_string="<center><h1>ecommunicate</h1>"
        html_string = html_string+"<h3>a free online communication service</h3></center>"
        html_string = html_string+"ecommunicate is an free online communication service in which all communication is viewable on the open internet. Currently, only text messaging is implemented. You can chat yourself (after registering and logging in) or you can view other people's conversations (see below).<br>"
        return html_string

def is_right_password(username, password):

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
        return [False,"Login failed. The username that you entered was not found."]
    else:
        assert(len(user_infos) == 1)

    user_info=user_infos[0]

    user_info_dict=dict(zip(colnames, user_info))

    hashed_password = user_info_dict["hashed_password"]

    h = hashlib.sha256()

    h.update(password)

    if h.hexdigest() == hashed_password:
        return [True,""]
    else:
        return [False,"Login failed. The password that you entered is not the one associated with the username that you entered."]

if __name__ == '__main__':
    cherrypy.config.update({'server.socket_port': 443}) #port 443 for https or port 80 for http
#    cherrypy.config.update({'server.socket_port': 80})
    cherrypy.config.update({'server.socket_host': 'ec2-52-42-148-78.us-west-2.compute.amazonaws.com'})
    #cherrypy.config.update({'tools.sessions.on': True})
    #cherrypy.config.update({'tools.auth.on': True})

    #cherrypy.tree.mount(View(),'/view')
    cherrypy.tree.mount(Root())
    #cherrypy.tree.mount(MakeContactRequest(),'/make_contact_requests')
    #cherrypy.tree.mount(ContactRequestResponses(),'/respond_to_contact_requests')
    #cherrypy.tree.mount(Register(),'/register')
#    cherrypy.tree.mount(LogInLogOut(),'/loginlogout')

    cherrypy.server.ssl_module = 'builtin'
    cherrypy.server.ssl_certificate = "cert.pem"
    cherrypy.server.ssl_private_key = "privkey.pem"

    cherrypy.engine.start()
    cherrypy.engine.block()

