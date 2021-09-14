from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes, random
from Crypto.Protocol.KDF import PBKDF2
import socket
import select
import sys

host = sys.argv[1]
port = int(sys.argv[2])
target_host = sys.argv[3]
target_port = int(sys.argv[4])
header = 1024
g = 2
p = 0x00cc81ea8157352a9e9a318aac4e33ffba80fc8da3373fb44895109e4c3ff6cedcc55c02228fccbd551a504feb4346d2aef47053311ceaba95f6c540b967b9409e9f0502e598cfc71327c5a455e2e807bede1e0b7d23fbea054b951ca964eaecae7ba842ba1fc6818c453bf19eb9c5c86e723e69a210d4b72561cab97b3fb3060b

a = random.randint(100, 1000)
A = str(pow(g, a, p))

b = random.randint(100, 1000)
B = str(pow(g, b, p))

sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock2.bind(('127.0.0.2', port))
sock2.listen(1)
(conn, address) = sock2.accept()

B_client = conn.recv(1024).decode()
conn.sendall(bytes(A, 'utf-8'))
password_client = str(pow(int(B_client), a, p))

nonce_client = conn.recv(16)
# print("The nonce from actual client is: ", nonce_client)
salt_client = conn.recv(16)
# print("The salt from actual client is:", salt_client)
key_client = PBKDF2(password_client, salt_client, 32, 100000)
# print("The Key between me and client is:", key_client)
cipher_client = AES.new(key_client, AES.MODE_GCM, nonce_client)
tag_client = conn.recv(16)
# print("The tag between me and client is:", tag_client)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((target_host, target_port))
sock.sendall(bytes(B, 'utf-8'))
A_server = sock.recv(1024).decode()
my_salt = get_random_bytes(16)
# print("The salt from me to server is:", my_salt)
my_password = str(pow(int(A_server), b, p))
my_key = PBKDF2(my_password, my_salt, 32, 100000)
# print("The Key between me and server is:", my_key)
my_cipher = AES.new(my_key, AES.MODE_GCM)
# print("My nonce is: ", my_cipher.nonce)
sock.sendall(my_cipher.nonce)  # Sending the Cipher Initialization vector
sock.sendall(my_salt)


# enc_from_client = conn.recv(1024)
# dec_from_client = cipher_client.decrypt(enc_from_client)
# print("Data Received from client is:", dec_from_client)
#
# my_data = b'This is the middle man'
# my_enc = my_cipher.encrypt(my_data)
# my_tag = my_cipher.digest()
# print("My tag is:  ", my_tag)
# sock.sendall(my_tag)
# sock.sendall(my_enc)

flag1 = False
flag2 = True
total_dec_data = b''
my_total_enc_data = b''

while flag1 or flag2:
    rlist, wlist, errlist = select.select([conn], [sock], [])
    if sock in wlist and flag1:
        my_tag = my_cipher.digest()
        sock.sendall(my_tag)
        sock.sendall(my_total_enc_data)
        flag1 = False

    if conn in rlist and flag2:
        enc_data = conn.recv(1024)
        if not enc_data:
            try:
                cipher_client.verify(tag_client)
            except ValueError:
                sys.stderr.write("Error: Integrity check failed")
            flag1 = True
            flag2 = False
        else:
            dec_data = cipher_client.decrypt(enc_data)
            # sys.stdout.buffer.write(dec_data)
            my_enc_data = my_cipher.encrypt(dec_data)
            my_total_enc_data += my_enc_data
            total_dec_data += dec_data

sock.close()
conn.close()


