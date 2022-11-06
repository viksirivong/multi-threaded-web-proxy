from socket import *
import sys
import os
import time
from _thread import *
import threading

IP = "127.0.0.1"
PROXY_PORT = 80
ORIGIN_PORT = 90
BUFFER_SIZE = 2048
SOCKETS = []
FILES = { "HelloWorld.html":"Thu, 6 Oct 2022 09:23:18" }
STATUS_200 = "HTTP/1.1 200 OK"
STATUS_304 = "HTTP/1.1 304 Not Modified"
STATUS_404 = "HTTP/1.1 404 Not Found"

def main():
    # Create origin/proxy server sockets
    proxySocket = createSocket()    
    originSocket = createSocket()
    # Bind proxy socket and set to listen
    bindSocket(proxySocket, '', PROXY_PORT)
    # Accept requests from client
    while True:
        print("The proxy server is ready to receive...")
        clientSocket, clientAddr = proxySocket.accept()
        SOCKETS.append(clientSocket)
        msg = clientSocket.recv(BUFFER_SIZE).decode()
        clientReqMsg = msg.split()
        # Maybe check instead of assuming these values?
        hostname = clientReqMsg[4]
        pathname = clientReqMsg[1]
        connectSocket(originSocket, IP, ORIGIN_PORT)
        originSocket.send(("GET " + pathname + " HTTP/1.1\r\n").encode())
        originSocket.send(("Host: " + hostname + "\r\n").encode())
        # File already exists
        if os.path.exists(pathname[1:]):
            print("if file exists")
            originSocket.send(("If-modified-since: " + FILES[pathname[1:]] + "\r\n").encode())
        originSocket.send("\r\n".encode())
        originSocket.shutdown(SHUT_WR)
        msg = receiveMsg(originSocket)
        responseMsg = msg.split("\r\n")
        # *****************************************************
        # Error 404 message received
        if responseMsg[0] == STATUS_404:
            clientSocket.send( (STATUS_404 + "\r\n\r\n").encode() )
        # Status 200 or 304 received
        else:
            clientSocket.send( (STATUS_200 + "\r\n\r\n").encode() )
            # Status code 304
            if responseMsg[0] == STATUS_304:
                file = open(pathname[1:], "r")
                outputdata = file.readlines()
                sendToClient(clientSocket, outputdata)
            # Status code 200
            else:
                file = open(pathname[1:], "w")
                outputdata = msg.split("\r\n\r\n")[1]
                sendToClient(clientSocket, outputdata)
                file.writelines(outputdata)
                lastModified = responseMsg[1].split()
                date = ''
                for i in range(1, len(lastModified)):
                    date = date + lastModified[i]
                FILES.update({pathname[1:]:date})
            clientSocket.send("\r\n".encode())
        # *******************************************************

        clientSocket.shutdown(SHUT_RDWR)
        closeSocket(clientSocket)
        originSocket.shutdown(SHUT_RDWR)
        closeSocket(originSocket)

def sendToClient(soc, data):
    for i in range(0, len(data)):
        soc.send(data[i].encode())
        
def receiveMsg(soc):
    msg = ''
    while True:
        data = soc.recv(BUFFER_SIZE).decode()
        if not data: break
        msg = msg + data
    return msg

def acquireFileDate(pathname):
    data = time.ctime(os.path.getmtime(pathname[1:])).split()
    return data[0], data[1], data[2], data[3], data[4]

def connectSocket(soc, ip, port):
    try:
        soc.connect( (ip, port) )
    except:
        print("Failed to connect to socket. Program terminating.")
        closeAllSockets()
        sys.exit()
        
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
