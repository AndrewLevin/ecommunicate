header_style = """

h1 { 

margin-top: 0.0em; 

margin-bottom: 0.0em; 

} 

h3 { 

margin-top: 0.0em; 

} 

.header1 {width:380px; float:left;}

.nav {

float: right;
padding: 20px 0px 0px 0px;
text-align: right;

}

header {background-color: White}

header {

position:fixed;
top:0px;
left:0px;
width:100%;
height:60px;
z-index:50;

}

.page{

width:960px; 
margin:0px auto 0px auto;

}


"""

not_authenticated_mobile_navigation_menu = """
<ul style="list-style:none;font-size:20px;padding-left:40px;">
<li style="padding-bottom:20px"><a href="/">Home</a></li>
<li style="padding-bottom:20px"><a href="/view/">View</a></li>
<li style="padding-bottom:20px"><a href="/register/">Register</a></li>
<li style="padding-bottom:20px"><a href="/loginlogout/login/">Login</a></li>
<li><a href="/about">About</a></li>
</ul>
"""

authenticated_mobile_navigation_menu = """
<ul style="list-style:none;font-size:20px;padding-left:40px;">
<li style="padding-bottom:20px"><a href="/">Home</a></li>
<li style="padding-bottom:20px"><a href="/view/">View</a></li>
<li style="padding-bottom:20px"><a href="/chat/">Chat</a></li>
<li style="padding-bottom:20px"><a href="/email/">Email</a></li>
<li style="padding-bottom:20px"><a href="/loginlogout/logout/">Logout</a></li>
<li><a href="/about">About</a></li>
</ul>
"""

not_authenticated_header = """

<header>
<div class = "page">
<div class="header1">
<h1> Ecommunicate </h1>
<h3>An online communication service</h3>
</div>
<div class="nav">
<a href="/">Home</a> / <a href="/view/">View</a> / <a href="/register/">Register</a> / <a href="/loginlogout/login/">Login</a> / <a href="/about/">About</a>
</div>
</div>
</header>


"""

authenticated_header = """

<header>
<div class = "page">
<div class="header1">
<h1> Ecommunicate </h1>
<h3>An online communication service</h3>
</div>
<div class="nav">
<a href="/">Home</a> / <a href="/view/">View</a> / <a href="/chat/">Chat</a> / <a href="/email/">Email</a> / <a href="/loginlogout/logout/">Logout</a>  / <a href="/about/">About</a>
</div>
</div>
</header>


"""

about_html_string = """
            Ecommunicate is intended to meet the need for electronic communication that is the opposite of private. All of the communication that takes place on this website is purposefully released to the public. Anyone, with or without an Ecommunicate account, can view the communication starting immediately when it is created and continuing indefinitely, similar to an online forum.   <br><br>
          
Text messaging (like Google Hangouts or WeChat) and e-mail (to other ecommunicate.ch e-mail addresses) are implemented already, and we hope to eventually add audio and video calling (like Skype). You can chat or e-mail yourself (after registering and logging in) or you can view other people's chat conversations or e-mail inboxes (see below). This website is experimental at this point. You should expect bugs, unexpected downtime, etc. Please contact ecommunicate.feedback@gmail.com for comments, feature requests, etc. <br><br>
  Below is a list of all of the services that we would like to provide. The ones that are operational are in bold.
<ol>
<li>Chat
<ol>
<li>Create
<ol>
<li><b>Browser</b>
<li><b>Android</b>
<li>iOS
</ol>
<li>View
<ol>
<li><b>Browser</b>
</ol>
</ol>
<li>E-mail
<ol>
<li>Create
<ol>
<li><b>Browser</b>
<li><b>Android</b>
<li>iOS
</ol>
<li>View
<ol>
<li><b>Browser</b>
</ol>
</ol>
<li>Audio/Video Call
<ol>
<li>Create
<ol>
<li>Windows
<li>MacOS
<li>Android
<li>iOS
</ol>
<li>View/Listen
<ol>
<li>Browser
</ol>
</ol>
</ol>
"""

not_authenticated_menubar_html_string = """
<div id="header">
<div id="nav">
<ul class="menubar">
<li class="menubar"><a href="/">Home</a></li>
<li class="menubar"><a href="/view/">View</a></li>
<li class="menubar"><a href="/register/">Register</a></li>
<li class="menubar"><a href="/loginlogout/login/">Login</a></li>
<li class="menubar"><a href="/about">About</a></li>
</ul>
</div>
</div>
"""

authenticated_menubar_html_string = """
<div id="header">
<div id="nav">
<ul class="menubar">
<li class="menubar"><a href="/">Home</a></li>
<li class="menubar"><a href="/view/">View</a></li>
<li class="menubar"><a href="/email/">Email</a></li>
<li class="menubar"><a href="/chat/">Chat</a></li>
<li class="menubar"><a href="/loginlogout/logout/">Logout</a></li>
<li class="menubar"><a href="/about">About</a></li>
</ul>
</div>
</div>
"""

chat_menubar_html_string = """
<div id="header">
<div id="nav">
<ul class="menubar">
<li class="menubar"><a href="/">Home</a></li>
<li class="menubar"><a href="/view/">View</a></li>
<li class="menubar"><a href="/email/">Email</a></li>
<li class="menubar">
<ul class = "submenubar">
<li class = "submenubar">
<ul class = "subsubmenubar">
<li class = "subsubmenubarleftmost"><a href="/chat">Chat</a></li>
<li class = "subsubmenubar"><a href="/loginlogout/logout">Logout</a></li>
<li class = "subsubmenubarrightmost"><a href="/about/">About</a></li>
</ul>
</li>
<li class = "submenubar" ><a href="/chat/makecontactrequests">Make Contact Requests</a></li>
<li class = "submenubar"><a href="/chat/respondtocontactrequests">Respond to Contact Requests</a></li>
</ul>
</ul>
</div>
</div>
"""

chat_menubar_style_html_string = """
ul.subsubmenubar {
text-align: left;
padding: 0;
}
li.subsubmenubarleftmost {
display: inline;
padding-left: 0px;
padding-right: 20px;
}
li.subsubmenubarrightmost {
display: inline;
padding-left: 20px;
padding-right: 0px;
}
li.subsubmenubar {
display: inline;
padding: 20px;
}
ul.submenubar {
list-style-type:none;
display: inline-block;
vertical-align:top;
text-align: left;
padding: 0;
}
li.submenubar {
display: block;
}
ul.menubar {
text-align: center;
}
li.menubar {
        display: inline;
        padding: 20px;
}
"""
