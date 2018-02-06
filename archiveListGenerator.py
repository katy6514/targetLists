#!/usr/bin/env python

#run these two commands first!!!!
# >source /soft/SYBASE_OCS15.5/SYBASE.csh
# >setenv LC_ALL C
#call(["source /soft/SYBASE_OCS15.5/SYBASE.csh"])
#call(["setenv LC_ALL C"])

import csv
import numpy
import Sybase as sybase
import math
import re
import getpass
import os
from subprocess import call


    
#--------------------------------------------------------------------------------------------------------#
#----------------------------------------------Queries---------------------------------------------------#
#--------------------------------------------------------------------------------------------------------#
# you need to run a few different queries in order to generate the complete target page, here they are


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

#ABSTRACT BIT QUERY
query_abs_table = """SELECT    
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

#A/T TABLE BIT QUERY
at_query_table = """SELECT     
                    p.abstract, 
                    p.title,  
                    p.category_descrip,  
                    p.type,   
                    p.proposal_number, 
                    p.proposal_id,
                    s.last,  
                    s.first  
                 FROM  
                    proposal p,  
                    axafusers..person_short s, 
                 WHERE p.proposal_number = '%s'  
                 AND p.piid=s.pers_id  
                 ORDER BY p.proposal_number"""



#--------------------------------------------------------------------------------------------------------#
#--------------------------------------------Functions---------------------------------------------------#
#--------------------------------------------------------------------------------------------------------#

#------------------Function to execute the query and organize the results-------------------#

def run_query(query,proposal,flag):
    # this line takes the query structure you pass into 
    # this function and attaches the proposal number to the query
    query = query%  (int(proposal))  
    cur.execute(query) #executes the query
    result_row = cur.fetchall() #grabs the result
    # the following for loop organizes the result into a python 
    # dictionary for easy parsing into you desired format below
    for result in result_row:
        if flag == "test": #for verifying that the script is doing what you want it to!
            proposal_dict = {'title' : result[0], 
                             'category' : result[1], 
                             'prop_type' : result[2]}
        elif flag == "table": #for generating the table portion of the target page
            proposal_dict = {'abstract': result[0],
                             'title' : result[1],
                             'category' : result[2],
                             'type' : result[3],
                             'prop_num': result[4],
                             'prop_id' : result[5],
                             'app_time' : int(result[6]),
                             'pi_lname' : result[7],
                             'pi_fname' : result[8]}
        elif flag == "A/T": #for generating the table portion of the target page
            proposal_dict = {'abstract': result[0],
                             'title' : result[1],
                             'category' : result[2],
                             'type' : result[3],
                             'prop_num': result[4],
                             'prop_id' : result[5],
                             'pi_lname' : result[6],
                             'pi_fname' : result[7]}
    return proposal_dict # return the dictionary 




#------------------Function to build the target list table-------------------#

# the numbers in curly braces correspond to the number of the 
# ordered items in the .format object that follows the print statement
def table_builder(proposal):

    #
    query = query_table
    flag = "table"
    
    prop_info = run_query(query,proposal,flag)
        #print prop_info['prop_num']
    return """   <tr>
      <td><a href=\"#{0}\">{1}</a></td>
      <td>{2}</td>
      <td>{3}</td>
      <td>{4}</td>
      <td>{5}</td>
      <td>{6}</td>
   </tr>""".format(str(prop_info['prop_num']), 
                   str(prop_info['prop_num']),
                   str(prop_info['category']),
                   str(prop_info['pi_lname']),
                   str(prop_info['type']),
                   str(prop_info['app_time']),
                   str(prop_info['title']))




#-----------------------------------------------------------------------------------------------#
#----------------------------------- function to do the thing  ---------------------------------#
#-----------------------------------------------------------------------------------------------#

def do_the_thing(proplist):
    page_title = proplist
    page_name = proplist.replace(" ","").lower()
    current_list = proposal_lists_dictionary[proplist]
    #print proplist.replace(" ","").lower(), len(proposal_lists_dictionary[proplist])
    
    cycle_num = str(prop_list[0])[0:2]

    #check to see if holding directory for scirpt output files exists
    write_directory = "/data/doh/wyman/targetLists/cycle"+cycle_num+"/output_HTML"
    #if not, create it
    directory_exists = os.path.isdir(write_directory)
    if directory_exists != True:
        call(["mkdir", write_directory])
    

    file = open(write_directory+"/"+page_name+".html", "w")


    file.write("""
    <!DOCTYPE html
            PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
             "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml" lang="en-US" xml:lang="en-US">

    <head>
        <title>Accepted Cycle {0} Observing Proposals</title>
        <meta http-equiv="content-language" content="en-US"/>
        <meta name="keywords" content="SI, Smithsonian, Smithsonian Institute" />
        <meta name="keywords" content="CfA, SAO, Harvard-Smithsonian, Center for Astrophysics" />
        <meta name="keywords" content="HEA, HEAD, High Energy Astrophysics Division" />
        <meta name="title" content="Chandra X-Ray Center"/>
        <meta name="creator" content="SAO-HEA"/>
        <meta name="description" content="SAO High Energy Astrophysics Division"/>
        <meta name="subject" content="SAO High Energy Astrophysics Division"/>
        <meta http-equiv="X-Frame-Options" content="Deny"/>
        <link rel="stylesheet" href="/incl/cxcstyle_hfonly.css" type="text/css" media="screen">
    </head>

    <body>
        <!--#include virtual="/incl/cxcheader.html"-->

    <center>
    <h1>Accepted Cycle {0} Archive Proposals</h1>
    <h2>{1}</h2>
    </center>""".format(str(cycle_num),
                        str(page_title))) 



    #------------------Build the Table-------------------#

    file.write( """<table border=1><tr bgcolor=\"#e6e6ff\">
              <th>Proposal Number</th>
              <th>Subject Category</th>
              <th>PI Name</th>
              <th>Title</th></tr>""")
    for proposal in current_list:
        file.write(table_builder(proposal)
    file.write( "</table>")



    #--------------Build the Abstract Bits---------------#



    query = query_table
    flag = "table"

    for proposal in current_list:
        prop_info = run_query(query,proposal,flag)
        file.write( """<hr>
          <a name=\"{0}\"></a>
          <strong>Subject Category:</strong> {1} <br/><br/>
          <strong>Proposal Number:</strong> {2} <br/><br/>
          <strong>Title:</strong> {3} <br/><br/>
          <strong>PI Name:</strong> {4} {5} <br/><br/>
          <strong>Abstract:</strong> {6} <br/><br/>""".format(str(prop_info['prop_num']), 
                                                              str(prop_info['category']),
                                                              str(prop_info['prop_num']),
                                                              str(prop_info['title']),
                                                              str(prop_info['pi_fname']),
                                                              str(prop_info['pi_lname']),
                                                              str(prop_info['abstract'])))


    file.write("""
    <!--#include virtual="/incl/cxcfooter.html"-->
    </BODY>
    </HTML>""")


    file.close()
#----------------------------------- do the thing end ---------------------------------#


#def test_function(page):
#    print page+"   "+pages[page]

#--------------------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------------------#
#----------------------------------------------Do the thing----------------------------------------------#
#--------------------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------------------#

# set the flag for which query type you want: test, abs, or table
     # use 'test' to verify that the script is working the way you want, 
     # use 'table' to generate the table portion of the target page, and
     # use 'abs' to generate the abstract portion of the target page.



prop_list = raw_input("Archive List?: ")
prop_list = numpy.loadtxt(archive_list, skiprows=0)

username = getpass.getuser()
userpass = getpass.getpass("DB password: ")

conn = sybase.connect('sqlsao',username, userpass) #establish a connection to the dB
cur = conn.cursor()
cur.execute("use proposal") # use the proposal dB


#arrays to be populated by proposals based on subject category (SC)
SC_100_prop_list = []
SC_200_prop_list = []
SC_300_prop_list = []
SC_400_prop_list = []
SC_500_prop_list = []
SC_600_prop_list = []
SC_700_prop_list = []
SC_800_prop_list = []
SC_900_prop_list = []
SC_910_prop_list = []
extra_prop_list = [] #this should always be empty, freak out if not.


for prop in prop_list:
    subj_number = str(prop)[2:5]
    if subj_number == '100':
        SC_100_prop_list.append(prop)
    elif subj_number == '200':
        SC_200_prop_list.append(prop)
    elif subj_number == '300':
        SC_300_prop_list.append(prop)
    elif subj_number == '400':
        SC_400_prop_list.append(prop)
    elif subj_number == '500':
        SC_500_prop_list.append(prop)
    elif (subj_number == '610') or (subj_number == '620'):
        SC_600_prop_list.append(prop)
    elif subj_number == '700':
        SC_700_prop_list.append(prop)
    elif subj_number == '800':
        SC_800_prop_list.append(prop)
    elif subj_number == '900':
        SC_900_prop_list.append(prop)
    elif subj_number == '910':
        SC_910_prop_list.append(prop)
    else:
        extra_prop_list.append(prop)

#check to make sure extra_prop_list is always empty, if it's not, it evaluates to true
if extra_prop_list:
    print "WARNING: possibly uncategorized proposal in extra_prop_list!"



proposal_lists_dictionary = {'ALL PROPOSALS': prop_list,
                             'SOLAR SYSTEM': SC_100_prop_list,
                             'STARS AND WD': SC_200_prop_list,
                             'WD BINARIES AND CV': SC_300_prop_list,
                             'BH AND NS BINARIES': SC_400_prop_list,
                             'SN SNR AND ISOLATED NS': SC_500_prop_list,
                             'NORMAL GALAXIES' : SC_600_prop_list,
                             'ACTIVE GALAXIES AND QUASARS' : SC_700_prop_list,
                             'CLUSTERS OF GALAXIES' : SC_800_prop_list,
                             'EXTRAGALACTIC DIFFUSE EMISSION AND SURVEYS' : SC_900_prop_list,
                             'GALACTIC DIFFUSE EMISSION AND SURVEYS':SC_910_prop_list}#,
                           #  'Theory':theory_list,
                           #  'Archive':archive_list,
                           #  'Large / X-ray Visionary':BPP_list} 

for proplist in proposal_lists_dictionary:
    do_the_thing(proplist)

 #   if page_name == 'SOLAR SYSTEM':
 #       prop_list = solarSystemPropList
 #   elif page_name ==



#for page in pages:
    #print page+"   "+pages[page]
    #test_function(page)
    #do_the_thing(page, prop_list)
    

#if __name__ == "__main__":
 #   main()
