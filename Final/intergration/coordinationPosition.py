# %%
import sympy
import numpy as np

class coordinatePosition():
    def __init__(self):
        self.ibeacon_lst = [[0,0],[2.6,2.67],[5.71,2.67],[9.7,2.67],[13.5,2.67],[15.1,0],[17.5,0],[16.9,3.9]]

    def computeDist(self, minor_lst, rssi_lst, measured_pwr=-44, N_fac = 2.4):
        # Find the position of ibeacons
        xa = self.ibeacon_lst[minor_lst[0]-1][0]
        ya = self.ibeacon_lst[minor_lst[0]-1][1]
        xb = self.ibeacon_lst[minor_lst[1]-1][0]
        yb = self.ibeacon_lst[minor_lst[1]-1][1]
        xc = self.ibeacon_lst[minor_lst[2]-1][0]
        yc = self.ibeacon_lst[minor_lst[2]-1][1]

        # Compute the dist for each ibeacon
        da = 10**((measured_pwr - rssi_lst[0])/(10*N_fac))
        db = 10**((measured_pwr - rssi_lst[1])/(10*N_fac))
        dc = 10**((measured_pwr - rssi_lst[2])/(10*N_fac))
        return xa,ya,da,xb,yb,db,xc,yc,dc

    def triposition(self, minor_lst, rssi_lst): 
        xa,ya,da,xb,yb,db,xc,yc,dc = self.computeDist(minor_lst, rssi_lst)
        # print(xa,ya,da,xb,yb,db,xc,yc,dc)
        x,y = sympy.symbols('x y')
        f1 = 2*x*(xa-xc)+np.square(xc)-np.square(xa)+2*y*(ya-yc)+np.square(yc)-np.square(ya)-(np.square(dc)-np.square(da))
        f2 = 2*x*(xb-xc)+np.square(xc)-np.square(xb)+2*y*(yb-yc)+np.square(yc)-np.square(yb)-(np.square(dc)-np.square(db))
        result = sympy.solve([f1,f2],[x,y])
        # print(result)
        locx,locy = result[x],result[y]
        return [locx,locy]

def getInput(json_lst):
    lst = []
    for minor_idx in json_lst:
        minor = json_lst[minor_idx]
        total = 0
        cnt = 0
        for d in minor:
            total += d['RSSI']
            cnt += 1
        lst.append((total/cnt, minor_idx))
    
    lst = sorted(lst, reverse=True)
    minor_lst, rssi_lst = [m for _,m in lst], [r for r,_ in lst]
    return minor_lst, rssi_lst
