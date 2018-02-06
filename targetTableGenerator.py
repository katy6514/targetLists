#!/usr/bin/env python

#run these two commands first!!!!
# source /soft/SYBASE15.7/SYBASE.csh
# setenv LC_ALL C

import csv
import numpy
import Sybase as sybase
import math
import re
import getpass
import os
from subprocess import call
import json
from decimal import Decimal


#--------------------------------------------------------------------------------------------------------#
# Work In progress, runs on a list of proposal numbers, 
# makes a data table for cutting and pasting into a page. 
# Eventually it'll all be done automatically.
#--------------------------------------------------------------------------------------------------------#

#TEST QUERY
query_test = """SELECT  
                   p.title,  
                   p.category_descrip,   
                   p.type,
                   p.abstract
                FROM proposal p 
                WHERE p.proposal_number = '%s' 
                ORDER BY p.proposal_number"""




#TABLE BIT QUERY
query_table = """SELECT     
                    p.abstract, 
                    p.title,  
                    p.category_descrip,  
                    p.type,   
                    p.proposal_number, 
                    p.proposal_id,
                    a.approved_time, 
                    s.last,  
                    s.first
                 FROM  
                    proposal p, 
                    axafusers..person_short s,  
                    axafocat..prop_info a  
                 WHERE p.proposal_number = '%s' 
                 AND p.piid=s.pers_id  
                 AND a.prop_num = p.proposal_number  
                 ORDER BY p.proposal_number"""


#TARGET BIT QUERY
query_target_table = """SELECT    
                        t.ra,    
                        t.dec,     
                        t.targname,     
                        t.approved_exposure_time,     
                        t.use_grating_id,     
                        t.use_instrument_id
                     FROM     
                        target t,
                        proposal p 
                     WHERE p.proposal_id = t.proposal_id
                     AND t.status = "accepted"
                     AND p.proposal_number= '%s'"""


#--------------------------------------------------------------------------------------------------------#

#---------------------------------------------------------#
# Function to Convert RA (deg) to H.M.S
#---------------------------------------------------------#
def RA_converter(RA_decimal):
    if type(RA_decimal) != float:
        return ""
    else:
        if (RA_decimal < 0):
            sign = -1
            RA   = -RA_decimal 
        else:
            sign = 1
            RA   = RA_decimal
        
        h = int(RA/15.0)
        RA -= h*15.0
        m = int(RA*4.0)
        RA -= m/4.0
        s = RA*240.0

        if(sign == -1):
            out = '-%02d:%02d:%05.2f'%(h,m,s)
        else: out = '+%02d:%02d:%05.2f'%(h,m,s)
   
        return out

#---------------------------------------------------------#
# Function to convert decimal Dec to degrees, minutes, seconds Dec
#---------------------------------------------------------#

def DEC_converter(DEC_decimal):
    if type(DEC_decimal) != float: 
        return ""
    else:
        if (DEC_decimal < 0):
            sign = -1
            DEC = -DEC_decimal
        else:
            sign = 1
            DEC = DEC_decimal
        
        d = int(DEC)
        DEC -= d
        DEC *= 100.
        m = int(DEC*3.0/5.0)
        DEC -= m*5.0/3.0
        s = DEC*180.0/5.0

        if (sign == -1):
            out = '-%02d:%02d:%05.2f'%(d,m,s)
        else: out = '+%02d:%02d:%05.2f'%(d,m,s)

        return out
        

#---------------------------------------------------------#
# Function to identify instruments
#---------------------------------------------------------#

def instrument_ID(n):
    if n == 1:
        return "ACIS-I"
    elif n == 2:
        return "ACIS-S"        
    elif n == 3:
        return "HRC-I"        
    elif n == 4:
        return "HRC-S"        


#---------------------------------------------------------#
# Function to identify gratings#
#---------------------------------------------------------#

def gratings_ID(n):
    if n == 1:
        return "None"
    elif n == 2:
        return "HETG"        
    elif n == 3:
        return "LETG"  


#---------------------------------------------------------
# Database connection
#---------------------------------------------------------
def db_conn(username, userpass): 
    global cur
    conn = sybase.connect('sqlsao',username, userpass) #establish a connection to the dB
    cur = conn.cursor()
    cur.execute("use proposal") # use the proposal dB



#---------------------------------------------------------
# Organize the tiny table details
#---------------------------------------------------------

def target_parser(proposal_num,query):
    target_data = []
    result_row = run_query(proposal_num,query)
    for result in result_row:
        target_info = {'RA': RA_converter(result[0]),
                       'DEC' : DEC_converter(result[1]),
                       'target' : result[2],
                       'approved_time': (result[3],4),
                       'grating' : gratings_ID(result[4]),
                       'inst' : instrument_ID(result[5])}
        target_data.append(target_info)
    return target_data # return the dictionary 



#---------------------------------------------------------
# Organize the big table details
#---------------------------------------------------------

def result_parser_working(result_row):
    for result in result_row:
        prop_info = {'abstract': result[0],
                     'title' : result[1],
                     'category' : result[2],
                     'type': result[3],
                     'prop_num' : result[4],
                     'prop_id' : result[5],
                     'app_time': parseFloat(result[6].toFixed(4)),
                     'name' : result[8]}
        return prop_info # return the dictionary 

#---------------------------------------------------------
# Organize the big table details
#---------------------------------------------------------

def result_parser(result_row):
    for result in result_row:
        prop_info = {'abstract': result[0],
                     'title' : result[1],
                     'category' : result[2],
                     'type': result[3],
                     'prop_num' : result[4],
                     'prop_id' : result[5],
                     'app_time': round(result[6],4),
                     'name' : result[8]+" "+result[7],
                     'targets' : target_parser(result[4],query_target_table)}
        return prop_info # return the dictionary 


#---------------------------------------------------------
# Execute the query 
#---------------------------------------------------------

def run_query(proposal,query):
    # this line takes the query structure you pass into 
    # this function and attaches the proposal number to the query
    query = query%  (str(proposal).zfill(8))  
    cur.execute(query) 
    result_row = cur.fetchall() #grabs the result
    # the following for loop organizes the result into a python 
    # dictionary for easy parsing into you desired format below
    return result_row

#--------------------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------------------#
#----------------------------------------------Do the thing----------------------------------------------#
#--------------------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------------------#

cycle_num = raw_input("Cycle #?: ")
cycle = "cycle"+cycle_num

prop_list_input = raw_input("File list of proposals? (include path if necessary): ")
FILE = open(prop_list_input,'r')

proposal_list = []

for line in FILE:
    line = line.replace("\n","")
    prop_num =  line.strip()
    proposal_list.append(prop_num)


username = getpass.getuser()
#print username
userpass = getpass.getpass("DB password: ")
db_conn(username, userpass)


proposal_dictionaries = []

for proposal in proposal_list:
    result_row = run_query(proposal, query_table)
    prop_dict = result_parser(result_row)
    proposal_dictionaries.append(prop_dict)


#print json.dumps(proposal_dictionaries, indent=4, sort_keys=True)

data = open(cycle+".json","w+")

data.write("""{
  "data": """)

data.write(json.dumps(proposal_dictionaries, indent=4, sort_keys=True))

data.write("""
} """)
data.close()


copy_cmd = "cp "+cycle+".json /data/cdoweb/wymanRep/target_lists/"+cycle
retvalue = os.system(copy_cmd)
if retvalue == 0:
    print "Copy successful"
