import cherrypy

import html_strings

import utils

class About(object):

    @cherrypy.expose
    def index(self):

        issessionauthenticated = utils.is_session_authenticated()

        html_string = """
<html>
<head>
<title>
Ecommunicate
</title>
<style>
li.menubar {
        display: inline;
        padding: 20px;
}
</style>
</head>
<body>
<center><h1>Ecommunicate</h1>
<h3>A free online communication service</h3>
"""+(html_strings.authenticated_menubar_html_string if utils.is_session_authenticated() else html_strings.not_authenticated_menubar_html_string)+"""
<h4>About This Website</h4>
</center>
"""+html_strings.about_html_string+"""
</body>
</html>
"""
        return html_string
