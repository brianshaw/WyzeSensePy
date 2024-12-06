sudo apt update
sudo apt -y install python3-pip python3-virtualenv pigpio python3-pigpio git vim ffmpeg mpg321
sudo systemctl enable pigpiod 

sudo chmod 666 /dev/hidraw0

git clone https://github.com/brianshaw/WyzeSensePy

cd WyzeSensePy
python3 -m venv venv
source venv/bin/activate

pip install docopt
pip install pigpio
pip install RPi.GPIO

# BLUETOOTH SPEAKER
sudo apt install -y bluetooth bluez bluez-tools pulseaudio pulseaudio-module-bluetooth
sudo systemctl enable bluetooth
sudo systemctl start bluetooth

sudo vi /etc/pulse/default.pa
# find and add
load-module module-bluetooth-discover
load-module module-bluetooth-policy
load-module module-alsa-sink


# user account audio
pulseaudio -k
pulseaudio --start

bluetoothctl
# then in bluetoothctl app
power on
agent on
default-agent
scan on
# Look for your speaker's name or MAC address in the output.
pair <MAC_ADDRESS>
trust <MAC_ADDRESS>
connect <MAC_ADDRESS>

# https://learn.adafruit.com/running-programs-automatically-on-your-tiny-computer/systemd-writing-and-enabling-a-service

sudo chmod +x sample.py
sudo vi /lib/systemd/system/wyzesensepy.service

[Unit]
Description=WyzeSensePy Service

[Service]
Type=simple
ExecStart=/home/pi/WyzeSensePy/venv/bin/python3 /home/pi/WyzeSensePy/sample.py --service
StandardOutput=journal+console
WorkingDirectory=/home/pi/WyzeSensePy/

[Install]
WantedBy=multi-user.target
Alias=wyzesensepy.service



sudo cp wyzesensepy.service /lib/systemd/system/wyzesensepy.service


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



Bluetooth speaker for system / service - https://www.freedesktop.org/wiki/Software/PulseAudio/Documentation/User/SystemWide/

sudo systemctl --global disable pulseaudio.service pulseaudio.socket

# Make sure the required groups (audio, bluetooth, and pulse-access) exist:
sudo groupadd -f pulse-access
# Add the pulse user to the required groups:
sudo usermod -aG audio,pulse-access,bluetooth pulse
# Add any other users who need access (including root or pi):
sudo usermod -aG pulse-access root
sudo usermod -aG pulse-access pi

# set autospawn = no in /etc/pulse/client.conf
sudo vi /etc/pulse/client.conf
# asd
sudo vi /etc/pulse/daemon.conf
# find and set to this
daemonize = yes
system-instance = yes
allow-exit = no

# Ensure PulseAudio's socket is writable by members of pulse-access:
sudo chmod g+w /var/run/pulse
sudo chown root:pulse-access /var/run/pulse


sudo cp pulseaudio.service /lib/systemd/system/pulseaudio.service
sudo systemctl enable pulseaudio
sudo systemctl start pulseaudio

# verify its running
sudo systemctl status pulseaudio
