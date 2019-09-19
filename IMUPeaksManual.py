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
dim = 2
interval = 1
markInterval = 2.5
magInterval = 10

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
valleyCount = 0

peakValue = []
valleyValue = []
distance = [0]
LED = []
print('start!')

while True:
    command = raw_input(" input anykey to continue and n to quit: ")
    if command != 'n':
        a = device.getRawCompassData()
        #time.sleep(interval)
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
                peakValue.append(xData[i-1])
                #Arduino.write('C')
                LED.append(0)
                
            else:
                print('here is a valley')
                valleyCount += 1 
                valleyValue.append(xData[i-1])
                #Arduino.write('3')
                LED.append(3)

        i = i + 1
        cornerCount = peakCount+valleyCount
        
        if len(peakValue)== 0 or len(valleyValue) ==0:
            pass
        else:
            ampInterval = abs(peakValue[-1] - valleyValue[-1])/3
            if  cornerCount%2 == 1:
                lastLED = int(round(abs(xValue - peakValue[-1])/ampInterval))
                if lastLED >= 2:
                    lastLED = 2

            elif cornerCount%2 == 0:
                lastLED = int(round(abs(xValue - valleyValue[-1])/ampInterval))+3
                if lastLED >=5:
                    lastLED = 5
                
            if lastLED < LED[-1]:
                    pass
            else:
                LED.append(lastLED)
                #Arduino.write(str(LED[-1]))
                
            distance.append(magInterval*(peakCount-1) + LED[-1]*magInterval/5)
            print('Now at the distance of ' + str(distance[-1]))

    else:
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
        xd = np.arange(len(distance))
        plt.figure(1)
        plt.plot(xd,xd*markInterval, '--')
        plt.plot(xd,distance)
        plt.savefig(filename + 'distance')
        break
    
plt.show()
#Arduino.write('0')        

    
#ts_api.global_broadcaster.setStreamingSlots(slot0='getAllRawComponentSensorData',filter=sensor_list)
#ts_api.global_broadcaster.startStreaming(filter=sensor_list)
#ts_api.global_broadcaster.startRecordingData(filter=sensor_list)

