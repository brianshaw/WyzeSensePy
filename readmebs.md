sudo apt update
sudo apt -y install python3-pip python3-virtualenv pigpio python3-pigpio git vim ffmpeg mpg321
sudo systemctl enable pigpiod 

sudo chmod 666 /dev/hidraw0

git clone https://github.com/brianshaw/WyzeSensePy

cd WyzeSensePy
python3 -m venv venv
source venv/bin/activate

pip install docopt




# https://learn.adafruit.com/running-programs-automatically-on-your-tiny-computer/systemd-writing-and-enabling-a-service

sudo chmod +x sample.py
sudo vi /lib/systemd/system/wyzesensepy.service

[Unit]
Description=WyzeSensePy Service

[Service]
ExecStart=/home/pi/WyzeSensePy/venv/bin/python3 /home/pi/WyzeSensePy/sample.py
StandardOutput=journal+console
WorkingDirectory=/home/pi/WyzeSensePy/

[Install]
WantedBy=multi-user.target
Alias=wyzesensepy.service



# Use this for no logging
StandardOutput=null
# Use this for logging
StandardOutput=journal+console
# use this to read the log
journalctl -u wyzesensepy.service

sudo systemctl enable wyzesensepy.service
sudo systemctl start wyzesensepy.service


sudo systemctl status wyzesensepy.service

sudo systemctl stop wyzesensepy.service
sudo systemctl disable wyzesensepy.service