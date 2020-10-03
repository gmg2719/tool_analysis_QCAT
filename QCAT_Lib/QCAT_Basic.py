#needed by python 2.x ( > 2.6)
from __future__ import print_function

import logging
import sys
# needed by QCAT client
import os
import win32com.client

# needed to extract logTimeList
import fnmatch
import re,datetime
from os.path import abspath, exists
import time

# great module to draw Visible output
# https://plot.ly/python/getting-started/
# import plotly
# import plotly.graph_objs as go

import pprint
from pyparsing import *

from math import sin, cos, sqrt, atan2, radians

# Test function to print out all list items in list recursively
def printOutAllListItems(curList):
    if isinstance(curList, list):
        for var in curList:
            if isinstance(var, list):
                printOutAllListItems(var)
            else:
                print (var)


# Function to print out the value of strItem in a well formatted list
# curList: <List> List to find out the value
# strItem: <string> matching string used to find the value
# length: <int> the number of list elements after the matching string of strItem
# example: printOutListItemValue(curList,"featureGroupIndRel10-v1060",4) will return '00000000 00101000 00000000 00000000'B
def printOutListItemValue(curList, strItem, length=1):
    ret_var = None
    if isinstance(curList, list):
        for var in curList:
            #pprint.pprint(var)
            if isinstance(var, list):
                ret_var = printOutListItemValue(var, strItem)

                if ret_var!=None:
                    #print ret_var + '_2'
                    break;

            else:
                #pprint.pprint(var)
                if var == strItem:
                    index = curList.index(strItem)
                    ret_var = curList[index+length]
                    #print strItem + '_1 = ' + ret_var
                    return ret_var

    return ret_var

def printOutFGIValue(curList, strItem, length=1):
    ret_var = None
    if isinstance(curList, list):
        for var in curList:
            #pprint.pprint(var)
            if isinstance(var, list):
                ret_var = printOutFGIValue(var, strItem)

                if ret_var!=None:
                    #print ret_var + '_2'
                    break;

            else:
                #pprint.pprint("hi:" + var)
                if var == strItem:
                    #print var
                    index = curList.index(strItem)
                    ret_var = ' '.join(curList[index+length:index+length+4])
                    #print strItem + '_1 = ' + ret_var
                    return ret_var

    return ret_var
# use qcat client to merge multiple logs into single
# input: a string with all logs path combined together
#        could be qmdl, isf, dlf, qmdl2, even mixed. for now will support only 1 format at a time.
# output: path to save the merged log.
#        could be isf, dlf, TXT; details see QCAT6 User Guide <<80-V1233-6 T>>
def qcat_merge_log(targetLogPath, mergedLogPath, filterList = None):
    # this requires Admin or Elevated permission
    #print ("Make sure you have Admin or Elevated permission if you see error like below:")
    #print ("pywintypes.com_error: (-2146959355, 'Server execution failed', None, None)")

    # invoke QCAT in invisible mode.
    qcatApp = win32com.client.Dispatch("QCAT6.Application")
    qcatApp.Visible = 0

    logger1 = logging.getLogger('qcat_merge_log')

    if qcatApp.OpenLog(targetLogPath) != 1:
        logger1.error("Error0: %s open failed!", targetLogPath)
        logger1.error(qcatApp.LastError)
        qcatapp = None
        exit()
    else:
        logger1.debug("%s Created!", targetLogPath)

    filter = qcatApp.PacketFilter;
    if filter == 0:
        logger1.error ("ERROR3: unable to retrieve the Filter Object.\n")
        exit()
    filter.SetAll(0)

    for subfilter in filterList:
        filter.Set(subfilter, 1)
    filter.Commit();

    mergeResult = 0
    if '.isf' in mergedLogPath.lower():
        mergeResult = qcatApp.SaveAsISF(mergedLogPath)
    if '.txt' in mergedLogPath.lower():
        mergeResult = qcatApp.SaveAsTXT(mergedLogPath)
    if '.dlf' in mergedLogPath.lower():
        mergeResult = qcatApp.SaveAsDLF(mergedLogPath)

    if (mergeResult == -1):
        logger1.error("Error1: ")
        logger1.error(qcatApp.LastError)
        exit()
    else:
        logger1.debug(mergedLogPath + " saved with parsed content!")

    qcatApp.closeFile()
    qcatapp = None
# Use qcat to parse log file into TXT
# logpath: path of log to be parsed
# filterList: special mask IDs in a line to be filtered out, example: 0x147E
# parsedFile: output txt
def qcat_parse_log(logpath, filterList, parsedFile):
    qcatApp = win32com.client.Dispatch("QCAT6.Application")
    qcatApp.Visible = 0

    logger1 = logging.getLogger('qcat_parse_log')
    if qcatApp.OpenLog(logpath) != 1:
        logger1.error("Error2:")
        logger1.error(qcatApp.LastError)
        qcatapp = None
        exit()

    filter = qcatApp.PacketFilter;
    if filter == 0:
        logger1.error ("ERROR3: unable to retrieve the Filter Object.\n")
        exit()
    filter.SetAll(0)

    for subfilter in filterList:
        filter.Set(subfilter, 1)
    filter.Commit();

    print ("Parsing messages...")
    if(qcatApp.Process(logpath,parsedFile,0,0)!=1):
        logger1.error ("ERROR4:")
        logger1.error (qcatApp.LastError)
    else:
        print ("Complete!!!\n" + parsedFile + " generated!")
        #print ("ParsedFiltered TXT saved to %s\n"%parsedFile)

    qcatApp.closeFile()
    qcatapp = None

