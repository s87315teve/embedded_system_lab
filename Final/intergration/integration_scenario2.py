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
import sympy as sp
import copy

json_list = {i: [] for i in range(1, 9)}
json_list_length_limit=10
time_limit=20
start_time=time.time()


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
                items.append({'Major': 2, 'Minor': key, 'RSSI': average_rssi})

    return json_list_copy

def get_input(json_list):
    # Initialize the list to store average RSSI values
    average_rssi = []
    # Calculate the average RSSI for each minor or fill with -1000 if the minor key does not exist
    for minor_value in range(1, 9):
        if json_list[minor_value]:
            rssi_values = [item['RSSI'] for item in json_list[minor_value]]
            average_rssi.append(np.mean(rssi_values))
        else:
            average_rssi.append(-1000)
    return average_rssi

class ParticleFilter:
    def __init__(self, num_particles=1000):
        self.num_particles = num_particles
        self.particles = None
        self.weights = None
        self.beacons = None
        self.x_min = None
        self.y_min = None
        self.x_max = None
        self.y_max = None

    def initialize_particles(self):
        if self.beacons is None:
            raise ValueError("Beacons must be set before initializing particles.")
        self.x_min, self.y_min = np.min(self.beacons, axis=0) - 1
        self.x_max, self.y_max = np.max(self.beacons, axis=0) + 1
        particles = np.empty((self.num_particles, 2))
        particles[:, 0] = np.random.uniform(self.x_min, self.x_max, self.num_particles)
        particles[:, 1] = np.random.uniform(self.y_min, self.y_max, self.num_particles)
        self.particles = particles
        self.weights = np.ones(self.num_particles) / self.num_particles

    @staticmethod
    def rssi_to_distance(rssi):
        tx_power = -59  # dBm (example value for 1 meter distance)
        n = 2.4  # Path loss exponent (example value for free space)
        distance = 10 ** ((tx_power - np.array(rssi)) / (10 * n))
        return distance

    @staticmethod
    def distance_to_rssi(distance):
        tx_power = -59  # dBm (example value for 1 meter distance)
        n = 2.4  # Path loss exponent (example value for free space)
        rssi = tx_power - 10 * n * np.log10(distance)
        return rssi

    def set_beacons(self, beacons):
        self.beacons = np.array(beacons)
        self.initialize_particles()

    def predict(self):
        # In this example, we assume no movement, so particles remain the same
        self.particles = np.clip(self.particles, [self.x_min, self.y_min], [self.x_max, self.y_max])
        return self.particles

    def update(self, distances):
        if self.particles is None:
            raise ValueError("Particles must be initialized before updating.")
        self.weights.fill(1.0)
        for i, beacon in enumerate(self.beacons):
            beacon_dist = np.linalg.norm(self.particles - beacon, axis=1)
            self.weights *= np.exp(-0.5 * ((beacon_dist - distances[i]) ** 2))
        self.weights += 1e-300  # to avoid division by zero
        self.weights /= np.sum(self.weights)  # normalize

    def resample(self):
        indices = np.random.choice(np.arange(self.num_particles), size=self.num_particles, p=self.weights)
        self.particles = self.particles[indices]
        self.weights = self.weights[indices]
        self.weights /= np.sum(self.weights)

    def run(self, rssi_values, iterations=100):
        if self.beacons is None:
            raise ValueError("Beacons must be set before running the filter.")
        distances = self.rssi_to_distance(rssi_values)
        for _ in range(iterations):
            self.particles = self.predict()
            self.update(distances)
            self.resample()

        # Estimate the device location as the mean of the particles
        estimated_location = np.mean(self.particles, axis=0)
        return estimated_location

