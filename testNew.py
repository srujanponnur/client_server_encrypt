
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
import socket
import sys


password = sys.argv[2]
host = sys.argv[3]
port = int(sys.argv[4])
header = 1024

# Server starts here
if host == '-l':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', port))
    sock.listen()
    #print("The Server Started Listening...")
    (conn, address) = sock.accept()
    with conn:
        #("Accepted a connection here", address)
        #print("Receiving the nonce first")
        result_enc_data = b''
        nonce = conn.recv(16)
        #print("The nonce is: ", nonce)

        #print("Receiving the salt now")
        salt = conn.recv(16)
        #print("Receiving the tag now")
        tag = conn.recv(16)
        #print("The tag is", tag)
        #print("Receiving data now...")
        while True:
            data = conn.recv(1024)
            print('partial output:', data)
            if not data:
                break
            result_enc_data += data
        #print("Received data is", result_enc_data)

        key = PBKDF2(password, salt, 16, 100000)
        #print("The key is", key)
        cipher = AES.new(key, AES.MODE_GCM, nonce)
        result_dec_data = cipher.decrypt(result_enc_data)
        print(result_dec_data.decode()),
        sock.close()

else:  # Client starts here
    sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock2.connect((host, port))
    # fileInput = input()
    salt = get_random_bytes(16)
    key = PBKDF2(password, salt, 16, 100000)
    EOI = b''
    # print("The key is", key)
    # print("The data is:", data)
    currentData = None
    cipher = AES.new(key, AES.MODE_GCM)
    with open(0, 'r') as fd:
        currentData = fd.read(1024)
    print('The current data read is', currentData)
    data = str.encode(currentData)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    print('Nonce: ', cipher.nonce)
    print('The tag', tag)
    print('The salt', salt)
    print('The cipher text is: ', ciphertext)
    sock2.sendall(cipher.nonce)  # Sending the Cipher Initialization vector
    sock2.sendall(salt)
    sock2.sendall(tag)
    sock2.sendall(ciphertext)
    sock2.close()

# file_out = open("encrypted.bin", "wb")
# [ file_out.write(x) for x in (cipher.nonce, tag, ciphertext) ]
# file_out.close()

# print(ciphertext)
# nonce = cipher.nonce
# cipher = AES.new(key, AES.MODE_GCM, nonce)
# print(cipher.decrypt_and_verify(ciphertext, tag))
