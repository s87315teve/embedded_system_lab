#coding=utf-8
#websocket example
import socket
import threading
import time
import os
import sys
import traceback
import argparse
import json
import numpy as np

json_list = {i: [] for i in range(1, 9)}


def check_and_average_minors(json_list):
    result = []
    for minor_key in range(1, 5):  # Check only for minors 1 to 4
        minor_list = json_list.get(minor_key, [])
        if len(minor_list) != 10:
            return None
        if len(minor_list) == 10:
            # Calculate average RSSI
            average_rssi = sum(item['RSSI'] for item in minor_list) / len(minor_list)
            # Construct new JSON entry with averaged RSSI
            result.append({
                'Minor': minor_key,
                'RSSI': average_rssi,
            })
    return result

def preprocess_msg_to_json(msg):
    encapsulated_json_string = f"[{msg}]"
    print(encapsulated_json_string)

    # Attempt to parse the newly structured JSON
    try:
        corrected_data_json = json.loads(encapsulated_json_string)
        # print(corrected_data_json)
        # Flatten the list of lists into a single list
        flattened_data = [item for sublist in corrected_data_json for item in sublist]
        return flattened_data
    except json.JSONDecodeError as e:
        # Handle JSON decoding errors
        error_message = str(e)
        encapsulated_json_string, error_message


def add_to_category_with_discard(data_json):
    global json_list
    if data_json==None:
        print("data_json is None")
        return
    for item in data_json:
        minor_key = item["Minor"]
        if item["RSSI"]==0:
            continue
        if minor_key in json_list:
            # Add the new item
            json_list[minor_key].append(item)
            # Ensure the list does not exceed 10 items, discarding the oldest if it does
            if len(json_list[minor_key]) > 10:
                json_list[minor_key].pop(0)
    
