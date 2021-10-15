# Low-level networking interface
import socket
# Create logs
import logging
# Low-level multithreading
import _thread as serv
# Import miscellaneous operating system functions
import os
# Import date and time
from datetime import datetime
# To exit thread
# import sys, time
# Import ingestor functions
from ingestor import check_machine_and_sensor, update_machine_operating_status, send_sensor_data
# Import FFT function capability
from FFTfunction import fftFunction

# get server device ip address
SERVERIP = '169.254.222.151'# #SERVERIP = socket.gethostbyname(socket.gethostname())
#SERVERIP = '172.22.1.110'
#SERVERIP = '10.104.143.199'
PORT = 5050
ADDRESS = (SERVERIP, PORT)
FORMAT = 'utf-8'
client_list = []
clientNumber = 0
# what type of ip address are we taking or accepting AF_INET = IPv4 addresses
# SOCK_STREAM(TCP) is the method of streaming
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Bind server to this specific IP and port to listen for requests
server.bind(ADDRESS)
  
# Erase file containing list of connected clients at server start
f = open('devicelist.txt','r+')
f.truncate(0)
f.close()

# Buffer size of data for recieving during file transfer from client, currently 8192
# Higher the number the more memory required but less read/write operations so its faster
CHUNK_SIZE = 2**15
# Disable automatic logs from these libraries
logging.getLogger('matplotlib.font_manager').disabled = True


