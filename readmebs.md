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
sudo apt install -y bluetooth bluez bluez-tools pulseaudio pulseaudio-module-bluetooth alsa-utils
sudo systemctl enable bluetooth
sudo systemctl start bluetooth

# finish setting up bluetooth
sudo vi /etc/pulse/default.pa
# find and add
load-module module-bluetooth-discover
load-module module-bluetooth-policy
load-module module-alsa-sink

# restart bluetooth
sudo systemctl restart bluetooth

# user account audio FOR a system service see below
pulseaudio -k
pulseaudio --start

# setup bluetooth
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

# small cisco speaker
pair 04:C8:70:21:10:20
trust 04:C8:70:21:10:20
connect 04:C8:70:21:10:20

# debug not connecting reboot



# https://learn.adafruit.com/running-programs-automatically-on-your-tiny-computer/systemd-writing-and-enabling-a-service

sudo chmod +x sample.py

sudo cp wyzesensepy.service /lib/systemd/system/wyzesensepy.service
# OR
sudo vi /lib/systemd/system/wyzesensepy.service
# start file contents
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
# end file contents


# Use this for no logging
StandardOutput=null
# Use this for logging
StandardOutput=journal+console
# use this to read the log
journalctl -e -u wyzesensepy.service


sudo systemctl enable wyzesensepy.service
sudo systemctl start wyzesensepy.service

sudo systemctl status wyzesensepy.service

sudo systemctl stop wyzesensepy.service
sudo systemctl disable wyzesensepy.service



Bluetooth speaker for system / service - https://www.freedesktop.org/wiki/Software/PulseAudio/Documentation/User/SystemWide/

# disable existing service
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
# find autospawn set
autospawn = no

# enable pulse daemon system mode
sudo vi /etc/pulse/daemon.conf
# find and set to this
daemonize = yes
system-instance = yes
allow-exit = no

# Modify the pulse user's home directory to /var/run/pulse:
sudo mkdir -p /var/run/pulse
sudo chown pulse:pulse-access /var/run/pulse
sudo usermod -d /var/run/pulse pulse
# create cookie folder
sudo mkdir -p /var/run/pulse/.config/pulse
sudo chown -R pulse:pulse-access /var/run/pulse
sudo chmod -R 775 /var/run/pulse


# setup the service
sudo cp pulseaudiosystem.service /lib/systemd/system/pulseaudiosystem.service
sudo systemctl enable pulseaudiosystem
sudo systemctl start pulseaudiosystem

# verify its running
sudo systemctl status pulseaudiosystem

# this didn't work
# Ensure PulseAudio's socket is writable by members of pulse-access:
sudo chmod g+w /var/run/pulse
sudo chown root:pulse-access /var/run/pulse


# Test audio
sudo mpg321 -g 50 -o alsa sounds/HEY\ -\ AUDIO\ FROM\ JAYUZUMI.COM.mp3


# DIDNT WORK
# volume control
# List all available audio sinks (output devices):
sudo pactl list sinks short
# You should see an entry for your Bluetooth device, such as: bluez_sink.XX_XX_XX_XX_XX_XX.a2dp_sink   module-bluetooth-device  SUSPENDED
# found this
bluez_sink.04_C8_70_21_10_20.a2dp_sink
# Set the volume to a specific percentage:
# pactl set-sink-volume <sink_name> 50%
# For example:

pactl set-sink-volume bluez_sink.04_C8_70_21_10_20.a2dp_sink 50%
# Increase the volume by 10%:
pactl set-sink-volume bluez_sink.04_C8_70_21_10_20.a2dp_sink +10%

# alsa backend
amixer -D pulse set Master 50%




# list all pulseaduio
sudo fuser -v /dev/snd/*