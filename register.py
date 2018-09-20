import MySQLdb
import os
import datetime
import cherrypy
import hashlib

import html_strings

from cherrypy.lib import static

from require import require

import utils

import json

#"""+(html_strings.authenticated_header if utils.is_session_authenticated() else html_strings.not_authenticated_header)+"""

class Register(object):
    @cherrypy.expose
    def index(self):

        is_mobile = False

        if "User-Agent" in cherrypy.request.headers and ("Android" in cherrypy.request.headers['User-Agent'] or "iPhone" in cherrypy.request.headers['User-Agent'] or "iPad" in cherrypy.request.headers['User-Agent']):
            is_mobile = True

        if is_mobile:

            return """<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">

"""+html_strings.google_adsense_conversion_tracking_global_site_tag+html_strings.google_adsense_conversion_tracking_event_snippet+"""

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

.terminal {
   border: none; 
   width: 100%;
}

.header {
float : right

}

.content {
padding-left:1em;
padding-right:1em;

}

input[type="text"] {
font-size: 120%;
border-radius: 5px;
border: 2px solid black;
padding: 2px;
outline: none;}

input[type="password"] {
font-size: 120%;
border-radius: 5px;
border: 2px solid black;
padding: 2px;
outline: none;}

</style>
</head>
<body>

<nav id="drawer" style="background-color:LightGrey">
<center><h2 style="margin-top:0">Ecommunicate</h2></center>
"""+(html_strings.authenticated_mobile_navigation_menu if utils.is_session_authenticated() else html_strings.not_authenticated_mobile_navigation_menu)+"""
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
<h2>Registration</h2>
</center>
      Ecommunicate is a free online communication service in which <b>all communication is viewable by anyone on the open internet</b> instead of being private. E-mail to other ecommunicate.ch e-mail addresses and text messaging (like Google Hangouts or WeChat) are implemented already, and we hope to eventually add audio and video calling (like Skype). You can chat or e-mail yourself (after registering and logging in) or you can view other people's chat conversations or e-mail inboxes. This website is experimental at this point. You should expect bugs, unexpected downtime, etc. Please contact ecommunicate.feedback@gmail.com for comments, feature requests, etc.<br> <br>
      Register here for your free account. Please remember your username and password, as there is no way to recover them at this time.
<br><br>
<center>
   <form id="register_form" target="console_iframe" method="post" action="register">
   <div style = "font-size:120%">username: *</div><br>
   <input type="text" id="username" name="username" size="18" /><br><br>
   <div style = "font-size:120%">password: *</div> <br>
   <input type="password" id="password" name="password" size="18" /> <br><br>
   <div style = "font-size:120%">name:</div> <br>
   <input type="text" id="name" name="name" size="18" /><br><br>

<b>By clicking the "Register" button, you agree that you have read and understand the above description of what Ecommunicate is.</b> 

<br> <br>

  <button id="register" type="submit" style="font-size: 16px;">
  Register
  </button>
  </form>
  <iframe name="console_iframe" id ="console_iframe" class="terminal" /></iframe>
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


$('#register_form').submit(function(event) {

   event.preventDefault();
   var $this = $(this);
   $.ajax({
      url: $this.attr('action'),
      type: 'POST',
      data: $this.serialize(),
      success: function(data){

        json_object = JSON.parse(data)

        if (json_object["success"]) {

            var console_iframe = document.getElementById('console_iframe');

            console_iframe.contentWindow.document.open();
            console_iframe.contentWindow.document.close();

            $('#register_form').hide();

            console_iframe.contentWindow.document.write('<head><base target="_parent"></head><center style="color:blue;font-size:20px;font-weight:bold">Registration was successful.<br>You can now <a href="/loginlogout/login/">login</a>.</center>');

            gtag_report_conversion();

        }

        else {

            var console_iframe = document.getElementById('console_iframe');

            console_iframe.contentWindow.document.open();
            console_iframe.contentWindow.document.close();

            console_iframe.contentWindow.document.write('<center style="color:red;font-size:20px;font-weight:bold;white-space:pre-wrap">'+json_object["errors"]+'</center>');

        }


      },
      error : function (data) {

        alert(data);

        var console_iframe = document.getElementById('console_iframe');
        console_iframe.write("Error.");
      }
   });
});

</script>        
  
  </center>
</body>
        </html>"""

        else:

            return """<html>
<head>
<title>
Ecommunicate
</title>

"""+html_strings.google_adsense_conversion_tracking_global_site_tag+html_strings.google_adsense_conversion_tracking_event_snippet+"""

<style>

.nonheader { width:960px; margin: 80px auto 0px auto;  } 

.terminal {
border: none; 
width: 100%;
}
"""+html_strings.header_style+"""
</style>
</head>
<body>
"""+(html_strings.authenticated_header if utils.is_session_authenticated() else html_strings.not_authenticated_header)+"""
<div class="nonheader">
<center>
<h2>Registration</h2>
</center>
      Ecommunicate is a free online communication service in which <b>all communication is viewable by anyone on the open internet</b> instead of being private. E-mail to other ecommunicate.ch e-mail addresses and text messaging (like Google Hangouts or WeChat) are implemented already, and we hope to eventually add audio and video calling (like Skype). You can chat or e-mail yourself (after registering and logging in) or you can view other people's chat conversations or e-mail inboxes. This website is experimental at this point. You should expect bugs, unexpected downtime, etc. Please contact ecommunicate.feedback@gmail.com for comments, feature requests, etc.<br> <br>
      Register here for your free account. Please remember your username and password, as there is no way to recover them at this time.
<br><br>
<center>
   <form id="register_form" target="console_iframe" method="post" action="register">
   username: * <br><br>
   <input type="text" id="username" name="username" size="18" /><br><br>
   password: * <br><br>
   <input type="password" id="password" name="password" size="18" /> <br><br>
   name: <br><br>
   <input type="text" id="name" name="name" size="18" /><br><br>

<b>By clicking the "Register" button, you agree that you have read and understand the above description of what Ecommunicate is.</b> 

<br> <br>

  <button id="register" type="submit">
  Register
  </button>
  </form>
  <iframe name="console_iframe" id ="console_iframe" class="terminal" /></iframe>
</center>

<script type="text/javascript" src="https://code.jquery.com/jquery-3.1.0.js"></script>
  <script type="text/javascript">
$('#register_form').submit(function(event) {
   event.preventDefault();
   var $this = $(this);
   $.ajax({
      url: $this.attr('action'),
      type: 'POST',
      data: $this.serialize(),
      success: function(data){
        json_object = JSON.parse(data)
        if (json_object["success"]) {
            var console_iframe = document.getElementById('console_iframe');
            console_iframe.contentWindow.document.open();
            console_iframe.contentWindow.document.close();
            $('#register_form').hide();
            console_iframe.contentWindow.document.write('<head><base target="_parent"></head><center style="color:blue;font-size:20px;font-weight:bold">Registration was successful.<br>You can now <a href="/loginlogout/login/">login</a>.</center>');
            gtag_report_conversion();

        }
        else {
            var console_iframe = document.getElementById('console_iframe');
            console_iframe.contentWindow.document.open();
            console_iframe.contentWindow.document.close();

            console_iframe.contentWindow.document.write('<center style="color:red;font-size:20px;font-weight:bold;white-space:pre-wrap">'+json_object["errors"]+'</center>');
        }
      },
      error : function (data) {
        var console_iframe = document.getElementById('console_iframe');
        console_iframe.write("Error.");
      }
   });
});
</script>        
  <br>
  <br>
  </center>
</div>
</body>
</html>"""



    @cherrypy.expose
    def register(self, username, password,name):

        print "len(username): "+str(len(username))
        print "username.encode('utf-8'): "+username.encode('utf-8')
        print "username: "+username
        print "len(password): "+str(len(password))
        print "name.encode('utf-8'): "+name.encode('utf-8')
        print "name: "+name

