sudo apt update
sudo apt -y install python3-pip python3-virtualenv pigpio python3-pigpio git vim ffmpeg mpg321
sudo systemctl enable pigpiod 

sudo chmod 666 /dev/hidraw0

python3 -m venv venv
source venv/bin/activate