import json
import struct
import os
import socket
import time
import sys

buffer = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
IP_PORT = ('127.0.0.1', 9999)

print('Please input your file name:')
file_name = input()
print('Client is ready!')
head = {'filepath':r'C:\Users\17980\Desktop\LFTP',
    'filename':file_name,
    'filesize':None}
try:
    file_path = os.path.join(head['filepath'], head['filename'])
    file_size = os.path.getsize(file_path)
except:
    print("Can't find the file.\nSocket is closed")
    sys.exit()
head['filesize'] = file_size

json_head = json.dumps(head)
bytes_head = json_head.encode('utf-8')

head_len = len(bytes_head)
pack_len = struct.pack('i', head_len)

s.sendto(pack_len, IP_PORT)
s.sendto(bytes_head, IP_PORT)

err = s.recv(1024).decode('utf-8')
if (err == "error"):
    print("Socket is closed.\nThe file is existed.")
    sys.exit()

count = 0
repeat = 0
cwnd = 1
ssthresh = 32
send_num = cwnd
first = True
ACKnum = 0
with open(file_path, 'rb') as f:
    last_ack = ''
    while file_size:
        if (file_size >= 0):
            #每次发送cwnd个分组
            while send_num:
                content = struct.pack('i1024s', count, f.read(buffer))  
                s.sendto(content, IP_PORT)
                file_size -= buffer
                count += 1
                send_num -= 1
                print("ack"+str(ACKnum), "and num"+str(count), "has been sent.")
                # time.sleep(0.1)
            ACKnum += 1

            #接收
            current_ack = s.recv(1024).decode('utf-8')
            print(current_ack, "and num"+str(count), "has been received.")
            #重复
            if current_ack == last_ack:
                repeat += 1
            last_ack = current_ack
            #出现丢包cwnd减半
            if repeat == 3:
                cwnd /= 2
                first = False
                break

            #没有重复的ack则cwnd翻倍
            if repeat == 0:
                if cwnd < ssthresh:
                    cwnd *= 2
                else:
                    cwnd += 1
            repeat = 0    
            
            #如果收到了正确的ACK则继续发
            if ACKnum - 1 == int(current_ack[3:]):
                send_num = cwnd

            #否则重新发送 增大file_size设置num
            else:
                ssthresh = cwnd/2
                n = last_ack[3:]
                send_num = count-int(n)-1
                for i in range(send_num):
                    file_size += buffer
        else:
            print("The file has been sent.\nSocket is closed.")
            exit()
            break