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
import copy

json_list = {i: [] for i in range(1, 9)}
json_list_length_limit=10
time_limit=20
start_time=time.time()



def check_minors(json_list):
    result = []
    for minor_key in range(1, 5):  # Check only for minors 1 to 4
        minor_list = json_list.get(minor_key, [])
        if len(minor_list) < json_list_length_limit:
            return None
    return True
        # if len(minor_list) == 10:
        #     # Calculate average RSSI
        #     average_rssi = sum(item['RSSI'] for item in minor_list) / len(minor_list)
        #     # Construct new JSON entry with averaged RSSI
        #     result.append({
        #         'Minor': minor_key,
        #         'RSSI': average_rssi,
        #     })
    # return result
def special_case_answer(json_list):
    len1=len(json_list[1])
    len2=len(json_list[2])
    len3=len(json_list[3])
    len4=len(json_list[4])
    if len1>len4+5 and len1>len2+3 and len1 > len3+3:
        return "C"
    if len4>len1+5 and len4>len2+3 and len4 > len3+3:
        return "A"
    
    return None

def fill_json_list(json_list, limit_length=json_list_length_limit):
    json_list_copy = copy.deepcopy(json_list)
    for key, items in json_list_copy.items():
        if len(items) < limit_length:
            # Calculate the average RSSI value from existing items
            if items:  # Check if there are any existing items to calculate the average
                average_rssi = sum(item['RSSI'] for item in items) / len(items)
            else:
                average_rssi = -1000  # Set RSSI to -200 if no initial values
            
            # Add additional items to fill the list to 10 items
            while len(items) < limit_length:
                items.append({'Major': 1, 'Minor': key, 'RSSI': average_rssi})

    return json_list_copy


def preprocess_msg_to_json(msg):
    encapsulated_json_string = f"[{msg}]"
    # print(encapsulated_json_string)

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
        if item["Major"]==2:
            continue
        minor_key = item["Minor"]
        if item["RSSI"]==0:
            continue
        if minor_key in json_list:
            # Add the new item
            json_list[minor_key].append(item)
            # Ensure the list does not exceed 10 items, discarding the oldest if it does
            if len(json_list[minor_key]) > json_list_length_limit:
                json_list[minor_key].pop(0)
    
def call_by_Ipad(json_list):
    # difine region
    outline_region =[0, 0, 4.3, 11.75]
    A_region = [0, 7.21, 4.3, 11.75]
    B_region = [0, 2.67, 4.3, 7.21]
    C_region = [0, 0, 4.3, 2.67]

    # get x, y
    x_total = 0
    y_total = 0
    Rssi_1 = json_list[1]
    Rssi_2 = json_list[2]
    Rssi_3 = json_list[3]
    Rssi_4 = json_list[4]
    
    if(np.mean([item["RSSI"] for item in Rssi_1 ]) > np.mean([item["RSSI"] for item in Rssi_2 ]) and np.mean([item["RSSI"] for item in Rssi_1 ]) > np.mean([item["RSSI"] for item in Rssi_3 ]) and np.mean([item["RSSI"] for item in Rssi_1 ]) > np.mean([item["RSSI"] for item in Rssi_4 ])):
        return "C"
    if(np.mean([item["RSSI"] for item in Rssi_4 ]) > np.mean([item["RSSI"] for item in Rssi_1 ]) and np.mean([item["RSSI"] for item in Rssi_3 ]) > np.mean([item["RSSI"] for item in Rssi_1 ])):
        return "A"


    for i in range(len(Rssi_1)):
        Rssi_list = [Rssi_1[i], Rssi_2[i], Rssi_3[i], Rssi_4[i]]
        x, y = Indoor_Localization_for_iBeacon_Using_Propergation_Model(Rssi_list)
        print(f"x{i}:{x:.2f}, y{i}:{y:.2f}")
        
        x_total += x
        y_total += y

    x_final = x_total / len(Rssi_1)
    y_final = y_total / len(Rssi_1)
    print(f"avg x:{x_final:.2f}, y:{y_final:.2f}")


    # determine the location in which region 
    if x_final >= outline_region[0] and x_final <= outline_region[2] and y_final >= outline_region[1] and y_final <= outline_region[3]:
        if x_final >= A_region[0] and x_final <= A_region[2] and y_final >= A_region[1] and y_final <= A_region[3]:
            return "A"
        elif x_final >= B_region[0] and x_final <= B_region[2] and y_final >= B_region[1] and y_final <= B_region[3]:
            return "B"
        elif x_final >= C_region[0] and x_final <= C_region[2] and y_final >= C_region[1] and y_final <= C_region[3]:
            return "C"
    else:
        if y_final > 7.21:
            return "A"
        elif y_final < 0:
            return "C"
        else:
            return "B"
        # return "outside the region"





