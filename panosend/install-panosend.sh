#!/bin/bash
# install-panosend.sh script written by Claude Pageau Sep-2020

ver="0.5"
INSTALL_DIR='panosend'  # Default folder install location

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
echo "-----------------------------------------------"
echo "$STATUS panosend-install.sh ver $ver"
echo "-----------------------------------------------"
echo "$STATUS Download GitHub Files"
if $is_upgrade ; then
    installFiles=("panosend.py" "panosend.sh" "panowatch.py" "panowatch.sh")
else
    installFiles=("panosend.py" "panosend.sh" "panowatch.py" "panowatch.sh")
fi

for fname in "${installFiles[@]}" ; do
    wget_output=$(wget -O $fname -q --show-progress https://raw.github.com/pageauc/panopi/master/panosend/$fname)
    if [ $? -ne 0 ]; then
        if [ $? -ne 0 ]; then
            echo "ERROR - $fname wget Download Failed. Possible Cause Internet Problem."
        else
            wget -O $fname https://raw.github.com/pageauc/panopi/master/panosend/$fname
        fi
    fi
done

echo "$STATUS Make required Files Executable"
chmod +x *.py
chmod +x *.sh

echo "$STATUS Installing panosend Dependencies"
sudo apt-get -yq install python-pip
sudo apt-get -yq install python3-pip
sudo apt-get -yq install python-numpy
sudo apt-get -yq install python3-numpy
sudo apt-get -yq install python-picamera
sudo apt-get -yq install python3-picamera
sudo apt-get -yq install python-opencv
sudo apt-get -yq install python3-opencv
sudo apt-get -yq install avahi-daemon
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

1 Start panowatch.py as a background task per

    cd ~/panosend
    ./panowatch.sh start

  Note: You can auto start panowatch on boot by editing the
        file /etc/rc.local
    
    sudo nano /etc/rc.local

  Then Add the command below just before exit 0 
    
    sudo -u pi /home/pi/panosend/panowatch.sh start

  To save changes and exit nano press ctrl-x y

2 Go to the panohub computer and follow the panohub install script instructions.
    
-----------------------------------------------
For Detailed Instructions See https://github.com/pageauc/panopi
$INSTALL_DIR version $ver
Good Luck Claude ...
Bye"
