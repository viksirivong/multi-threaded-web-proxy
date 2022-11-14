"""
Group: Ricardo Garcia, Thongsavik Sirivong, and Renato Safra
Project: Multi-threaded web proxy server
Files: client.py, proxy_server.py, origin_server.py, and helper.py
Date: 11/13/22
Description: This program incorporates a multi-threaded proxy server.
"""
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
    # Create, bind, and set to listen (proxy)
    proxySocket = helper.createSocket("proxy")
    helper.bindSocket(proxySocket, PROXY_PORT)
    # Accept requests from client server
    while True:
        time.sleep(1)
        THREAD_LOCK.acquire()
        print("Proxy server is ready to receive...")
        THREAD_LOCK.release()
        clientSocket, clientAddr = proxySocket.accept()
        t = threading.Thread(target=proxyThreading, args=((clientSocket, )) )
        t.start()
    t.join()

def proxyThreading(clientSocket):
    """
    Handles the threading of the communication between the client and proxy server
    & the proxy and origin server.

    Parameters:
    clientSocket (socket): Socket connection accepted from client. 
    """
    try:
        # Wait for request message from client
        reqMsg = clientSocket.recv(BUFFER_SIZE).decode()
        THREAD_LOCK.acquire()
        # Find current working thread number
        thread_num = threading.current_thread().name.split()[0]
        print(f"\n{thread_num} created:")
        print("Proxy server received request message from client.")
        # Establish TCP connection with origin server
        originSocket = helper.createSocket("origin")
        THREAD_LOCK.release()

        #**************************************
        print(f"[{thread_num} PROCESSING] ...")
        time.sleep(3)
        #**************************************
        
        # Parse request message
        reqMsg = reqMsg.split()
        hostname = reqMsg[4]
        pathname = reqMsg[1]
        
        # Send conditional GET message to origin server
        THREAD_LOCK.acquire()
        print(f"\n{thread_num} resumed:")
        print("Initiating connection with origin server.")
        # Connect to origin ip:port
        errCode = helper.connectSocket(originSocket, ORIGIN_IP, ORIGIN_PORT)
        # Failed to connect to origin
        if errCode == -1:
            THREAD_LOCK.release()
            raise exception
        # Build conditional GET message
        condGetMsg = helper.buildCondGET(pathname, hostname)
        print("Conditional GET message built.")
        # send message to origin server
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
                print(f"{pathname[1:]} is up to date.")
            # Status code 200 (proxy is out of date)
            else:
                # Update file with information sent from origin server
                file = open(pathname[1:], "w")
                outputdata = msg.split("\r\n\r\n")[1]
                file.writelines(outputdata)
                print(f"{pathname[1:]} cache version updated.")
                # Send updated file information to client
                file = open(pathname[1:], "r")
                outputdata = file.readlines()
                helper.sendData(clientSocket, outputdata)
            clientSocket.send("\r\n".encode())
            print("Response message sent to client.")
        # Close open socket connections
        clientSocket.shutdown(SHUT_RDWR)
        print("Attempting to close client socket.")
        helper.closeSocket(clientSocket)
        print(f"{thread_num} finished.")
        THREAD_LOCK.release()
    except:
        # Error with socket connection. Close thread.
        THREAD_LOCK.acquire()
        print(f"\n{thread_num}: Socket connection interrupted.\nTerminating thread.")
        print("Attempting to close client socket.")
        helper.closeSocket(clientSocket)
        print("Attempting to close origin socket.")
        helper.closeSocket(originSocket)
        THREAD_LOCK.release()
    
if __name__ == "__main__":
    main()
