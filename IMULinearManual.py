import time
import threespace_api as ts_api
#import serial
import matplotlib.pyplot as plt
import numpy as np

device_list = ts_api.getComPorts()
#Arduino = serial.Serial('COM4',9600)   

com_port, friendly_name, device_type = device_list[0]
device = None
if device_type == "USB":
    device = ts_api.TSUSBSensor(com_port=com_port)
elif device_type == "WL":
    device = ts_api.TSWLSensor(com_port=com_port)
elif device_type == "EM":
    device = ts_api.TSEMSensor(com_port=com_port)
elif device_type == "DL":
    device = ts_api.TSDLSensor(com_port=com_port)
elif device_type == "BT":
    device = ts_api.TSBTSensor(com_port=com_port)

filename = raw_input("enter the filename: ")   
f = open(filename + '.txt', 'w')
t = open(filename + 'distance.txt','w')
sensor_list = [device]

# dim = 0 for x, 1 for y, 2 for z
dim = 1
interval = 1
markInterval = 2.5
magInterval = 30

print('start!')
device.tareWithCurrentOrientation()
data = [device.getRawCompassData()]
xData = [data[0][0]]
time.sleep(interval)

a = device.getRawCompassData()
xValue = a[dim]
time.sleep(interval)
data.append(a)
xData.append(xValue)

diff = [xData[1] - xData[0]]
i = 2 
peakCount = 0
peakRef = 1.9            # adjust the ref
valleyRef = -0.5          # adjust the ref
valleyCount = 0
kRef = (peakRef - valleyRef)/magInterval

cornerValue = []
distance = [0]
LED = []

while True:
    command = raw_input(" input y to continue and n to quit: ")
    if command != 'n':
        a = device.getRawCompassData()
        time.sleep(interval)
        xValue = a[dim]
        data.append(a)
        xData.append(xValue)
        diff.append (xData[i] - xData[i-1])

        if diff[i-1]*diff[i-2] >= 0 :
            pass
        else:
            if diff[i-2] > 0:
                print('here is a peak')
                peakCount += 1
                peakValue = (xData[i-1])
                
            else:
                print('here is a valley')
                valleyCount += 1 
                valleyValue = (xData[i-1])

        i = i + 1

        if valleyCount == 1 :
            distance.append((xValue - valleyValue)/kRef)
            print('the distance is '+ str(distance[-1]))      
            
        else:
            #distance.append(0)
            print('not in the effective range')


    else:
    #except:
        print('\n'+ 'stop')
        device.stopStreaming()
        x = np.arange(i)
        f.write('\n'.join(str(x) for x in xData))
        t.write('\n'.join(str(y) for y in distance))
        f.close()
        t.close()
        plt.figure(0)
        plt.plot(x,xData,marker = 'o')
        plt.savefig(filename + 'data')
        plt.figure(1)
        xd = np.arange(len(distance))
        plt.plot(xd,distance)
        plt.plot(xd,xd*markInterval, '--')
        plt.savefig(filename + 'distance')
        break
    

plt.show()
#Arduino.write('0')        

    
#ts_api.global_broadcaster.setStreamingSlots(slot0='getAllRawComponentSensorData',filter=sensor_list)
#ts_api.global_broadcaster.startStreaming(filter=sensor_list)
#ts_api.global_broadcaster.startRecordingData(filter=sensor_list)