def Indoor_Localization_for_iBeacon_Using_Propergation_Model(Rssi_list,TxPower=-59, n=2.0):
    # RSSI = RSSI value
    # TxPower = RSSI value at 1 meter
    # n = signal propagation exponent

    for i in Rssi_list:
        if i["Minor"] == 1:
            Rssi1 = i["RSSI"]
        elif i["Minor"] == 2:
            Rssi2 = i["RSSI"]
        elif i["Minor"] == 3:
            Rssi3 = i["RSSI"]
        elif i["Minor"] == 4:
            Rssi4 = i["RSSI"]


    # define the region 
    outline_region =[0, 0, 4.3, 11.75]
    A_region = [0, 7.21, 4.3, 11.75]
    B_region = [0, 2.67, 4.3, 7.21]
    C_region = [0, 0, 4.3, 2.67]

    # define the ibeacon location
    iBeacon_1 = [2.21, 0]
    iBeacon_2 = [4.3, 5.7]
    iBeacon_3 = [4.3, 7.8]
    iBeacon_4 = [2.64, 11.75]

    # define the distance between the ibeacon
    # 建二維陣列
    d = np.zeros((4, 4))
    d[0][1] = d[1][0] = np.sqrt((iBeacon_1[0] - iBeacon_2[0]) ** 2 + (iBeacon_1[1] - iBeacon_2[1]) ** 2)
    d[0][2] = d[2][0] = np.sqrt((iBeacon_1[0] - iBeacon_3[0]) ** 2 + (iBeacon_1[1] - iBeacon_3[1]) ** 2)
    d[0][3] = d[3][0] = np.sqrt((iBeacon_1[0] - iBeacon_4[0]) ** 2 + (iBeacon_1[1] - iBeacon_4[1]) ** 2)
    d[1][2] = d[2][1] = np.sqrt((iBeacon_2[0] - iBeacon_3[0]) ** 2 + (iBeacon_2[1] - iBeacon_3[1]) ** 2)
    d[1][3] = d[3][1] = np.sqrt((iBeacon_2[0] - iBeacon_4[0]) ** 2 + (iBeacon_2[1] - iBeacon_4[1]) ** 2)
    d[2][3] = d[3][2] = np.sqrt((iBeacon_3[0] - iBeacon_4[0]) ** 2 + (iBeacon_3[1] - iBeacon_4[1]) ** 2)
    


    # calculate the distance



    distance1 = 10 ** ((abs(Rssi1) - TxPower) / (10 * n))
    distance2 = 10 ** ((abs(Rssi2) - TxPower) / (10 * n))
    distance3 = 10 ** ((abs(Rssi3) - TxPower) / (10 * n))
    distance4 = 10 ** ((abs(Rssi4) - TxPower) / (10 * n))

    print("distance1 = {:.2f} || distance2 = {:.2f} || distance3 = {:.2f} || distance4 = {:.2f}".format(distance1, distance2, distance3, distance4))

    # Cosine Law

    # for iBeacon_1
    cosine_1 = (d[0][1] ** 2 + distance1 ** 2 - distance2 ** 2) / (2 * d[0][1] * distance1)
    x1, y1 =  iBeacon_1[0] + distance1 * (cosine_1), iBeacon_1[1] + distance1 * (np.sqrt(1 - cosine_1 ** 2))
    x2, y2 = iBeacon_1[0] + distance1 * (cosine_1), iBeacon_1[1] - distance1 * (np.sqrt(1 - cosine_1 ** 2))
    print("x1 = {:.2f}, y1 = {:.2f}, calculate the distance from (x1,y1) to Beacon1 : {:.2f})".format(x1, y1, np.sqrt((x1 - iBeacon_1[0]) ** 2 + (y1 - iBeacon_1[1]) ** 2))) 
    print("x2 = {:.2f}, y2 = {:.2f}, calculate the distance from (x2,y2) to Beacon1 : {:.2f})".format(x2, y2, np.sqrt((x2 - iBeacon_1[0]) ** 2 + (y2 - iBeacon_1[1]) ** 2)))

    if(abs(np.sqrt((x1 - iBeacon_1[0]) ** 2 + (y1 - iBeacon_1[1]) ** 2) - distance1) < abs(np.sqrt((x2 - iBeacon_1[0]) ** 2 + (y2 - iBeacon_1[1]) ** 2) - distance1)):
        x = x1
        y = y1
    else:
        x = x2
        y = y2
    
    # for iBeacon_2

    # determine the region of the user
    if x >= outline_region[0] and x <= outline_region[2] and y >= outline_region[1] and y <= outline_region[3]:
        if x >= A_region[0] and x <= A_region[2] and y >= A_region[1] and y <= A_region[3]:
            return "A"
        elif x >= B_region[0] and x <= B_region[2] and y >= B_region[1] and y <= B_region[3]:
            return "B"
        elif x >= C_region[0] and x <= C_region[2] and y >= C_region[1] and y <= C_region[3]:
            return "C"
        else:
            return "outside the region"
    else:
        return "outside the region"
       

