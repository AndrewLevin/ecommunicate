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

        #os.system("python2.6 insert_batch.py "+HypernewsPost+" "+wf_names_fname+" \""+AnnouncementTitle+"\" "+StatisticsFilename+" \""+Description+"\" "+ProcessingVersion+" "+Site+";")

        hnrequest=HypernewsPost
        wf_names=wf_names_fname
        email_title=AnnouncementTitle
        stats_file=StatisticsFilename
        description=Description
        proc_ver=ProcessingVersion
        site=Site

        print "hnrequest = "+hnrequest
        print "wf_names = "+wf_names
        print "email_title = "+email_title
        print "stats_file = "+stats_file
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

        f_index=0
        g_index=0

        f=open(wf_names, 'r')

        #check that the workflow name contains only letters, numbers, '-' and '_' 
        for line in f:
            workflow=line.rstrip('\n')
            for c in workflow:
                if c != 'a' and c != 'b' and c != 'c' and c != 'd' and c != 'e' and c != 'f' and c != 'g' and c != 'h' and c != 'i' and c != 'j' and c != 'k' and c != 'l' and c != 'm' and c != 'n' and c != 'o' and c != 'p' and c != 'q' and c != 'r' and c != 's' and c != 't' and c != 'u' and c != 'v' and c != 'w' and c != 'x' and c != 'y' and c != 'z' and c != 'A' and c != 'B' and c != 'C' and c != 'D' and c != 'E' and c != 'F' and c != 'G' and c != 'H' and c != 'I' and c != 'J' and c != 'K' and c != 'L' and c != 'M' and c != 'N' and c != 'O' and c != 'P' and c != 'Q' and c != 'R' and c != 'S' and c != 'T' and c != 'U' and c != 'V' and c != 'W' and c != 'X' and c != 'Y' and c != 'Z' and c != '0' and c != '1' and c != '2' and c != '3' and c != '4' and c != '5' and c != '6' and c != '7' and c != '8' and c != '9' and c != '_' and c != '-':
                    print "workflow "+workflow+" contains the character "+str(c)+" which is not allowed, exiting"
                    sys.exit(0)          

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
                    print "workflow "+ workflow1+" is repeated twice in the input file, exiting"
                    sys.exit(1)
                g_index=g_index+1
            f_index=f_index+1

        f=open(wf_names, 'r')

        print "creating a new batch with batch_id = "+str(batchid)

        curs.execute("insert into batches set batch_id="+str(batchid)+", hn_req=\""+hnrequest+"\", announcement_title=\""+email_title+"\", stats_file=\""+stats_file+"\", processing_version="+proc_ver+", site=\""+site+"\", description=\""+description+"\", status=\"inserted\", current_status_start_time=\""+datetime.datetime.now().strftime("%y:%m:%d %H:%M:%S")+"\"")


        for line in f:
            workflow = line.rstrip('\n')
            curs.execute("insert into workflows set batch_id="+str(batchid)+", workflow_name=\""+workflow+"\";")

        conn.commit()

        curs.close()

        conn.close()

        os.popen("echo "+Description+" | mail -s \"[RelVal] "+ AnnouncementTitle +"\" andrew.m.levin@vanderbilt.edu --");  

        return return_value

if __name__ == '__main__':
    cherrypy.quickstart(RelvalBatchAssigner())

