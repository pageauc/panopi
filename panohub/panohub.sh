#!/bin/bash
ver="0.5"
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"  # get cur dir of this script
progName=$(basename -- "$0")

cd $DIR
echo "$progName $ver  written by Claude Pageau"

#==================================
#   panosend.sh User Settings
#==================================
app_fname="panohub.py"  # Filename of Program to Monitor for Run Status


progDir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )" # folder location of this script
cd $progDir
# ------------------------------------------------------
function do_stop ()
{
    now=$(/bin/date +%Y-%m-%d-%H:%M:%S)
    if [ -z "$(pgrep -f $app_fname)" ] ; then
        echo "$now INFO  : $progName Already Stopped"
    else
        progPID=$( pgrep -f "$app_fname" )
        echo "$now INFO  : Stopping $app_fname PID $progPID"
        sudo kill $progPID >/dev/null 2>&1
        sleep 3
        if [ -z "$(pgrep -f $app_fname)" ] ; then
            echo "$now INFO  : Killed $app_fname PID $progPID "
        else
            echo "$now ERROR : PID $progPID Kill Failed $app_fname "
        fi
    fi
}

function do_start ()
{
    now=$(/bin/date +%Y-%m-%d-%H:%M:%S)
    if [ -z "$(pgrep -f $app_fname)" ] ; then
        # start the app
       ./$app_fname  >/dev/null 2>&1 &
        sleep 2
        if [ -z "$(pgrep -f $app_fname)" ] ; then
            echo "$now INFO  : Start Failed $app_fname"
        else
            progPID=$( pgrep -f $app_fname )
            echo "$now INFO  : Started $app_fname PID $progPID"
        fi
        progPID=$( pgrep -f $app_fname )
    else 
        progPID=$( pgrep -f $app_fname )
        echo "$now WARN  : $app_fname Already Running PID $progPID. Only One Allowed."        
    fi
}

function do_restart ()
{
    do_stop
    do_start
}

function do_status ()
{
    now=$(/bin/date +%Y-%m-%d-%H:%M:%S)
    if [ -z "$(pgrep -f $app_fname)" ] ; then
        echo "$now INFO  : $app_fname is Not Running"
    else
        progPID=$( pgrep -f $app_fname )
        echo "$now INFO  : $app_fname is Running PID $progPID"
    fi
}

# ------------------------------------------------------
# Main script processing
now=$(/bin/date +%Y-%m-%d-%H:%M:%S)
if [ "$1" = "stop" ]; then
    do_stop
elif [ "$1" = "start" ]; then
    do_start
elif [ "$1" = "restart" ]; then
    do_restart
elif [ "$1" = "status" ]; then
    do_status
else
    echo "=================================="
    echo "$0 Controls Running of $app_fname"
    echo ""
    echo "syntax:"    
    echo "$0 [option]"
    echo "where [option] is start, stop, restart, status"
    echo ""
    echo "example:"
    echo "$0 status"
    do_status
fi

echo "------------------------------------------
$progName Bye ..."