class multi_sock(threading.Thread):
    def __init__(self, conn, addr, code, buffer_size, timeout):
        threading.Thread.__init__(self)
        self.conn=conn
        self.addr=addr
        self.code=code
        self.buffer_size=buffer_size
        self.timeout=timeout
        print("{} connected to server".format(addr))
        
                    
    def run(self):
        global json_list
        if self.timeout!=None:
            self.conn.settimeout(self.timeout)
        while True:
            try:
                msg=self.conn.recv(self.buffer_size)
                if not msg:
                    print("client {} is gone ".format(self.addr))
                    print("connection closed")
                    self.conn.close()
                    break
                msg=msg.decode(self.code)
                # print(msg)
                data_json = preprocess_msg_to_json(msg)
                # print("data_josn:\n")
                # print(data_json)
                # print("=======")
                add_to_category_with_discard(data_json)
                # print("recv: ",msg)
                for minor_key, records in json_list.items():
                    print(f"Minor {minor_key}:")
                    for record in records:
                        print(record)
                    print()  # Add a newline for better separation between minors
                input_json_list=check_and_average_minors(json_list)
                if input_json_list!=None:
                    answer=Indoor_Localization_for_iBeacon_Using_Propergation_Model(Rssi_list=input_json_list)
                    send_back_msg=f"{answer}"
                    send_back_msg=send_back_msg.encode(self.code)
                    self.conn.send(send_back_msg)
                
                else:
                    #check and return 
                    send_back_msg=f"wait"
                    send_back_msg=send_back_msg.encode(self.code)
                    self.conn.send(send_back_msg)
                
                

            except socket.timeout:
                print("{} socket timeout".format(self.addr))
                print("connection closed")
                self.conn.close()
                break
            except Exception as e:
                error_class = e.__class__.__name__ #取得錯誤類型
                detail = e.args[0] #取得詳細內容
                cl, exc, tb = sys.exc_info() #取得Call Stack
                lastCallStack = traceback.extract_tb(tb)[-1] #取得Call Stack的最後一筆資料
                fileName = lastCallStack[0] #取得發生的檔案名稱
                lineNum = lastCallStack[1] #取得發生的行號
                funcName = lastCallStack[2] #取得發生的函數名稱
                errMsg = "File \"{}\", line {}, in {}: [{}] {}".format(fileName, lineNum, funcName, error_class, detail)
                print(errMsg)
                self.conn.close()
                print("{} connection closed".format(self.addr))
                break

class TCP_server():
    def __init__(self, host="127.0.0.1", port=6000, code="utf-8", buffer_size=1024, timeout=None):
        try:
            self.host=host
            self.port=port
            self.code=code
            self.buffer_size=buffer_size
            self.timeout=timeout
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #建立socket
            self.client_list=[]
        except Exception as e:
            error_class = e.__class__.__name__ #取得錯誤類型
            detail = e.args[0] #取得詳細內容
            cl, exc, tb = sys.exc_info() #取得Call Stack
            lastCallStack = traceback.extract_tb(tb)[-1] #取得Call Stack的最後一筆資料
            fileName = lastCallStack[0] #取得發生的檔案名稱
            lineNum = lastCallStack[1] #取得發生的行號
            funcName = lastCallStack[2] #取得發生的函數名稱
            errMsg = "File \"{}\", line {}, in {}: [{}] {}".format(fileName, lineNum, funcName, error_class, detail)
            print(errMsg)

    def start(self):
        try:

            self.sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1) #讓socket可以reuse
            bind_addr=(self.host, self.port)
            self.sock.bind(bind_addr) #self.addr
            self.sock.listen()
            print("server start")
            print("server is listening to {}".format(bind_addr))
        except Exception as e:
            error_class = e.__class__.__name__ #取得錯誤類型
            detail = e.args[0] #取得詳細內容
            cl, exc, tb = sys.exc_info() #取得Call Stack
            lastCallStack = traceback.extract_tb(tb)[-1] #取得Call Stack的最後一筆資料
            fileName = lastCallStack[0] #取得發生的檔案名稱
            lineNum = lastCallStack[1] #取得發生的行號
            funcName = lastCallStack[2] #取得發生的函數名稱
            errMsg = "File \"{}\", line {}, in {}: [{}] {}".format(fileName, lineNum, funcName, error_class, detail)
            print(errMsg)
            print("server failed to start")
        try:
            while True:
                conn, addr = self.sock.accept()
                self.client_list.append(multi_sock(conn=conn, addr=addr, code=self.code, buffer_size=self.buffer_size, timeout=self.timeout))
                self.client_list[-1].start()
        except Exception:
            pass
            
    
