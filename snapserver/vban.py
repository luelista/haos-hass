#!/usr/bin/python

import sys,socket; sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP);
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1); sock.bind(('', 6980));
lastaddr=None
sys.stderr.write("Listening on 6980\n")
while True:
  data, addr = sock.recvfrom(1024)
  if addr != lastaddr:
    sys.stderr.write("Now receiving from address: " + str(addr) + "\n")
    lastaddr = addr
  sys.stdout.buffer.write(data[28:])
