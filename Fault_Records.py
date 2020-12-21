##THIS SCRIPT IS TRIGGERED WHEN FAULT SWITCH IS ON
##IMPORT REP MODULE HERE

import datetime
import rep

###################################################################################
#THIS DICT CONTAINS THE NAME AND FAULT CODE OF ALL THE POSSIBLE FAULTS IN INVERTER
#####################################################################################

error_dict  = {"100":"Fan Malfunction",
               "103":"EEPROM Failure",
               "104":"Firmware Version Unmatched",
               "105":"Communication Error",
               "101":"Sampling Difference Error",
               "107":"Relay Fault",
               "117":"Bus voltage is too High",
               "121":"Communication Error",
               "122":"Bus Voltage is too High",
               "104":"Model Error",
               "119":"GFCI module check fails",
               "125":"PV IP insulation impdance is low",
               "128":"PV voltage is over 1000v",
               "126":"Leakage current is too high",
               "127":"Output DC current is too high",
               "129":"Grid Voltage is out of range",
               "130":"Grid frequency is out of range",}

#############################################################
#THIS FUNCTION SPLITS ARRAY 'l' INTO EQUAL ARRAYS
#######################################################

def divide_chunks(l, n):
    for i in range(0, len(l), n): 
        yield l[i:i + n]

###########################################################################################################
#HERE FAULT RECORDS ARE SENT TO THE CLOUD
#MODBUS TIME FORMAT INTO HUMAN READABLE FORMAT
# xxxx (4digit number / may be 5)-> MODBUS FORMAT OF TIME THAT REPRESENTS (YEAR,MONTH),(DAY,HOURS),(MINUTES,SECONDS) ()->COMBINED IN BINARY FORMAT
# first two x --> represents year
# second two x --> represents month same for other binary pairs
# for getting year leftshift xx by 8 bits and add offset ((xxxx)>>8)+2000
#for getting month perform BITWISE AND on the number by 255
###################################################################################################
def main():
    data = rep.startCommunication(90,25, 5)
    if(data == -1):
        print("[INFO] Fault table not recieved...")
        return -1
    to_send ={}
    fault =[]
    x = list(divide_chunks(data, 5))
    for j in range(0,len(x)):
        t = datetime.datetime(((x[j][1]>>8)+2000),(x[j][1]&255),(x[j][2]>>8),(x[j][2]&255),(x[j][3]>>8),(x[j][3]&255))
        fault.append({"value":x[j][4]*0.1,"timestamp":rep.genTimeStamp(t),"context":{"fault_type":error_dict[str(x[j][0])]}})
    to_send = {"fault":fault}
    chk = rep.postData(rep.url, rep.header, to_send, 2)
    if(chk == -1):
        print("[ERROR] Error posting fault to cloud...")
        return -1
    print(chk)
    return 0
