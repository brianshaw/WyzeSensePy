sudo cp /home/pi/WyzeSensePy/wyzesense.service /lib/systemd/system/
sudo systemctl enable wyzesensepy.service
sudo systemctl start wyzesensepy.service