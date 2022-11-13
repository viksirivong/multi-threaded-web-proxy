from socket import *
import sys
import time
import os
import datetime
import threading

BUFFER_SIZE = 2048
THREAD_LOCK = threading.Lock()

def createSocket(str):
    """
    Create a TCP socket (AF_INET, SOCK_STREAM).
    If it fails to create a socket, then the program will terminate.

    Parameters:
    sockets (list): List of created sockets.

    Returns:
    tempSocket (socket): Created socket.
    """
    try:
        tempSocket = socket(AF_INET, SOCK_STREAM)
        print(f"TCP IPv4 socket created for {str}.")
        return tempSocket
    except:
        print(f"Failed to create TCP IPv4 socket for {str}.")
        print("Program terminated.")
        sys.exit()

def closeSocket(soc):
    """
    Close the socket passed as an argument.

    Parameters:
    soc (socket): Socket to be closed
    sockets (list): List of created sockets.
    """
    try:
        soc.close()
        print("Closed:", soc)
    except:
        print("Failed to close:", soc)

def connectSocket(soc, ip, port):
    """
    Initiate connection to (ip, port).
    
    Parameters:
    soc (socket): Socket initiating the connection.
    ip (string): IP address to connect to.
    port (int): Port number to connect to.
    """

    try:
        soc.connect( (ip, port) )
        print(f"Connected to: {ip}:{port}")
        return 1
    except:
        print(f"Failed to initiate connection to {ip}:{port}.")
        return -1

def bindSocket(soc, port):
    """
    Bind the port number to the socket and set it to listen.

    Paramaeters:
    soc (socket): Socket to listen.
    port (int): Port number to bind.
    sockets (list): List of created sockets.
    """
    try:
        soc.bind( ('', port) )
        soc.listen(5)
        print("Port number is binded and the socket listening.")
    except:
        print("Failed to bind port number. Program terminating.")
        sys.exit()

def receiveMsg(soc):
    """
    Receives encoded message and concatonates all the data.
    Once 0 bytes are received, the message is returned.

    Parameters:
    soc (socket): Socket that data will be received from.

    Returns:
    msg (string): Message received through socket. 
    """
    msg = ''
    while True:
        data = soc.recv(BUFFER_SIZE).decode()
        if not data: break
        msg += data
    return msg

def shutdownSocket(soc, code):
    if code == SHUT_WR:
        print("Further sends are disallowed on this socket.")
    elif code == SHUT_RD:
        print("Further receives are disallowed on this socket.")
    elif code == SHUT_RDWR:
        print("Further sends and receives are disallowed on this socket.")
    else:
        print("An error occurred while using socket.SHUT()")
    soc.shutdown(code)
    return

def buildReqMsg(pathname, port, ip):
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
    reqMsg += "Host: " + ip + ":" + str(port) + "\r\n"
    reqMsg += "Accept-Language: en-US\r\n"
    reqMsg += "Connection: keep-alive\r\n"
    reqMsg += "\r\n"
    return reqMsg

def buildCondGET(pathname, hostname):
    msg = "GET " + pathname + " HTTP/1.1\r\n"
    msg += "Host: " + hostname + "\r\n"
    if os.path.exists(pathname[1:]):
        dayOfWeek, month, day, time, year = acquireFileDate(pathname)
        msg += "If-modified-since: " + dayOfWeek + ", " + day + " " + month + " " + year + " " + time + "\r\n"
    return msg

def acquireDatetime(pathname):
    fileTime = time.ctime(os.path.getmtime(pathname[1:]))
    fileDatetime = datetime.datetime.strptime(fileTime, "%a %b %d %H:%M:%S %Y")
    return fileDatetime

def sendData(soc, data):
    for i in range(0, len(data)):
        soc.send(data[i].encode())

def sendUpdatedFile(pathname, file, soc):
    print("enter sendUpdatedFile()")
    dayOfWeek, month, day, time, year = acquireFileDate(pathname)
    outputdata = file.readlines()
    print(outputdata)
    soc.send("HTTP/1.1 200 OK\r\n".encode())
    soc.send( ("Last-modified: " + dayOfWeek + ", " + day + " " + month + " " + year + " " + " " + time + "\r\n").encode() )
    soc.send("\r\n".encode())
    for i in range(0, len(outputdata)):
        soc.send(outputdata[i].encode())
    soc.send("\r\n".encode())
    print("exit sendUpdatedFile()")

def acquireFileDate(pathname):
    """
    [Day of the week, month, day, time, year]
    """
    data = time.ctime(os.path.getmtime(pathname[1:])).split()
    return data[0], data[1], data[2], data[3], data[4]

def convertToDatetime(msg):
    fileTime = msg[6][0:3]
    for i in range(7, len(msg)):
        fileTime = fileTime + " " + msg[i]
    fileDatetime = datetime.datetime.strptime(fileTime, "%a %d %b %Y %H:%M:%S")
    return fileDatetime
