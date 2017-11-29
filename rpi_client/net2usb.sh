#!/bin/bash
# Check root user
if [ $UID != 0 ]; then
    echo "ERROR: Not root user?"
    exit 1
fi
# example of one time manual run
# sleep 10
# python3 ./net2usb.py -i "ahoj fiitka"

# example of running the application connected to remote server
python3 ./net2usb.py -a ws://147.175.149.172:5432

# example of running the application connected to local server
# python3 ./server.py
# python3 ./net2usb.py -a ws://localhost:5432
