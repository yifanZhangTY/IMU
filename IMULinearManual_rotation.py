import time
import threespace_api as ts_api
#import serial
import matplotlib.pyplot as plt
import numpy as np
import math

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


sensor_list = [device]

# dim = 0 for x, 1 for y, 2 for z
dim = 1
interval = 1
sampleInterval = 0.05
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
currentTime = []
gyrox = []
gyroy = []
gyroz = []
xAngle = []
yAngle = []
zAngle = []
rawApply = []
rotApply = []


while True:
    command = raw_input(" input y to continue and n to quit: ")
    if command != 'n':
        try:
            for inf in range(10000):
                time.sleep(sampleInterval)
                gyro = device.getCorrectedGyroRate()
                gyrox.append(gyro[0])
                gyroy.append(gyro[1])
                gyroz.append(gyro[2])
                time.sleep(sampleInterval)
                currentTime.append(time.clock())
        
        except:
            print('collect data here')
            xAngle.append(np.trapz(gyrox,dx = sampleInterval))
            yAngle.append(np.trapz(gyroy,dx = sampleInterval))
            zAngle.append(np.trapz(gyroz,dx = sampleInterval))
            angle = np.column_stack((xAngle,yAngle,zAngle))
            Rx = np.array([[1,0,0],
                           [0,math.cos(xAngle[-1]),-math.sin(xAngle[-1])],
                           [0,math.sin(xAngle[-1]),math.cos(xAngle[-1])]])
            Ry = np.array([[math.cos(yAngle[-1]),0,math.sin(yAngle[-1])],
                           [0,1,0],
                           [-math.sin(yAngle[-1]),0,math.cos(yAngle[-1])]])
            Rz = np.array([[math.cos(zAngle[-1]),-math.sin(zAngle[-1]),0],
                           [math.sin(zAngle[-1]),math.cos(zAngle[-1]),0],
                           [0,0,1]])
            Rot = np.matmul(np.matmul(Rz,Ry),Rx)
            invRot = np.linalg.inv(Rot)

            rawData = device.getRawCompassData()
            aPrime = np.transpose(rawData)
            rotData = np.matmul(invRot,aPrime)
            
            rawApply.append(rawData[dim])
            rotApply.append(rotData[dim])
            
            a = rotData   # choose the group for following analyzation
            
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
        with open(filename + '.txt', 'w') as f:
            f.write('\n'.join(str(x) for x in xData))
        with open(filename + 'distance.txt','w') as t:
            t.write('\n'.join(str(y) for y in distance))
        with open(filename + 'angle.txt','w') as r:
            r.write(str(angle).replace('[','').replace(']',''))

        plt.figure(0)
        xm = np.arange(len(rawApply))
        plt.plot(xm,rawApply,'o',xm,rawApply)
        plt.plot(xm,rotApply,'ro',xm,rotApply)
        plt.title('magnetometer data')
        plt.savefig(filename + 'data')
        plt.figure(1)
        xd = np.arange(len(distance))
        plt.plot(xd,distance)
        plt.plot(xd,xd*markInterval, '--')
        plt.title('distance measurement')
        plt.savefig(filename + 'distance')
        break
    

plt.show()
#Arduino.write('0')        

    
#ts_api.global_broadcaster.setStreamingSlots(slot0='getAllRawComponentSensorData',filter=sensor_list)
#ts_api.global_broadcaster.startStreaming(filter=sensor_list)
#ts_api.global_broadcaster.startRecordingData(filter=sensor_list)

