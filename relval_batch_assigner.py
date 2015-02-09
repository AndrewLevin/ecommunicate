import MySQLdb
import sys
import datetime
import sys,os
import cherrypy

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
    def handle_POST(self, Description, AnnouncementTitle, ListOfWorkflows, ProcessingVersion, HI):
        dn=cherrypy.request.headers['Cms-Authn-Dn']

        if Description == "":
            return_value="Your request was rejected for the following reason:\n"
            return_value=return_value+"<br>\n"
            return_value=return_value+"No description given.\n"
            return return_value
        elif AnnouncementTitle == "":
            return_value="Your request was rejected for the following reason:\n"
            return_value=return_value+"<br>\n"
            return_value=return_value+"No announcement e-mail title was given.\n"
            return return_value
        elif ProcessingVersion == "":
            return_value="Your request was rejected for the following reason:\n"
            return_value=return_value+"<br>\n"
            return_value=return_value+"No processing version was given.\n"
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
        proc_ver=ProcessingVersion

        if HI == "Yes":
            site = "T2_CH_CERN"
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

        conn = MySQLdb.connect(host='dbod-altest1.cern.ch', user='relval', passwd="relval", port=5505)
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
                print "workflow "+workflow+" was already inserted into the database, exiting"
                sys.exit(1)
                    

        #the batch id of the new batch should be 1 more than any existing batch id
        curs.execute("select MAX(batch_id) from batches;")
        max_batchid_batches=curs.fetchall()[0][0]
        curs.execute("select MAX(batch_id) from batches_archive;")
        max_batchid_batches_archive=curs.fetchall()[0][0]

        if max_batchid_batches == None and max_batchid_batches_archive == None:
            batchid=0;
        elif max_batchid_batches == None and max_batchid_batches_archive != None:
            batchid=max_batchid_batches_archive+1
        elif max_batchid_batches != None and max_batchid_batches_archive == None:
            batchid=max_batchid_batches+1
        else:     
            batchid=max(max_batchid_batches,max_batchid_batches_archive)+1

        #sanity checks to make sure this is really a new batchid
        curs.execute("select batch_id from batches where batch_id="+ str(batchid) +";")
        if len(curs.fetchall()) > 0:
            print "batch_id "+str(batchid)+" was already inserted into the batches database, exiting"
            sys.exit(1)

        curs.execute("select batch_id from workflows where batch_id="+ str(batchid) +";")
        if len(curs.fetchall()) > 0:
            print "batch_id "+str(batchid)+" was already inserted into the workflows database, exiting"
            sys.exit(1)     


        now=datetime.datetime.now()    

        useridyear=now.strftime("%Y")
        useridmonth=now.strftime("%m")
        useridday=now.strftime("%d")

        print "select MAX(user_num) from batches where useridyear=\""+useridyear+"\" and useridmonth=\""+useridmonth+"\" and useridday=\""+useridday+"\";"

        #the batch id of the new batch should be 1 more than any existing batch id
        curs.execute("select MAX(useridnum) from batches where useridyear=\""+useridyear+"\" and useridmonth=\""+useridmonth+"\" and useridday=\""+useridday+"\";")
        max_user_num_batches=curs.fetchall()[0][0]
        curs.execute("select MAX(useridnum) from batches_archive where useridyear=\""+useridyear+"\" and useridmonth=\""+useridmonth+"\" and useridday=\""+useridday+"\";")
        max_user_num_batches_archive=curs.fetchall()[0][0]

        if max_user_num_batches == None and max_user_num_batches_archive == None:
            usernum=0;
        elif max_user_num_batches == None and max_user_num_batches_archive != None:
            usernum=max_user_num_batches_archive+1
        elif max_user_num_batches != None and max_user_num_batches_archive == None:
            usernum=max_user_num_batches+1
        else:     
            usernum=max(max_user_num_batches,max_user_num_batches_archive)+1

        #sanity checks to make sure this is really a new userbatchid
        curs.execute("select batch_id from batches where useridyear=\""+useridyear+"\" and useridmonth=\""+useridmonth+"\" and useridday=\""+useridday+"\" and useridnum="+str(usernum)+";")
        if len(curs.fetchall()) > 0:
            print "batch_id "+str(batchid)+" was already inserted into the batches database, exiting"
            sys.exit(1)

        curs.execute("select batch_id from batches_archive where useridyear=\""+useridyear+"\" and useridmonth=\""+useridmonth+"\" and useridday=\""+useridday+"\" and useridnum="+str(usernum)+";")
        if len(curs.fetchall()) > 0:
            print "batch_id "+str(batchid)+" was already inserted into the workflows database, exiting"
            sys.exit(1)     

        userbatchid=useridyear + "_"+useridmonth+"_"+useridday+"_"+str(usernum)

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

        print "creating a new batch with batch_id = "+str(batchid)

        curs.execute("insert into batches set batch_id="+str(batchid)+", announcement_title=\""+email_title+"\", processing_version="+proc_ver+", site=\""+site+"\", DN=\""+dn+"\", description=\""+description+"\", status=\"inserted\", useridyear=\""+useridyear+"\", useridmonth=\""+useridmonth+"\", useridday=\""+useridday+"\", useridnum="+str(usernum)+", current_status_start_time=\""+datetime.datetime.now().strftime("%y:%m:%d %H:%M:%S")+"\"")


        for line in f:
            workflow = line.rstrip('\n')
            curs.execute("insert into workflows set batch_id="+str(batchid)+", workflow_name=\""+workflow+"\";")

        conn.commit()

        curs.close()

        conn.close()

        os.popen("echo "+Description+" | mail -s \"[RelVal] "+ AnnouncementTitle +"\" andrew.m.levin@vanderbilt.edu --");  

        return_value="Your request has been received.\n"
        return_value=return_value+"<br>\n"
        return_value=return_value+"<br>\n"
        return_value=return_value+"This batch was given the following batch id: "+str(userbatchid)
        return_value=return_value+"<br>\n"
        return_value=return_value+"<br>\n"
        return_value=return_value+"You may monitor its progress at http://cms-project-relval.web.cern.ch/cms-project-relval/relval_monitor.txt\n"
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

        hn_email=os.popen("mktemp").read()    

        os.system("echo \"Dear all,\" >> "+hn_email)    
        os.system("echo \"\" >> "+hn_email)
        os.system("echo \"A new batch of relval workflows was requested.\" >> "+hn_email)
        os.system("echo \"\" >> "+hn_email)
        os.system("echo \"Batch ID:\" >> "+hn_email)
        os.system("echo \"\" >> "+hn_email)
        os.system("echo \""+str(userbatchid)+"\" >> "+hn_email)
        os.system("echo \"\" >> "+hn_email)
        os.system("echo \"Requestor:\" >> "+hn_email)
        os.system("echo \"\" >> "+hn_email)
        os.system("echo \""+dn+"\" >> "+hn_email)
        os.system("echo \"\" >> "+hn_email)
        os.system("echo \"Description of this request:\" >> "+hn_email)
        os.system("echo \"\" >> "+hn_email)
        os.system("echo \""+description+"\" >> "+hn_email)
        os.system("echo \"\" >> "+hn_email)
        os.system("echo \"List of workflows:\" >> "+hn_email)
        for wf in ListOfWorkflows.split('\n'):
            wf = wf.rstrip('\n')
            wf = wf.rstrip('\r')
            if wf.strip() == "":
                continue
            os.system("echo \""+wf+"\" >> "+hn_email)
        os.system("echo \"\" >> "+hn_email)
        os.system("echo \"RelVal Batch Manager\" >> "+hn_email)

        os.popen("cat "+hn_email+" | mail -s \"[RelVal] "+ AnnouncementTitle +"\" hn-cms-hnTest@cern.ch --");      

        return return_value

if __name__ == '__main__':
    cherrypy.quickstart(RelvalBatchAssigner())