class Triangulation:
    @staticmethod
    def rssi_to_distance(rssi):
        tx_power = -59  # dBm (example value for 1 meter distance)
        n = 2.4  # Path loss exponent (example value for free space)
        distance = 10 ** ((tx_power - np.array(rssi)) / (10 * n))
        return distance

    @staticmethod
    def distance_to_rssi(distance):
        tx_power = -59  # dBm (example value for 1 meter distance)
        n = 2.4 # Path loss exponent (example value for free space)
        rssi = tx_power - 10 * n * np.log10(distance)
        return rssi

    def compute_dist(self, beacons, rssi_values):
        distances = self.rssi_to_distance(rssi_values)
        coords_and_dists = []
        for i, beacon in enumerate(beacons):
            coords_and_dists.append((beacon[0], beacon[1], distances[i]))
        return coords_and_dists

    def triposition(self, beacons, rssi_values):
        coords_and_dists = self.compute_dist(beacons, rssi_values)
        (xa, ya, da), (xb, yb, db), (xc, yc, dc) = coords_and_dists[:3]
        x, y = sp.symbols('x y')
        f1 = 2*x*(xa-xc) + xc**2 - xa**2 + 2*y*(ya-yc) + yc**2 - ya**2 - (dc**2 - da**2)
        f2 = 2*x*(xb-xc) + xc**2 - xb**2 + 2*y*(yb-yc) + yc**2 - yb**2 - (dc**2 - db**2)
        result = sp.solve([f1, f2], (x, y))
        locx, locy = result[x], result[y]
        return [float(locx), float(locy)]

def detect_location(rssi_values, beacons, mode="pf"):
    if mode == "pf":
        # Get the indices of the two-largest RSSI values
        largest_indices = np.argsort(rssi_values)[-3:]
        largest_beacons = [beacons[i] for i in largest_indices]
        largest_rssi_values = [rssi_values[i] for i in largest_indices]

        # Create and configure the particle filter
        pf = ParticleFilter()
        pf.set_beacons(largest_beacons)

        # Run the particle filter
        estimated_location = pf.run(largest_rssi_values)
    elif mode == "tri":
        # Use triangulation to locate the device
        tri = Triangulation()
        estimated_location = tri.triposition(beacons, rssi_values)
    else:
        raise ValueError("Unsupported mode. Use 'pf' for particle filter or 'tri' for triangulation.")

    return estimated_location

def clip_location(loc):
    y_min, y_max = 0, 0
    if loc[0] < 0:
        x = 0
    elif loc[0] > 0 and loc[0] < 14.0:
        y_max = 2.67 
        x = loc[0]
    elif loc[0] > 14.0 and loc[0] < 18.1:
        y_max = 3.9
        x = loc[0]
    elif loc[0] > 18.1:
        x = 18.1
    
    if loc[1] < y_min:
        y = y_max/2
    elif loc[1] > y_max:
        y = y_max/2
    else:
        y = loc[1]
    
    return [x,y]

def get_input(json_list):
    # Initialize the list to store average RSSI values
    average_rssi = []
    # Calculate the average RSSI for each minor or fill with -1000 if the minor key does not exist
    for minor_value in range(1, 9):
        if json_list[minor_value]:
            rssi_values = [item['RSSI'] for item in json_list[minor_value]]
            average_rssi.append(np.mean(rssi_values))
        else:
            average_rssi.append(-1000)
    return average_rssi