# Function of thread to handle all client operations
def handle_client(clientCon, clientAdd, clientNumber):
    print("[NEW CONNECTION] %s, %i connected" % (clientAdd[0],clientAdd[1]))
    # Declare variables
    connected = True
    clientName = ''
    clean_up = 0 
    machine_id = None
    sensor_id = None
    
    while connected:
        # Remain on this line until a messassdfsfge is recieved from the client
        # Obtain length of message stored within 128 bytes
        msg_length = clientCon.recv(128).decode(FORMAT)
   
        if msg_length:
            msg_length = int(msg_length) # through this, it gets rms from client
            # Recieve message
            msg = clientCon.recv(msg_length).decode(FORMAT)
            # Each message has two parts, [1]-Label, [2]-Data
            # This splits the single string into two
            split_msg = msg.split(',')
            print(split_msg)
            # Identify and store which client is connected, PI_1 or PI_2
            if split_msg[0] == "identify":
                clientName = split_msg[1]
                sensorName = split_msg[2]
                sensorThreshold = split_msg[3]
                sensorName1 = split_msg[4]
                sensorThreshold1 = split_msg[5]

                print(clientName)
                print(sensorName)
                print(sensorThreshold)
                print(sensorName1)
                print(sensorThreshold1)
                
                
                result = check_machine_and_sensor(clientName, sensorName, float(sensorThreshold))
                machine_id = result[0]
                sensor_id = result[1]                 
                result = check_machine_and_sensor(clientName, sensorName1, float(sensorThreshold1))
                sensor_id1 = result[1] 
                
                
                # check whether this clinet is already on the list and running 
                # before storeing in device_list.txt file
                # if the client already exist then exit the thread after deleting
                # the redundant cient from the list
                f = open('devicelist.txt','r')
                lines = f.readlines()
                f.close()

                for line in lines:
                    if line.strip("\n") == clientName:
                        print("this client is redundant & cleaned up")
                        clientCon.close()
                
                # Store client name in a file
                f = open('devicelist.txt','a+')
                f.seek(0)
                f.write(split_msg[1]+"\n")
                f.close()
                update_machine_operating_status(machine_id, "Online")
                # Let client know that engine is ready
                readyMessage = "ready"
                clientCon.send(readyMessage.encode(FORMAT))
            # Reset corresponding graph data and clean received_signal file 
            # This can be moved to inside the if statement above once closing 
            # redundant client is ensured. 
            if clean_up == 0:                
                try:
                    f = open('recievedSignal' + clientName + '.txt','r+')
                    f.truncate(0)
                    f.close()
                    print('recievedSignal' + clientName + '.txt' + " is cleaned up")
                except Exception:
                    print('recievedSignal' + clientName + '.txt' + " does not exist")
                    print("cleaning up recievedSignal file has been skipped")
                clean_up = 1                
            else:
                clean_up = 1
            
            # If message indicates RMS threshold is triggered    
            if split_msg[1] == "rmsThresTrig":
                timestamp = datetime.now().astimezone().replace(microsecond=0).isoformat()
                
                if split_msg[0] == "vibration": 
                    send_sensor_data(machine_id, sensor_id, split_msg[2], timestamp)
                elif split_msg[0] == "current": 
                    send_sensor_data(machine_id, sensor_id1, split_msg[2], timestamp)
                    
                # Prepare to recieve the signal file from client
                print("~~~~Recieving Signal File~~~~")
                f = open('recievedSignal' + clientName + '.txt','wb')
                while True:
                    # If no data being recieved for 1 second continue with code
                    clientCon.settimeout(20)
                    try:
                        # Recieve data
                        xx = clientCon.recv(CHUNK_SIZE) 
                        while (xx):
                            f.write(xx)
                            xx = clientCon.recv(CHUNK_SIZE)
                    except socket.timeout:
                        print("receiving failed")
                        pass
                    clientCon.settimeout(None)
                    print("~~~~Signal File Recieved~~~~")
                    filesize = os.path.getsize('recievedSignal' + clientName + '.txt')
                    if filesize == 0:
                        print("File size is 0")
                    else:
                        print("File size is " + str(filesize))     
                    # Perform FFT
                    
                    if split_msg[0] == "vibration": 
                        fftFunction(clientName, machine_id, sensor_id, timestamp)
                    elif split_msg[0] == "current": 
                        fftFunction(clientName, machine_id, sensor_id1, timestamp)
                    f.close()
                    break
                # Notify client that process for RMS breach is complete
                doneMessage = "done"
                clientCon.send(doneMessage.encode(FORMAT))
            
            # If message indicates RMS level is normal
            if split_msg[1] == "rmsNormal":
                timestamp = datetime.now().astimezone().replace(microsecond=0).isoformat()
                
                
                if split_msg[0] == "vibration": 
                    send_sensor_data(machine_id, sensor_id, split_msg[2], timestamp)
                elif split_msg[0] == "current": 
                    send_sensor_data(machine_id, sensor_id1, split_msg[2], timestamp)
                
            
            # If message from client is close then connection is closed
            if split_msg[0] == "close":
                # clean up the device list
                f = open('devicelist.txt','r')
                lines = f.readlines()
                f.close()
                
                f = open('devicelist.txt','w')
                for line in lines:
                    if line.strip("\n") != clientName:
                        f.write(line)
                f.close()
                update_machine_operating_status(machine_id, "Offline")
                
                doneMessage = "done"
                clientCon.send(doneMessage.encode(FORMAT))
                connected = False            
    clientCon.close()
    print("client is closed")


# Function to broadcast message to all clients
def send_all(data_format):
    for i in client_list:
        i.send(data_format.encode(FORMAT))


# Function to handle accepting of clients
def accept_client():
    global clientNumber, client_list
    while True:
        clientNumber += 1
        clientCon, clientAddr = server.accept()
        client_list += [clientCon]
        print("Client accepted.")
        serv.start_new_thread(handle_client, (clientCon,clientAddr,clientNumber,))
   

# Main program to listen for clients and handle closing of server via keyboard interrupt
if __name__ == '__main__':
    server.listen()
    print("[LISTENING] Engine is listening on %s" % SERVERIP)
    serv.start_new_thread(accept_client, ())
    try:
        while True:
            pass
    except KeyboardInterrupt:
        # If server is closed then clear file of connceted devices
        f = open('devicelist.txt','r+')
        f.truncate(0)
        f.close()
        server.close()
        print("Exited")