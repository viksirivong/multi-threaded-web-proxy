SIZE = 1024
FORMAT = "utf-8"

def handle_client(connection, addr):
    print(f"[NEW CONNECTION] {addr}")
    
    try:
        message = connection.recv(SIZE).decode(FORMAT)
        filename = message.split()[1]
        f = open(filename[1:])
        outputData = f.read()

        # Send on HTP eader line into socket
        connection.send("\nHTTP/1.1 200 OK\r\n\r\n".encode(FORMAT))
        
        # Send the content of the requested file to the client
        for i in range(0, len(outputData)):
            connection.send(outputData[i].encode(FORMAT))
        connection.send("\r\n".encode(FORMAT))

        connection.close()
    except IOError:
        # Send response message for file not found
        connection.send("\nHTTP/1.1 404 NOT FOUND\r\n\r\n".encode(FORMAT))

        connection.close()