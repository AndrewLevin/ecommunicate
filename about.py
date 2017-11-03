import cherrypy

import html_strings

import utils

class About(object):

    @cherrypy.expose
    def index(self):

        html_string = """
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
<h2>About This Website</h2>
</center>
"""+html_strings.about_html_string+"""

</div>

</body>
</html>
"""
        return html_string
