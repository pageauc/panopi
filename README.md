# panopi
#### Create panoramic timelapse images from multiple RPI computers with picamera's

Use multiple raspberry pi computers with picamera's installed and working to take overlapping images
panosend.py will send images to a panohub.py computer via zmq. panohub.py will save images into
a ***~/panohub/media/timelapse*** folder then stitch the overlapping sequence images into a cropped pano images and save
into ***~/panohub/media/pano-images*** folder.  These files can be viewed by running the panohub webserver.

***NOTE:***  This project is still in the development stage but I will be happy to assist anyone
if you post a github issue on the panopi github repo.

## Quick Install

### PANOHUB
On a raspberry pi computer on your local area network (uses zeroconf). Install the panohub software per curl
script below.  Note This does not need a picamera.  You can also choose to install on one of the
panosend RPI's.

**IMPORTANT** - It is suggested you do a Raspbian ***sudo apt-get update*** and ***sudo apt-get upgrade***
before curl install.

***Step 1*** With mouse left button highlight curl command in code box below. Right click mouse in **highlighted** area and Copy.
***Step 2*** On RPI putty SSH or terminal session right click, select paste then Enter to download and run script.

    curl -L https://raw.github.com/pageauc/panopi/master/panohub/install-panhub.sh | bash

This will create a /home/pi/panohub folder and required files for communicating with panosend RPI's and 
stitching received images.  Default timelapse period is 60 seconds.  The webserver can be used to
view and align images.  

### PANOSEND
On each RPI computer with a picamera installed and working, the curl script below will install the panosend files
into a /home/pi/panosend folder.

***Step 1*** With mouse left button highlight curl command in code box below. Right click mouse in **highlighted** area and Copy.
***Step 2*** On RPI putty SSH or terminal session right click, select paste then Enter to download and run script.

    curl -L https://raw.github.com/pageauc/panopi/master/panosend/install-pansend.sh | bash


## INSTRUCTIONS 
(Assumes you are comfortable with SSH, Terminal Session commands)

1 Edit panohub.yaml to change CAM_HOST_NAMES to reflect the panosend zeroconf host names.
  review other settings as required.
    cd ~/panohub
    nano panohub.yaml
    To save changes and exit nano press ctrl-x y
2 Edit panosend.yaml to reflect IP address of panohub computer.
    ifconfig      # displays ip address details
    nano panosend.yaml  
    To save changes and exit nano press ctrl-x y
3 On each panosend host start the panowatch.sh script
    cd ~/panosend
    ./panowatch.sh start  
  This will run panowatch.py as a background deamon.
4 On panohub computer start panohub.py
    cd ~/panohub
    ./panohub.py
  Review output and confirm images are being received. ctrl-c to exit
5 Start the webserver to view images
    cd ~/panohub
    ./webserver.py
  From browser input webserver url:port per instructions.
  Once you have url. ctl-c to exit webserver then restart in background
    ./webserver.sh start
6 Restart./panohub.py and align camera(s) using the webserver timelapse images
  You need to align vertically and horizontally.  Review image-stitching
  output.  It is best to start with two panosend cameras and get alignment
  You can then add additional panosend hosts to the configuration by
  adding them to the panohub.yaml CAM_HOST_NAMES list variable.
