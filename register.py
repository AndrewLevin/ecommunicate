import MySQLdb
import sys
import datetime
import sys,os
import cherrypy
import hashlib

import smtplib
import email

import mailbox

from email.MIMEMultipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate

import subprocess

import time

from HTMLParser import HTMLParser

import json

import urllib

import httplib

import re

import StringIO

import html_strings

from cherrypy.lib import static

from require import require

class Register(object):
    @cherrypy.expose
    def index(self):
        return """<html>
<head>
<style>
.terminal {
border: none; 
}
li.menubar {
        display: inline;
        padding: 20px;
}
</style>
<title>Ecommunicate</title>
</head>
<body>
<center><h1>Ecommunicate</h1>
<h3>A free online communication service</h3>
"""+html_strings.not_authenticated_menubar_html_string+"""
<h4>Registration</h4>
</center>
      Ecommunicate is a free online communication service in which all communication is viewable by anyone on the open internet instead of being private. E-mail to other ecommunicate.ch e-mail addresses and text messaging (like Google Hangouts or WeChat) are implemented already, and we hope to eventually add audio and video calling (like Skype). You can chat or e-mail yourself (after registering and logging in) or you can view other people's chat conversations or e-mail inboxes. This website is experimental at this point. You should expect bugs, unexpected downtime, etc. Please contact ecommunicate.feedback@gmail.com for comments, feature requests, etc.<br> <br>
      Register here for your free account. Please remember your username and password, as there is no way to recover them at this time.
<br><br>
<center>
   <form id="register" target="console_iframe" method="post" action="register">
   username: <br><br>
   <input type="text" id="username" name="username" size="18" /><br><br>
   password: <br><br>
   <input type="password" id="password" name="password" size="18" /> <br><br>
   name: <br><br>
   <input type="text" id="name" name="name" size="18" /><br><br>
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
    def register(self, username, password,name):

#        $( "iframe" ).clear()
        def register_function():

            if len(username) > 30:
                yield "Username is too long."
                return
                
            for c in username:
                if c != 'a' and c != 'b' and c != 'c' and c != 'd' and c != 'e' and c != 'f' and c != 'g' and c != 'h' and c != 'i' and c != 'j' and c != 'k' and c != 'l' and c != 'm' and c != 'n' and c != 'o' and c != 'p' and c != 'q' and c != 'r' and c != 's' and c != 't' and c != 'u' and c != 'v' and c != 'w' and c != 'x' and c != 'y' and c != 'z' and c != 'A' and c != 'B' and c != 'C' and c != 'D' and c != 'E' and c != 'F' and c != 'G' and c != 'H' and c != 'I' and c != 'J' and c != 'K' and c != 'L' and c != 'M' and c != 'N' and c != 'O' and c != 'P' and c != 'Q' and c != 'R' and c != 'S' and c != 'T' and c != 'U' and c != 'V' and c != 'W' and c != 'X' and c != 'Y' and c != 'Z' and c != '0' and c != '1' and c != '2' and c != '3' and c != '4' and c != '5' and c != '6' and c != '7' and c != '8' and c != '9' and c != '_' and c != '-' and c != '.':
                    yield "The username contains a character that is not allowed."
                    return

            #only allow one person to register at a time
            ret=os.system("if [ -f /home/ec2-user/registering_someone ]; then exit 0; else exit 1; fi");

            if ret == 0:
                yield "Registration was not succesful. Please try again later."
                return

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
                yield "That username is already taken."
                return
            
            if len(password) < 6:
                yield "Please choose a password that is at least 6 characters."
                return
            
            curs.execute("insert into user_info set username = \""+username+"\", hashed_password = \""+h.hexdigest()+"\", name = \""+name+"\", registration_time = now(6)")

            conn.commit()

            os.system("echo \""+username+"@ecommunicate.ch ecommunicate.ch/"+username +"/\" >> /etc/postfix/vmailbox")

            os.system("postmap /etc/postfix/vmailbox")

            os.system("rm /home/ec2-user/registering_someone");

            yield "Your registration was succesful. Please remember your username and password, as there is no way to recover them at this time."

            conn.close()

        return register_function()
