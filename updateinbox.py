import mysql.connector
import os
import datetime
import time

unicodeToAsciiMap = {u'\u2019':"'", u'\u2018':"`", u'\xf1': "n",
                     u'\u2013': "-"}

class MySqlDBConn:
    def __init__(self, server, dbname, user, password):
        self.infoLog("init")
        self.counter = 0
        self.config = {
            'host': server,
            'port': 3306,
            'database': dbname,
            'user': user,
            'password': password,
            'charset': 'utf8',
            'use_unicode': True,
            'get_warnings': True,
        }
        self.infoLog(self.config)
        self.cnx = mysql.connector.Connect(**self.config)
        self.cur = self.cnx.cursor()

    def exec_query (self, query_str):
        self.infoLog("[EXEC] %s" % query_str)
        self.cur.execute(query_str)
        self.cnx.commit()

    def fetch_query (self, query_str):
        self.infoLog("[FETCH] %s" % query_str)
        self.cur.execute(query_str)
        rows = self.cur.fetchall()
        return rows



    def convertToTimestamp (self, epoch_time ):
        return  datetime.datetime.fromtimestamp(epoch_time).strftime('%Y-%m-%d %H:%M:%S')

    def infoLog(self, data):
        try:
            print data
        except:
            print "unicode error"


def updateBaseOnUDH ( DB , table):
    udh_list = DB.fetch_query("SELECT UDH FROM %s WHERE UDH <> ''" % table)
    udh_substring = []
    for udh in udh_list:
        udh_temp = udh[0][:-2]
        if udh_temp not in udh_substring:
            udh_substring.append(udh_temp)

    for udh in udh_substring:
        udh_data = DB.fetch_query("SELECT ID,UDH,TextDecoded FROM " + table + " WHERE UDH LIKE '" +  udh + "%' ORDER BY UDH")
        print udh_data
        if len(udh_data) == 1:
            print "only one text message here"
            continue
        text_data = ""
        for udh_d in udh_data:
            print udh_d
            text_data += udh_d[2]
        try:
            print "text_data:", text_data
        except:
            print "unicode  error"
        text_data = unicodeToAscii(text_data)
        text_data = text_data.replace("'","")
        text_data = text_data.replace('"',"")
        first_id = udh_data[0][0]
        print "first_id : ", first_id
        update_sql = "UPDATE %s SET TextDecoded='%s',UDH='' WHERE ID=%d" % (table, text_data, first_id)
        try:
            print "update_sql :" , update_sql
        except:
            print "unicode error"
        DB.exec_query(update_sql)
        # get the remaining ids   
        other_elements = udh_data[1:]
        for elem in other_elements:
            delete_sql = "DELETE FROM %s WHERE ID=%d" % (table, elem[0])
            print "deleting ..." ,delete_sql
            DB.exec_query(delete_sql)


def unicodeToAscii(inStr):
    inStr = inStr.replace("'", "")
    try:
        return str(inStr)
    except:
        pass
    outStr = ""
    for i in inStr:
        try:
            outStr = outStr + str(i)
        except:
            if unicodeToAsciiMap.has_key(i):
                outStr = outStr + unicodeToAsciiMap[i]
            else:
                try:
                    print "unicodeToAscii: add to map:", i, repr(i), "(encoded as _)"
                except:
                    print "unicodeToAscii: unknown code (encoded as _)", repr(i)
                outStr = outStr + "_"
    return outStr



def updateBaseOnTime ( DB ):
    sms_list = DB.fetch_query("SELECT ID,SenderNumber,ReceivingDateTime,TextDecoded FROM inbox")
    last_sender = ""
    last_recieve = ""
    counter = 0
    SMS_HASH = {}
    SMS_IDS = []
    for sms in sms_list:
        if last_recieve == "":
            last_sender = sms[1]
            last_recieve = sms[2]
            continue
        if last_sender == sms[1] :
            current_time = sms[2]
            time_delta = current_time - last_recieve
            print "time_delta :", time_delta.seconds
            if time_delta.seconds < 120:
                print "this is still part of the message %d" % counter
                print "sender : %s" % sms[1]
                print "time : %s" % sms[2]
                print "message : %s" % sms[3]
                temp_id = "%s-%d" % (sms[1], counter)
                if temp_id in SMS_HASH:
                    SMS_HASH[temp_id].append(sms)
                else:
                    SMS_HASH[temp_id] = []
                    SMS_HASH[temp_id].append(sms)
                if temp_id not in SMS_IDS:
                    SMS_IDS.append(temp_id)
            else:
                counter = counter + 1
        else:
            counter = counter + 1

        last_recieve = current_time
        last_sender = sms[1]

        for temp_id in SMS_IDS:
            print SMS_HASH[temp_id]
            if len(SMS_HASH[temp_id]) > 1:
                text_data = ""
                for sms in SMS_HASH[temp_id]:
                    text_data += sms[3]
                print "!!!!! text_data %s" % text_data 


