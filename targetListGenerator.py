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

#TEST QUERY
query_test = """SELECT  
                   p.title,  
                   p.category_descrip,   
                   p.type 
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


#ABSTRACT BIT QUERY for the mini tables (only observations with time)
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





#------------------------------------------------------
# 0.1 Function to assign subject categories based on proposal numbers
#-------------------------------------------------------

#  also organizes each prop_list passed to it into python dictionaries for querying later


def assign_subject_categories(prop_list):

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

    # do the organizing
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
    return proposal_lists_dictionary


#----------SC Function End-----------#




#---------------------------------------------------------#
# 0.2 Function to make directories to drop generated HTML files in
#---------------------------------------------------------#

write_directory = ""
cycle_num = 0

def make_directories(prop_list):
    #page_title = prop_list
    #page_name = prop_list.replace(" ","").lower()
    #current_list = proposal_lists_dictionary[prop_list]
    # #print proplist.replace(" ","").lower(), len(proposal_lists_dictionary[proplist])
    
    global cycle_num
    cycle_num = str(prop_list[0])[0:2]

    #check to see if holding directory for script output files exists
    #global write_directory
    
   
    global write_directory
    write_directory = "/data/doh/wyman/targetLists/test/cycle"+cycle_num
    #if not, create it
    directory_exists = os.path.isdir(write_directory)
    if directory_exists != True:
        call(["mkdir", write_directory])




#---------------------------------------------------------
# 1.1 Execute the query and organize the results TIME proposals
#---------------------------------------------------------

def run_time_query(query,proposal):
    query = query_table
    # this line takes the query structure you pass into 
    # this function and attaches the proposal number to the query
    query = query%  (int(proposal))  
    cur.execute(query) #executes the query
    result_row = cur.fetchall() #grabs the result
    # the following for loop organizes the result into a python 
    # dictionary for easy parsing into you desired format below
    for result in result_row:
        proposal_dict = {'abstract': result[0],
                         'title' : result[1],
                         'category' : result[2],
                         'type' : result[3],
                         'prop_num': result[4],
                         'prop_id' : result[5],
                         'app_time' : int(result[6]),
                         'pi_lname' : result[7],
                         'pi_fname' : result[8]}
    return proposal_dict # return the dictionary 


#---------------------------------------------------------#
# 1.2 Execute the query and organize the results AT proposals
#---------------------------------------------------------#

def run_AT_query(proposal):
    query = at_query_table
    # this line takes the query structure you pass into 
    # this function and attaches the proposal number to the query
    query = query%  (int(proposal))  
    cur.execute(query) #executes the query
    result_row = cur.fetchall() #grabs the result
    # the following for loop organizes the result into a python 
    # dictionary for easy parsing into you desired format below
    for result in result_row:
        proposal_dict = {'abstract': result[0],
                         'title' : result[1],
                         'category' : result[2],
                         'type' : result[3],
                         'prop_num': result[4],
                         'prop_id' : result[5],
                         'pi_lname' : result[6],
                         'pi_fname' : result[7]}
    return proposal_dict # return the dictionary 

   
#---------------------------------------------------------#
# 1.3 build the target list table
#---------------------------------------------------------#


def target_list_with_time(proplist):
    
    file = open(write_directory+"/"+page_name+".html", "a")
    file.write( """<table border=1><tr bgcolor=\"#e6e6ff\">
              <th>Proposal Number</th>
              <th>Subject Category</th>
              <th>PI Name</th>
              <th>Type</th>
              <th>Time (ks)</th>
              <th>Title</th></tr>""")
    for proposal in current_list:
        file.write(table_builder(proposal))

    file.write( "</table>")
    file.close()

#---------------------------------------------------------#
# 1.4 build the target list table (AT)
#---------------------------------------------------------#

def target_list_without_time(proplist):
    file.write( """<table border=1><tr bgcolor=\"#e6e6ff\">
              <th>Proposal Number</th>
              <th>Subject Category</th>
              <th>PI Name</th>
              <th>Title</th></tr>""")
    for proposal in current_list:
        file.write(table_builder(proposal))

    file.write( "</table>")




#---------------------------------------------------------#
# 2.1 Function to build the target list table (time)
#---------------------------------------------------------#

# the numbers in curly braces correspond to the number of the 
# ordered items in the .format object that follows the print statement
def table_builder(proposal):
    query = query_table
    
    prop_info = run_time_query(query,proposal)
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

#---------------------------------------------------------#
# 2.2 Function to build the target list table (AT)
#---------------------------------------------------------#


#---------------------------------------------------------#
# 2.3 build the details/abstract bits
#---------------------------------------------------------#
def proposal_details(proplist):
    query = query_table
    #flag = "table"

    file = open(write_directory+"/"+page_name+".html", "a")

    for proposal in current_list:
        prop_info = run_time_query(query,proposal)
        file.write( """<hr>
          <a name=\"{0}\"></a>
          <strong>Subject Category:</strong> {1} <br/><br/>
          <strong>Proposal Number:</strong> {2} <br/><br/>
          <strong>Title:</strong> {3} <br/><br/>
          <strong>Type:</strong> {4} <strong>Total Time (ks):</strong> {5} <br/><br/>
          <strong>PI Name:</strong> {6} {7} <br/><br/>
          <strong>Abstract:</strong> {8} <br/><br/>""".format(str(prop_info['prop_num']), 
                                                              str(prop_info['category']),
                                                              str(prop_info['prop_num']),
                                                              str(prop_info['title']),
                                                              str(prop_info['type']),
                                                              str(prop_info['app_time']),
                                                              str(prop_info['pi_fname']),
                                                              str(prop_info['pi_lname']),
                                                              str(prop_info['abstract'])))
        #--------------Build the Teeny Tables---------------#
        file.write( """<table border=1>
              <tr bgcolor=\"#e6e6ff\">
                 <th>R.A.</th>
                 <th>Dec.</th>
                 <th>Target Name</th>
                 <th>Det.</th>
                 <th>Grating</th>
                 <th>Exp. Time (ks)</th>
              </tr>""")  

        cur.execute(query_abs_table%  (int(proposal)))
        target_info = cur.fetchall()
        for result in target_info:
           # if type(result[3]) == NoneType:
           #     print target_info
            target_dict = {'ra': result[0],
                           'dec' : result[1],
                           'targname' : result[2],
                           'app_expo_time' : result[3],#int(result[3]), why did i recast as int?
                           'grating_id': result[4],
                           'inst_id' : result[5]}
            #print RA_converter(target_dict['ra']),DEC_converter(target_dict['dec'])
            file.write( """          <tr>
                 <td>{0}</td>
                 <td>{1}</td>
                 <td>{2}</td>
                 <td>{3}</td>
                 <td>{4}</td>
                 <td>{5}</td>
              </tr>""".format(str(RA_converter(target_dict['ra'])),
                              str(DEC_converter(target_dict['dec'])),
                              str(target_dict['targname']),
                              str(instrument_ID(target_dict['inst_id'])),
                              str(gratings_ID(target_dict['grating_id'])),
                              str(target_dict['app_expo_time'])))
        file.write("</table>")

    file.close()


#---------------------------------------------------------#
# 3.1 Function to Convert RA (deg) to H.M.S
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
# 3.2 Function to convert decimal Dec to degrees, minutes, seconds Dec
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
# 3.3 Function to identify instruments
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
# 3.4 Function to identify gratings#
#---------------------------------------------------------#

def gratings_ID(n):
    if n == 1:
        return "None"
    elif n == 2:
        return "HETG"        
    elif n == 3:
        return "LETG"  



#---------------------------------------------------------#
# 4.1 Function to open the page
#---------------------------------------------------------#

page_name = ""
current_list = []

def open_file(proplist):
    page_title = proplist
    
    global page_name
    page_name = proplist.replace(" ","").lower()
    global current_list
    current_list = proposal_lists_dictionary[proplist]
    #print proplist.replace(" ","").lower()#, len(proposal_lists_dictionary[proplist])


    #print write_directory#+"/"+page_name+".html"

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
    <h1>Accepted Cycle {0} Observing Proposals</h1>
    <h2>{1}</h2>
    </center>""".format(str(cycle_num),
                        str(page_title))) 

   # if page_name == "allproposals":
    #make_SC_menu_bar(proplist)

    #file = open(write_directory+"/"+page_name+".html", "a")
    #print prop_list
    #stop()
    if prop_list == 'ALL PROPOSALS':
        file.write("""<table><tr bgcolor=\"#e6e6ff\">""")
        for page in proposal_lists_dictionary:
            if page != 'ALL PROPOSALS':
                file.write("""<td><a href=\"{0}.html\">{1}</a></td>""".format(str(page.replace(" ","").lower()),str(page)))
        file.write("""</tr></table>""")
    else: file.write("""<a href="allproposals.html">Back to All Proposals</a>""")
    
    file.close()




