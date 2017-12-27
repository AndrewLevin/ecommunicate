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

        is_mobile = False

        if "User-Agent" in cherrypy.request.headers and ("Android" in cherrypy.request.headers['User-Agent'] or "iPhone" in cherrypy.request.headers['User-Agent'] or "iPad" in cherrypy.request.headers['User-Agent']):
            is_mobile = True

        if is_mobile:

            html_string = """
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">

"""+html_strings.google_adsense_conversion_tracking_global_site_tag+"""

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

.terminal {
    width: 100%;
    height: 30em;
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

<iframe id="console_iframe2" name="console_iframe2" class="terminal" /></iframe>

</div>

</main>

"""

        else:

            html_string = """<html>
<head><title>Ecommunicate</title>

"""+html_strings.google_adsense_conversion_tracking_global_site_tag+"""

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

"""

        html_string += """

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

</script>"""

        if is_mobile:
            html_string += """

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


"""

        html_string += "</body></html>"

        return html_string

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
