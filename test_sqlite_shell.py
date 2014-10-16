# -*- coding: utf-8 -*-
"""
Created on Sat Mar 08 21:18:36 2014

@author: Eric Conklin
"""

# A minimal SQLite shell for experiments

import sqlite3

con = sqlite3.connect('twitter_data.db')
con.isolation_level = None
cur = con.cursor()

buf = ""

print "\n\nEnter your SQL commands to execute in sqlite3, terminated with a <;>."
print "Enter a blank line to exit."
print "===========================\n"

while True:
    buf = ""
    line = raw_input('> ')
    if line == "":
        break
    buf += line
    if sqlite3.complete_statement(buf):

        try:
            buf = buf.strip()

            cur.execute(buf)
            if buf.lstrip().upper().startswith("SELECT"):
                print '\n'
                for l in cur.fetchall():
                    print l
        except sqlite3.Error as e:
            print "An error occurred:", e.args[0]
    else:
        print 'please end your statement with a <;>!'
    print "\n===========================\n"

con.close()