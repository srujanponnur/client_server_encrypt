
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
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('localhost', port))
        sock.listen()
        # print("The Server Started Listening...")
        (conn, address) = sock.accept()
        with conn:
            result_enc_data = b''
            nonce = conn.recv(16)
            # print("The nonce is: ", nonce)
            salt = conn.recv(16)
            # print('The salt is', salt)
            key = PBKDF2(password, salt, 32, 100000)
            # print("The key is", key)
            cipher = AES.new(key, AES.MODE_GCM, nonce)
            tag = conn.recv(16)
            # print("The tag is\n", tag)
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                enc_data = cipher.decrypt(data)
                sys.stdout.buffer.write(enc_data)
                result_enc_data += data
            # print("The total data received is", result_enc_data)
            cipher.verify(tag)
            # print("Successfully verified")
            sock.close()
    except ValueError:
        sys.stderr.write("Error: Integrity check failed\n")

else:  # Client starts here
    sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock2.connect((host, port))
    # fileInput = input()
    salt = get_random_bytes(16)
    key = PBKDF2(password, salt, 32, 100000)
    full_cipher_text = b''
    # print("The data is:", data)
    currentData = None
    cipher = AES.new(key, AES.MODE_GCM)
    # print('Nonce: ', cipher.nonce)
    # print('The salt', salt)
    # print("The key is", key)
    sock2.sendall(cipher.nonce)  # Sending the Cipher Initialization vector
    sock2.sendall(salt)
    with open(0, 'rb') as fd:
        while True:
            data = fd.read(1024)
            if not data:
                break
            ciphertext = cipher.encrypt(data)
            full_cipher_text += ciphertext
    tag = cipher.digest()
    # print('The tag is', tag)
    sock2.sendall(tag)
    # print('Fully encrypted data is : ',full_cipher_text)
    sock2.sendall(full_cipher_text)
    sock2.close()