# Use qcat to parse log file into TXT
# logpath: path of log to be parsed
# filterList: special mask IDs in a line to be filtered out, example: 0x147E
# parsedFile: output txt
def qcat_filter_log(logpath, filterList, parsedFile):
    qcatApp = win32com.client.Dispatch("QCAT6.Application")
    qcatApp.Visible = 0

    logger1 = logging.getLogger('qcat_parse_log')
    if qcatApp.OpenLog(logpath) != 1:
        logger1.error("Error2:")
        logger1.error(qcatApp.LastError)
        qcatapp = None
        exit()

    filter = qcatApp.PacketFilter;
    if filter == 0:
        logger1.error ("ERROR3: unable to retrieve the Filter Object.\n")
        exit()
    filter.SetAll(0)

    for subfilter in filterList:
        filter.Set(subfilter, 1)
    filter.Commit();

    print ("Filter messages...")

    if(qcatApp.SaveAsISF(parsedFile)!=1):
        logger1.error ("ERROR4:")
        logger1.error (qcatApp.LastError)
    else:
        print ("Complete!!!\n" + parsedFile + " generated!")
        #print ("ParsedFiltered TXT saved to %s\n"%parsedFile)

    qcatApp.closeFile()
    qcatapp = None

def qcat_export_text(logpath, analyzer, parsedFile):
    """Export grid to txt file"""
    if analyzer == None:
        # analyzer = ("LTE", "Time Grids")
        analyzer = ";LTE;Time Grids;LTE Pdsch Stat Indication vs. Time"

    qcatApp = win32com.client.Dispatch("QCAT6.Application")
    qcatApp.Visible = 0

    logger1 = logging.getLogger('qcat export text')
    if qcatApp.OpenLog(logpath) != 1:
        logger1.error("Error2:")
        logger1.error(qcatApp.LastError)
        qcatapp = None
        exit()

    worksp = qcatApp.Workspace
    worksp.SelectOutput(";", 0)
    worksp.SelectOutput(analyzer, 1)
    worksp.ExportToText(parsedFile, ",")  # Export with comma delimiter
    # worksp.ExportToText(parsedFile, "\t") # Export with TAB delimiter
    qcatApp.closeFile()
    qcatapp = None

def qcat_export_grids(logpath, analyzer, parsedFile):
    """export all grids in analyzer to a file"""
    if analyzer == None:
        # analyzer = ("LTE", "Time Grids")
        analyzer = ";LTE;Time Grids;LTE Pdsch Stat Indication vs. Time"

    qcatApp = win32com.client.Dispatch("QCAT6.Application")
    qcatApp.Visible = 0

    logger1 = logging.getLogger('qcat export grids ...')
    if qcatApp.OpenLog(logpath) != 1:
        logger1.error("Error2:")
        logger1.error(qcatApp.LastError)
        qcatapp = None
        exit()

    worksp = qcatApp.Workspace

    for grid in analyzer:
        a = grid.strip()
        worksp.SelectOutput(";", 0)
        worksp.SelectOutput(grid.strip(), 1)
        worksp.ExportToText(parsedFile, ",")  # Export with comma delimiter
        # worksp.ExportToText(parsedFile, "\t") # Export with TAB delimiter
    qcatApp.closeFile()
    qcatapp = None

def qcat_export_excel(logpath, analyzer, parsedFile):
    """Export grid to excel file"""
    if analyzer == None:
        # analyzer = ("LTE", "Time Grids")
        analyzer = ";LTE;Time Grids;LTE Pdsch Stat Indication vs. Time"

    qcatApp = win32com.client.Dispatch("QCAT6.Application")
    qcatApp.Visible = 0

    logger1 = logging.getLogger('qcat export excel')
    if qcatApp.OpenLog(logpath) != 1:
        logger1.error("Error2:")
        logger1.error(qcatApp.LastError)
        qcatapp = None
        exit()

    worksp = qcatApp.Workspace
    worksp.SelectOutput(";", 0)
    worksp.SelectOutput(analyzer, 1)
    worksp.ExportToExcel(parsedFile, 0)
    qcatApp.closeFile()
    qcatapp = None

def qcat_export_bitmap(logpath, analyzer, parsedFile):
    """Plot to bitmap file"""
    if analyzer == None:
        analyzer = ";LTE;Time Grids;Physical Grid;LTE DCI Info vs. Time"
        # analyzer = "LTE;Time Plots;LTE Phy/RLC/PDCP DL Plot"

    qcatApp = win32com.client.Dispatch("QCAT6.Application")
    qcatApp.Visible = 0

    logger1 = logging.getLogger('qcat export bitmap')
    if qcatApp.OpenLog(logpath) != 1:
        logger1.error("Error2:")
        logger1.error(qcatApp.LastError)
        qcatapp = None
        exit()

    worksp = qcatApp.Workspace
    worksp.SelectOutput(";", 0)
    worksp.SelectOutput(analyzer, 1)
    worksp.ExportToBitmap(parsedFile)
    qcatApp.closeFile()
    qcatapp = None

