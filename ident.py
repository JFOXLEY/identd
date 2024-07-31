from os import setuid,setgid,path
from json import load
from time import time
from select import select
import socket
identf = open("name")
ident = identf.read().strip()
identf.close()
osf = open("os")
os = osf.read().strip()
osf.close()
def handle_ident(fd, host):
  print("Incoming from " + host)
  fd.settimeout(1)
  try:
    data=fd.recv(1024).strip()
    print(host + " " + str(data))
  except:
    print("Host " + host + " gave socket error")
    fd.send("0,0:ERROR:UNKNOWN-ERROR\n") # TODO: catch exceptions which are actual errors, as opposed to no-data reports
    return
  ports=data.decode("ASCII").split(',',2)
  rm_ports = []
  for i in range(len(ports)):
    ports[i] = ports[i].strip()
    if isinstance(valid_port(host, ports[i]), int):
     rm_ports.append(ports[i])
  data = ",".join(rm_ports) + ":USERID:" + os + ":" + ident  + "\n"
  print(data.strip())
  fd.send(data.encode("ASCII"))
  fd.close()
def valid_port(host, port):
  try:
    port=int(port)
  except ValueError as e:
    print("Given invalid port " + port + " by client " + host)
    return False
  if port>0 and port<65536:
    return port
  return False
if __name__=='__main__':
  pwd=path.dirname(path.realpath(__file__))
  servers=[]
  for host,port in [["", 113]]:
    if ':' in host: # TODO: write actual ip6 detection, properly?
      servers.append(socket.socket(socket.AF_INET6,socket.SOCK_STREAM))
    else:
      servers.append(socket.socket(socket.AF_INET,socket.SOCK_STREAM))
    servers[-1].setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
    servers[-1].setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT,1)
    servers[-1].bind((host,port))

    servers[-1].listen(5)
    servers[-1].setblocking(0)
  try:
   while True:
     in_ready,_,_=select(servers,[],[])
     for ready in in_ready:
       if ready in servers:
         client,addr=ready.accept()
         in_ready.append(client)
       else:
         try:
           handle_ident(ready, ":".join(list(addr)))
         except:
           pass
  except:
   print("Unexpected error (port unbound?)")