def deleteAdv (DB):
    DB.exec_query("DELETE FROM inbox WHERE SenderNumber='SMART'")
    DB.exec_query("DELETE FROM inbox WHERE SenderNumber='2256'")
    DB.exec_query("DELETE FROM inbox WHERE SenderNumber='8888'")
    DB.exec_query("DELETE FROM inbox WHERE SenderNumber='2123'")
    DB.exec_query("DELETE FROM inbox WHERE SenderNumber='MERALCO'")
    DB.exec_query("DELETE FROM inbox WHERE SenderNumber='2363'")
    DB.exec_query("DELETE FROM inbox WHERE SenderNumber='AutoLoadMAX'")
    #DB.exec_query("DELETE FROM inbox WHERE SenderNumber='+639175991688'")
    

def isTimeDeltaInsideBracket (DB):
    retval = False
    sms_list = DB.fetch_query("SELECT ID,SenderNumber,ReceivingDateTime,TextDecoded FROM inbox ORDER BY ID DESC LIMIT 1")
    print sms_list[0]
    ReceivingDateTime = sms_list[0][2]
    print "ReceivingDateTime: ", ReceivingDateTime
    today = datetime.datetime.now() 
    time_delta = today - ReceivingDateTime
    print "time_delta.minutes " , time_delta.seconds
    if time_delta.seconds > 2 and time_delta.seconds < 600:
        print "inside the 3 to 10 minutes mark"
        return True 
    return retval


def convertArrToJson (messages):

    message_data = []
    for m in messages:
        temp = {}
        #temp['UpdatedInDB'] = m[0]
        temp['ReceivingDateTime'] = m[1]
        #temp['Text'] = m[2]
        temp['SenderNumber'] = m[3]
        #temp['Coding'] = m[4]
        temp['UDH'] = m[5]
        #temp['SMSCNumber'] = m[6]
        #temp['Class'] = m[7]
        temp['TextDecoded'] = m[8]
        temp['ID'] = m[9]
        temp['RecipientID'] = m[10]
        temp['Processed'] = m[11]
        temp['textCount'] =len(temp['TextDecoded'])
        message_data.append(temp)
    return message_data


def combineMessages (DB, messageGroup):
    finalText = ""
    table = "inbox"
    for m in messageGroup:
        finalText += m['TextDecoded']
    finalText = unicodeToAscii(finalText)
    finalText = finalText.replace("'", "")
    print "finalText: " , finalText
    update_sql = "UPDATE %s SET TextDecoded='%s',UDH='' WHERE ID=%d" % (table, finalText, messageGroup[0]['ID'])
    print update_sql
    DB.exec_query(update_sql)
    other_elements = messageGroup[1:]

    for elem in other_elements:
        delete_sql = "DELETE FROM %s WHERE ID=%d" % (table, elem['ID'])
        print "deleting ..." ,delete_sql
        DB.exec_query(delete_sql)




def cleanEachData (DB, RecipientID):
    messages  = DB.fetch_query("Select * from ( select * from inbox WHERE RecipientID='%s' ORDER BY ID DESC LIMIT 50) sub ORDER BY ID ASC" % RecipientID)
    messages = convertArrToJson (messages)
    last_data = {}
    possible_group = []
    last_senderNumber = ""
    flag = 0 
    count = 0 
    for m in messages:
        print m
        if m['textCount'] == 153:
            # check the next message if it has the same sender number
            if messages[count + 1]['SenderNumber'] == m['SenderNumber']:
                print "found unfinished message!!!!!!!!!!!!!!!"
                possible_group.append(m)
                flag = 1 
            else:
                 # this is the last part of the message
                possible_group.append(m)
                combineMessages (DB, possible_group)
                # emtyp possible group
                possible_group = []
                # set the last sender to empty
                last_senderNumber = ""


        elif m['textCount'] < 153:
            # check if there is last possible group of messages
            if len(possible_group) > 0:
                 # this is the last part of the message
                possible_group.append(m)
                combineMessages (DB, possible_group)
                # emtyp possible group
                possible_group = []
                # set the last sender to empty
                last_senderNumber = ""

            else:
                print "no last group message"
        last_senderNumber = m['SenderNumber']
        count = count + 1






time.sleep(2)
DB = MySqlDBConn('localhost', 'smsd', 'root','root')
# delay for 15 seconds




if isTimeDeltaInsideBracket(DB):
    deleteAdv(DB)
    updateBaseOnUDH (DB,"inbox")
    cleanEachData (DB, 'smart')
    cleanEachData (DB, 'globe')


#updateBaseOnUDH (DB,"sentitems")

