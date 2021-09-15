from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes, random
from Crypto.Protocol.KDF import PBKDF2
import socket
import sys

g = 2
p = 0x00cc81ea8157352a9e9a318aac4e33ffba80fc8da3373fb44895109e4c3ff6cedcc55c02228fccbd551a504feb4346d2aef47053311ceaba95f6c540b967b9409e9f0502e598cfc71327c5a455e2e807bede1e0b7d23fbea054b951ca964eaecae7ba842ba1fc6818c453bf19eb9c5c86e723e69a210d4b72561cab97b3fb3060b
host = sys.argv[1]
port = int(sys.argv[2])
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
            a = random.randint(100, 1000)
            A = str(pow(g, a, p))

            B = conn.recv(1024).decode()
            conn.sendall(bytes(A, 'utf-8'))
            # print('The B is:', B)

            password = str(pow(int(B), a, p))
            # print("The password is:", password)

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
    salt = get_random_bytes(16)

    full_cipher_text = b''

    b = random.randint(100, 1000)
    B = str(pow(g, b, p))

    sock2.sendall(bytes(B, 'utf-8'))

    A = sock2.recv(1024).decode()

    password = str(pow(int(A), b, p))
    # print("The password is:", password)
    key = PBKDF2(password, salt, 32, 100000)
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
