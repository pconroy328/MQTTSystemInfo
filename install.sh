#!/bin/bash
###
sudo cp mqttsysteminfo.service /etc/systemd/system/.
sudo chmod 644 /etc/systemd/system/mqttsysteminfo.service
sudo systemctl daemon-reload
sudo systemctl start mqttsysteminfo
sudo systemctl status mqttsysteminfo
sudo systemctl enable mqttsysteminfo

