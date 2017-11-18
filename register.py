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

class Register(object):
    @cherrypy.expose
    def index(self):
        return """<html>
<head>
<style>

.nonheader { width:960px; margin: 80px auto 0px auto;  } 

.terminal {
border: none; 
width: 400px;
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
   username: <br><br>
   <input type="text" id="username" name="username" size="18" /><br><br>
   password: <br><br>
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

            console_iframe.contentWindow.document.write('<center style="color:blue;font-size:20px;font-weight:bold">Registration was successful.</center>');

        }

        else {

            var console_iframe = document.getElementById('console_iframe');


            console_iframe.contentWindow.document.write('<center style="color:red;font-size:20px;font-weight:bold">'+json_object["errors"]+'</center>');

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
  
  <br>
  <br>
  </center>
</div>
</body>
        </html>"""
    @cherrypy.expose
    def register(self, username, password,name):

#        $( "iframe" ).clear()
        def register_function():

            json_object = {}

            json_object["success"] = True

            json_object["errors"] = []

            if len(username) > 30:
                json_object["success"] = False
                json_object["errors"].append("username too long")
                return json.dumps(json_object)
                
            for c in username:
                if c != 'a' and c != 'b' and c != 'c' and c != 'd' and c != 'e' and c != 'f' and c != 'g' and c != 'h' and c != 'i' and c != 'j' and c != 'k' and c != 'l' and c != 'm' and c != 'n' and c != 'o' and c != 'p' and c != 'q' and c != 'r' and c != 's' and c != 't' and c != 'u' and c != 'v' and c != 'w' and c != 'x' and c != 'y' and c != 'z' and c != 'A' and c != 'B' and c != 'C' and c != 'D' and c != 'E' and c != 'F' and c != 'G' and c != 'H' and c != 'I' and c != 'J' and c != 'K' and c != 'L' and c != 'M' and c != 'N' and c != 'O' and c != 'P' and c != 'Q' and c != 'R' and c != 'S' and c != 'T' and c != 'U' and c != 'V' and c != 'W' and c != 'X' and c != 'Y' and c != 'Z' and c != '0' and c != '1' and c != '2' and c != '3' and c != '4' and c != '5' and c != '6' and c != '7' and c != '8' and c != '9' and c != '_' and c != '-' and c != '.':
                    json_object["success"] = False
                    json_object["errors"].append("Username contains a character that is not allowed.")
                    return json.dumps(json_object)

            #only allow one person to register at a time
            ret=os.system("if [ -f /home/ec2-user/registering_someone ]; then exit 0; else exit 1; fi");

            if ret == 0:
                json_object["success"] = False
                return json.dumps(json_object)

            os.system("touch /home/ec2-user/registering_someone");

            secrets_file=open("/home/ec2-user/secrets.txt")

            passwords=secrets_file.read().rstrip('\n')

            db_password = passwords.split('\n')[0]

            dbname = "ecommunicate"

            h = hashlib.sha256()

            h.update(password)

            conn = MySQLdb.connect(host='ecommunicate-production.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='browser', passwd=db_password, port=3306)

            curs = conn.cursor()

            curs.execute("use "+dbname+";")

            curs.execute("select * from user_info where username = \""+username+"\"")

            user_infos = curs.fetchall()

            if len(user_infos) > 0:
                json_object["success"] = False
                json_object["errors"].append("This username already taken.")
                os.system("rm /home/ec2-user/registering_someone");
                return json.dumps(json_object)
            
            if len(username) == 0:
                json_object["success"] = False
                json_object["errors"].append("Username is empty.")
                os.system("rm /home/ec2-user/registering_someone");
                return json.dumps(json_object)

            if len(password) < 6:
                json_object["success"] = False
                json_object["errors"].append("Password shorter than 6 characters.")
                os.system("rm /home/ec2-user/registering_someone");
                return json.dumps(json_object)
            
            curs.execute("insert into user_info set username = \""+username+"\", hashed_password = \""+h.hexdigest()+"\", name = \""+name+"\", registration_time = now(6)")

            conn.commit()

            os.system("echo \""+username+"@ecommunicate.ch ecommunicate.ch/"+username +"/\" >> /etc/postfix/vmailbox")

            os.system("postmap /etc/postfix/vmailbox")

            os.system("rm /home/ec2-user/registering_someone");

            conn.close()

            return json.dumps(json_object)

        return register_function()
