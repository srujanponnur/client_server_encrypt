User: sponnur
Student Id:200417755


 
Part 4: The proxy is listenting to 127.0.0.2 on a given port.

Example:

python3 eft-dh.py -l 2424 > output.txt #server

python3 dh-proxy.py -l 2424 localhost 2424   #proxy

python3 eft-dh.py 127.0.0.2 2424 < input.txt  #client
