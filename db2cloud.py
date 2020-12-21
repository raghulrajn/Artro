import time, sys
import rep

SELECT_ERROR_TABLE = "SELECT * from ERROR_TABLE"

def main():
    rows = rep.post_into_database(rep.DB_NAME, SELECT_ERROR_TABLE)
    if(rows == -1):
        print("[INFO] Error Table empty / previously uploaded...")
        return -1
    print(rows)    
    tup_len = len(rows[1])
    row_len = len(rows)
    list1= []
    tString = {}
    for i in range(tup_len-1):
        for j in range(row_len):
            list1.append({"value" : rows[j][i+1],"timestamp":rows[j][0]})
        tString.update({rep.VAR_NAME[i]:list1})
        list1 = []
    print(tString)
    chk = rep.postData(rep.url, rep.header, tString, 5)
    if(chk == -1):
        print("[ERROR] Internet Failure, Couldnt upload values to cloud...")
        return -1
    rep.post_into_database(rep.DB_NAME, "DROP TABLE IF EXISTS ERROR_TABLE")
    print("[INFO] Values uploaded and table deleted...")

                
