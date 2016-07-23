import MySQLdb
import sys
import datetime
import sys,os
import cherrypy

import smtplib
import email

from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate

import subprocess

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

class Open(object):
    @cherrypy.expose
    def index(self):
        return """<html>
<head><title>open</title>
</head>
<body>

<form action="show_messages" method="get">

All of your e-mails and chat messages will be viewable immediately on the open internet.
<br>
<br>

Enter username1 here:
<br>
<input type="text" name="username1" size=100 />

<br>
<br>

Enter username2 here:
<br>
<input type="text" name="username2" size=100 />


<br>
<br>
<br>

<input type="submit" value="Submit"/>

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

        conn = MySQLdb.connect(host='tutorial-db-instance.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='open', passwd=db_password, port=3306)
        #conn = MySQLdb.connect(host=' tutorial-db-instance.cphov5mfizlt.us-west-2.rds.amazonaws.com:3306', user='open', passwd="openserver")

        curs = conn.cursor()

        curs.execute("use "+dbname+";")

        curs.execute("select * from messages order by time")

        colnames = [desc[0] for desc in curs.description]

        messages=curs.fetchall()

        return_message=""

        for message in messages:
            message_dict=dict(zip(colnames, message))
            
            if username1 != message_dict["username1"] or username2 != message_dict["username2"]:
                continue


            if message_dict["forward"] == 1:
                return_message=return_message+message_dict["username1"] +": " + message_dict["message"]+"<br>";
            elif message_dict["forward"] == 0:
                return_message=return_message+message_dict["username2"] + ": " + message_dict["message"]+"<br>";

        #return_message = str(messages)

        return return_message

if __name__ == '__main__':
    cherrypy.config.update({'server.socket_port': 8080})
    cherrypy.config.update({'server.socket_host': 'ec2-52-42-148-78.us-west-2.compute.amazonaws.com'})
    cherrypy.quickstart(Open())