class ParticleFilter:
    def __init__(self, num_particles=1000):
        self.num_particles = num_particles
        self.particles = None
        self.weights = None
        self.beacons = None
        self.x_min = None
        self.y_min = None
        self.x_max = None
        self.y_max = None

    def initialize_particles(self):
        if self.beacons is None:
            raise ValueError("Beacons must be set before initializing particles.")
        self.x_min, self.y_min = np.min(self.beacons, axis=0) - 1
        self.x_max, self.y_max = np.max(self.beacons, axis=0) + 1
        particles = np.empty((self.num_particles, 2))
        particles[:, 0] = np.random.uniform(self.x_min, self.x_max, self.num_particles)
        particles[:, 1] = np.random.uniform(self.y_min, self.y_max, self.num_particles)
        self.particles = particles
        self.weights = np.ones(self.num_particles) / self.num_particles

    @staticmethod
    def rssi_to_distance(rssi):
        tx_power = -59  # dBm (example value for 1 meter distance)
        n = 2.4  # Path loss exponent (example value for free space)
        distance = 10 ** ((tx_power - np.array(rssi)) / (10 * n))
        return distance

    @staticmethod
    def distance_to_rssi(distance):
        tx_power = -59  # dBm (example value for 1 meter distance)
        n = 2.4  # Path loss exponent (example value for free space)
        rssi = tx_power - 10 * n * np.log10(distance)
        return rssi

    def set_beacons(self, beacons):
        self.beacons = np.array(beacons)
        self.initialize_particles()

    def predict(self):
        # In this example, we assume no movement, so particles remain the same
        self.particles = np.clip(self.particles, [self.x_min, self.y_min], [self.x_max, self.y_max])
        return self.particles

    def update(self, distances):
        if self.particles is None:
            raise ValueError("Particles must be initialized before updating.")
        self.weights.fill(1.0)
        for i, beacon in enumerate(self.beacons):
            beacon_dist = np.linalg.norm(self.particles - beacon, axis=1)
            self.weights *= np.exp(-0.5 * ((beacon_dist - distances[i]) ** 2))
        self.weights += 1e-300  # to avoid division by zero
        self.weights /= np.sum(self.weights)  # normalize

    def resample(self):
        indices = np.random.choice(np.arange(self.num_particles), size=self.num_particles, p=self.weights)
        self.particles = self.particles[indices]
        self.weights = self.weights[indices]
        self.weights /= np.sum(self.weights)

    def run(self, rssi_values, iterations=100):
        if self.beacons is None:
            raise ValueError("Beacons must be set before running the filter.")
        distances = self.rssi_to_distance(rssi_values)
        for _ in range(iterations):
            self.particles = self.predict()
            self.update(distances)
            self.resample()

        # Estimate the device location as the mean of the particles
        estimated_location = np.mean(self.particles, axis=0)
        return estimated_location

class Triangulation:
    @staticmethod
    def rssi_to_distance(rssi):
        tx_power = -59  # dBm (example value for 1 meter distance)
        n = 2.4  # Path loss exponent (example value for free space)
        distance = 10 ** ((tx_power - np.array(rssi)) / (10 * n))
        return distance

    @staticmethod
    def distance_to_rssi(distance):
        tx_power = -59  # dBm (example value for 1 meter distance)
        n = 2.4 # Path loss exponent (example value for free space)
        rssi = tx_power - 10 * n * np.log10(distance)
        return rssi

    def compute_dist(self, beacons, rssi_values):
        distances = self.rssi_to_distance(rssi_values)
        coords_and_dists = []
        for i, beacon in enumerate(beacons):
            coords_and_dists.append((beacon[0], beacon[1], distances[i]))
        return coords_and_dists

    def triposition(self, beacons, rssi_values):
        coords_and_dists = self.compute_dist(beacons, rssi_values)
        (xa, ya, da), (xb, yb, db), (xc, yc, dc) = coords_and_dists[:3]
        x, y = sp.symbols('x y')
        f1 = 2*x*(xa-xc) + xc**2 - xa**2 + 2*y*(ya-yc) + yc**2 - ya**2 - (dc**2 - da**2)
        f2 = 2*x*(xb-xc) + xc**2 - xb**2 + 2*y*(yb-yc) + yc**2 - yb**2 - (dc**2 - db**2)
        result = sp.solve([f1, f2], (x, y))
        locx, locy = result[x], result[y]
        return [float(locx), float(locy)]