#---------------------------------------------------------#
# 4.2 Function to make menu bar to SC-specific pages
#---------------------------------------------------------#

#def make_SC_menu_bar(prop_list):
#    file = open(write_directory+"/"+page_name+".html", "a")
#    print prop_list
#    #stop()
#    if prop_list == 'ALL PROPOSALS':
#        file.write("""<table><tr bgcolor=\"#e6e6ff\">""")
#        for page in proposal_lists_dictionary:
#            if page != 'ALL PROPOSALS':
#                file.write("""<td><a href=\"{0}.html\">{1}</a></td>""".format(str(page.replace(" ","").lower()),str(page)))
#        file.write("""</tr></table>""")
#    else: file.write("""<a href="allproposals.html">Back to All Proposals</a>""")
#    file.close()



#---------------------------------------------------------#
# 4.3 function to close the page
#---------------------------------------------------------#

#def close_file():

 #   file.write("""
 #   <!--#include virtual="/incl/cxcfooter.html"-->
 #   </BODY>
 #   </HTML>""")

  #  file.close()




#------------------------------------------------------------------------#
#------------------------- Function List --------------------------------#
#------------------------------------------------------------------------#

# 0.0 Large scale organization
#   0.1 assign_subject_categories
#   0.2 make_directories
# 1.0 Run Queries and Organize the results
#   1.1 run_time_query
#   1.2 run_AT_query
#   1.3 target_list_with_time
#   1.4 target_list_without_time
# 2.0 Build the pages
#   2.1 table_builder
#   2.2 table_builder_AT
#   2.3 proposal_details
# 3.0 Little functions
#   3.1 RA_converter
#   3.2 DEC_converter
#   3.3 instrument_ID
#   3.4 gratings_ID
# 4.0 Page Specific functions
#   4.1 open_file
#   4.2 make_SC_menu_bar
#   4.3 close_file
#
#





