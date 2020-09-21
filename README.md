# panopi
#### Create panoramic timelapse images from multiple RPI computers using picamera modules.

This project uses imagezmq to transfer images from panosend RPI's to a panohub RPI. All images are
send a timestamp so images are all taken at the same time. The panhub computer
stores timelapse sequence images and will then attempt a stitch of images.  If successful the pano
images will be save in a pano-images folder and can be viewed using my included webserver.  There
are still a few issues with getting consistent cropping in our computer/sewing room. Other locations may be better.
If necessary I will use my video editor's image stabilization filter. Currently the project is still a work in progress.

Claude ....

## Quick Install

### PANOHUB Install
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

### PANOSEND Install
On each RPI computer with a picamera installed and working, the curl script below will install the panosend files
into a /home/pi/panosend folder.

***Step 1*** With mouse left button highlight curl command in code box below. Right click mouse in **highlighted** area and Copy.    
***Step 2*** On RPI putty SSH or terminal session right click, select paste then Enter to download and run script.

    curl -L https://raw.github.com/pageauc/panopi/master/panosend/install-pansend.sh | bash

## Project Description

Use multiple raspberry pi computers with picamera's installed and working to take overlapping timelapse images
panosend.py will send images to a panohub.py computer via zmq. panosend.py will then receive a new timelapse timestamp
that will ensure all images are taken at the same time. panohub.py will save images into
a ***~/panohub/media/timelapse*** folder then stitch the overlapping sequence images into a cropped pano image and save
into ***~/panohub/media/pano-images*** folder.  These files can be viewed by running the panohub webserver.
The stitching program is a modified version of openpano.  For details see my Repo at https://github.com/pageauc/OpenPano

***NOTE:***  This project is still in the development stage but I will be happy to assist anyone
if you post a github issue on the panopi github repo.

## RPI STAND 
I found aligning the camera's very tricky.  I designed a simple stand that allows adjusting the
camera views accurately. The camera image overlap and alignment can be set easily.  Also since the stands
are just dowels I mounted mine on a board so all cameras can be moved together.  I am using wifi
and will use a ANKER powered hub with one ft long usb cables.  This should give me a clean setup.

Below is the foamboard design template in pdf format. This can be printed and used as a template. Adjust height to your liking
if you wish.  I have several different heights to allow cameras to see over window frames.  My RPI's have cases that mount the
 camera internally.

[pdf of rpi-stand template drawing](https://github.com/pageauc/panopi/blob/master/rpi-stand.pdf)
 Image with three cameras mounted on a board using wooden dowels per design drawing details.
![rpi-stand](https://github.com/pageauc/panopi/blob/master/rpi-stand.png)

## INSTRUCTIONS 
(Assumes you are comfortable with SSH, Terminal Session commands)

1. Edit panohub.yaml to change CAM_HOST_NAMES to reflect the panosend zeroconf host names.
  review other settings as required.    
  
    cd ~/panohub
    nano panohub.yaml

To save changes and exit nano press ctrl-x y     

2. Edit panosend.yaml to reflect IP address of panohub computer.

    ifconfig      # displays ip address details
    nano panosend.yaml  

To save changes and exit nano press ctrl-x y

3. On each panosend host start the panowatch.sh script   

    cd ~/panosend
    ./panowatch.sh start  

This will run panowatch.py as a background deamon.

4. On panohub computer start panohub.py   

    cd ~/panohub
    ./panohub.py

Review output and confirm images are being received. ctrl-c to exit    

5. Start the webserver to view images

    cd ~/panohub
    ./webserver.py

From browser input webserver url:port per instructions.

Once you have url. ctl-c to exit webserver then restart in background

    ./webserver.sh start

6. Restart ./panohub.py and align camera(s) using the webserver timelapse images
  You need to align vertically and horizontally.  Review image-stitching
  output on panohub.py.  
  
  It is best to start initially with two panosend cameras. You can then get 
  correct image overlap alignment.  Try a lot of overlap initially then narrow overlap.
  Images need to align vertically and horizontally.
  You can then add additional panosend hosts to the configuration by
  adding them to the panohub.yaml CAM_HOST_NAMES list variable.

## Sample Image

This is one of the images taken in our computer/sewing room.  Not very exciting and will post better one
when the project is further developed.  These are old RPI's.

![rpi-stand image](https://github.com/pageauc/panopi/blob/master/pano-tl-1284.jpg)
