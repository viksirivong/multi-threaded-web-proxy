"""
Group: Ricardo Garcia, Thongsavik Sirivong, and Renato Safra
Project: Multi-threaded web proxy server
Files: client.py, proxy_server.py, origin_server.py, and helper.py
Date: 11/13/22
Description: All the functions used in the client, proxy, and origin programs. 
"""
from socket import *
import sys
import time
import os
import datetime
import threading

BUFFER_SIZE = 2048
THREAD_LOCK = threading.Lock()

def createSocket(socName):
    """
    Create a TCP socket (AF_INET, SOCK_STREAM).
    If it fails to create a socket, then the program will terminate.

    Parameters:
    socName (string): Name of socket created.
    """
    try:
        tempSocket = socket(AF_INET, SOCK_STREAM)
        print(f"TCP IPv4 socket created for {socName}.")
        return tempSocket
    except:
        print(f"Failed to create TCP IPv4 socket for {socName}.")
        print("Program terminated.")
        sys.exit()

def closeSocket(soc):
    """
    Close the socket passed as an argument.

    Parameters:
    soc (socket): Socket to be closed.
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

    Returns:
    int (int): Error code. 
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
    If it fails, then the program will terminate.

    Paramaeters:
    soc (socket): Socket to listen.
    port (int): Port number to bind.
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
    Once zero bytes are received, the message is returned.

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
    """
    Constructs a conditional GET message.

    Parameters:
    pathname (string): Pathname for the html file. 
    hostname (string): Hostname where the object resides.

    Returns:
    msg (string): conditional GET message in string format. 
    """
    msg = "GET " + pathname + " HTTP/1.1\r\n"
    msg += "Host: " + hostname + "\r\n"
    # If file exists, then add the 'if-modified-since' header line.
    if os.path.exists(pathname[1:]):
        dayOfWeek, month, day, time, year = acquireFileDate(pathname)
        msg += "If-modified-since: " + dayOfWeek + ", " + day + " " + month + " " + year + " " + time + "\r\n"
    return msg

def acquireDatetime(pathname):
    """
    Discovers the date and time associated with the html file (pathname)
    and converts it to a datetime object.
    Example of datetime format: 2022-10-06 09:23:18

    Parameters:
    pathname (string): Pathname for the html file.

    Returns:
    fileDatetime (datetime): Datetime object in '2022-10-06 09:23:18' format.
    """
    fileTime = time.ctime(os.path.getmtime(pathname[1:]))
    fileDatetime = datetime.datetime.strptime(fileTime, "%a %b %d %H:%M:%S %Y")
    return fileDatetime

def sendData(soc, data):
    """
    Sends data to socket.
    
    Parameters:
    soc (socket): Socket data being sent to.
    data (array): Data that is sent. 
    """
    for i in range(0, len(data)):
        soc.send(data[i].encode())

def sendUpdatedFile(pathname, file, soc):
    """
    Sends entire response message (status line, header line, and entity body)
    through the socket connection.

    Parameters:
    pathname (string): File name
    file (html object): File object for html file
    soc (socket): Socket that response message will be sent to. 
    """
    dayOfWeek, month, day, time, year = acquireFileDate(pathname)
    outputdata = file.readlines()
    # status line and header line
    soc.send("HTTP/1.1 200 OK\r\n".encode())
    soc.send( ("Last-modified: " + dayOfWeek + ", " + day + " " + month + " " + year + " " + " " + time + "\r\n").encode() )
    soc.send("\r\n".encode())
    # entity body
    for i in range(0, len(outputdata)):
        soc.send(outputdata[i].encode())
    soc.send("\r\n".encode())

def acquireFileDate(pathname):
    """
    Acquires the time and date from the file (pathname)
    and returns their respetive values individually.
    
    Parameters:
    pathname (string): File name.
    
    Returns:
    data[0] (string): Day of the week
    data[1] (string): Month
    data[2] (string): Day
    data[3] (string): Time
    data[4] (string): Year
    """
    data = time.ctime(os.path.getmtime(pathname[1:])).split()
    return data[0], data[1], data[2], data[3], data[4]

def convertToDatetime(msg):
    """
    Converts a string that holds the date and time to a
    datetime object in format '2022-10-06 09:23:18'.

    Parameters:
    msg (string): String message that has date and time.

    Returns:
    fileDatetime (datetime): Datetime object in '2022-10-06 09:23:18' format.
    """
    fileTime = msg[6][0:3]
    for i in range(7, len(msg)):
        fileTime = fileTime + " " + msg[i]
    fileDatetime = datetime.datetime.strptime(fileTime, "%a %d %b %Y %H:%M:%S")
    return fileDatetime