class TCP_client():
    def __init__(self, host="127.0.0.1", port=6000, code="utf-8", buffer_size=1024):
        try:
            self.host=host
            self.port=port
            self.code=code
            self.buffer_size=buffer_size
            #self.timeout=timeout
            self.addr = (self.host, self.port)
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #建立TCP socket
            self.sock.connect(self.addr) #self.addr
            print("connected to server")
        except Exception as e:
            error_class = e.__class__.__name__ #取得錯誤類型
            detail = e.args[0] #取得詳細內容
            cl, exc, tb = sys.exc_info() #取得Call Stack
            lastCallStack = traceback.extract_tb(tb)[-1] #取得Call Stack的最後一筆資料
            fileName = lastCallStack[0] #取得發生的檔案名稱
            lineNum = lastCallStack[1] #取得發生的行號
            funcName = lastCallStack[2] #取得發生的函數名稱
            errMsg = "File \"{}\", line {}, in {}: [{}] {}".format(fileName, lineNum, funcName, error_class, detail)
            print(errMsg)
            print("connection failed ")
    def send_msg(self, msg=""):
        try:
            msg=msg.encode(self.code)
            self.sock.send(msg)
        except Exception as e:
            error_class = e.__class__.__name__ #取得錯誤類型
            detail = e.args[0] #取得詳細內容
            cl, exc, tb = sys.exc_info() #取得Call Stack
            lastCallStack = traceback.extract_tb(tb)[-1] #取得Call Stack的最後一筆資料
            fileName = lastCallStack[0] #取得發生的檔案名稱
            lineNum = lastCallStack[1] #取得發生的行號
            funcName = lastCallStack[2] #取得發生的函數名稱
            errMsg = "File \"{}\", line {}, in {}: [{}] {}".format(fileName, lineNum, funcName, error_class, detail)
            print(errMsg)


class UDP_server():
    def __init__(self, host="127.0.0.1", port=6000, code="utf-8", buffer_size=1024):
        try:
            self.host=host
            self.port=port
            self.code=code
            self.buffer_size=buffer_size
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #建立UDP socket
        except Exception as e:
            error_class = e.__class__.__name__ #取得錯誤類型
            detail = e.args[0] #取得詳細內容
            cl, exc, tb = sys.exc_info() #取得Call Stack
            lastCallStack = traceback.extract_tb(tb)[-1] #取得Call Stack的最後一筆資料
            fileName = lastCallStack[0] #取得發生的檔案名稱
            lineNum = lastCallStack[1] #取得發生的行號
            funcName = lastCallStack[2] #取得發生的函數名稱
            errMsg = "File \"{}\", line {}, in {}: [{}] {}".format(fileName, lineNum, funcName, error_class, detail)
            print(errMsg)

    def start(self):
        try:

            self.sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1) #讓socket可以reuse
            bind_addr=(self.host, self.port)
            self.sock.bind(bind_addr) #self.addr
            print("server start")
            print("server is listening to {}".format(bind_addr))
        except Exception as e:
            error_class = e.__class__.__name__ #取得錯誤類型
            detail = e.args[0] #取得詳細內容
            cl, exc, tb = sys.exc_info() #取得Call Stack
            lastCallStack = traceback.extract_tb(tb)[-1] #取得Call Stack的最後一筆資料
            fileName = lastCallStack[0] #取得發生的檔案名稱
            lineNum = lastCallStack[1] #取得發生的行號
            funcName = lastCallStack[2] #取得發生的函數名稱
            errMsg = "File \"{}\", line {}, in {}: [{}] {}".format(fileName, lineNum, funcName, error_class, detail)
            print(errMsg)
            print("server failed to start")
        while True:
            while True:
                try:
                    msg, addr=self.sock.recvfrom(self.buffer_size)
                    if not msg:
                        print("no msg from {}",addr)
                        break
                    msg=msg.decode(self.code)
                    print("recv from {} : {}".format(addr,msg))
                except Exception as e:
                    error_class = e.__class__.__name__ #取得錯誤類型
                    detail = e.args[0] #取得詳細內容
                    cl, exc, tb = sys.exc_info() #取得Call Stack
                    lastCallStack = traceback.extract_tb(tb)[-1] #取得Call Stack的最後一筆資料
                    fileName = lastCallStack[0] #取得發生的檔案名稱
                    lineNum = lastCallStack[1] #取得發生的行號
                    funcName = lastCallStack[2] #取得發生的函數名稱
                    errMsg = "File \"{}\", line {}, in {}: [{}] {}".format(fileName, lineNum, funcName, error_class, detail)
                    print(errMsg)
                    print("sleep 1s and restart socket")
                    time.sleep(1)
                    break
