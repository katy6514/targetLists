#!/usr/bin/env python

#import csv
#import Sybase as sybase

#import re
#import getpass
import numpy

d = numpy.loadtxt("XVPlist.csv", skiprows=0)
for prop_num in d:
    print int(prop_num)


#with open('XVPlist.csv') as f:
#    f=[x.strip() for x in f if x.strip()]
#    print f
  #  data=[tuple(map(float,x.split())) for x in f[2:]]
  #  charges=[x[1] for x in data]
  #  times=[x[0] for x in data]
  #  print('times',times)
  #  print('charges',charges)

#import sqlanydb

#cycle = int(raw_input("Cycle?: "))

#prop_list = open(raw_input("List?: "))
#prop_list = csv.reader(prop_list)



# Create a connection object
#con = sqlanydb.connect( database=proposal,userid=kwyman,password=bluepandahat )
#conn = sybase.connect(user='kwyman', passwd='bluepandahat')

#cur = conn.cursor()

#cur.execute("use proposal")

#cur.execute("SELECT * FROM grating")

#print "Query Returned %d row(s)" % cur.rowcount
#for row in cur:
#    print row

#for i in prop_list:
## Execute a SQL string
#sql = "SELECT title, proposal_number FROM proposal WHERE proposal_number = 13610808 ORDER BY proposal_number"
#cursor.execute(sql)


## Get a cursor description which contains column names
#desc = cursor.description
#print len(desc)


#for i in prop_list:
 #   print i


# Close the connection
#conn.close()
