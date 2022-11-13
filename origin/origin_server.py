from socket import *
import sys
import os
import time
import datetime
from _thread import *
import threading

# helper.py functions used for all three py files
sys.path.append("..")
import helper

IP = "127.0.0.1"
PROXY_PORT = 80
ORIGIN_PORT = 90
BUFFER_SIZE = 2048
SOCKETS = []

def main():
    # Create origin server socket
    originSocket = createSocket()
    # Bind origin socket and set to listen
    bindSocket(originSocket, '', ORIGIN_PORT)
    # Accept requests from proxy server
    while True:
        print("Ready to receive")
        connectionSocket, addr = originSocket.accept()
        SOCKETS.append(connectionSocket)
        print("Connection accepted:", addr)
        requestMsg = receiveMsg(connectionSocket)
        pathname = requestMsg[1]
        try:
            file = open(pathname[1:], "r")
            # File found by proxy server (if-modified-since)
            if len(requestMsg) > 5:
                print("Proxy found file")
                originFileDatetime = acquireDatetime(pathname)
                proxyFileDatetime = convertToDatetime(requestMsg)
                if proxyFileDatetime >= originFileDatetime:
                    print("Proxy server file is up to date.")
                    connectionSocket.send("HTTP/1.1 304 Not Modified\r\n".encode())
                    connectionSocket.send("\r\n".encode())
                else: # proxyFileDateTime < originFileDateTime
                    print("Origin server file is newer.")
                    sendUpdatedFile(pathname, file, connectionSocket)                    
            # File not found by proxy server
            else:
                print("Proxy didn't find file")
                sendUpdatedFile(pathname, file, connectionSocket)
        except IOError:
            print("Error 404 File Not Found.")
            connectionSocket.send("HTTP/1.1 404 Not Found\r\n".encode())
            connectionSocket.send("\r\n".encode())
        connectionSocket.shutdown(SHUT_WR)
        closeSocket(connectionSocket)
    originSocket.shutdown(SHUT_RDWR)
    closeAllSockets()

def sendUpdatedFile(pathname, file, soc):
    dayOfWeek, month, day, time, year = acquireFileDate(pathname)
    outputdata = file.readlines()
    soc.send("HTTP/1.1 200 OK\r\n".encode())
    soc.send( ("Last-modified: " + dayOfWeek + ", " + day + " " + month + " " + year + " " + " " + time + "\r\n").encode() )
    soc.send("\r\n".encode())
    for i in range(0, len(outputdata)):
        soc.send(outputdata[i].encode())
    soc.send("\r\n".encode())

def acquireFileDate(pathname):
    data = time.ctime(os.path.getmtime(pathname[1:])).split()
    return data[0], data[1], data[2], data[3], data[4]

def convertToDatetime(msg):
    fileTime = msg[6][0:3]
    for i in range(7, len(msg)):
        fileTime = fileTime + " " + msg[i]
    fileDatetime = datetime.datetime.strptime(fileTime, "%a %d %b %Y %H:%M:%S")
    return fileDatetime

# Acquire datetime object for pathname
def acquireDatetime(pathname):
    fileTime = time.ctime(os.path.getmtime(pathname[1:]))
    fileDatetime = datetime.datetime.strptime(fileTime, "%a %b %d %H:%M:%S %Y")
    return fileDatetime

def receiveMsg(soc):
    msg = ''
    while True:
        data = soc.recv(BUFFER_SIZE).decode()
        if not data: break
        msg = msg + data
    return msg.split()

def bindSocket(soc, ip, port):
    try:
        soc.bind( (ip, port) )
        soc.listen(1)
    except:
        print("Failed to bind socket. Program terminating.")
        closeAllSockets()
        sys.exit()
        
def createSocket():
    try:
        tempSocket = socket(AF_INET, SOCK_STREAM)
        SOCKETS.append(tempSocket)
        print("Socket initialized.")
    except:
        print("Failed to initialize socket. Program terminated.")
        closeAllSockets()
        sys.exit()
    return tempSocket

def closeAllSockets():
    for soc in SOCKETS:
        print("Closing:", soc)
        soc.close()
    SOCKETS.clear()
    print("Finished closing all the sockets.")

def closeSocket(soc):
    print("Closing:", soc)
    soc.close()
    SOCKETS.remove(soc)
    
if __name__ == "__main__":
    main()
