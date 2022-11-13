"""
Things to fix if time permits: check the pathname entered by user.
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
SOCKETS = []
THREAD_LOCK = threading.Lock()

def main():
    while True:
        # Request pathname for the proxy to search
        #time.sleep(5)
        THREAD_LOCK.acquire()
        pathname = input("Enter pathname:")
        THREAD_LOCK.release()
        # Thread the communication between client and proxy
        t = threading.Thread(target=clientThreading, args=((pathname, )))
        t.start()
    t.join()

def clientThreading(pathname):
    try:
        # Lock thread for sending data to the proxy server
        THREAD_LOCK.acquire()
        # Find the current thread number
        thread_num = threading.current_thread().name.split()[0]
        print(f"{thread_num} started")
        # Create socket and connect to proxy server
        clientSocket = helper.createSocket(SOCKETS)
        helper.connectSocket(clientSocket, PROXY_IP, PROXY_PORT)
        # Build request message and send to proxy
        reqMsg = buildReqMsg(pathname)
        print(reqMsg)
        clientSocket.send(reqMsg.encode())
        clientSocket.shutdown(SHUT_WR)
        print(f"{thread_num} is waiting on proxy server\n")
        THREAD_LOCK.release()
        time.sleep(5)
        
        # Wait for response from proxy server
        responseMsg = clientSocket.recv(BUFFER_SIZE).decode()
        # Lock thread after response is received
        THREAD_LOCK.acquire()
        print(f"\nResuming {thread_num}")
        print("Proxy server has responded")
        # Receive response message from proxy server
        responseMsg += helper.receiveMsg(clientSocket)
        print(responseMsg)
        print(f"{thread_num} finished\n")
        THREAD_LOCK.release()
    except:
        THREAD_LOCK.acquire()
        print(f"{thread_num}: Socket connection interrupted.\nTerminating thread.")
        helper.closeSocket(clientSocket, SOCKETS)
        THREAD_LOCK.release()

def buildReqMsg(pathname):
    """
    Constructs a request message for the proxy server.

    Parameters:
    pathname(string): Pathname that object resides on.

    Returns:
    reqMsg (string): Complete request message.
    """
    # Check that pathname starts with forward slash
    if pathname[0] != '/':
        pathname = '/' + pathname
    # Build GET message
    reqMsg = "GET " + pathname + ".html HTTP/1.1\r\n"
    reqMsg += "Host: " + PROXY_IP + ":" + str(PROXY_PORT) + "\r\n"
    reqMsg += "Accept-Language: en-US\r\n"
    reqMsg += "Connection: keep-alive\r\n"
    reqMsg += "\r\n"
    return reqMsg
    
if __name__ == "__main__":
    main()
