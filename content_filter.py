#!/usr/bin/env python

import sys

import email

import mailbox

import MySQLdb

import time

import os

tmp_filename=os.popen("mktemp").read().rstrip('\n')

log_file = open(tmp_filename,"w")

log_file.write("andrew debug 1\n")

log_file.write(sys.argv[0]+"\n")

log_file.write("andrew debug 2\n")

log_file.write(sys.argv[1]+"\n")

log_file.write("andrew debug 3\n")

log_file.write(sys.argv[2]+"\n")

msg_string = ""

for line in sys.stdin:
    log_file.write("andrew debug 6\n")
    msg_string = msg_string + line
    log_file.write("andrew debug 7\n")

log_file.write("andrew debug 8\n")

log_file.write(msg_string)

log_file.write("andrew debug 9\n")

msg=mailbox.MaildirMessage(email.message_from_string(msg_string))

log_file.write("andrew debug 10\n")

log_file.write(msg.as_string())

log_file.write("andrew debug 11\n")

log_file.write('/efsemail/mail/vhosts/ecommunicate.ch/'+sys.argv[1].split("@")[0]+'/'+"\n")

log_file.write('/efsemail/mail/vhosts/ecommunicate.ch/'+sys.argv[2].split("@")[0]+'/'+"\n")

log_file.write("andrew debug 12\n")

maildir_receiver = mailbox.Maildir('/efsemail/mail/vhosts/ecommunicate.ch/'+sys.argv[1].split("@")[0]+'/', factory=mailbox.MaildirMessage,create=True)

maildir_sender = mailbox.Maildir('/efsemail/mail/vhosts/ecommunicate.ch-sent/'+sys.argv[2].split("@")[0]+'/', factory=mailbox.MaildirMessage,create=True)

log_file.write("andrew debug 13\n")

add_return_value_receiver=maildir_receiver.add(msg)

add_return_value_sender=maildir_sender.add(msg)

log_file.write("andrew debug 14\n")

dbname="ecommunicate"

log_file.write("andrew debug 15\n")

secrets_file=open("/home/vmail/secrets.txt")

log_file.write("andrew debug 16\n")

passwords=secrets_file.read().rstrip('\n')

log_file.write("andrew debug 17\n")

db_password = passwords.split('\n')[0]

log_file.write("andrew debug 18\n")

conn = MySQLdb.connect(host='ecommunicate-production.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='browser', passwd=db_password, port=3306)

log_file.write("andrew debug 19\n")

curs = conn.cursor()

log_file.write("andrew debug 20\n")

curs.execute("use "+dbname+";")

log_file.write("andrew debug 21\n")

log_file.write(time.strftime('%Y-%m-%d %H:%M:%S',email.utils.parsedate(msg['Date'])))

log_file.write("andrew debug 22\n")

curs.execute("insert into received_emails set username = \""+sys.argv[1].split("@")[0]+"\", id=\""+add_return_value_receiver+"\", received_time=\""+time.strftime('%Y-%m-%d %H:%M:%S',email.utils.parsedate(msg['Date']))+"\", is_read = 0;")

curs.execute("insert into sent_emails set username = \""+sys.argv[2].split("@")[0]+"\", id=\""+add_return_value_sender+"\", sent_time=\""+time.strftime('%Y-%m-%d %H:%M:%S',email.utils.parsedate(msg['Date']))+"\";")

log_file.write("andrew debug 23\n")

curs.close()

log_file.write("andrew debug 24\n")

conn.commit()

log_file.write("andrew debug 25\n")

conn.close()

log_file.write("andrew debug 26\n")

os.system("mv " + tmp_filename + " /home/vmail/" + add_return_value_receiver + ".log")