def Indoor_Localization_for_iBeacon_Using_Propergation_Model(Rssi_list, TxPower=-59, n=2.0):
    # RSSI = RSSI value
    # TxPower = RSSI value at 1 meter
    # n = signal propagation exponent
    
    # define the input RSSI value
    for i in Rssi_list:
        if i["Minor"] == 1:
            Rssi1 = i["RSSI"]
        elif i["Minor"] == 2:
            Rssi2 = i["RSSI"]
        elif i["Minor"] == 3:
            Rssi3 = i["RSSI"]
        elif i["Minor"] == 4:
            Rssi4 = i["RSSI"]
    my_Rssi_List  = [[Rssi1,1], [Rssi2,2], [Rssi3,3], [Rssi4,4]]

    # define the region 
    '''
    outline_region =[0, 0, 4.3, 11.75]
    A_region = [0, 7.21, 4.3, 11.75]
    B_region = [0, 2.67, 4.3, 7.21]
    C_region = [0, 0, 4.3, 2.67]
    '''

    # define the ibeacon location
    iBeacon_list = [[2.21, 0], [4.3, 5.7], [4.3, 7.8], [2.64, 11.75]]
    # iBeacon_1 = [2.21, 0]
    # iBeacon_2 = [4.3, 5.7]
    # iBeacon_3 = [4.3, 7.8]
    # iBeacon_4 = [2.64, 11.75]

    # define the distance between the ibeacon
    d = np.zeros((4, 4))
    d[0][1] = d[1][0] = np.sqrt((iBeacon_list[0][0] - iBeacon_list[1][0]) ** 2 + (iBeacon_list[0][1] - iBeacon_list[1][1]) ** 2)
    d[0][2] = d[2][0] = np.sqrt((iBeacon_list[0][0] - iBeacon_list[2][0]) ** 2 + (iBeacon_list[0][1] - iBeacon_list[2][1]) ** 2)
    d[0][3] = d[3][0] = np.sqrt((iBeacon_list[0][0] - iBeacon_list[3][0]) ** 2 + (iBeacon_list[0][1] - iBeacon_list[3][1]) ** 2)
    d[1][2] = d[2][1] = np.sqrt((iBeacon_list[1][0] - iBeacon_list[2][0]) ** 2 + (iBeacon_list[1][1] - iBeacon_list[2][1]) ** 2)
    d[1][3] = d[3][1] = np.sqrt((iBeacon_list[1][0] - iBeacon_list[3][0]) ** 2 + (iBeacon_list[1][1] - iBeacon_list[3][1]) ** 2)
    d[2][3] = d[3][2] = np.sqrt((iBeacon_list[2][0] - iBeacon_list[3][0]) ** 2 + (iBeacon_list[2][1] - iBeacon_list[3][1]) ** 2)
    


    # calculate the distance
    distance_list = []
    for rssi in my_Rssi_List:
        # print(rssi[0], TxPower, n)
        distance = 10 ** ((TxPower - rssi[0]) / (10 * n))
        # print(distance)
        distance_list.append(distance)

    # distance1 = 10 ** ((abs(Rssi1) - TxPower) / (10 * n))
    # distance2 = 10 ** ((abs(Rssi2) - TxPower) / (10 * n))
    # distance3 = 10 ** ((abs(Rssi3) - TxPower) / (10 * n))
    # distance4 = 10 ** ((abs(Rssi4) - TxPower) / (10 * n))

    # print("distance1 = {:.2f} || distance2 = {:.2f} || distance3 = {:.2f} || distance4 = {:.2f}".format(distance1, distance2, distance3, distance4))
    
    #****************************************************************************************************************************************************#


    # 三角定位演算法，把rssi最小的拔掉，剩下三個做三角定位
    index_min = 5
    min_Rssi = 0
    for i in range(len(my_Rssi_List)) :
        if my_Rssi_List[i][0] < min_Rssi:
            min_Rssi = my_Rssi_List[i][0]
            index_min = i
    
    
    
    answer_coordinate = []
    # check the circles are overlapped or not
    for i in range(4):
        for j in range(i,4):
            if(i != j and i != index_min and j != index_min):
                x_c, y_c, x_d, y_d = calculate_the_two_point_coordinate_of_circle(iBeacon_list[i][0], iBeacon_list[i][1], distance_list[i], iBeacon_list[j][0], iBeacon_list[j][1], distance_list[j], d[i][j])               
                for k in range(4):
                    if(k != i and k != j and k != index_min):
                        if(abs(np.sqrt((x_c - iBeacon_list[k][0]) ** 2 + (y_c - iBeacon_list[k][1]) ** 2) - distance_list[k]) < 
                           abs(np.sqrt((x_d - iBeacon_list[k][0]) ** 2 + (y_d - iBeacon_list[k][1]) ** 2) - distance_list[k])):
                            answer_coordinate.append([x_c, y_c])
                        else : 
                            answer_coordinate.append([x_d, y_d])
                           
    # 找中心點
    x_sum = 0
    y_sum = 0
    for i in answer_coordinate:
        x_sum += i[0]
        y_sum += i[1]
    x_final = x_sum / len(answer_coordinate)
    y_final = y_sum / len(answer_coordinate)
    return x_final, y_final