def qcat_export_all(logpath, parsedFile):
    """Export all packets in logfile"""
    if not logpath:
        logging.getLogger("No input log!!!")
        return

    qcatApp = win32com.client.Dispatch("QCAT6.Application")
    qcatApp.Visible = 0

    qcatApp.Process(logpath, parsedFile, 0, 1)
    qcatApp.closeFile()
    qcatapp = None

def qcat_get_field(logpath, packet_id, filter_str, parsedFile):
    """Loop through packets, searching for specified fields"""
    qcatApp = win32com.client.Dispatch("QCAT6.Application")
    qcatApp.Visible = 0

    logger1 = logging.getLogger('qcat filters str')
    if qcatApp.OpenLog(logpath) != 1:
        logger1.error("This log does not exist!!")
        logger1.error(qcatApp.LastError)
        qcatapp = None
        exit()

    first_package = qcatApp.FirstPacket
    if first_package == None:
        logger1.error(qcatApp.LastError)
        qcatApp = None
        exit()

    else:
        with open(parsedFile, 'w') as f:
            while first_package:
                if first_package.Type == packet_id and first_package.FieldExists(filter_str):
                    f.write(first_package.GetFieldArray(filter_str))
                if first_package.Next() == None:
                    break

    qcatApp.closeFile()
    qcatapp = None



# test for another method
def qcat_parse_per_log_package(logpath, filterID, filterStr, parsedFile):
    qcatApp = win32com.client.Dispatch("QCAT6.Application")
    qcatApp.Visible = 0

    logger1 = logging.getLogger('qcat_parse_per_log_package')
    if qcatApp.OpenLog(logpath) != 1:
        logger1.error("Error5:")
        logger1.error(qcatApp.LastError)
        qcatapp = None
        exit()

    myLogPackage = qcatApp.FirstPacket;
    if (myLogPackage == None):
        logger1.error(qcatApp.LastError)
        qcatApp = None
        exit()
    else:
        while myLogPackage != None :
            currentLogPackageID = myLogPackage.Type
            #logger1.debug("%x",currentLogPackageID)
            #logger1.debug("%s", myLogPackage.TimestampAsString)
            if ( currentLogPackageID == filterID) and (filterStr in myLogPackage.Text) :
                fparseFile = open(parsedFile,"a")
                fparseFile.write(myLogPackage.Text)
                fparseFile.close()

                logger1.debug("%s", myLogPackage.GetField(filterStr))

            if myLogPackage.Next() == False:
                break

    qcatApp.closeFile()
    qcatApp = None

# filter special lines contain a list of words, example: ["l_PgaGain", "q_AdcAmpIp1mV"]
def findandsavelogs(substr, infile, outfile):
    #lines = filter(substr, open(infile))
    #lines = filter(lambda x: substr in x, open(infile))
    finfile = open(infile,'r')
    foutfile = open(outfile, 'w')
    finfileLines = finfile.readlines()

    for curline in finfileLines:
        for checkStr in substr:
            if curline.find(checkStr) != -1:
                foutfile.writelines(curline)

    print (outfile +" generated!")

    finfile.close()
    foutfile.close()


def getTimeListFromLog(logfile):
    fLogfile = open(logfile, 'r')
    TimeList = list()
    if fLogfile == False:
        exit()

    fLoglines = fLogfile.readlines()
    for fLogline in fLoglines:
        for time_1 in fLogline.split(' '):
            if ':' in time_1:
                TimeList.append(time_1)

    fLogfile.close()
    return TimeList

# find out words contains time format string, example: '20:56:13.945',
# and return the list of time
def getTimeFromLog(logfile, id):
    logger1 = logging.getLogger('getTimeFromLog')
    fLogfile = open(logfile, 'r')
    timeList = list()
    if fLogfile == False:
        logger1.error("Failed to open "+logfile)
        exit()

    logger1.debug(id)

    fLoglines = fLogfile.readlines()
    for fLogline in fLoglines:
        for items in fLogline.split(' '):
            #logger1.debug("%s",items)
            if id in items:
                timeList.append(items)
    fLogfile.close()
    return timeList

# find out words contains a value after a name example: q_AdcAmpIp1mV = 111,
# and return the list of value
def getSpecialPointFromLog(logfile, id):
    logger1 = logging.getLogger('getSpecialPointFromLog')
    fLogfile = open(logfile, 'r')
    retList = list()
    if fLogfile == False:
        logger1.error("Failed to open "+logfile)
        exit()

    logger1.debug(id)

    fLoglines = fLogfile.readlines()
    for fLogline in fLoglines:
            if id in fLogline:
                retList.append(float(fLogline.strip('\n').strip('\t').split(' ')[-1]))

    fLogfile.close()
    return retList
