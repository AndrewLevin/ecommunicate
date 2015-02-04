from datetime import datetime
import sys,os

import cherrypy

class StringGenerator(object):
    @cherrypy.expose
    def index(self):
        return """<html>
<head><title>batch request manager</title>
</head>
<body>

<form action="handle_POST" method="get">

Please contact amlevin@mit.edu if you have problems with this service.

<br>
<br>

Enter the hypernews post where this batch was requested (e.g. https://hypernews.cern.ch/HyperNews/CMS/get/dataopsrequests/5493.html) <br>
<input type="text" name="HypernewsPost" size=100 />

<br>
<br>

Enter a description of this batch (e.g. "https://hypernews.cern.ch/HyperNews/CMS/get/dataopsrequests/5493.html first try") <br>
<input type="text" name="Description" size=100 />

<br>
<br>

Enter the title of the announcement e-mail here (e.g. standard relval samples for 710pre7):<br> 
<input type="text" name="AnnouncementTitle" size=100 />

<br>
<br>

Enter the list of workflows here: <br>
<textarea name="ListOfWorkflows" rows="20" cols="80"></textarea>

<br>
<br>

Enter the processing version here: <br>
<input type="text" name="ProcessingVersion" size=1></textarea>

<br>
<br>

Select the site where the workflow will run here:<br>

<select name="Site">
<option selected>T2_CH_CERN</option>
<option>T1_US_FNAL</option>
</select>

<br>
<br>

Enter the name of the file where the statistics about the output datasets will be stored (e.g. CMSSW_7_2_0_pre5_pileup.txt):<br> 
<input type="text" name="StatisticsFilename" size=50 />

<br>
<br>
<br>

<input type="submit" value="Submit"/>

</form>

</body>
        </html>"""

    @cherrypy.expose
    def handle_POST(self, HypernewsPost, Description, AnnouncementTitle, ListOfWorkflows, ProcessingVersion, Site, StatisticsFilename):
        f = open("relval_batch_assigner_logs/log.dat", 'a')
        f.write(str(datetime.now())+"\n")
        f.flush()
        return_value="Description: "+Description+"\n"
        return_value=return_value+"<br>\n"
        return_value=return_value+"Hypernews Post: "+HypernewsPost+"\n"
        return_value=return_value+"<br>\n"
        return_value=return_value+"StatisticsFilename: "+StatisticsFilename+"\n"
        return_value=return_value+"<br>\n"
        return_value=return_value+"Announcement e-mail title: "+AnnouncementTitle+"\n"
        return_value=return_value+"<br>\n"
        return_value=return_value+"Site: "+Site+"\n"
        return_value=return_value+"<br>\n"
        return_value=return_value+"Processing version: "+ProcessingVersion+"\n"
        return_value=return_value+"<br>\n"
        return_value=return_value+"Workflows:"
        return_value=return_value+"<br>\n"
        for wf in ListOfWorkflows.split('\n'):
            wf = wf.rstrip('\n')
            wf = wf.rstrip('\r')
            if wf.strip() == "":
                continue
            return_value=return_value+wf+"\n"
            return_value=return_value+"<br>"

        wf_names_fname=os.popen("mktemp").read()
        wf_names_fname=wf_names_fname.rstrip('\n')
        wf_names_fname=wf_names_fname.rstrip('\r')
        
        for wf in ListOfWorkflows.split('\n'):
            wf = wf.rstrip('\n')
            wf = wf.rstrip('\r')
            if wf.strip() == "":
                continue
            os.system("echo "+wf+" >> "+wf_names_fname)

        os.system("python2.6 insert_batch.py "+HypernewsPost+" "+wf_names_fname+" \""+AnnouncementTitle+"\" "+StatisticsFilename+" \""+Description+"\" "+ProcessingVersion+" "+Site+";")

        os.popen("echo "+Description+" | mail -s \"[RelVal] "+ AnnouncementTitle +"\" andrew.m.levin@vanderbilt.edu --");  

        return return_value

if __name__ == '__main__':
    cherrypy.quickstart(StringGenerator())
