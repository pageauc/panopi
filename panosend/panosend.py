#!/usr/bin/python3
'''
panosend.py -- written by Claude Pageau https://github.com/pageauc/panopi

Description:
This program will take a picamera image and
send it to the panohub.py RPI computer via zmq settings.
It will then wait for a return message containing the time for the next
image to be taken.  panohub.py will then
attempt to stitch images into a panorama image if properly overlapped.
Settings for panosend.py are set in the panhub.yaml file on panohub RPI.
The settings are transferred to each panosend.py RPI and saved as panosend.yaml
This is just a copy so don't try to edit this file since it will be overwritten.

Press Ctrl-C To End program
'''

from __future__ import print_function
PROG_VER = '0.63'
print("panosend.py: ver %s Loading ...." % PROG_VER)

import sys
import os
import time
import datetime
import socket
import numpy as np

try:
    import yaml
except ImportError:
    print('''panosend.py
    You need to install yaml python library per

    sudo pip install pyYAML
    sudo pip3 install pyYAML

    ''')
    sys.exit(1)

try:
    import picamera
except ImportError:
    print('''panosend.py: You need to install picamera library per

    sudo apt install -y python-picamera
    sudo apt install -y python3-picamera

    ''')
    sys.exit(1)

try:
    import cv2
except ImportError:
    print('''panosend.py: You need to install opencv library per

    sudo apt install -y python-opencv
    sudo apt install -y python3-opencv

    Note you may need stretch or buster for python3-opencv install
    ''')
    sys.exit(1)

try:
    import imagezmq
except ImportError:
    print('''panosend.py: You need to install imagezmq library per

    sudo pip3 install imagezmq

    ''')
    sys.exit(1)

#---------------------------------------------------------------
def read_yaml_file(yaml_file_path, yaml_section_name):
    ''' Read configuration variables from a yaml file
    per the specified yaml file path and yaml file section name.
    Only the specified yaml file section variables will be read,
    all other yaml sections will be ignored.
    '''
    if os.path.isfile(yaml_file_path):
        print("panosend.py: Read %s variables from yaml file %s" %
              (yaml_section_name, yaml_file_path))
        with open(yaml_file_path) as conf:
            config = yaml.safe_load(conf)
        try:
            for var in config[yaml_section_name]:
                globals()[str(var)] = config[yaml_section_name][var]
                print("panosend.py: %s = %s" %(str(var), config[yaml_section_name][var]))
        except KeyError:
            print('panosend.py: ERROR Could Not find yaml_section_name: %s' % yaml_section_name)
            print('                   Please verify yaml section name in file %s' % yaml_file_path)
            sys.exit(1)
    else:
        print('panosend.py: ERROR File Not Found %s' % yaml_file_path)
        print('                   Cannot Read configuration variables.')
        sys.exit(1)

#---------------------------------------------------------------
def timestamp_to_string(my_time):
    ''' Convert text string to datatime format
    '''
    return datetime.datetime.fromtimestamp(my_time).strftime('%Y/%m/%d %H:%M:%S')

#---------------------------------------------------------------
def take_stitch_image():
    ''' Take timelapse images and send over network to pano-hub.py via zmq.
    On receipt of image pano-hub.py will send reply with next timelapse timestamp
    This will ensure all panosend.py cameras take images at the same time.
    '''
    RPI_NAME = socket.gethostname()
    print('panosend.py: %s Initializing PiCamera' % RPI_NAME)
    ZMQ_PROTOCOL = 'tcp://'
    ZMQ_HUB = ZMQ_PROTOCOL + ZMQ_PANOHUB_IP + ":" + str(ZMQ_PANOHUB_PORT)
    print('panosend.py: Connect %s to %s' % (RPI_NAME, ZMQ_HUB))
    sender = imagezmq.ImageSender(connect_to=ZMQ_HUB)

    # fix rounding problems with picamera resolution
    fwidth = (CAM_WIDTH + 31) // 32 * 32
    fheight = (CAM_HEIGHT + 15) // 16 * 16
    print('panosend.py: Adjusted camera resolution roundup from %ix%i to %ix%i' %
          (CAM_WIDTH, CAM_HEIGHT, fwidth, fheight))

    with picamera.PiCamera() as camera:
        camera.resolution = (fwidth, fheight)
        camera.hflip = CAM_HFLIP
        camera.vflip = CAM_VFLIP
        image_buf = np.empty((fheight, fwidth, 3), dtype=np.uint8)
        time.sleep(2)  # Allow Camera to Warm Up
        next_timelapse = datetime.datetime.now()
        while True:
            if datetime.datetime.now() > next_timelapse:
                camera.capture(image_buf, 'bgr')
                ret_code, jpg_buffer = cv2.imencode(".jpg",
                                                    image_buf,
                                                    [int(cv2.IMWRITE_JPEG_QUALITY),
                                                     CAM_JPEG_QUALITY])
                print('panosend.py: %s ZMQ Transmit Image to Hub at %s' %
                      (ZMQ_HUB, datetime.datetime.now()))

                hub_reply = sender.send_jpg(RPI_NAME, jpg_buffer)

                # Convert reply_from zmq hub reply message to time format
                next_timelapse = datetime.datetime.strptime(hub_reply.decode('utf-8'),
                                                            '%Y/%m/%d %H:%M:%S')
                print('panosend.py: Waiting for next_timelapse at %s' %
                       hub_reply.decode('utf-8'))

#---------------------------------------------------------------
if __name__ == '__main__':

    YAML_FILEPATH = './panosend.yaml'
    YAML_SECTION_NAME = 'panosend_settings'

    # Read variable settings from yaml file.
    print('panosend.py: Import Settings from %s %s' %
          (YAML_FILEPATH, YAML_SECTION_NAME))
    read_yaml_file(YAML_FILEPATH, YAML_SECTION_NAME)
    try:
        take_stitch_image()
    except KeyboardInterrupt:
        print('')
        print('panosend.py: User Exited with ctrl-c')
        print("panosend.py: ver %s Bye ..." % PROG_VER)

