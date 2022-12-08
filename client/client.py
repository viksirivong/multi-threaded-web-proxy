"""
Group: Ricardo Garcia, Thongsavik Sirivong, and Renato Safra
Project: Multi-threaded web proxy server
Files: client.py, proxy_server.py, origin_server.py, and helper.py
Date: 11/13/22
Description: This program incorporates a multi-threaded client program.
		For testing and demonstration purposes.
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
BUFFER_SIZE = 2048
THREAD_LOCK = threading.Lock()

def main():
    pathname = 0
    while True:
        # Request pathname for the proxy to search
        time.sleep(3)
        THREAD_LOCK.acquire()
        pathname = input("Enter pathname:")
        THREAD_LOCK.release()
        if pathname == '-1':
            break
        # Thread the communication between client and proxy
        t = threading.Thread(target=clientThreading, args=((pathname, )))
        t.start()
    
    # Test case 1: file (HelloWorld) exists in the origin server, but not in the proxy server
    t1 = threading.Thread(target=clientThreading, args=(("HelloWorld", )))
    t1.start()
    
    # Test case 2: file (HelloWorld) exists in the origin server as well as in the proxy server
    t2 = threading.Thread(target=clientThreading, args=(("HelloWorld", )))
    t2.start()

    # Test case 3: file (HelloWorld) does not exist in the origin server.
    t3 = threading.Thread(target=clientThreading, args=(("Hello", )))
    t3.start()

    # Test case 4: sample-webpage
    t4 = threading.Thread(target=clientThreading, args=(("sample-webpage", )))
    t4.start()

    # Test case 3: sample-web is an incorrect pathname
    t5 = threading.Thread(target=clientThreading, args=(("sample-web", )))
    t5.start()

    t1.join()
    t2.join()
    t3.join()
    t4.join()
    t5.join()
    

def clientThreading(pathname):
    """
    Handles the threading of the communication between the
    client and proxy server.

    Parameters:
    pathname (string): Pathname entered by user.
    """
    try:
        # Lock thread for sending data to the proxy server
        THREAD_LOCK.acquire()
        thread_num = threading.current_thread().name.split()[0]
        print(f"\n{thread_num} created:")
        # Create socket and connect to proxy server
        clientSocket = helper.createSocket(thread_num)
        errCode = helper.connectSocket(clientSocket, PROXY_IP, PROXY_PORT)
        # Raise exception if connection socket.connect() fails
        if errCode == -1:
            THREAD_LOCK.release()
            raise exception
        # Build request message and send to proxy
        reqMsg = helper.buildReqMsg(pathname, PROXY_PORT, PROXY_IP)
        print("Request message has been built:")
        print(reqMsg, end='')
        clientSocket.send(reqMsg.encode())
        print("Request message has been sent to proxy server.")
        clientSocket.shutdown(SHUT_WR)
        THREAD_LOCK.release()
        
        # Wait for response from proxy server
        responseMsg = clientSocket.recv(BUFFER_SIZE).decode()
        # Lock thread after response is received
        THREAD_LOCK.acquire()
        print(f"\n{thread_num}:")
        print("Response message received from proxy server.")
        # Receive response message from proxy server
        responseMsg += helper.receiveMsg(clientSocket)
        print(responseMsg, end='')
        clientSocket.shutdown(SHUT_RDWR)
        helper.closeSocket(clientSocket)
        print(f"{thread_num} finished.\n")
        THREAD_LOCK.release()
    except:
        # Error with socket connection. Close thread.
        THREAD_LOCK.acquire()
        print(f"{thread_num} resumed:")
        print("Socket connection interrupted.\nTerminating thread.")
        helper.closeSocket(clientSocket)
        THREAD_LOCK.release()
    
if __name__ == "__main__":
    main()