#        $( "iframe" ).clear()
        def register_function():

            json_object = {}

            json_object["success"] = True

            json_object["errors"] = []

            if len(username) > 30:
                json_object["success"] = False
                json_object["errors"].append("username too long")
                print json.dumps(json_object)
                return json.dumps(json_object)
            
            if len(username) == 0:
                json_object["success"] = False
                json_object["errors"].append("Username is empty.")
                print json.dumps(json_object)
                return json.dumps(json_object)

            if len(username.strip(" ")) == 0:
                json_object["success"] = False
                json_object["errors"].append("Empty spaces are not allowed in the username. The username that you entered is \""+username+"\".")
                print json.dumps(json_object)
                return json.dumps(json_object)

            if username[0] == " ":
                json_object["success"] = False
                json_object["errors"].append("Empty spaces are not allowed in the username. The username that you entered is \""+username+"\". There are one or more empty spaces at the beginning.")
                print json.dumps(json_object)
                return json.dumps(json_object)
    
            for c in username.rstrip(" "):
                if c != 'a' and c != 'b' and c != 'c' and c != 'd' and c != 'e' and c != 'f' and c != 'g' and c != 'h' and c != 'i' and c != 'j' and c != 'k' and c != 'l' and c != 'm' and c != 'n' and c != 'o' and c != 'p' and c != 'q' and c != 'r' and c != 's' and c != 't' and c != 'u' and c != 'v' and c != 'w' and c != 'x' and c != 'y' and c != 'z' and c != 'A' and c != 'B' and c != 'C' and c != 'D' and c != 'E' and c != 'F' and c != 'G' and c != 'H' and c != 'I' and c != 'J' and c != 'K' and c != 'L' and c != 'M' and c != 'N' and c != 'O' and c != 'P' and c != 'Q' and c != 'R' and c != 'S' and c != 'T' and c != 'U' and c != 'V' and c != 'W' and c != 'X' and c != 'Y' and c != 'Z' and c != '0' and c != '1' and c != '2' and c != '3' and c != '4' and c != '5' and c != '6' and c != '7' and c != '8' and c != '9' and c != '_' and c != '-' and c != '.':
                    json_object["success"] = False

                    if c == " ":
                        json_object["errors"].append("Empty spaces are not allowed in the username.")
                    elif c != '"' and c != "'":
                        print "ord(c): "+str(ord(c))
                        json_object["errors"].append('"' + c + '"' +" not allowed in username.")
                    else:
                        json_object["errors"].append(c +" not allowed in username.")
                        
                    print json.dumps(json_object)
                    return json.dumps(json_object)

            if len(username) != len(username.rstrip(" ")):
                json_object["success"] = False
                json_object["errors"].append("Empty spaces are not allowed in the username. The username that you entered is \""+username+"\". There are one or more empty spaces at the end.")
                print json.dumps(json_object)
                return json.dumps(json_object)

            for c in password.rstrip(" "):
                if c != 'a' and c != 'b' and c != 'c' and c != 'd' and c != 'e' and c != 'f' and c != 'g' and c != 'h' and c != 'i' and c != 'j' and c != 'k' and c != 'l' and c != 'm' and c != 'n' and c != 'o' and c != 'p' and c != 'q' and c != 'r' and c != 's' and c != 't' and c != 'u' and c != 'v' and c != 'w' and c != 'x' and c != 'y' and c != 'z' and c != 'A' and c != 'B' and c != 'C' and c != 'D' and c != 'E' and c != 'F' and c != 'G' and c != 'H' and c != 'I' and c != 'J' and c != 'K' and c != 'L' and c != 'M' and c != 'N' and c != 'O' and c != 'P' and c != 'Q' and c != 'R' and c != 'S' and c != 'T' and c != 'U' and c != 'V' and c != 'W' and c != 'X' and c != 'Y' and c != 'Z' and c != '0' and c != '1' and c != '2' and c != '3' and c != '4' and c != '5' and c != '6' and c != '7' and c != '8' and c != '9' and c != '_' and c != '-' and c != '.' and c != '~' and c != '`' and c != '!' and c != '@' and c != '#' and c != '$' and c != '%' and c != '^' and c != '&' and c != '*' and c != '(' and c != ')' and c != '+' and c != '=' and c != ' ' and c != '{' and c != '}' and c != '[' and c != ']' and c != ':' and c != ';' and c != '?' and c != '/' and c != ',' and c != '<' and c != '>' and c != '?' and c != '/' and c != "'" and c != '"' and c != '|':
                    json_object["success"] = False
                    print "ord(c): "+str(ord(c))
                    json_object["errors"].append("One of the characters in the password that you entered is not allowed.")
                    print json.dumps(json_object)
                    return json.dumps(json_object)


            secrets_file=open("/home/ec2-user/secrets.txt")

            passwords=secrets_file.read().rstrip('\n')

            db_password = passwords.split('\n')[0]

            dbname = "ecommunicate"

            h = hashlib.sha256()

            h.update(password)

            #only allow one person to register at a time
            ret=os.system("if [ -f /home/ec2-user/registering_someone ]; then exit 0; else exit 1; fi");

            if ret == 0:
                json_object["success"] = False
                print json.dumps(json_object)
                return json.dumps(json_object)

            os.system("touch /home/ec2-user/registering_someone");

            conn = MySQLdb.connect(host='ecommunicate-production.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='browser', passwd=db_password, port=3306)

            curs = conn.cursor()

            curs.execute("use "+dbname+";")

            curs.execute("select * from user_info where username = \""+username+"\"")

            user_infos = curs.fetchall()

            if len(user_infos) > 0:
                json_object["success"] = False
                json_object["errors"].append("This username is already taken.")
                os.system("rm /home/ec2-user/registering_someone");
                print json.dumps(json_object)
                return json.dumps(json_object)
            
            if len(password) < 6:
                json_object["success"] = False
                json_object["errors"].append("Password shorter than 6 characters.")
                os.system("rm /home/ec2-user/registering_someone");
                print json.dumps(json_object)
                return json.dumps(json_object)
            
            curs.execute("insert into user_info set username = \""+username+"\", hashed_password = \""+h.hexdigest()+"\", name = \""+name+"\", registration_time = now(6)")

            conn.commit()

            os.system("echo \""+username+"@ecommunicate.ch ecommunicate.ch/"+username +"/\" >> /etc/postfix/vmailbox")

            os.system("postmap /etc/postfix/vmailbox")

            os.system("rm /home/ec2-user/registering_someone");

            conn.close()

            print json.dumps(json_object)

            return json.dumps(json_object)

        return register_function()
