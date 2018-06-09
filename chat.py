import MySQLdb
import datetime
import cherrypy
import time

import json

import httplib

from makecontactrequest import MakeContactRequest
from contactrequestresponses import ContactRequestResponses

import html_strings

from require import require

import utils

class Chat(object):

    makecontactrequests=MakeContactRequest()

    respondtocontactrequests=ContactRequestResponses()

    @cherrypy.expose
    @require()
    def index(self):

        is_mobile = False

        if "Android" in cherrypy.request.headers['User-Agent'] or "iPhone" in cherrypy.request.headers['User-Agent'] or "iPad" in cherrypy.request.headers['User-Agent']:
            is_mobile = True

        secrets_file=open("/home/ec2-user/secrets.txt")

        passwords=secrets_file.read().rstrip('\n')

        db_password = passwords.split('\n')[0]

        dbname = "ecommunicate"

        conn = MySQLdb.connect(host='ecommunicate-production.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='browser', passwd=db_password, port=3306)

        curs = conn.cursor()

        curs.execute("use "+dbname+";")

        curs.execute("select * from contacts where username1 = \""+cherrypy.session.get('_cp_username')+"\"")

        contacts = curs.fetchall()

        curs.execute("select * from contacts where username2 = \""+cherrypy.session.get('_cp_username')+"\"")

        contacts += curs.fetchall()

        contacts_string = "<td><ul class=\"contactlistclass\" id=\"contactslist\">\n"

        contacts_string += "<li id=\""+cherrypy.session.get('_cp_username')+"\" name=\""+cherrypy.session.get('_cp_username')+"\" class=\"contact\">"+cherrypy.session.get('_cp_username')+"</li>\n"

        iframes_string = "";

        iframes_string += "<iframe id=\"console_"+cherrypy.session.get('_cp_username')+"\" name=\"console_"+cherrypy.session.get('_cp_username')+"\" class=\"terminal\" src = \"about:blank\"/>  </iframe>\n"

        iframes_hide_string = "";

#this syntax does not work when the username has aperiod in it
#        iframes_hide_string += "$(\'#console_" + cherrypy.session.get('_cp_username') + "\').hide();\n"
        iframes_hide_string += "$(\"[id='console_" + cherrypy.session.get('_cp_username') + "']\").hide();\n"

#        iframes_touch_string = "var console_" + cherrypy.session.get('_cp_username') + " = document.getElementById('console_" + cherrypy.session.get('_cp_username') + "');\n"
        
        iframes_touch_string = "document.getElementById('console_" + cherrypy.session.get('_cp_username') + "').addEventListener('touchstart', function(e) { drawer.classList.remove('open'); });\n"

        for contact in contacts:

            colnames = [desc[0] for desc in curs.description]

            contact_dict=dict(zip(colnames, contact))

            if contact_dict["username2"] == cherrypy.session.get('_cp_username'):
                username = contact_dict["username1"]
            else:
                assert(contact_dict["username1"] == cherrypy.session.get('_cp_username'))
                username = contact_dict["username2"]

            contacts_string += "<li id=\""+username+"\" name=\""+username+"\" class=\"contact\">"+username+"</li>\n" 

            iframes_string += "<iframe id=\"console_"+username+"\" name=\"console_"+username+"\" class=\"terminal\" />  </iframe>\n"

            #this syntax does not work when the username has a period in it
            #iframes_hide_string += "$(\'#console_" + username + "\').hide();\n"
            iframes_hide_string += "$(\"[id='console_" + username + "']\").hide();\n"




        contacts_string += "</ul></td>\n</td>"

#this syntax does not work when the username has a period in it
#        click_on_self_string = "$(\'#"+cherrypy.session.get('_cp_username')+"\').click();"
        click_on_self_string = "$(\"[id='"+cherrypy.session.get('_cp_username')+"']\").click();"

        conn.close()

        if is_mobile:

            html_string = """

<head>

"""+html_strings.google_adsense_conversion_tracking_global_site_tag+"""

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

ul.contactlistclass {
    list-style:none;
    padding-left:0;
    width:100%;
}
    .contact {
        color : black;
        background-color: green;
        height: 50px;
        font-size: 24px;
        width: 98.5%;
        padding-top: 20px;
        margin-top: 2px;
        font-family: Verdana;
        font-weight: bold;
        cursor: default;
        border-top: 2px solid black;
        border-bottom: 2px solid black;
        white-space:nowrap;
        overflow:hidden;
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

<table border = "0" style="float:left;padding:0;border-spacing:0;font-family:verdana;" width = "100%">
<tr> <td style="padding:0;background-color:green">
<table border="2"  id="makecontactrequeststable" width = "100%"><tr> <td width="100%" style="font-weight:bold"><center>Make Contact Requests</center></td></tr>
</table>
</td>
</tr>
<tr>
</tr>
<td>
</td>
<tr>
<td style="padding:0;background-color:green">
<table border="2" id = "respondtocontactrequeststable" width="100%">  <tr> <td width="100%" style="font-weight:bold"><center>Respond to Contact Requests</center></td></tr>
</table>
</td>
</tr>
</table>

  <table border=2 width = "100%">
  <tr>
  <td width = "100%">
"""+ iframes_string + """
<form id="add_message_form" name = "add_messages_form" target="console_iframe1" method="POST" action="add_message" width = "100%">
 <input type="text" id="add_message_text" name="add_message_text" style="width:100%;border:2px solid black;font-size: 120%;outline: none;" /> <br> <br>
 <input type="hidden" id="username2" name="username2"/>
 </form>
 <iframe id="console_iframe1" name="console_iframe1" class="messageerrorbox" />  </iframe>
</td>
  </tr>
  </table>

  <table border=2 width = "100%">
  <tr>
""" + contacts_string + """ 
  </tr>
</table>

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

messages_json = "";
messages_json_old = "";
username2  = "";
max_time = ""
function show_messages(e){
   var target = e.target;
   if( target.id != "contactslist"){
    var console_iframe2 = document.getElementById('console_'+e.target.id);
    if (username2 != ""){
// this syntax does not work when username2 has a period in it    
//        $('#console_'+username2).hide();
        $("[id='console_"+username2+"']").hide();
    }
//    console_iframe2.slideDown('slow');
 
    username2=e.target.id;
// this syntax does not work when username2 has a period in it    
   // $('#console_'+username2).show();
    $("[id='console_"+username2+"']").show();

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


            //writing to the document clears all of the event listeners that were already attached to it, so you need to reattach them
//this syntax does not work when item has a period in it
//            $('#console_'+item).contents().on('touchstart', function(event) { 
            $("[id='console_"+item+"']").contents().on('touchstart', function(event) { 
                event.preventDefault();
                drawer.classList.remove('open');
                } 
            );



        }
    }
}
function chat_initial() {
   $.ajax({
      url: 'get_messages',
      type: 'GET',
      dataType: 'html',
      success: function(data) {
         parsed_data = JSON.parse(data);
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
                 if (item in messages_json_old){
                    if ( messages_json[item].length > messages_json_old[item].length ) {
                        for ( var i = messages_json_old[item].length, l = messages_json[item].length; i < l; i++ ) { 
                            if (messages_json[item][i][0] == item && item != username2){
//this syntax does not work when item has a period in it
//                                $('#'+item).css('background-color','blue');
                                $("[id='"+item+"']").css('background-color','blue');
                            }
                        }  
                     }
                 } else {
                    for ( var i = 0, l = messages_json[item].length; i < l; i++ ) { 
                        if (messages_json[item][i][0] == item && item != username2){
//this syntax does not work when item has a period in it
//                                $('#'+item).css('background-color','blue');
                                $("[id='"+item+"']").css('background-color','blue');
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
var makecontactrequeststable = document.getElementById('makecontactrequeststable');

makecontactrequeststable.addEventListener('mouseover',function(e) { $('#makecontactrequeststable').css('background-color','orange');  } ,  false);

makecontactrequeststable.addEventListener('mouseout',function(e) { $('#makecontactrequeststable').css('background-color','green');  } ,  false);

makecontactrequeststable.addEventListener('click',function(e) { open('/chat/makecontactrequests/','_self')  } ,  false);

var respondtocontactrequeststable = document.getElementById('respondtocontactrequeststable');

respondtocontactrequeststable.addEventListener('mouseover',function(e) { $('#respondtocontactrequeststable').css('background-color','orange');  } ,  false);

respondtocontactrequeststable.addEventListener('mouseout',function(e) { $('#respondtocontactrequeststable').css('background-color','green');  } ,  false);

respondtocontactrequeststable.addEventListener('click',function(e) { open('/chat/respondtocontactrequests/','_self') } ,  false);

function contact_mouseover(e){
var target = e.target;

if( target.id != "contactslist"){

 //this syntax does not work when the target.id has a period in it
//    $('#'+target.id).css('background-color','orange');
    $("[id='"+target.id+"']").css('background-color','orange');
}

}
function contact_mouseout(e){
var target = e.target;

if( target.id != "contactslist"){
 //this syntax does not work when the target.id has a period in it
//    $('#'+target.id).css('background-color','green');
    $("[id='"+target.id+"']").css('background-color','green');
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

contactslist.addEventListener('touchstart',function(e) { contact_mouseover(e); } ,  false)
contactslist.addEventListener('touchend',function(e) { contact_mouseout(e); } ,  false)
contactslist.addEventListener('touchcancel',function(e) { contact_mouseout(e); } ,  false)


"""+iframes_touch_string+"""

$(document).ready(function() {
"""+iframes_hide_string+"""

var console_iframe_var = document.getElementById('console_test1');

chat_initial();

"""+click_on_self_string+"""
});

</script>  

</body></html>

"""

        else:

            html_string = """<html>

"""+html_strings.google_adsense_conversion_tracking_global_site_tag+"""

<head><title>Ecommunicate</title>
<style>

.nonheader { width:960px; margin: 80px auto 0px auto;  }

"""+html_strings.header_style+"""
ul.contactlistclass {
    list-style:none;
    padding-left:0;
    width:125px;
}
    .contact {
        color : black;
        background-color: green;
        height: 50px;
        font-size: 24px;
        width: 98.5%;
        padding-top: 20px;
        margin-top: 2px;
        font-family: Verdana;
        font-weight: bold;
        cursor: default;
        border-top: 2px solid black;
        border-bottom: 2px solid black;
        white-space:nowrap;
        overflow:hidden;
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
<center>
<h2>Chat</h2>
</center>

<table border = "0" style="float:left;padding:0;border-spacing:0;font-family:verdana;" width = "15%">
<tr> <td style="padding:0;background-color:green">
<table border="2"  id="makecontactrequeststable"><tr> <td width="15%" style="font-weight:bold">Make Contact Requests</td></tr>
</table>
</td>
</tr>
<tr>
</tr>
<td>
</td>
<tr>
<td style="padding:0;background-color:green">
<table border="2" id = "respondtocontactrequeststable">  <tr> <td width="15%" style="font-weight:bold"> Respond to Contact Requests</td></tr>
</table>
</td>
</tr>
</table>


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

</div>

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

//  this syntax does not work when username2 has a period in it
//        $('#console_'+username2).hide();
    $("[id='console_"+username2+"']").hide();    

    }
//    console_iframe2.slideDown('slow');
 
    username2=e.target.id;
//  this syntax does not work when username2 has a period in it
//    $('#console_'+username2).show();
    $("[id='console_"+username2+"']").show();

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
function chat_initial() {
   $.ajax({
      url: 'get_messages',
      type: 'GET',
      dataType: 'html',
      success: function(data) {
         parsed_data = JSON.parse(data);
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
                 if (item in messages_json_old){
                    if ( messages_json[item].length > messages_json_old[item].length ) {
                        for ( var i = messages_json_old[item].length, l = messages_json[item].length; i < l; i++ ) { 
                            if (messages_json[item][i][0] == item && item != username2){
// this syntax does not work when the item has a period in it
//                                $('#'+item).css('background-color','blue');
                                $("[id='"+item+"']").css('background-color','blue');
                            }
                        }  
                     }
                 } else {
                    for ( var i = 0, l = messages_json[item].length; i < l; i++ ) { 
                        if (messages_json[item][i][0] == item && item != username2){
// this syntax does not work when the item has a period in it
//                                $('#'+item).css('background-color','blue');
                                $("[id='"+item+"']").css('background-color','blue');
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
var makecontactrequeststable = document.getElementById('makecontactrequeststable');

makecontactrequeststable.addEventListener('mouseover',function(e) { $('#makecontactrequeststable').css('background-color','orange');  } ,  false);

makecontactrequeststable.addEventListener('mouseout',function(e) { $('#makecontactrequeststable').css('background-color','green');  } ,  false);

makecontactrequeststable.addEventListener('click',function(e) { open('/chat/makecontactrequests/','_self')  } ,  false);

var respondtocontactrequeststable = document.getElementById('respondtocontactrequeststable');

respondtocontactrequeststable.addEventListener('mouseover',function(e) { $('#respondtocontactrequeststable').css('background-color','orange');  } ,  false);

respondtocontactrequeststable.addEventListener('mouseout',function(e) { $('#respondtocontactrequeststable').css('background-color','green');  } ,  false);

respondtocontactrequeststable.addEventListener('click',function(e) { open('/chat/respondtocontactrequests/','_self') } ,  false);

function contact_mouseover(e){
var target = e.target;
if( target.id != "contactslist"){
 //this syntax does not work when the target.id has a period in it
//    $('#'+target.id).css('background-color','orange');
    $("[id='"+target.id+"']").css('background-color','orange');
}

}
function contact_mouseout(e){
var target = e.target;


if( target.id != "contactslist"){
 //this syntax does not work when the target.id has a period in it
//    $('#'+target.id).css('background-color','green');
    $("[id='"+target.id+"']").css('background-color','green');
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
$(document).ready(function() {
"""+iframes_hide_string+"""
   chat_initial();
"""+click_on_self_string+"""
});
</script>
        </html>"""

        return html_string

    @cherrypy.expose
    @require()
    def get_messages(self,upon_update=False,client_max_time=None):

        if client_max_time == "null":
            client_max_time = None

        #dn=cherrypy.request.headers['Cms-Authn-Dn']

        #client_max_time="2017-06-30 08:01:06.562369";

        username1=cherrypy.session.get('_cp_username')

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

                curs.execute("select MAX(time) from messages where username1=\""+username1+"\";")

                #tmp = curs.fetchall()

                server_max_time = curs.fetchall()[0][0]

                if server_max_time != None and client_max_time == None:
                    break

                if server_max_time != None and server_max_time > datetime.datetime.strptime(client_max_time,"%Y-%m-%d %H:%M:%S.%f"):
                    break

                curs.execute("select MAX(time) from messages where username2=\""+username1+"\";")

                server_max_time = curs.fetchall()[0][0]

                if server_max_time != None and client_max_time == None:
                    break

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

            if len(messages) > 0:

                messages_json[username] = []

                for message in messages:

                    message_dict=dict(zip(colnames, message))

                    if message_dict["forward"] == 1:
                        messages_json[username].append([message_dict["username1"], message_dict["message"]])
                    elif message_dict["forward"] == 0:
                        messages_json[username].append([message_dict["username2"], message_dict["message"]])

        curs.execute("select * from messages where username1 = \""+cherrypy.session.get('_cp_username')+"\" and username2 = \""+cherrypy.session.get('_cp_username')+"\" order by time;")

        colnames = [desc[0] for desc in curs.description]

        messages=curs.fetchall()

        if len(messages) > 0:
            messages_json[cherrypy.session.get('_cp_username')] = []
            for message in messages:
                message_dict=dict(zip(colnames, message))
                messages_json[cherrypy.session.get('_cp_username')].append([cherrypy.session.get('_cp_username'), message_dict["message"]])

        #return str(messages_json)

        curs.execute("select MAX(time) from messages where username1=\""+cherrypy.session.get('_cp_username')+"\";")

        max_time1 = curs.fetchall()[0][0]

        curs.execute("select MAX(time) from messages where username2=\""+cherrypy.session.get('_cp_username')+"\";")

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

        conn.close()

        return json.dumps([messages_json,max_time])

        #return '{"a1" : "b1"}'



    @cherrypy.expose
    @require()
    def add_message(self, add_message_text,username2):

        username1=cherrypy.session.get('_cp_username')

        if len(add_message_text) > 5000:
            return

        if add_message_text == "":
            return

        for c in add_message_text:
            if c != 'a' and c != 'b' and c != 'c' and c != 'd' and c != 'e' and c != 'f' and c != 'g' and c != 'h' and c != 'i' and c != 'j' and c != 'k' and c != 'l' and c != 'm' and c != 'n' and c != 'o' and c != 'p' and c != 'q' and c != 'r' and c != 's' and c != 't' and c != 'u' and c != 'v' and c != 'w' and c != 'x' and c != 'y' and c != 'z' and c != 'A' and c != 'B' and c != 'C' and c != 'D' and c != 'E' and c != 'F' and c != 'G' and c != 'H' and c != 'I' and c != 'J' and c != 'K' and c != 'L' and c != 'M' and c != 'N' and c != 'O' and c != 'P' and c != 'Q' and c != 'R' and c != 'S' and c != 'T' and c != 'U' and c != 'V' and c != 'W' and c != 'X' and c != 'Y' and c != 'Z' and c != '0' and c != '1' and c != '2' and c != '3' and c != '4' and c != '5' and c != '6' and c != '7' and c != '8' and c != '9' and c != '_' and c != '-' and c != '.' and c != '~' and c != '`' and c != '!' and c != '@' and c != '#' and c != '$' and c != '%' and c != '^' and c != '&' and c != '*' and c != '(' and c != ')' and c != '+' and c != '=' and c != ' ' and c != '{' and c != '}' and c != '[' and c != ']' and c != ':' and c != ';' and c != '?' and c != '/' and c != ',' and c != '<' and c != '>' and c != '?' and c != '/' and c != "'" and c != '"' and c != '|':
                print "not allowed character:"
                print ord(c)
                return
        
        sorted_usernames= sorted([username1,username2])

        if sorted_usernames == [username1,username2] and username1 != username2:
            forward = "1"
        else:
            forward = "0"

        username1=sorted_usernames[0]

        username2=sorted_usernames[1]

        secrets_file=open("/home/ec2-user/secrets.txt")

        passwords=secrets_file.read().rstrip('\n')

        db_password = passwords.split('\n')[0]

        dbname = "ecommunicate"

        conn = MySQLdb.connect(host='ecommunicate-production.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='browser', passwd=db_password, port=3306)

        curs = conn.cursor()

        curs.execute("use "+dbname+";")

        curs.execute("insert into messages set username1 = \""+username1+"\", username2 = \""+username2+"\", forward="+forward+", time=now(6), message = \""+add_message_text.replace('"','\\\"').replace("'","\\\'")+"\";")

        if forward == "1":
            curs.execute("update contacts set new_message_username2 = 1 where username1 = \""+username1+"\" and username2 = \""+username2+"\";")
        else: 
            curs.execute("update contacts set new_message_username1 = 1 where username1 = \""+username1+"\" and username2 = \""+username2+"\";")

        conn.commit()

        conn.close()

        params_json = {'username1': username1, 'username2': username2, 'forward' : forward}

        headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}

        http_conn  =  httplib.HTTPSConnection("chat.android.ecommunicate.ch")
        http_conn.request('POST','/new_message_browser/', headers = headers, body = json.dumps(params_json))

        #do not wait for the response, since web browsers limit the number of simultaneous requests, and if there many messages added in quick succession, there will be a backlog
        #r=http_conn.getresponse()
        #print r.status
        #print r.reason


