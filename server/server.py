import json
import struct
import os
import socket
import sys

buffer = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('127.0.0.1', 9999))
print('Server is ready!')

pack_len, addr = s.recvfrom(4)
head_len = struct.unpack('i', pack_len)[0]

json_head, addr = s.recvfrom(head_len)
json_head = json_head.decode('utf-8')
head = json.loads(json_head)
filesize = head['filesize']
filename = head['filename']

if (os.path.exists(filename)):
    info = "error"
    err = info.encode('utf-8')
    s.sendto(err, addr)

count = 0
lost = 0
l = []
rwnd = 32
with open('Myfile', 'wb') as f:
    while filesize:
        if filesize >= buffer:
            content, addr = s.recvfrom(buffer + 4)
            filesize -= buffer
            Id, data = struct.unpack('i1024s', content)
            #收到的包编号不对就舍弃
            if (Id != count):
                lost += 1
                ack = (('ACK'+str(count-1)).encode('utf-8'))
                s.sendto(ack, addr)
            #否则写入list并发送正确的ack
            else:
                count += 1
                f.write(data)
                ack = (('ACK'+str(Id)).encode('utf-8'))
                s.sendto(ack, addr)
                print(count)
        else:
            print(filesize)
            content, addr = s.recvfrom(filesize)
            mystr = str(filesize - 4)
            Id, data = struct.unpack('i'+mystr+'s', content)
            f.write(data)
            break
s.close()