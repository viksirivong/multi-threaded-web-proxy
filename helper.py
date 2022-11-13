from socket import *
import sys
import time
import os
import datetime

BUFFER_SIZE = 2048

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
        # sockets.append(tempSocket)
        return tempSocket
    except:
        print(f"Failed to create TCP IPv4 socket for {str}.")
        print("Program terminated.")
        # closeAllSockets(sockets)
        sys.exit()

def closeAllSockets(sockets):
    """
    Closes all currently open sockets.

    Parameters:
    sockets (list): List of created sockets.
    """
    print("Closing all sockets.\n")
    for soc in sockets:
        try:
            soc.close()
            print("Closed:", soc, "\n")
        except:
            print("Failed to close:", soc, "\n")
    sockets.clear()
    print("Finished closing all the sockets.\n")

def closeSocket(soc):
    """
    Close the socket passed as an argument.

    Parameters:
    soc (socket): Socket to be closed
    sockets (list): List of created sockets.
    """
    try:
        soc.close()
        print("Closed:", soc, "\n")
        #sockets.remove(soc)
    except:
        print("Failed to close:", soc, "\n")

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
    
##def connectSocket(soc, ip, port):
##    """
##    Initiate connection to (ip, port).
##    
##    Parameters:
##    soc (socket): Socket initiating the connection.
##    ip (string): IP address to connect to.
##    port (int): Port number to connect to.
##    """
##    attempts = 0
##    maxAttempts = 5
##    #print("Attempting to connect to socket.")
##    while attempts < maxAttempts:
##        try:
##            soc.connect( (ip, port) )
##            print(f"Connected to: {ip}:{port}")
##            return
##        except:
##            attempts += 1
##    print(f"Failed to initiate connection to {ip}:{port}.")
##     raise

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
        #closeAllSockets(sockets)
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
        dt = acquireDatetime(pathname)
        msgs += "If-modified-since: " + dt + "\r\n"
    return msg

def acquireDatetime(pathname):
    fileTime = time.ctime(os.path.getmtime(pathname[1:]))
    fileDatetime = datetime.datetime.strptime(fileTime, "%a %b %d %H:%M:%S %Y")
    return fileDatetime

def sendData(soc, data):
    for i in range(0, len(data)):
        soc.send(data[i].encode())
