# PANOPI
#### Create panoramic timelapse images from multiple Raspberry Pi computers using picamera modules.

This project uses [imagezmq](https://github.com/jeffbass/imagezmq) to transfer images from multiple panosend RPI's to a single panohub RPI. 
All panosend RPI's are sent a timestamp so all sequence images are taken at the same time. The panhub computer
stores timelapse sequence images in ***media/timelapse*** folder and will then attempt to stitch the images in the sequence.
If successful the pano images will be save in the ***media/pano-images*** folder and can be viewed using my included webserver.  There
are still a few issues with getting consistent cropping in our computer/sewing room, probably due to lighting. 
Other locations may be better. If necessary I will use my video editor's image stabilization filter. 
Currently the project is still a work in progress. Using a RPI4 as hub I was able to get 720p images stitch times of about six seconds.
Will do more testing as project moves along.

Claude ....

## QUICK INSTALL

### PANOHUB INSTALL
On a raspberry pi computer on your local area network (using zeroconf). Install the panohub software per curl
script below.  Note This does not need a picamera.  You can also choose to install on one of the
panosend RPI's. Stitching takes some time to process so I advise a faster RPI for the panohub RPI.

**IMPORTANT** - It is suggested you do a Raspbian ***sudo apt-get update*** and ***sudo apt-get upgrade***
before curl install.

***Step 1*** With mouse left button highlight curl command in code box below. Right click mouse in **highlighted** area and Copy.    
***Step 2*** On RPI putty SSH or terminal session right click, select paste then Enter to download and run script.

    curl -L https://raw.githubusercontent.com/pageauc/panopi/master/panohub/install-panohub.sh | bash

This will create a /home/pi/panohub folder and required files for communicating with panosend RPI's and 
stitching received images.  Default timelapse period is 60 seconds.  The webserver can be used to
view and align images.  

### PANOSEND INSTALL
On each RPI computer with a picamera installed and working, the curl script below will install the panosend files
into a /home/pi/panosend folder.

***Step 1*** With mouse left button highlight curl command in code box below. Right click mouse in **highlighted** area and Copy.    
***Step 2*** On RPI putty SSH or terminal session right click, select paste then Enter to download and run script.

    curl -L https://raw.githubusercontent.com/pageauc/panopi/master/panosend/install-panosend.sh | bash

## PROJECT DESCRIPTION

Use multiple raspberry pi computers with picamera's installed and working to take overlapping timelapse images
panosend.py will send images to a panohub.py computer via zmq. panosend.py will then receive a new timelapse timestamp
that will ensure all images are taken at the same time. panohub.py will save images into
a ***~/panohub/media/timelapse*** folder then stitch the overlapping sequence images into a cropped pano image and save
into ***~/panohub/media/pano-images*** folder.  These files can be viewed by running the panohub webserver.
The stitching program is a modified version of openpano.  For details see my Repo at https://github.com/pageauc/OpenPano

***NOTE:***  This project is still in the development stage but I will be happy to assist anyone
if you post a github issue on the panopi github repo.

## RPI CAM STAND 
I found aligning the camera's very tricky.  I designed a simple foamboard stand that allows adjusting the
camera views accurately. The camera image overlap and alignment can be set easily.  Also since the stand
mounts are just dowels, I mounted mine on a board so camera setup can be transported easily.  I am using wifi
and will use a ANKER powered hub with one ft long usb cables. This will give a clean setup. The cam stand
dowel can be inserted into any horizontal or vertical serface (as long as you can drill a dowel hole). I suggest
you mount to board and then mount the board on a wall or flat surface.

Below is the foam board design template in pdf format. This can be printed and used as a template. Adjust height to your liking
if you wish.  I have made several different heights to allow cameras to see over window frames.  My RPI's have cases that mount the
 camera internally. If you have different case your camera mounting details might be different.

[RPI CAM STAND PDF template](https://github.com/pageauc/panopi/blob/master/rpi-stand-2.pdf)    

Image with three cameras mounted on a board using wooden dowels per design drawing details.
![RPI CAM STAND CLOSE](https://github.com/pageauc/panopi/blob/master/rpi-stand-1.jpg)


1080p pano taken by the panosend RPI's        
![PANOSEND OF ME](https://github.com/pageauc/panopi/blob/master/pano-tl-1130_1080.jpg)    

Image of the rpi-stand taken by myself    
![RPI CAM STAND FAR](https://github.com/pageauc/panopi/blob/master/rpi-stand-2.jpg)    

## INSTRUCTIONS 
(Assumes you are comfortable with SSH, Terminal Session commands)

1. Edit panohub.yaml to change ***panohub_settings*** CAM_HOST_NAMES to reflect the panosend zeroconf host names.
Review other settings like IMAGE_PREFIX, TIMELAPSE_TIMER, Etc as required. 
Move down to ***panosend_settings*** and review CAM_WIDTH, CAM_HEIGHT, Etc
***IMPORTANT*** You DO NOT need to change the ***ZMQ_PANOHUB_IP*** setting since this will
be changed automatically by panohub.py to reflect the actual panohub computer ip address.    
  
    cd ~/panohub    
    nano panohub.yaml

To save changes and exit nano press ctrl-x y     

2. On each panosend host start the panowatch.sh script per commands below.       

    cd ~/panosend    
    ./panowatch.sh start  

This will run panowatch.py as a background task.

3. On panohub computer start the webserver to view images per commands below.    

    cd ~/panohub    
    ./webserver.sh start

4. On any local area computer, Web browser input webserver url:port on the web browser
url bar per examples below.  Note change to suit your actual network details.    

    192.168.1.177:8080    
    mypanohub.local:8080

When panohub.py is started, received images will be saved into the folders ***timelapse*** and ***pano_images***
    
5. On panohub computer start panohub.py per commands below. This RPI can be any RPI your network.
You will get faster stitching using a RPI4. panohub.py will read the panohub.yaml file panosend_settings
section, modify the ZMQ_PANOHUB_IP setting and stream to panowatch.py on each panosend computer.
panowatch.py will create a panosend.yaml from the panohub stream. panowatch will  
then start/restart panosend.sh that will read its settings from the transmitted panosend.yaml file.       

    cd ~/panohub    
    ./panohub.py

Review panohub.py log messages and confirm images are being received from each panosend camera.     
Align panosend computer camera(s) using the webserver timelapse images as a guide. Pick a
few objects in images for reference. You will need to align camera views vertically and horizontally.
When stitching is successful you can view results in the pano_images folder via web browser interface.
 
It is best to start initially with two panosend cameras. It will then be easier to get 
correct image overlap alignment. Try a lot of overlap initially then narrow overlap.
Images need to align vertically and horizontally.

You can then add additional panosend hosts to the configuration by
adding them to the panohub.yaml panohub_settings, CAM_HOST_NAMES list variable.
When panohub.py is stopped, it will send a zmq stop message to each panosend computer and panowatch will
stop the panosend background task. When panohub is restarted the panosend_settings will be send to panowatch
on each panosend machine and panosend.py will be restarted as a background task.
Press ctrl-c to exit panohub.py.

Once images are aligned properly and stitching is working, you can start panohub.py 
as a background task using command 

    ./panohub.sh start  

## SAMPLE IMAGES
This is one of the images taken in our computer/sewing room.  Not very exciting and will post better one
when the project is further developed.  I use old RPI's.  Note the displayed image below is really resized.
Select link for Actual image size which is much larger depending on the camera resolution.
Original panosend images were 720p before stitching.

#### 1080p PANO
![1080p Pano Timelapse Image Sample](https://github.com/pageauc/panopi/blob/master/pano-tl-1130_1080.jpg)    
[Click to View Full Size 1080p Pano Timelapse Image Sample](https://github.com/pageauc/panopi/blob/master/pano-tl-1130_1080.jpg)  

#### 720p PANO  
![720p Pano Timelapse Image Sample](https://github.com/pageauc/panopi/blob/master/pano-tl-1145-720.jpg)    
[Click to View Full Size 720p Pano Timelapse Image Sample](https://github.com/pageauc/panopi/blob/master/pano-tl-1145-720.jpg)

Regards    
Claude ...
