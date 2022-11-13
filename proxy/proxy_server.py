from socket import *
import sys
import os
import time
from _thread import *
import threading
# helper.py functions used for all three py files
sys.path.append("..")
import helper

PROXY_IP = "127.0.0.1"
PROXY_PORT = 80
ORIGIN_IP = "127.0.0.1"
ORIGIN_PORT = 90
BUFFER_SIZE = 2048
STATUS_200 = "HTTP/1.1 200 OK"
STATUS_304 = "HTTP/1.1 304 Not Modified"
STATUS_404 = "HTTP/1.1 404 Not Found"
THREAD_LOCK = threading.Lock()

def main():
    #Create proxy server sockets
    proxySocket = helper.createSocket("proxy")
    # Bind proxy socket and set to listen
    helper.bindSocket(proxySocket, PROXY_PORT)
    while True:
        THREAD_LOCK.acquire()
        print("Proxy server is ready to receive...")
        THREAD_LOCK.release()
        clientSocket, clientAddr = proxySocket.accept()
        t = threading.Thread(target=proxyThreading, args=((clientSocket, )) )
        t.start()
    t.join()

def proxyThreading(clientSocket):
    try:
        # Wait for request message from client
        reqMsg = clientSocket.recv(BUFFER_SIZE).decode()
        # Lock thread after receiving data
        THREAD_LOCK.acquire()
        # Find current working thread number
        thread_num = threading.current_thread().name.split()[0]
        print(f"\n{thread_num} created:")
        print("Proxy server received request message from client.")
        originSocket = helper.createSocket("origin")
        THREAD_LOCK.release()
        # Parse request message
        reqMsg = reqMsg.split()
        hostname = reqMsg[4]
        pathname = reqMsg[1]

        # Send conditional GET message to origin server
        THREAD_LOCK.acquire()
        print(f"\n{thread_num} resumed:")
        print("Initiating connection with origin server.")
        errCode = helper.connectSocket(originSocket, ORIGIN_IP, ORIGIN_PORT)
        if errCode == -1:
            THREAD_LOCK.release()
            raise exception
        condGetMsg = helper.buildCondGET(pathname, hostname)
        print("Conditional GET message built.")
        originSocket.send(condGetMsg.encode())
        originSocket.send("\r\n".encode())
        print("Sent conditional GET message to origin server.")
        originSocket.shutdown(SHUT_WR)
        THREAD_LOCK.release()

        # Receive response message from origin server
        msg = originSocket.recv(BUFFER_SIZE).decode()
        THREAD_LOCK.acquire()
        msg += helper.receiveMsg(originSocket)
        print(f"\n{thread_num} resumed:")
        print("Received response message from origin server.")
        resMsg = msg.split("\r\n")
        print(resMsg)
        # Status code 404 received
        if resMsg[0] == STATUS_404:
            clientSocket.send( (STATUS_404 + "\r\n").encode() )
            clientSocket.send( "\r\n".encode() )
            print("Status code 404 sent to client.")
        # Check if status code 200 or 304 received
        else:
            clientSocket.send( (STATUS_200 + "\r\n").encode() )
            clientSocket.send( "\r\n".encode() )
            # Status code 304 (proxy is up to date)
            if resMsg[0] == STATUS_304:
                file = open(pathname[1:], "r")
                outputdata = file.readlines()
                helper.sendData(clientSocket, outputdata)
                print(f"{pathname[1:]} up to date.")
            # Status code 200 (proxy is out of date)
            else:
                file = open(pathname[1:], "w")
                outputdata = msg.split("\r\n\r\n")[1]
                file.writelines(outputdata)
                print(f"{pathname[1:]} cache version updated.")
                file = open(pathname[1:], "r")
                outputdata = file.readlines()
                helper.sendData(clientSocket, outputdata)
            clientSocket.send("\r\n".encode())
            print("Response message sent to client.")
        clientSocket.shutdown(SHUT_RDWR)
        print("Attempting to close client socket.")
        helper.closeSocket(clientSocket)
        print(f"{thread_num} finished.")
        THREAD_LOCK.release()
    except:
        THREAD_LOCK.acquire()
        print(f"\n{thread_num}: Socket connection interrupted.\nTerminating thread.")
        print("Attempting to close client socket.")
        helper.closeSocket(clientSocket)
        print("Attempting to close origin socket.")
        helper.closeSocket(originSocket)
        THREAD_LOCK.release()
    
if __name__ == "__main__":
    main()
