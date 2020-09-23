#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
panohub.py -- written by Claude Pageau https://github.com/pageauc

Description:
A simple program that uses imagezmq to receive images from
multiple network computers running pano-send.py and stitch images
to produce a stitched panoramic image. Camera resolution setting
is configured in the pano-send.py file.
Note: images need to properly overlap for stitching to be successful.

Press Ctrl-C To End programs
'''

from __future__ import print_function
print('panohub.py: Loading ...')
import os
import sys
import socket
import time
import datetime
import subprocess
import numpy as np

try:
    import zmq
except ImportError:
    print('''panohub.py: You need to install ZMQ python library per

    sudo pip install pyzmq
    sudo pip3 install pyzmq

    ''')
    sys.exit(1)

try:
    import yaml
except ImportError:
    print('''panohub.py: You need to install yaml python library per

    sudo pip install pyYAML
    sudo pip3 install pyYAML

    ''')
    sys.exit(1)

try:
    import cv2
except ImportError:
    print('''panohub.py: You need to install opencv python library per

    sudo apt install -y python-opencv
    sudo apt install -y python3-opencv

    Note you may need stretch or buster for python3 install
    ''')
    sys.exit(1)

try:
    import imagezmq
except ImportError:
    print('''panohub.py: You need to install imagezmq python library per

    sudo pip install imagezmq
    sudo pip3 install imagezmq

    Note you may need stretch or buster for python3 install
    ''')
    sys.exit(1)


# System Calculated Settings
# --------------------------
# Find the full path of this python script
MY_PATH = os.path.abspath(__file__)
# get the path location only (excluding script name)
BASE_DIR = os.path.dirname(MY_PATH)
BASE_FILENAME = os.path.splitext(os.path.basename(MY_PATH))[0]
PROG_NAME = os.path.basename(__file__)
PROG_VER = 'ver 0.61'

# Yaml File Settings to read variables
YAML_FILEPATH = './panohub.yaml'
YAML_SECTION_NAME = 'panohub_settings'
YAML_PANOSEND_SECTION_NAME = 'panosend_settings'
TIMELAPSE_SEQ_COUNTER_PATH = os.path.join(BASE_DIR, BASE_FILENAME + '.dat')

def read_yaml_to_stream(yaml_file_path, yaml_section_name):
    '''
    Read configuration variables from a yaml file per the specified
    yaml file path and yaml file section name.
    Only the specified yaml file section variables will be read, all other yaml
    sections will be ignored.
    '''
    yaml_stream = 'panosend_settings:\n' + '\n'
    if os.path.isfile(yaml_file_path):
        print("panohub.py: Read %s section from yaml file %s" % (yaml_section_name, yaml_file_path))
        yaml_stream = YAML_PANOSEND_SECTION_NAME + ':\n'
        with open(yaml_file_path) as conf:
            config = yaml.safe_load(conf)
            for var in config[yaml_section_name]:
                if str(var) == 'ZMQ_PANO_HUB_IP':
                    config[yaml_section_name][var] = socket.gethostbyname(socket.gethostname() + '.local')
                yaml_stream += '    ' + var + ' : ' + str(config[yaml_section_name][var]) + '\n'
        return yaml_stream.encode('ascii')
    else:
        print('panohub.py: ERROR: File Not Found %s' % yaml_file_path)
        print('            Cannot Read configuration variables.')
        sys.exit(1)

#---------------------------------------------------------------
def get_remote_host_ip(remote_host_name):
    '''
    Get ip address of a fully qualified hostname and
    return the ip address of the host. Return None if
    there is a socket error and print warning message.
    '''
    try:
        ip = socket.gethostbyname(remote_host_name)
    except socket.error as err_msg:
        print("panohub.py: WARN hostname: %s  %s" %(remote_host_name, err_msg))
        ip = None
    return ip

#---------------------------------------------------------------
def get_senders(host_list):
    '''
    Take a list of host names, get associated ip address
    for for valid hostnames and return a dictionary with
    hostname as key and ip address and tcp port list as value.
    '''
    host_dict = {}
    for hostname in host_list:
        ip_addr = get_remote_host_ip(hostname)
        if ip_addr is not None:
            host_dict.update({hostname:[ip_addr, ZMQ_WATCH_PORT]})
            print('panohub.py: %s zmq connect at tcp://%s:%s' % (hostname, ip_addr, ZMQ_WATCH_PORT))
    return host_dict

#---------------------------------------------------------------
def notify_senders(host_list, restart=True):
    '''
    Notify watcher.py per list of host, send yaml settings data
    to each host and restart or stop panosend.py as appropriate
    This will ensure panosend is always started after panohub.py
    '''

    if restart:
        yaml_data = read_yaml_to_stream(YAML_FILEPATH, YAML_PANOSEND_SECTION_NAME)
        print('panohub.py: Restart panosend.py on remote hosts')
    else:
        yaml_data = b'stop'
        print('panohub.py: Kill panosend.py on remote hosts')

    pano_senders = get_senders(host_list)

    for key, val in pano_senders.items():
        host_name = pano_senders[key]
        ip, port = val  # Read sender connection details
        ip_addr = ip.encode('utf-8')
        print('panohub.py: %s Connect' % key)
        context = zmq.Context()
        sender = context.socket(zmq.REQ)
        sender.connect(ZMQ_PROTOCOL + ip + ":" + port)
        print('panohub.py: %s Send yaml data at %s:%s' % (key, ip, port))
        reply_from = b''
        while not (reply_from == ip_addr):
            sender.send(yaml_data)
            reply_from = sender.recv()
            if reply_from == ip_addr:
                print('panohub.py: Success: Got Reply from %s' % reply_from)
            else:
                print('panohub.py: Retry .. Got Reply from %s instead of %s' % (reply_from, ip_addr))
            time.sleep(0.2)  # Allow short delay before retry.

#---------------------------------------------------------------
def read_yaml_vars(yaml_file_path, yaml_section_name):
    '''
    Read configuration variables from a yaml file
    per the specified yaml file path and yaml file section name.
    Only the specified yaml file section variables will be read,
    all other yaml sections will be ignored.
    '''
    if os.path.isfile(yaml_file_path):
        print("panohub.py: Read %s section from yaml file %s" %
              (yaml_section_name, yaml_file_path))
        print('panohub.py: ----- Begin %s ------' % yaml_section_name)
        with open(yaml_file_path) as conf:
            config = yaml.safe_load(conf)

        for var in config[yaml_section_name]:
            globals()[str(var)] = config[yaml_section_name][var]
            print("panohub.py: %s = %s" %(str(var), config[yaml_section_name][var]))
        print('panohub.py: ----- End %s ------' % yaml_section_name)
    else:
        print('panohub.py: ERROR: File Not Found %s' % yaml_file_path)
        print('            Cannot Read configuration variables.')
        sys.exit(1)

#---------------------------------------------------------------
def make_ip_dict(host_list):
    '''
    Take a list of host names, get associated ip address
    for for valid hostnames and return a dictionary with
    hostname as key and ip address a key value.
    '''
    host_dict = {}
    for hostname in host_list:
        ip_addr = get_remote_host_ip(hostname)
        if ip_addr is not None:
            host_dict.update({hostname:ip_addr})
    return host_dict

#---------------------------------------------------------------
def write_seq_num(counter, counter_path):
    '''
    Save the current sequence number to a .dat
    file to allow continuing sequence after restart.
    '''
    if not os.path.isfile(counter_path):
        print('panohub.py: Create New Counter File SEQ_NUM=%s %s' %
              (counter, counter_path))
        open(counter_path, 'w').close()
    f = open(counter_path, 'w+')
    f.write(str(counter))
    f.close()
    print('panohub.py: Next SEQ_NUM=%s %s' % (counter, counter_path))

#---------------------------------------------------------------
def get_saved_seq_num(number_path, number_start):
    ''' Create a .dat file to store currentCount
        or read file if it already Exists.  Fix
        corrupt integer entry in .dat file if it cannot
        be recognized as an integer.
    '''
    if not os.path.isfile(number_path):
        # Create numberPath file if it does not exist
        print('panohub.py: Creating New File %s numberstart= %s' %
               (number_path, number_start))
        open(number_path, 'w').close()
        f = open(number_path, 'w+')
        f.write(str(number_start))
        f.close()
    # Read the numberPath file to get the last sequence number
    with open(number_path, 'r') as f:
        write_count = f.read()
        f.closed
        try:
            number_counter = int(write_count)
        # Found Corrupt dat file since cannot convert to integer
        except ValueError:
            # Try to determine if this is motion or timelapse
            if number_path.find(IMAGE_PREFIX) > 0:
                file_path = IMAGE_DIR + "/*" + IMAGE_FORMAT
                fprefix = IMAGE_DIR + IMAGE_PREFIX

            try:
               # Scan image folder for most recent file
               # and try to extract most recent number counter
                newest = max(glob.iglob(filePath), key=os.path.getctime)
                write_count = newest[len(fprefix) + 1:newest.find(IMAGE_FORMAT)]
            except:
                write_count = number_start

            try:
                number_counter = int(write_count) + 1
            except ValueError:
                number_counter = number_start
            print('panohub.py: Found Invalid Data in %s Resetting Counter to %s' %
                  (number_path, number_counter))
        f = open(number_path, 'w+')
        f.write(str(number_counter))
        f.close()
        f = open(number_path, 'r')
        write_count = f.read()
        f.close()
        number_counter = int(write_count)
    return number_counter

#---------------------------------------------------------------
def timelapse_check(timelapse_start):
    '''
    Check if timelapse timer has expired
    '''
    timelapse_found = False
    right_now = datetime.datetime.now()
    time_diff = (right_now - timelapse_start).total_seconds()
    if time_diff > TIMELAPSE_TIMER:
        timelapse_found = True
    return timelapse_found

#---------------------------------------------------------------
def timestamp_to_string(my_time):
    '''
    Convert text string to datatime format
    '''
    return datetime.datetime.fromtimestamp(my_time).strftime('%Y/%m/%d %H:%M:%S')

#---------------------------------------------------------------
def stitch_images(image_seq_num, stitch_cmd):
    '''
    Run a subprocess to run stitch command
    '''
    print('panohub.py: Seq %i Working ......' % image_seq_num)
    print('panohub.py: Seq %i %s' % (image_seq_num, stitch_cmd))
    try:
        print('panohub.py:  ------------- Start Stitching -----------------------')
        proc = subprocess.call(stitch_cmd, shell=True, stdin=None,
                                stdout=None, stderr=None, close_fds=True)
        print('panohub.py: -------------- End Stitching ------------------------')
        time.sleep(1)
    except IOError:
        print('panohub.py: IOError subprocess %s' % stitch_cmd)

    if TIMELAPSE_SEQ_NUM_MAX == 0:
        pass
    elif (image_seq_num > (TIMELAPSE_SEQ_NUM_START + TIMELAPSE_SEQ_NUM_MAX)
        and TIMELAPSE_SEQ_NUM_RECYCLE_ON):
        image_seq_num = TIMELAPSE_SEQ_NUM_START
        print('panohub.py: Recycle Enabled. Restart SEQ at %i' %
               TIMELAPSE_SEQ_NUM_START)
    elif image_seq_num > (TIMELAPSE_SEQ_NUM_START + TIMELAPSE_SEQ_NUM_MAX):
        print('panohub.py: Exit Program: SEQ_MAX=%i and RECYCLE_ON=%s' %
               (TIMELAPSE_SEQ_NUM_MAX, TIMELAPSE_SEQ_NUM_RECYCLE_ON))
        sys.exit(1)
    print('panohub.py: Seq %i Waiting for Next Timelapse Images ...' %
          image_seq_num)
    print('panohub.py: Seq %i Current Time is %s' %
          (image_seq_num, datetime.datetime.now()))

#---------------------------------------------------------------
def do_pano_hub():
    '''
    Read images sent from pano-send.py via ZMQ and reply with
    the next timelapse timestamp. Once all images are received,ne
    attempt to stitch them into a panoramic image.
    Note images need to overlap properly.
    '''

    image_hub = imagezmq.ImageHub()  # Initialize image hub instance
    CAMS_IN_NET = len(CAM_HOST_NAMES)
    image_seq_num = get_saved_seq_num(TIMELAPSE_SEQ_COUNTER_PATH,
                                      TIMELAPSE_SEQ_NUM_START)
    stitch_filename = IMAGE_PREFIX + str(image_seq_num) + '.jpg'
    stitch_path = os.path.join(IMAGE_PANO_DIR, stitch_filename)
    stitch_cmd = STITCH_PROGRAM + ' ' + stitch_path
    cam_recv_cnt = 0
    timelapse_counter = TIMELAPSE_TIMER
    timelapse_start = datetime.datetime.now()
    timelapse_time = time.time() + TIMELAPSE_TIMER
    next_timelapse_message = timestamp_to_string(timelapse_time)
    first_timelapse = True
    print('panohub.py: Next timelapse is at %s' % next_timelapse_message)
    print('panohub.py: Time Now is %s' % datetime.datetime.now())
    print('panohub.py: Seq %i Listening for Images ...' % image_seq_num)
    while True:  # process sent images until Ctrl-C pressed
        pano_send_recv = []  # Blank list to keep track sending nodes
        take_timelapse = timelapse_check(timelapse_start)
        if take_timelapse:
            timelapse_start = datetime.datetime.now()
            timelapse_time = time.time() + TIMELAPSE_TIMER
            next_timelapse_message = timestamp_to_string(timelapse_time)
            print('panohub.py: Seq %i Next timelapse is at %s' %
                  (image_seq_num, next_timelapse_message))
            first_timelapse = False

        if (not first_timelapse) and take_timelapse:
            # Receive images from the specified camera nodes
            while cam_recv_cnt < CAMS_IN_NET:
                rpi_name, jpg_buffer = image_hub.recv_jpg()
                if rpi_name in pano_send_recv:
                    image_hub.send_reply(next_timelapse_message.encode('utf-8'))
                else:
                    pano_send_recv.append(rpi_name)
                    cam_recv_cnt += 1
                    image_filename = (IMAGE_PREFIX + rpi_name + '-' +
                                      str(image_seq_num) + IMAGE_FORMAT)
                    image_path = os.path.join(IMAGE_DIR, image_filename)
                    print('panohub.py: Seq %i Image %i/%i Processing %s' %
                          (image_seq_num, cam_recv_cnt, CAMS_IN_NET, image_path))

                    #decode and save image file from a camera node
                    image = cv2.imdecode(np.frombuffer(jpg_buffer, dtype='uint8'), -1)
                    cv2.imwrite(image_path, image)
                    # send message back to sender confirming receipt of image
                    image_hub.send_reply(next_timelapse_message.encode('utf-8'))
                    # append next image path to stitch command
                    stitch_cmd += ' ' + image_path

        # Does number of images received equal number of sender hosts
        if cam_recv_cnt == CAMS_IN_NET:
            stitch_images(image_seq_num, stitch_cmd)
            if os.path.isfile(stitch_path):
                print('panohub.py: Seq %i Saved Pano Image to %s' % (image_seq_num, stitch_path))
            else:
                print('panohub.py: WARN - Problem with stitching. Try realigning camera overlap.')

            # create next stitch_path and stitch_cmd initial command string
            image_seq_num += 1
            write_seq_num(image_seq_num, TIMELAPSE_SEQ_COUNTER_PATH)
            stitch_filename = IMAGE_PREFIX + str(image_seq_num) + '.jpg'
            stitch_path = os.path.join(IMAGE_PANO_DIR, stitch_filename)
            stitch_cmd = STITCH_PROGRAM + ' ' + stitch_path
            cam_recv_cnt = 0

print('-----------------------------------------------------------')
print('%s: %s written by Claude Pageau' % (PROG_NAME, PROG_VER))
print('-----------------------------------------------------------')
print('panohub.py: Version %s Initializing ...' % PROG_VER)
read_yaml_vars(YAML_FILEPATH, YAML_SECTION_NAME)
print('%s: %s modified by Claude Pageau from https://github.com/ppwwyyxx/OpenPano' %
      (PROG_NAME, STITCH_PROGRAM))

notify_senders(CAM_HOST_NAMES, True)  # Send yaml file to panowatch.py
                                      # and restart panosend.py on remote hosts
# Create required folder paths if req'd
if not os.path.isdir(IMAGE_PANO_DIR):
    os.makedirs(IMAGE_PANO_DIR)
if not os.path.isdir(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

try:
    do_pano_hub()
except KeyboardInterrupt:
    print('')
    print('panohub.py: User Exited with keyboard ctrl-c')
finally:
    notify_senders(CAM_HOST_NAMES, False)
    print('panohub.py: Version %s Bye ...' % PROG_VER)
