#!/bin/bash
# install-panosend.sh script written by Claude Pageau Sep-2020

ver="0.61"
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
    installFiles=("panohub.py" "panohub.sh" "panohub.yaml" \
                  "webserver.py" "webserver.sh" "image-stitching" "config.cfg")
else
    installFiles=("panohub.py" "panohub.sh" "panohub.yaml" \
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
sudo apt-get -yq install avahi-daemon
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
  Review other settings as required eg camera resolution.
    cd ~/panohub
    nano panohub.yaml
    To save changes and exit nano press ctrl-x y
2 On each panosend host start the panowatch.sh script
    cd ~/panosend
    ./panowatch.sh start
  This will run panowatch.py as a background deamon.
3 On panohub computer start panohub.py
    cd ~/panohub
    ./panohub.py
  Review output and confirm all host images are being received. ctrl-c to exit
4 Start the webserver to get URL:PORT
    cd ~/panohub
    ./webserver.py
  Record browser URL:PORT per instructions
  ctl-c to exit then restart webserverin background
    ./webserver.sh start
  To view images Enter URL:PORT into URL bar of a network computer web browser.
5 Restart./panohub.py and align camera(s) using the webserver timelapse images
  You need to align vertically and horizontally.  Review image-stitching
  output.  It is best to start with two panosend cameras and get alignment
  You can then add additional panosend hosts to the configuration by
  adding them to the panohub.yaml CAM_HOST_NAMES list variable.

-----------------------------------------------
For Detailed Instructions See https://github.com/pageauc/panopi/wiki
$INSTALL_DIR version $ver
Good Luck Claude ...
Bye"

