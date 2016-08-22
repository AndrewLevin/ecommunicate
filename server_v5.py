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

# create a subclass and override the handler methods
class MyHTMLParser(HTMLParser):
    email = ""
    get_name = False
    name = ""
    def handle_data(self, data):
        if (data.find('@') != -1):
            self.email = data
        if (data.find('CMS Member Info:') != -1):
            self.get_name = True
            return False
        if self.get_name:
            self.name = data
            self.get_name = False
    def result(self):
        return self.email
    def userName(self):
        return self.name

def get_HNews_info(user_name):
    if user_name.lower() == "defilip":    ##when users are registered in HN with
        user_name = "ndefilip"            ##different email than lxplus account
    elif user_name.lower() == "ligabue":
        user_name = "fligabue"
    hyperNews_url = 'https://hypernews.cern.ch/HyperNews/CMS/view-member.pl?'+user_name.lower()
    args = ['curl','--insecure', hyperNews_url, '-s']
    proc = subprocess.Popen(args, stdout = subprocess.PIPE)
    proc_output = proc.communicate()[0]
    parser = MyHTMLParser()
    html_resp = parser.feed(proc_output)
    return parser #return a HTML parser

class Register(object):
    @cherrypy.expose
    def index(self):
        return """<html>
<head><title>open</title>
</head>
<body>

<form id="ping_form" target="console_iframe" method="post" action="register">
  username: <br><br>
  <input type="text" id="username" name="username" size="18" /><br><br>
  password: <br><br>
  <input type="text" id="password" name="password" size="18" /> <br><br>
  <button id="ping" class="fg-button ui-state-default ui-corner-all" type="submit">
  Register
  </button>
  </form>

</body>
        </html>"""
    @cherrypy.expose
    def register(self, username, password):
        secrets_file=open("/home/ec2-user/secrets.txt")

        passwords=secrets_file.read().rstrip('\n')

        db_password = passwords.split('\n')[0]

        dbname = "open"

        h = hashlib.sha256()

        h.update(password)

        conn = MySQLdb.connect(host='tutorial-db-instance.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='open', passwd=db_password, port=3306)

        curs = conn.cursor()

        curs.execute("use "+dbname+";")

        curs.execute("insert into user_info set username = \""+username+"\", hashed_password = \""+h.hexdigest()+"\"")

        conn.commit()

class ShowMessages(object):
    @cherrypy.expose
    def index(self):
        return """<html>
<head><title>open</title>
</head>
<body>

<form id="ping_form" target="console_iframe" method="post" action="show_messages">
  username1: <br><br>
  <input type="text" id="username1" name="username1" size="18" /><br><br>
  username2: <br><br>
  <input type="text" id="username2" name="username2" size="18" /> <br><br>
  <button id="ping" class="fg-button ui-state-default ui-corner-all" type="submit">
  Display Messages
  </button>
  </form>

</body>
        </html>"""

    @cherrypy.expose
    def show_messages(self, username1, username2):
        #dn=cherrypy.request.headers['Cms-Authn-Dn']

        secrets_file=open("/home/ec2-user/secrets.txt")

        passwords=secrets_file.read().rstrip('\n')

        db_password = passwords.split('\n')[0]

        dbname = "open"

        #conn = MySQLdb.connect(host=' tutorial-db-instance.cphov5mfizlt.us-west-2.rds.amazonaws.com:3306', user='open', passwd="openserver")

        return_message=""

        #return_message = str(messages)

        def print_messages():

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
                    yield str(message_dict["username1"] +": " + message_dict["message"]+"<br>");
                elif message_dict["forward"] == 0:
                    yield str(message_dict["username2"] + ": " + message_dict["message"]+"<br>");

            while True:

                time.sleep(1)

                conn = MySQLdb.connect(host='tutorial-db-instance.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='open', passwd=db_password, port=3306)

                curs = conn.cursor()

                curs.execute("use "+dbname+";")

                current_time_old=current_time
                current_time=datetime.datetime.now()

                #curs.execute("select * from messages where username1 = \""+username1+"\" and username2 = \""+username2+"\" order by time;")
                curs.execute("select * from messages where username1 = \""+username1+"\" and username2 = \""+username2+"\" and time > \""+current_time_old.strftime("%y:%m:%d %H:%M:%S.%u")+"\" order by time;")

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

        return print_messages()

    show_messages._cp_config = {'response.stream': True}     


class Chat(object):
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

<form id="show_messages_form" target="console_iframe1" method="post" action="chat">
  your username: <br><br>
  <input type="text" id="username1" name="username1" size="18" /><br><br>
  username of the user that you want to chat with: <br><br>
  <input type="text" id="username2" name="username2" size="18" /> <br><br>
  <button id="chat" class="fg-button ui-state-default ui-corner-all" type="submit">
  Display Messages
  </button>
  </form>

 <form id="add_message_form" target="console_iframe2" method="post" action="add_message">
  <input type="text" id="message" name="message" size="18" />
  <button id="chat" class="fg-button ui-state-default ui-corner-all" type="submit">
  Chat
  </button>
  </form>

  <iframe name="console_iframe1" class="terminal" />  
  <iframe name="console_iframe2" class="terminal" />  


</body>
        </html>"""


    @cherrypy.expose
    def add_message(self, message):


        username1 = cherrypy.session.get("username1")
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

    @cherrypy.expose
    def chat(self, username1, username2):

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

    chat._cp_config = {'response.stream': True}


if __name__ == '__main__':
    cherrypy.config.update({'server.socket_port': 8080})
    cherrypy.config.update({'server.socket_host': 'ec2-52-42-148-78.us-west-2.compute.amazonaws.com'})
    cherrypy.config.update({'tools.sessions.on': True})
    cherrypy.tree.mount(ShowMessages(),'/show_messages')
    cherrypy.tree.mount(Chat(),'/chat')
    cherrypy.tree.mount(Register(),'/register')
    #cherrypy.quickstart(Open())

    cherrypy.server.ssl_module = 'builtin'

    cherrypy.server.ssl_certificate = "cert.pem"
    cherrypy.server.ssl_private_key = "privkey.pem"
    #cherrypy.server.ssl_certificate_chain = "/etc/pki/tls/certs/ca-bundle.crt"

    cherrypy.engine.start()
    cherrypy.engine.block()