def detect_location(rssi_values, beacons, mode="pf"):
    if mode == "pf":
        # Get the indices of the two-largest RSSI values
        largest_indices = np.argsort(rssi_values)[-2:]
        largest_beacons = [beacons[i] for i in largest_indices]
        largest_rssi_values = [rssi_values[i] for i in largest_indices]

        # Create and configure the particle filter
        pf = ParticleFilter()
        pf.set_beacons(largest_beacons)

        # Run the particle filter
        estimated_location = pf.run(largest_rssi_values)
    elif mode == "tri":
        # Use triangulation to locate the device
        tri = Triangulation()
        estimated_location = tri.triposition(beacons, rssi_values)
    else:
        raise ValueError("Unsupported mode. Use 'pf' for particle filter or 'tri' for triangulation.")

    return estimated_location

def clip_location(loc):
    y_min, y_max = 0, 0
    if loc[0] < 0:
        x = 0
    elif loc[0] > 0 and loc[0] < 14.0:
        y_max = 2.67 
        x = loc[0]
    elif loc[0] > 14.0 and loc[0] < 18.1:
        y_max = 3.9
        x = loc[0]
    elif loc[0] > 18.1:
        x = 18.1
    
    if loc[1] < y_min:
        y = y_min
    elif loc[1] > y_max:
        y = y_max
    else:
        y = loc[1]
    
    return [x,y]

def scenario2(json_list, mode="tri"):
    # Set beacons' location 
    beacons = np.array([[0,0], [2.6,2.67], [5.71,2.67], [9.7,2.67], [13.5,2.67], [15.1,0], [17.5,0], [16.9,3.9]])
    # Compute average rssi value 
    rssi_values = get_input(json_list)
    # Compute location by pf/tri algorithm
    location = detect_location(rssi_values, beacons, mode)
    DEBUG_FLAG = 1
    if DEBUG_FLAG:
        print(f"rssi_lst: {rssi_values}, location: {location}")
    location = clip_location(location)
    return f"x: {location[0]:.2f}m, y: {location[1]:.2f}m"


def check_minors(json_list):
    result = []
    minor_flag_num=0
    for minor_key in range(1, 9):  # Check only for minors 1 to 8
        minor_list = json_list.get(minor_key, [])
        if len(minor_list) != 10:
            continue
        else:
            minor_flag_num+=1
            if minor_flag_num>=3:
                return True
    return None
        # if len(minor_list) == 10:
        #     # Calculate average RSSI
        #     average_rssi = sum(item['RSSI'] for item in minor_list) / len(minor_list)
        #     # Construct new JSON entry with averaged RSSI
        #     result.append({
        #         'Minor': minor_key,
        #         'RSSI': average_rssi,
        #     })
    # return result



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
        if item["Major"]==1:
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
    



def calculate_the_two_point_coordinate_of_circle(x_a, y_a, r_a, x_b, y_b, r_b, d_ab):
    # for point C and D
    # caculate d_ae : the distance between point A and E
    d_ae = (r_a ** 2 - r_b ** 2 + d_ab ** 2) / (2 * d_ab)

    # calculate d_ce : the distance between point C and E
    d_ce = np.sqrt(r_a ** 2 - d_ae ** 2)

    # calculate the coordinate of point E
    x_e = x_a + d_ae * (x_b - x_a) / d_ab
    y_e = y_a + d_ae * (y_b - y_a) / d_ab

    # calculate the slope of the line AB
    if(x_a == x_b):
        k_ab = 0
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
                    print("start to compute position")
                    answer=scenario2(json_list=json_list, mode="pf")
                    send_back_msg=f"{answer}"
                    send_back_msg=send_back_msg.encode(self.code)
                    self.conn.send(send_back_msg)
                else:
                    #check and return 
                    send_back_msg=f"wait"
                    send_back_msg=send_back_msg.encode(self.code)
                    self.conn.send(send_back_msg)
                if current_time>=time_limit:
                    filled_json_list=fill_json_list(json_list)
                    print(f"timeout ({time_limit}s) \nstart to compute position")
                    answer=scenario2(json_list=filled_json_list, mode="pf")
                    send_back_msg=f"{answer}"
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
    