#--------------------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------------------#
#----------------------------------------------Do the thing----------------------------------------------#
#--------------------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------------------#




all_prop_list = raw_input("All Proposals List?: ")
all_prop_list = numpy.loadtxt(all_prop_list, skiprows=0)


username = getpass.getuser()
userpass = getpass.getpass("DB password: ")

conn = sybase.connect('sqlsao',username, userpass) #establish a connection to the dB
cur = conn.cursor()
cur.execute("use proposal") # use the proposal dB



#---------------------------------------------------#
#---------------- Build Main Pages -----------------#
#---------------------------------------------------#

#make proposal_lists_dictionary

proposal_lists_dictionary = assign_subject_categories(all_prop_list)

make_directories(all_prop_list)

for prop_list in proposal_lists_dictionary:
    open_file(prop_list)
    target_list_with_time(prop_list)
    proposal_details(prop_list)

exit()



#make_SC_menu_bar(all_prop_list) #only for all_prop_list and maybe BPP

#target_list_with_time()


#make_page()

#close_file()



#---------------------------------------------------#
#--------------- Build Theory Pages ----------------#
#---------------------------------------------------#

#theory_list = raw_input("Theory List?: ")
#theory_list = numpy.loadtxt(theory_list, skiprows=0)

#proposal_lists_dictionary = assign_subject_categories(theory_list)
#make directory here, no function call




#---------------------------------------------------#
#--------------- Build Archive Pages ---------------#
#---------------------------------------------------#

#archive_list = raw_input("Archive List?: ")
#archive_list = numpy.loadtxt(archive_list, skiprows=0)



#---------------------------------------------------#
#----------------- Build BPP Pages -----------------#
#---------------------------------------------------#

#BPP_list = raw_input("BPP List?: ")
#BPP_list = numpy.loadtxt(BPP_list, skiprows=0)




#if __name__ == "__main__":
 #   main()
