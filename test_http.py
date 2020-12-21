import time, rep, Fault_Records, json
import db2cloud, main_logger
import paho.mqtt.client as mqttClient


def logging():
    
    chk = rep.startCommunication(0,1,2)
    if (chk == -1):
        sleep = {"inverter-state":{"value":4, "context":{"state":"Sleep-Mode"}}}
        chk = rep.postData(rep.url, rep.header, sleep, 3)
        if(chk == -1):
            print("[ERROR] Unable to update inverter state in Cloud...")
        print("[ERROR] MODBUS Connection Error..." )
        return -1
    
    elif(chk[0]==0):
        s = {"inverter-state": {"value": chk[0], "context":{"state":rep.STATE[str(chk[0])]}}}
        chk = rep.postData(rep.url, rep.header, s, 3)
        
        if(chk == -1):
            print("[ERROR] Unable to update inverter state in Cloud...")
        
        print("[INFO] Posting previous error values...")
        chk = db2cloud.main()
        if (chk == -1):
            return -1
    elif(chk[0] == 1 or chk[0] == 3):
        s = {"inverter-state": {"value": chk[0], "context":{"state":rep.STATE[str(chk[0])]}}}
        chk = rep.postData(rep.url, rep.header, s, 3)
        if(chk == -1):
            print("[ERROR] Unable to update inverter state in Cloud...")
        print("[INFO] Calling Main Logging Function...")
        time.sleep(10)
        main_logger.main()
        print ("[INFO] Posting Todays energy generated data...")
        chk = energyPost()
        
        if(chk == -1):
            return -1
        return 0

def energyPost():
    rows = rep.post_into_database(rep.DB_NAME,"SELECT TIMESTAMP,ENERGY_TODAY from INVERTER")
    data = {"energy_today" :{"value":(rows[len(rows)-1])[1],"timestamp":(rows[len(rows)-1])[0]}}
    chk = rep.postData(rep.url, rep.header, data, 2)
    print("[INFO]Energy today posted into cloud...")
    if(chk == -1):
        print("[ERROR] Unable to post Energy data to cloud... Retrying...")
        return -1
    return 0

while True:
    logging()
    print("waiting")
    time.sleep(600)


    