class UDP_client():
    def __init__(self, host="127.0.0.1", port=6000, code="utf-8", buffer_size=1024):
        try:
            self.host=host
            self.port=port
            self.code=code
            self.buffer_size=buffer_size
            self.addr = (self.host, self.port)
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #建立UDP socket
            #self.sock.connect(self.addr) #self.addr
            print("connected to server")
        except Exception as e:
            error_class = e.__class__.__name__ #取得錯誤類型
            detail = e.args[0] #取得詳細內容
            cl, exc, tb = sys.exc_info() #取得Call Stack
            lastCallStack = traceback.extract_tb(tb)[-1] #取得Call Stack的最後一筆資料
            fileName = lastCallStack[0] #取得發生的檔案名稱
            lineNum = lastCallStack[1] #取得發生的行號
            funcName = lastCallStack[2] #取得發生的函數名稱
            errMsg = "File \"{}\", line {}, in {}: [{}] {}".format(fileName, lineNum, funcName, error_class, detail)
            print(errMsg)
            print("connection failed ")
    def send_msg(self, msg=""):
        try:
            msg=msg.encode(self.code)
            self.sock.sendto(msg,self.addr)
        except Exception as e:
            error_class = e.__class__.__name__ #取得錯誤類型
            detail = e.args[0] #取得詳細內容
            cl, exc, tb = sys.exc_info() #取得Call Stack
            lastCallStack = traceback.extract_tb(tb)[-1] #取得Call Stack的最後一筆資料
            fileName = lastCallStack[0] #取得發生的檔案名稱
            lineNum = lastCallStack[1] #取得發生的行號
            funcName = lastCallStack[2] #取得發生的函數名稱
            errMsg = "File \"{}\", line {}, in {}: [{}] {}".format(fileName, lineNum, funcName, error_class, detail)
            print(errMsg)
def run(opt):
    if opt.mode=="TCP_server":
        server=TCP_server(host=opt.host, port=opt.port, code=opt.code, buffer_size=opt.buffer, timeout=opt.timeout)
        server.start()
    elif opt.mode=="TCP_client":
        client=TCP_client(host=opt.host, port=opt.port, code=opt.code, buffer_size=opt.buffer)
        client.send_msg("connection success")
        msg=input("input msg: ")
        while msg!="exit":
            client.send_msg(msg)
            msg=input("input msg: ")
    elif opt.mode=="UDP_server":
        server=UDP_server(host=opt.host, port=opt.port, code=opt.code, buffer_size=opt.buffer)
        server.start()
    elif opt.mode=="UDP_client":
        client=UDP_client(host=opt.host, port=opt.port, code=opt.code, buffer_size=opt.buffer)
        client.send_msg("connection success")
        msg=input("input msg: ")
        while msg!="exit":
            client.send_msg(msg)
            msg=input("input msg: ")
    else:
        print("argument illegal, please restart this program")



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", "-m", type=str, default=None, help="select mode")
    parser.add_argument("--host", type=str,  default="127.0.0.1", help="set host IP")
    parser.add_argument("--port", "-p", type=int, default=6000, help="set host port")
    parser.add_argument("--code", "-c", type=str, default="utf-8", help="set how to encode/decode")
    parser.add_argument("--buffer", "-b", type=int, default=1024, help="setbuffer size")
    parser.add_argument("--timeout", "-t", type=int, default=None, help="set timeout")
    opt = parser.parse_args()
    print("your option:")
    print(opt)
    run(opt)
    


