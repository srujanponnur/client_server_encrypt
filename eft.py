import socket
import sys


host = sys.argv[1]
port = int(sys.argv[2])

# Server starts here
if host == '-l':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', port))
    sock.listen()
    print("The Server Started Listening...")
    (conn, address) = sock.accept()
    with conn:
        print("Accepted a connection here", address)
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print(data.decode())
        sock.close()

else:  # Client starts here
    sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock2.connect((host, port))
    fileInput = input()
    print("Client is sending the data")
    sock2.sendall(str.encode(fileInput))
    sock2.close()
