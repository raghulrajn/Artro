################################################################################################
#THIS SCRIPT RUNS REPEATEDLY, POLL THE INVERTER FOR 1ST 42 REGISTERS AND PUSH THE DATA TO CLOUD
#HERE 'copy' module IS USED TO MAKE THE COPY OF trimmedRegArray, SO ALTERING THIS WILL NOT CHANGE DATABASE LIST
#################################################################################################
import sys, copy, time, requests
import rep, datetime, Fault_Records

#######################################################################################################################
#THIS IS USED TO CREATE DATABASE AND TABLES WHERE DATA ARE LOGGED LOCALLY passed as parameters into post_into_database#
#######################################################################################################################

CREATE_INV_TABLE = '''CREATE TABLE IF NOT EXISTS INVERTER(TIMESTAMP INTEGER,PPV REAL,VPV1 REAL,PV1CURR REAL,
                      PV1WATT REAL,VPV2 REAL,PV2CURR REAL,PV2WATT REAL,PAC REAL,FAC REAL,ENERGY_TODAY REAL,
                      ENERGY_TOTAL_HIGH REAL,ENERGY_TOTAL_LOW REAL,TEMPERATURE REAL,IMP_TEMPERATURE REAL)''' 

CREATE_ERROR_TABLE = '''CREATE TABLE IF NOT EXISTS ERROR_TABLE(TIMESTAMP INTEGER,PPV REAL,VPV1 REAL,PV1CURR REAL,
                        PV1WATT REAL,VPV2 REAL,PV2CURR REAL,PV2WATT REAL,PAC REAL,FAC REAL,ENERGY_TODAY REAL,
                        ENERGY_TOTAL_HIGH REAL,ENERGY_TOTAL_LOW REAL,TEMPERATURE REAL,IMP_TEMPERATURE REAL)'''

INSERT_INV_TABLE = '''INSERT INTO INVERTER(TIMESTAMP,PPV,VPV1,PV1CURR,PV1WATT,VPV2,PV2CURR,PV2WATT,PAC,FAC,ENERGY_TODAY,
                      ENERGY_TOTAL_HIGH,ENERGY_TOTAL_LOW,TEMPERATURE,IMP_TEMPERATURE) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'''

INSERT_ERROR_TABLE = '''INSERT INTO ERROR_TABLE(TIMESTAMP,PPV,VPV1,PV1CURR,PV1WATT,VPV2,PV2CURR,PV2WATT,PAC,FAC,ENERGY_TODAY,
            ENERGY_TOTAL_HIGH,ENERGY_TOTAL_LOW,TEMPERATURE,IMP_TEMPERATURE) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'''

#######################################################
#THIS CREATES THE JSON STRING THAT IS SENT TO THE CLOUD
#######################################################
NORM_WAIT_TIME = 30
def payloadGenerator(VAR_NAME,trimmedList):
    tString = {}
    for i in range (len(trimmedList)):
        tString.update({VAR_NAME[i]:trimmedList[i]})
    print("[INFO] Payload Generated...")
    return tString
###################################################################################
#IN THIS FUNCTION INVERTER IS POLLED AND DATA IS POSTED INTO CLOUD
#1)startCommunication is imported from rep
#2)fault_switch is imported from rep
#3)post_into_database posts value into database in both INVERTER and ERROR_TABLE

#THIS FUNCTION
##->POLL INVERTER,
##->POST THE DATA INTO CLOUD,
##->CHECK FOR THE STATUS OF FAULT SWITCH
##->LOG THE DATA INTO DATABASE

#######################################################################################
def main():
    while True:
        chk = rep.startCommunication(0,42,retries = 5)
        if (chk == -1):
            print("[ERROR] Maximum Retries Reached... Retrying ...")
            return -1
        if(chk[0] == 0):#chk[0] is the status of the inverter 0-fault, 1-normal,3-waiting#
            print("[ERROR] Inverter under fault state...")
            return -1
        to_get = [2,3,4,6,7,8,10,12,13,27,28,29,32,41] # register numbers wee needed, refer 'rep module' for name of registers
        trimmedRegArray = []
        for i in range(len(to_get)):
            trimmedRegArray.append(chk[to_get[i]]) 
        dbList = copy.deepcopy(trimmedRegArray)#deep copy is used to make the copy of the list completely immutable#
        print("[INFO] Updating database with values...")
        rep.post_into_database(rep.DB_NAME, INSERT_INV_TABLE,[rep.genTimeStamp(datetime.datetime.now())]+dbList )    
        payloaddict = payloadGenerator(rep.VAR_NAME, trimmedRegArray)
        rep.fault_switch()
        chk = rep.postData(url = rep.url, header=rep.header, payload = payloaddict)
        if(chk == -1):
            print("[ERROR] Posting into Error Database...")
            rep.post_into_database(rep.DB_NAME, INSERT_ERROR_TABLE,[rep.genTimeStamp(datetime.datetime.now())]+dbList )
        elif(chk == 200):
            print("[INFO] Request Successful, Data posted to cloud Successfully...")
        time.sleep(NORM_WAIT_TIME)
        


rep.post_into_database(rep.DB_NAME, CREATE_INV_TABLE)    
rep.post_into_database(rep.DB_NAME, CREATE_ERROR_TABLE)    
                
