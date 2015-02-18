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

class RelvalBatchApprover(object):
    @cherrypy.expose
    def index(self):
        dbname = "relval"

        conn = MySQLdb.connect(host='dbod-altest1.cern.ch', user='relval', passwd="relval", port=5505)

        curs = conn.cursor()

        curs.execute("use "+dbname+";")

        curs.execute("select * from batches")

        batches=curs.fetchall()

        colnames = [desc[0] for desc in curs.description]

        return_value="""<html>
<head><title>batch request manager</title>
</head>
<body>
<form action="relval5.php" method="post">"""

        for batch in batches:
            for name, value in zip(colnames, batch):
                if name=="status":
                    status=value
                elif name == "batch_id":
                    batchid=value
                elif name == "site":
                    site=value

            #if status != "inserted":
            #    continue
               
            return_value=return_value+str(batchid)+"\n"
            return_value=return_value+"<br>"
            return_value=return_value+site+"\n"
            return_value=return_value+"<br>"
            return_value=return_value+"<input  name='batch"+str(batchid)+"' value='approve' type='radio'/> approve <input  name='batch"+str(batchid)+"' value='disapprove' type='radio'/> disapprove <input checked='checked' name='batch"+str(batchid)+"' value='null' type='radio'/> do nothing<br/>\n"


        return_value=return_value+"""

<input type=\"submit\" value=\"Submit\"/>

</form>

</body>
        </html>"""
        return return_value

    @cherrypy.expose
    def handle_POST_2(self,User,*args,**kwargs):

        print User

        if User!="anlevin" and User!="amaltaro" and User!="jbadillo":
            return "User "+User+" is not allowed to approve requests"

        dbname = "relval"

        conn = MySQLdb.connect(host='dbod-altest1.cern.ch', user='relval', passwd="relval", port=5505)

        curs = conn.cursor()

        curs.execute("use "+dbname+";")

        for arg in args:
            print arg

        return_value=""

        for kwarg in kwargs:
            if kwargs[kwarg] == "approve":
                curs.execute("update batches set status=\"approved\", current_status_start_time=\""+datetime.datetime.now().strftime("%y:%m:%d %H:%M:%S")+"\" where batch_id = "+ kwarg.strip("batch") +";")
                return_value=return_value+kwarg+" was approved\n"
                return_value=return_value+"<br>\n"
            elif kwargs[kwarg] == "disapprove":    
                curs.execute("update batches set status=\"disapproved\", current_status_start_time=\""+datetime.datetime.now().strftime("%y:%m:%d %H:%M:%S")+"\" where batch_id = "+ kwarg.strip("batch") +";")
                return_value=return_value+kwarg+" was disapproved\n"
                return_value=return_value+"<br>\n"

        conn.commit()        



        return return_value

if __name__ == '__main__':
    cherrypy.config.update({'server.socket_port': 8084})
    cherrypy.config.update({'server.socket_host': 'relvaltest005.cern.ch'})
    cherrypy.quickstart(RelvalBatchApprover())
