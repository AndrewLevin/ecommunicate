import MySQLdb

import time

import datetime

import cherrypy

import json

from cherrypy.lib import static

import html_strings

import utils

class ViewChat(object):
    @cherrypy.expose
    def index(self,username1,username2):

        html_string_usernames = "username1="+username1+"\n"
        html_string_usernames += "username2="+username2

        return """<html>
<head><title>Ecommunicate</title>
<style>
ul.menubar {
text-align: center;
}

.nonheader { width:960px; margin: 140px auto 0px auto;  } 
"""+html_strings.header_style+"""
ul {
    list-style:none;
    padding-left:0;
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
"""+(html_strings.authenticated_header if utils.is_session_authenticated() else html_strings.not_authenticated_header)+"""

<div class = "nonheader">

<iframe id="console_iframe2" name="console_iframe2" class="terminal" /></iframe>

</div>

<script type="text/javascript" src="https://code.jquery.com/jquery-3.1.0.js"></script> 
<script>
messages_list = "";
messages_list_old = "";
"""+html_string_usernames+"""
max_time = ""
function update_messages(){
    if (messages_list != "") {
            var console_iframe2 = document.getElementById('console_iframe2');
            //clear the iframe
            console_iframe2.contentWindow.document.open();
            console_iframe2.contentWindow.document.close();
            for ( var i = 0, l = messages_list.length; i < l; i++ ) {
                console_iframe2.contentWindow.document.write(messages_list[i][0]+": "+messages_list[i][1]);
                console_iframe2.contentWindow.document.write("<br>");
            }
            var console_iframe2_contentWindow_document = console_iframe2.contentWindow.document;
            //this will "over-scroll", but it works i.e. it moves to the bottom    
            $(console_iframe2_contentWindow_document).scrollTop($(console_iframe2_contentWindow_document).height());  
       
    }
}
function view_recursive() {
get_messages_url = "get_messages?username1="+username1+"&username2="+username2+"&upon_update=True&client_max_time="+max_time;
   $.ajax({
      url: get_messages_url,
      type: 'GET',
      dataType: 'html',
      success: function(data) {
         parsed_data = JSON.parse(data);
         messages_list = parsed_data[0];
         max_time = parsed_data[1];
         messages_list_old = messages_list;
         update_messages();  
         view_recursive();
      }
   });
}
function view_initial() {
get_messages_url = 'get_messages?username1='+username1+'&username2='+username2;
   $.ajax({
      url: get_messages_url,
      type: 'GET',
      dataType: 'html',
      success: function(data) {
         parsed_data = JSON.parse(data);
         messages_list = parsed_data[0];
         max_time=parsed_data[1]; 
         messages_list_old = messages_list;
         update_messages(); 
         view_recursive();
      }
   });
}
$(document).ready(function() {
   view_initial();
});
</script>
        </html>"""


    @cherrypy.expose
    def get_messages(self,username1,username2,upon_update=False,client_max_time=""):

        sorted_usernames= sorted([username1,username2])

        username1=sorted_usernames[0]

        username2=sorted_usernames[1]

        secrets_file=open("/home/ec2-user/secrets.txt")

        passwords=secrets_file.read().rstrip('\n')

        db_password = passwords.split('\n')[0]

        dbname = "ecommunicate"

        conn = MySQLdb.connect(host='ecommunicate-production.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='browser', passwd=db_password, port=3306)

        if upon_update:

            #the connection will timeout eventually
            for i in range(0,1000):

                conn.commit()
                
                curs = conn.cursor()

                curs.execute("use "+dbname+";")

                curs.execute("select MAX(time) from messages where username1=\""+username1+"\" and username2=\""+username2+"\";")

                server_max_time = curs.fetchall()[0][0]

                if server_max_time != None and server_max_time > datetime.datetime.strptime(client_max_time,"%Y-%m-%d %H:%M:%S.%f"):
                    break

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
                    return_string+=str(message_dict["username1"] +": " + message_dict["message"]+"<br>");
                    messages_list.append([message_dict["username1"], message_dict["message"]])
                elif message_dict["forward"] == 0:
                    return_string+=str(message_dict["username2"] + ": " + message_dict["message"]+"<br>");
                    messages_list.append([message_dict["username2"], message_dict["message"]])

        #return str(messages_json)

        curs.execute("select MAX(time) from messages where username1 = \""+username1+"\" and username2 = \""+username2+"\";")

        max_time = str(curs.fetchall()[0][0])

        curs.close()

        conn.close()

        return json.dumps([messages_list,max_time])
