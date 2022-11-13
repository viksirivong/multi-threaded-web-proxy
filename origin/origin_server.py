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

PROXY_PORT = 80
ORIGIN_PORT = 90
ORIGIN_IP = "127.0.0.1"
BUFFER_SIZE = 2048
THREAD_LOCK = threading.Lock()

def main():
    # Create origin server socket
    originSocket = helper.createSocket("origin")
    # Bind origin socket and set to listen
    helper.bindSocket(originSocket, ORIGIN_PORT)
    # Accept requests from proxy server
    while True:
        time.sleep(1)
        THREAD_LOCK.acquire()
        print("Origin server is ready to receive...")
        THREAD_LOCK.release()
        proxySocket, addr = originSocket.accept()
        t = threading.Thread(target=originThreading, args=((proxySocket,)) )
        t.start()
    t.join()

def originThreading(proxySocket):
    try:
        condGetMsg = proxySocket.recv(BUFFER_SIZE).decode()
        THREAD_LOCK.acquire()
        condGetMsg += helper.receiveMsg(proxySocket)
        #condGetMsg = condGetMsg.split()
        pathname = condGetMsg[1]
        thread_num = threading.current_thread().name.split()[0]
        print(f"\n{thread_num} created:")
        print("Origin server received conditional GET message from proxy server.")
        THREAD_LOCK.release()
        condGetMsg = condGetMsg.split()
        pathname = condGetMsg[1]

        # File found by origin server
        if os.path.exists(pathname[1:]):
            file = open(pathname[1:], "r")
            # conditional GET message has a if-modified-since header line
            if len(condGetMsg) > 5:
                originFileDatetime = helper.acquireDatetime(pathname)
                proxyFileDatetime = helper.convertToDatetime(condGetMsg)
                THREAD_LOCK.acquire()
                print(f"\n{thread_num} resumed:")
                if proxyFileDatetime >= originFileDatetime:
                    print("Proxy server file is up to date.")
                    proxySocket.send("HTTP/1.1 304 Not Modified\r\n".encode())
                    proxySocket.send("\r\n".encode())
                    proxySocket.shutdown(SHUT_WR)
                    print("Status code 304 sent.")
                # proxyFileDatetime < originFileDatetime
                else:
                    print("Origin server file is newer.")
                    helper.sendUpdatedFile(pathname, file, proxySocket)
                    proxySocket.shutdown(SHUT_WR)
                    print("Sent status code 200 with updated file data to proxy server.")
                THREAD_LOCK.release()
            # File not found by origin server
            else:
                THREAD_LOCK.acquire()
                print(f"\n{thread_num} resumed:")
                print("Origin server file is newer.")
                helper.sendUpdatedFile(pathname, file, proxySocket)
                proxySocket.shutdown(SHUT_WR)
                print("Sent status code 200 with updated file data to proxy server.")
                THREAD_LOCK.release()
        # File not found by origin server
        else:
            THREAD_LOCK.acquire()
            print(f"\n{thread_num} resumed:")
            print("File Not Found in origin server.")
            proxySocket.send("HTTP/1.1 404 Not Found\r\n".encode())
            proxySocket.send("\r\n".encode())
            print("Status code 404 sent.")
            proxySocket.shutdown(SHUT_WR)
            #helper.closeSocket(proxySocket)
            #print(f"{thread_num} finished")
            THREAD_LOCK.release()
        THREAD_LOCK.acquire()
        print(f"\n{thread_num} resumed:")
        proxySocket.shutdown(SHUT_RDWR)
        print("Attempting to close proxy socket.")
        helper.closeSocket(proxySocket)
        print(f"{thread_num} finished.")
        THREAD_LOCK.release()
    except:
        THREAD_LOCK.acquire()
        print(f"\n{thread_num}: Socket connection interrupted.")
        print("Terminating thread.")
        print("Attempting to close proxy socket.")
        helper.closeSocket(proxySocket)
        THREAD_LOCK.release()
    
    
if __name__ == "__main__":
    main()
