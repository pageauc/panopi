#!/bin/bash
# install-panosend.sh script written by Claude Pageau Sep-2020

ver="0.5"
INSTALL_DIR='panohub'  # Default folder install location

cd ~
is_upgrade=false
if [ -d "$INSTALL_DIR" ] ; then
  STATUS="Upgrade"
  is_upgrade=true
else
  STATUS="New Install"
  mkdir -p $INSTALL_DIR
  echo "$STATUS Created Folder $INSTALL_DIR"
fi

# Remember where this script was launched from
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd $INSTALL_DIR
INSTALL_PATH=$( pwd )
mkdir -p media
echo "-----------------------------------------------"
echo "$STATUS panosend-install.sh ver $ver"
echo "-----------------------------------------------"
echo "$STATUS Download GitHub Files"
if $is_upgrade ; then
    installFiles=("panohub.py" "panohub.sh" "panohub.yaml" "panosend.yaml" \
                  "webserver.py" "webserver.sh" "image-stitching" "config.cfg")
else
    installFiles=("panohub.py" "panohub.sh" "panohub.yaml" "panosend.yaml" \
                  "webserver.py" "webserver.sh" "image-stitching" "config.cfg")
fi

for fname in "${installFiles[@]}" ; do
    wget_output=$(wget -O $fname -q --show-progress https://raw.github.com/pageauc/panopi/master/panohub/$fname)
    if [ $? -ne 0 ]; then
        if [ $? -ne 0 ]; then
            echo "ERROR - $fname wget Download Failed. Possible Cause Internet Problem."
        else
            wget -O $fname https://raw.github.com/pageauc/panopi/master/panohub/$fname
        fi
    fi
done

echo "$STATUS Make required Files Executable"
chmod +x *.py
chmod +x *.sh
chmod +x image-stitching

echo "$STATUS Installing panosend Dependencies"
sudo apt-get -yq install python-pip
sudo apt-get -yq install python3-pip
sudo apt-get -yq install python-numpy
sudo apt-get -yq install python3-numpy
sudo apt-get -yq install python-opencv
sudo apt-get -yq install python3-opencv
sudo apt-get -yq install dos2unix
sudo pip install pyYAML
sudo pip3 install pyYAML
sudo pip3 install imagezmq
echo "Dependencies Install Complete"

dos2unix -q *

cd $DIR
echo "
-----------------------------------------------
$STATUS Complete
-----------------------------------------------
INSTRUCTIONS (Assumes you are comfortable with SSH, Terminal Session commands)

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

-----------------------------------------------
For Detailed Instructions See https://github.com/pageauc/panopi/wiki
$INSTALL_DIR version $ver
Good Luck Claude ...
Bye"

