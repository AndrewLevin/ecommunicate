import MySQLdb

import hashlib

import cherrypy

import html_strings

import utils

def is_right_password(username, password):

    secrets_file=open("/home/ec2-user/secrets.txt")

    passwords=secrets_file.read().rstrip('\n')

    db_password = passwords.split('\n')[0]

    dbname = "ecommunicate"

    conn = MySQLdb.connect(host='ecommunicate-production.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='browser', passwd=db_password, port=3306)

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

    conn.close()

    if h.hexdigest() == hashed_password:
        return [True,""]
    else:
        return [False,"Login failed. The password that you entered is not the one associated with the username that you entered."]

class LogInLogOut(object):

    def login_html(self,  message="", from_page="/"):

        from_page = from_page.replace(chr(1),"&&").replace(chr(0),"%22")

        is_mobile = False

        if "Android" in cherrypy.request.headers['User-Agent'] or "iPhone" in cherrypy.request.headers['User-Agent'] or "iPad" in cherrypy.request.headers['User-Agent']:
            is_mobile = True

        if is_mobile:

            login_html_string = """

<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>
Ecommunicate
</title>
</head>
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
<ul style="list-style:none;font-size:20px;padding-left:40px;">
<li style="padding-bottom:20px"><a href="/">Home</a></li>
<li style="padding-bottom:20px"><a href="/view/">View</a></li>
<li style="padding-bottom:20px"><a href="/register/">Register</a></li>
<li style="padding-bottom:20px"><a href="/loginlogout/login/">Login</a></li>
<li><a href="/about">About</a></li>
</ul>
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
<h2>Login</h2>
</center>

"""

            login_html_string += "<center>"
            login_html_string += "<form method=\"post\" action=\"/loginlogout/login\">"
            login_html_string += "<input type=\"hidden\" name=\"from_page\" value=\""+from_page+"\" />"
            login_html_string += "<div style = \"font-size:120%\">username:</div><br>"
            login_html_string += "<input type=\"text\" id=\"username\" name=\"username\" size=\"18\" /><br><br>"
            login_html_string += "<div style = \"font-size:120%\">password:</div> <br>"
            login_html_string += "<input type=\"password\" id=\"password\" name=\"password\" size=\"18\" /> <br><br>"
            login_html_string += "<button type=\"submit\">"
            login_html_string += "Login"
            login_html_string += "</button>"
            if message != "":
                login_html_string += "<br><br>"
                login_html_string += message
            login_html_string += "</center>"

            login_html_string += """


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

</script>

</body>

</html>

"""

        else:

            login_html_string = """
<html>
<head>
<title>
Ecommunicate
</title>
<style>

.nonheader { width:960px; margin: 80px auto 0px auto;  }

"""+html_strings.header_style+"""

</style>
</head>
<body>
"""+(html_strings.authenticated_header if utils.is_session_authenticated() else html_strings.not_authenticated_header)+"""

<div class = "nonheader">

<center>
<h2>Login</h2>
</center>
"""

            login_html_string += "<center>"
            login_html_string += "<form method=\"post\" action=\"/loginlogout/login\">"
            login_html_string += "<input type=\"hidden\" name=\"from_page\" value=\""+from_page+"\" />"
            login_html_string += "username: <br><br>"
            login_html_string += "<input type=\"text\" id=\"username\" name=\"username\" size=\"18\" /><br><br>"
            login_html_string += "password: <br><br>"
            login_html_string += "<input type=\"password\" id=\"password\" name=\"password\" size=\"18\" /> <br><br>"
            login_html_string += "<button type=\"submit\">"
            login_html_string += "Login"
            login_html_string += "</button>"
            if message != "":
                login_html_string += "<br><br>"
                login_html_string += message
            login_html_string += "</center>"
            login_html_string += "</div>"

            login_html_string += "</body>"
            login_html_string += "</html>"

        return login_html_string    
        
        
    @cherrypy.expose
    def login(self, username=None, password=None, from_page="/"):

        from_page = from_page.strip('"')

        if username is None or password is None:
            return self.login_html(from_page=from_page)
        
        [pass_password_check,error_msg] = is_right_password(username, password)
        if not pass_password_check:
            return self.login_html(error_msg, from_page)
        else:

            cherrypy.request.login = username

            cherrypy.session.acquire_lock() 

            cherrypy.session['_cp_username'] = username

            cherrypy.session.release_lock()

            from_page = from_page.strip('"')
            
            raise cherrypy.HTTPRedirect(from_page)
    
    @cherrypy.expose
    def logout(self, from_page="/"):

        cherrypy.session.acquire_lock()

        cherrypy.session['_cp_username'] = None

        cherrypy.session.release_lock()

        cherrypy.request.login = None
        raise cherrypy.HTTPRedirect(from_page)
