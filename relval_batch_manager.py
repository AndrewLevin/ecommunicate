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

class RelvalBatchAssigner(object):
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

Enter a description of this batch (e.g. "https://hypernews.cern.ch/HyperNews/CMS/get/dataopsrequests/5493.html first try") <br>
<textarea name="Description" rows="5" cols="150"></textarea>

<br>
<br>

Enter your username: <br>
<input type="text" name="User" size=100 />

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

Does this batch include any heavy ion workflows? (This affects where the workflows can be run.)<br>

<select name="HI">
<option selected>No</option>
<option>Yes</option>
</select>

<br>
<br>
<br>

<input type="submit" value="Submit"/>

</form>

</body>
        </html>"""

    @cherrypy.expose
    def handle_POST(self, Description, User, AnnouncementTitle, ListOfWorkflows, HI):
        #dn=cherrypy.request.headers['Cms-Authn-Dn']
        dn=User

        if Description == "":
            return_value="Your request was rejected for the following reason:\n"
            return_value=return_value+"<br>\n"
            return_value=return_value+"No description given.\n"
            return return_value
        if User == "":
            return_value="Your request was rejected for the following reason:\n"
            return_value=return_value+"<br>\n"
            return_value=return_value+"No username given.\n"
            return return_value
        elif AnnouncementTitle == "":
            return_value="Your request was rejected for the following reason:\n"
            return_value=return_value+"<br>\n"
            return_value=return_value+"No announcement e-mail title was given.\n"
            return return_value
        elif ListOfWorkflows == "":
            return_value="Your request was rejected for the following reason:\n"
            return_value=return_value+"<br>\n"
            return_value=return_value+"No workflows were given.\n"
            return return_value

        wf_names_fname=os.popen("mktemp").read()
        wf_names_fname=wf_names_fname.rstrip('\n')
        wf_names_fname=wf_names_fname.rstrip('\r')
        
        for wf in ListOfWorkflows.split('\n'):
            wf = wf.rstrip('\n')
            wf = wf.rstrip('\r')
            if wf.strip() == "":
                continue
            os.system("echo "+wf+" >> "+wf_names_fname)

        #os.system("python2.6 insert_batch.py "+HypernewsPost+" "+wf_names_fname+" \""+AnnouncementTitle+"\" "+StatisticsFilename+" \""+Description+"\" "+ProcessingVersion+" "+Site+";")

        wf_names=wf_names_fname
        email_title=AnnouncementTitle
        description=Description
        proc_ver=str(1)

        if HI == "Yes":
            #site = "T2_CH_CERN_T0"
            #site = "T2_CH_CERN_AI"
            site = "T1_FR_CCIN2P3"
        elif HI == "No":
            site = "T1_US_FNAL"
        else:
            print "unknown value of site, exiting"
            return "Your request was rejected due to an unexpected value of the HI variable."

        print "wf_names = "+wf_names
        print "email_title = "+email_title

        print "description = "+description
        print "proc_ver = "+proc_ver
        print "site = "+site

        dbname = "relval"

        conn = MySQLdb.connect(host='dbod-cmsrv1.cern.ch', user='relval', passwd="relval", port=5506)
        #conn = MySQLdb.connect(host='localhost', user='relval', passwd="relval")

        curs = conn.cursor()

        curs.execute("use "+dbname+";")

        f=open(wf_names, 'r')

        #do some checks before inserting the workflows into the database
        for line in f:
            workflow = line.rstrip('\n')
            if workflow == "":
                print "empty line in the file, exiting"
                sys.exit(1)
            curs.execute("select workflow_name from workflows where workflow_name=\""+ workflow +"\";")
            if len(curs.fetchall()) > 0:
                return_value="Your request was rejected for the following reason:\n"
                return_value=return_value+"<br>\n"
                return_value=return_value+"The workflow "+workflow+" was already requested.\n"
                return return_value

        now=datetime.datetime.now()    

        useridyear=now.strftime("%Y")
        useridmonth=now.strftime("%m")
        useridday=now.strftime("%d")

        #the batch id of the new batch should be 1 more than any existing batch id
        curs.execute("select MAX(useridnum) from batches where useridyear=\""+useridyear+"\" and useridmonth=\""+useridmonth+"\" and useridday=\""+useridday+"\";")
        max_user_num_batches=curs.fetchall()[0][0]

        if max_user_num_batches == None:
            usernum=0;
        else:    
            usernum=max_user_num_batches+1

        userbatchid=useridyear + "_"+useridmonth+"_"+useridday+"_"+str(usernum)+"_0"

        #sanity checks to make sure this is really a new userbatchid
        curs.execute("select * from batches where useridyear=\""+useridyear+"\" and useridmonth=\""+useridmonth+"\" and useridday=\""+useridday+"\" and useridnum="+str(usernum)+";")
        if len(curs.fetchall()) > 0:
            print "batch_id "+str(userbatchid)+" was already inserted into the batches database, exiting"
            sys.exit(1)

        f_index=0
        g_index=0

        f=open(wf_names, 'r')

        #check that the workflow name contains only letters, numbers, '-' and '_' 
        for line in f:
            workflow=line.rstrip('\n')
            for c in workflow:
                if c != 'a' and c != 'b' and c != 'c' and c != 'd' and c != 'e' and c != 'f' and c != 'g' and c != 'h' and c != 'i' and c != 'j' and c != 'k' and c != 'l' and c != 'm' and c != 'n' and c != 'o' and c != 'p' and c != 'q' and c != 'r' and c != 's' and c != 't' and c != 'u' and c != 'v' and c != 'w' and c != 'x' and c != 'y' and c != 'z' and c != 'A' and c != 'B' and c != 'C' and c != 'D' and c != 'E' and c != 'F' and c != 'G' and c != 'H' and c != 'I' and c != 'J' and c != 'K' and c != 'L' and c != 'M' and c != 'N' and c != 'O' and c != 'P' and c != 'Q' and c != 'R' and c != 'S' and c != 'T' and c != 'U' and c != 'V' and c != 'W' and c != 'X' and c != 'Y' and c != 'Z' and c != '0' and c != '1' and c != '2' and c != '3' and c != '4' and c != '5' and c != '6' and c != '7' and c != '8' and c != '9' and c != '_' and c != '-':
                    return_value="Your request was rejected for the following reason:\n"
                    return_value=return_value+"<br>\n"
                    return_value=return_value+"workflow "+workflow+" contains the character "+str(c)+" which is not allowed.\n"
                    return return_value

        #need to reopen the file because it was already iterated over        
        f=open(wf_names, 'r')

        #check that no workflows are repeated in the file
        for line1 in f:
            workflow1 = line1.rstrip('\n')
            g=open(wf_names, 'r')
            for line2 in g:
                if f_index == g_index:
                    continue
                    g_index=g_index+1
                workflow2 = line2.rstrip('\n')
                if workflow1 == workflow2:
                    return_value="Your request was rejected for the following reason:\n"
                    return_value=return_value+"<br>\n"
                    return_value=return_value+"workflow "+ workflow1+" is repeated twice in the list of workflows\n"
                    return return_value
                g_index=g_index+1
            f_index=f_index+1

        f=open(wf_names, 'r')


        #os.popen("echo "+Description+" | mail -s \"[RelVal] "+ AnnouncementTitle +"\" andrew.m.levin@vanderbilt.edu --");  

        return_value="Your request has been received.\n"
        return_value=return_value+"<br>\n"
        return_value=return_value+"<br>\n"
        return_value=return_value+"This batch was given the following batch id: "+str(userbatchid)
        return_value=return_value+"<br>\n"
        return_value=return_value+"<br>\n"
        return_value=return_value+"You may monitor its progress at http://cms-project-relval.web.cern.ch/cms-project-relval/relval_monitor_most_recent_50_batches.txt\n"
        return_value=return_value+"<br>\n"
        return_value=return_value+"<br>\n"
        return_value=return_value+"The information we have received is shown below.\n"
        return_value=return_value+"<br>\n"
        return_value=return_value+"<br>\n"
        return_value=return_value+"Description: "+Description+"\n"
        return_value=return_value+"<br>\n"
        return_value=return_value+"HI: "+HI+"\n"
        return_value=return_value+"<br>\n"
        return_value=return_value+"Announcement e-mail title: "+AnnouncementTitle+"\n"
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

        hn_email="Dear all,\n"
        hn_email=hn_email+"\n"
        hn_email=hn_email+"A new batch of relval workflows was requested.\n"
        hn_email=hn_email+"\n"
        hn_email=hn_email+"Batch ID:"
        hn_email=hn_email+"\n"
        hn_email=hn_email+"\n"
        hn_email=hn_email+str(userbatchid)
        hn_email=hn_email+"\n"
        hn_email=hn_email+"\n"
        hn_email=hn_email+"Requestor:\n"
        hn_email=hn_email+"\n"
        hn_email=hn_email+dn+"\n"
        hn_email=hn_email+"\n"
        hn_email=hn_email+"Description of this request:\n"
        hn_email=hn_email+"\n"
        hn_email=hn_email+description+"\n"
        hn_email=hn_email+"\n"
        hn_email=hn_email+"List of workflows:\n"
        hn_email=hn_email+"\n"
        for wf in ListOfWorkflows.split('\n'):
            wf = wf.rstrip('\n')
            wf = wf.rstrip('\r')
            if wf.strip() == "":
                continue
            hn_email=hn_email+wf+"\n"
        hn_email=hn_email+"\n"
        hn_email=hn_email+"RelVal Batch Manager"

        #os.popen("cat "+hn_email+" | mail -s \"[RelVal] "+ AnnouncementTitle +"\" hn-cms-hnTest@cern.ch --");      
        
        first_messageID = email.Utils.make_msgid()

        msg = MIMEMultipart()
        reply_to = []
        send_to = ["hn-cms-dataopsrequests@cern.ch","andrew.m.levin@vanderbilt.edu","andrew.m.levin.filter1@gmail.com"]
        #send_to = ["hn-cms-hnTest@cern.ch"]
        #send_to = ["andrew.m.levin@vanderbilt.edu"]
        msg_subj = AnnouncementTitle


        hnemail= get_HNews_info(dn).result()

        if hnemail == "":
            msg['From'] = "amlevin@mit.edu"
        else:
            msg['From'] = hnemail
        #msg['From'] = str(dn)+"@cern.ch"
        msg['reply-to'] = COMMASPACE.join(reply_to)
        msg['To'] = COMMASPACE.join(send_to)
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = msg_subj
        msg['Message-ID'] = email.Utils.make_msgid()
    
        print msg['Message-ID']

        try:
            msg.attach(MIMEText(hn_email))
            smtpObj = smtplib.SMTP()
            smtpObj.connect()
            smtpObj.sendmail("amlevin@mit.edu", send_to, msg.as_string())
            smtpObj.close()
        except Exception as e:
            print "Error: unable to send email: %s" %(str(e))

        curs.execute("insert into batches set announcement_title=\""+email_title+"\", batch_version_num=0, processing_version="+proc_ver+", site=\""+site+"\", DN=\""+dn+"\", description=\""+description+"\", status=\"approved\", hn_message_id=\""+msg['Message-ID']+"\", useridyear=\""+useridyear+"\", useridmonth=\""+useridmonth+"\", useridday=\""+useridday+"\", useridnum="+str(usernum)+", current_status_start_time=\""+datetime.datetime.now().strftime("%y:%m:%d %H:%M:%S")+"\", batch_creation_time=\""+datetime.datetime.now().strftime("%y:%m:%d %H:%M:%S")+"\"")

        for line in f:
            workflow = line.rstrip('\n')
            curs.execute("insert into workflows set batch_version_num=0, useridyear=\""+useridyear+"\", useridmonth=\""+useridmonth+"\", useridday=\""+useridday+"\", useridnum="+str(usernum)+", workflow_name=\""+workflow+"\";")

        conn.commit()

        curs.close()

        conn.close()


        return return_value

if __name__ == '__main__':
    cherrypy.config.update({'server.socket_port': 8080})
    cherrypy.config.update({'server.socket_host': 'cmsrelval002.cern.ch'})
    cherrypy.quickstart(RelvalBatchAssigner())
