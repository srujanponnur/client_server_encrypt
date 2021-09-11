import socket
import sys


host = sys.argv[1]
port = int(sys.argv[2])

# Server starts here
if host == '-l':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', port))
    sock.listen()
    (conn, address) = sock.accept()
    prev_data = data = None
    index = 1
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            sys.stdout.buffer.write(data)
        sock.close()

else:  # Client starts here
    sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock2.connect((host, port))
    currentData = b''
    with open(0, 'rb') as fd:
        while True:
            data = fd.read(1024)
            if not data:
                break
            currentData += data
            sock2.sendall(data)
    sock2.close()