def calculate_the_two_point_coordinate_of_circle(x_a, y_a, r_a, x_b, y_b, r_b, d_ab):
    # for point C and D
    # caculate d_ae : the distance between point A and E
    d_ae = (r_a ** 2 - r_b ** 2 + d_ab ** 2) / (2 * d_ab)

    # calculate d_ce : the distance between point C and E
    d_ce = np.sqrt(abs(r_a ** 2 - d_ae ** 2))

    # calculate the coordinate of point E
    x_e = x_a + d_ae * (x_b - x_a) / d_ab
    y_e = y_a + d_ae * (y_b - y_a) / d_ab

    # calculate the slope of the line AB
    if(x_a == x_b):
        k_ab = 1e-14
    else:
        k_ab = (y_b - y_a) / (x_b - x_a)

    # calculate the slope of the line CD
    k_cd = -1 / k_ab

    # calculate the coordinate of point C and D
    angle = np.arctan(k_cd)

    x_c = x_e + d_ce * np.cos(angle)
    y_c = y_e + d_ce * np.sin(angle)
    x_d = x_e - d_ce * np.cos(angle)
    y_d = y_e - d_ce * np.sin(angle)

    return x_c, y_c, x_d, y_d

       

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
                    print(f"Minor {minor_key} queue len={len(records)}")
                    # for record in records:
                    #     print(record)
                    print()  # Add a newline for better separation between minors
                minors_flag=check_minors(json_list)
                current_time=time.time()-start_time
                if minors_flag!=None:
                    answer=call_by_Ipad(json_list=json_list)
                    send_back_msg=f"{answer}"
                    send_back_msg=send_back_msg.encode(self.code)
                    self.conn.send(send_back_msg)
                else:
                    if current_time<time_limit:
                        #check and return 
                        send_back_msg=f"wait"
                        send_back_msg=send_back_msg.encode(self.code)
                        self.conn.send(send_back_msg)
                    else:
                        print(f"timeout ({time_limit}s) \nstart to compute position")
                        special_answer=special_case_answer(json_list)
                        if special_answer!=None:
                            send_back_msg=f"{special_answer}"
                            send_back_msg=send_back_msg.encode(self.code)
                            self.conn.send(send_back_msg)
                            print(f"special_answer: {send_back_msg}" )
                            continue
                        if current_time>=time_limit:
                            filled_json_list=fill_json_list(json_list)
                            print(f"Filled json list:\n{filled_json_list}")
                            answer=call_by_Ipad(json_list=filled_json_list)
                            print(f"Answer: {answer}")
                            send_back_msg=f"{answer}"
                            send_back_msg=send_back_msg.encode(self.code)
                            self.conn.send(send_back_msg)
                            continue

                            
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
    


