#!/usr/bin/python3
'''
panowatch.py will normally run as a background task. It will
receive data from panohub.py and restarts or stop panosend.py
A restart will create an updated panosend.yaml file based
on the message received from panohub.py.

'''
import time
import zmq
import socket
import sys
import subprocess

# Watcher.py Settings

PANOSEND_YAML_FILEPATH = './panosend.yaml'
PANOSEND_STOP_CMD = './panosend.sh stop'
PANOSEND_RESTART_CMD = './panosend.sh restart'

ZMQ_WATCH_LOCKOUT = 1    # seconds to sleep before receiving next message
ZMQ_WATCH_PROTOCOL = 'tcp://'
ZMQ_WATCH_HOST = '*:'
ZMQ_WATCH_PORT = '5556'
ZMQ_WATCH_CONNECT = (ZMQ_WATCH_PROTOCOL +
                     ZMQ_WATCH_HOST +
                     ZMQ_WATCH_PORT)

PROG_VER = '0.5'

#---------------------------------------------------------------
def write_yaml_file(filepath, data):
    ''' Save data into a yaml filepath
    '''
    with open(filepath, 'w') as yaml_file:
        yaml_file.write(data)
    print('panowatch.py: Saved yaml data to %s' % filepath)

#---------------------------------------------------------------
def bytes_to_string(byte_str):
    ''' Convert a byte stream to a string
    '''
    return "".join(map(chr, byte_str))

# Start of Main Program Code

print("panowatch.py: ZMQ Connect ...")
WATCHER_HOST_NAME = (socket.gethostname()).encode('utf-8') + b'.local'
WATCHER_HOST_IP = (socket.gethostbyname(WATCHER_HOST_NAME)).encode('utf-8')
print('panowatch.py: Host: %s IP: %s' % (WATCHER_HOST_NAME, WATCHER_HOST_IP))

context = zmq.Context()
panohub = context.socket(zmq.REP)
panohub.bind(ZMQ_WATCH_CONNECT)

while True:
    print('panowatch.py: Waiting for yaml_data ...')
    yaml_data = panohub.recv()  # Wait for hub
    print("panowatch.py: Got yaml_data from %s pano_hub.py")
    panohub.send(WATCHER_HOST_IP) # send ip as string to hub
    if yaml_data == b'stop':
        print('panowatch.py: Stop panosend.py')
        return_val = subprocess.call(PANOSEND_STOP_CMD, shell=True)
    else:
        print('panowatch.py: Restart panosend.py')
        yaml_str = bytes_to_string(yaml_data)
        write_yaml_file(PANOSEND_YAML_FILEPATH, yaml_str)
        return_val = subprocess.call(PANOSEND_RESTART_CMD, shell=True)
    print('panowatch.py: panosend.sh return value is %i' % return_val)
    time.sleep(ZMQ_WATCH_LOCKOUT)

