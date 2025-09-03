#!/bin/bash
lxterminal -t "Starting Flask" -e sh -c "cd /home/pi/Desktop/flask ; ./start.sh"
sleep 5  #adjust time as needed
lxterminal -t "Ping to Server" -e ping 192.168.21.4
lxterminal -e firefox-esr -P flask  --private-window localhost:5000 --kiosk