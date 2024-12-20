#!/usr/bin/env python

"""Example of using WyzeSense USB bridge.

**Usage:** ::
  sample.py [options]

**Options:**

    -d, --debug     output debug log messages to stderr
    -v, --verbose   print and log more information
    --device PATH   USB device path [default: /dev/hidraw0]
    -s, --service   run as service,
    -r, --rpi       run on raspberry pi
    --volume=<volume>  Volume of sound [default: 50]
    --soundclips=<soundclips>  Sound clips toplay [default: 3] 
    --soundtime=<soundtime>  Time between sound clips [default: 5]
    --speakerid=<speakerid>  Speaker ID MAC address (format: XX:XX:XX:XX:XX:XX)

**Examples:** ::

  sample.py --device /dev/hidraw0   # Using WyzeSense USB bridge /dev/hidraw0

"""
from __future__ import print_function

from builtins import input

import re
import sys
import logging
import binascii
import wyzesense
import Sound
import asyncio
import time
import threading


rpiButtonsLeds = None
runningsounds = False
soundclips = 3
soundtime = 5
timer = 0
motionActive = False
volume = 50


start_event = threading.Event()
stop_event = threading.Event()
exit_event = threading.Event()
def playSounds(start_event, stop_event, exit_event):
    playing = False
    global volume
    while not exit_event.is_set():
        # print('playSounds loop')
        if start_event.wait(1) and start_event.is_set() and not stop_event.is_set():
            # asyncio.run(Sound.play_random_sounds(soundclips, soundtime, f'mpg321 -g {volume}', resetSoundAndLed))
            asyncio.run(Sound.play_random_sounds(soundclips, soundtime, f'mpg321 -g {volume} -o alsa', resetSoundAndLed))
        # if stop_event.is_set():
        #     playing = False
        # if start_event.is_set():
        #     playing = True


playSoundsThread = threading.Thread(target=playSounds, args=[start_event, stop_event, exit_event])
playSoundsThread.start()
# async def playSounds():
#     await asyncio.sleep(0)
#     asyncio.run(Sound.play_random_sounds(soundclips, soundtime, 'mpg321', resetSoundAndLed))

def resetSoundAndLed():
    global motionActive
    global playSoundsThread
    # global rpiButtonsLeds
    # if rpiButtonsLeds: rpiButtonsLeds.ledOn()
    print('resetSoundAndLed')
    logging.debug('resetSoundAndLed')
    # if not motionActive:
        # playSoundsThread.join()
        # stop_event.set()
        
    

def on_event(ws, e):
    global rpiButtonsLeds
    global timer
    global motionActive
    global playSoundsThread
    s = "[%s][%s]" % (e.Timestamp.strftime("%Y-%m-%d %H:%M:%S"), e.MAC)
    if e.Type == 'state':
        s += "StateEvent: sensor_type=%s, state=%s, battery=%d, signal=%d" % e.Data
        print(f'e.Data {e.Data}')
        if e.Data[0] == 'motion' and e.Data[1] == 'active':
            print(f'Active')
            logging.debug("Active")
            timer = time.perf_counter()
            motionActive = True
            if rpiButtonsLeds: rpiButtonsLeds.ledOff()
            stop_event.clear()
            start_event.set()
            # asyncio.run(Sound.play_random_sounds(soundclips, soundtime, 'mpg321', resetSoundAndLed))
            # playSoundsThread.join()
            # playSoundsThread.start()
            
            # playSounds()
            # asyncio.create_task(playSounds())
                # if rpiButtonsLeds: rpiButtonsLeds.ledOn()
                # runningsounds = False
                # Sound.play_random_sound('mpg321')
        if e.Data[0] == 'motion' and e.Data[1] == 'inactive':
            print(f'Inactive')
            logging.debug("Inactive")
            motionActive = False
            stop_event.set()
            start_event.clear()
            if rpiButtonsLeds: rpiButtonsLeds.ledOn()

            end_timer = time.perf_counter()
            timeDiff = end_timer - timer
            print(f'timeDiff {timeDiff}')
            logging.debug(f'timeDiff {timeDiff}')
            timer = 0
            
    else:
        s += "RawEvent: type=%s, data=%r" % (e.Type, e.Data)
    print(s)
    logging.debug(s)

async def buttonPressed():
    print('Button short press callback called')
    logging.debug('Button short press callback called')
    print('Stopping Sound')
    logging.debug('Stopping Sound')
    stop_event.set()
async def buttonLongPressed():
    print('Button long press callback called')
    logging.debug('Button long press callback called')
    exit_event.set()
    if rpiButtonsLeds: rpiButtonsLeds.ledOn()
    from subprocess import call
    call("say 'Shutting down'", shell=True)
    call("sudo shutdown -h now", shell=True)


def validate_mac(mac):
    """Validates if the provided string is a valid MAC address."""
    mac_regex = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
    if re.match(mac_regex, mac):
        return True
    return False

async def main(args):
    global rpiButtonsLeds
    global volume
    if args['--debug']:
        loglevel = logging.DEBUG - (1 if args['--verbose'] else 0)
        logging.getLogger("wyzesense").setLevel(loglevel)
        logging.getLogger().setLevel(loglevel)

    speakerid = args['--speakerid']
    if validate_mac(speakerid):
        Sound.connectToSpeaker(speakerid)

    device = args['--device']
    print("Openning wyzesense gateway [%r]" % device)

    is_service = args['--service']
    if is_service:
        print("Service mode")
        logging.debug("Service mode")
    
    if args['--rpi']:
      print("Running on Raspberry Pi")
      logging.debug("Running on Raspberry Pi")
      from rpi_buttons_leds import RpiButtonsLeds
      rpiButtonsLeds = RpiButtonsLeds()
      rpiButtonsLeds.ledOn()
      rpiButtonsLeds.setButtonCallback(callback=buttonPressed)
      rpiButtonsLeds.setButtonCallbackLongPress(callback=buttonLongPressed)

    global soundclips
    if args['--soundclips']:
        soundclips = int(args['--soundclips'])
    if args['--volume']:
        volume = int(args['--volume'])
    global soundtime
    if args['--soundtime']:
        soundtime = int(args['--soundtime'])
    try:
        ws = wyzesense.Open(device, on_event)
        if not ws:
            print("Open wyzesense gateway failed")
            return 1
        print("Gateway info:")
        print("\tMAC:%s" % ws.MAC)
        print("\tVER:%s" % ws.Version)
        print("\tENR:%s" % binascii.hexlify(ws.ENR))
    except IOError:
        print("No device found on path %r" % device)
        while True:
            if rpiButtonsLeds: rpiButtonsLeds.ledOff()
            await asyncio.sleep(1)
            if rpiButtonsLeds: rpiButtonsLeds.ledOn()
            await asyncio.sleep(1)
        return 2

    def List(unused_args):
        result = ws.List()
        print("%d sensor paired:" % len(result))
        logging.debug("%d sensor paired:", len(result))
        for mac in result:
            print("\tSensor: %s" % mac)
            logging.debug("\tSensor: %s", mac)

    def Pair(unused_args):
        result = ws.Scan()
        if result:
            print("Sensor found: mac=%s, type=%d, version=%d" % result)
            logging.debug("Sensor found: mac=%s, type=%d, version=%d", *result)
        else:
            print("No sensor found!")
            logging.debug("No sensor found!")

    def Unpair(mac_list):
        for mac in mac_list:
            if len(mac) != 8:
                print("Invalid mac address, must be 8 characters: %s", mac)
                logging.debug("Invalid mac address, must be 8 characters: %s", mac)
                continue

            print("Un-pairing sensor %s:" % mac)
            logging.debug("Un-pairing sensor %s:", mac)
            ws.Delete(mac)
            print("Sensor %s removed" % mac)
            logging.debug("Sensor %s removed", mac)

    def HandleCmd():
        cmd_handlers = {
            'L': ('L to list', List),
            'P': ('P to pair', Pair),
            'U': ('U to unpair', Unpair),
            'X': ('X to exit', None),
        }

        for v in list(cmd_handlers.values()):
            print(v[0])

        cmd_and_args = input("Action:").strip().upper().split()
        if len(cmd_and_args) == 0:
            return True

        cmd = cmd_and_args[0]
        if cmd not in cmd_handlers:
            return True

        handler = cmd_handlers[cmd]
        if not handler[1]:
            return False

        handler[1](cmd_and_args[1:])
        return True

    try:
        if is_service:
            while True:
                if rpiButtonsLeds:
                    await rpiButtonsLeds.checkButtons()
                pass
        else:
            while HandleCmd():
                if rpiButtonsLeds:
                    await rpiButtonsLeds.checkButtons()
                pass
    finally:
        ws.Stop()
        if rpiButtonsLeds: rpiButtonsLeds.ledOff()
        exit_event.set()
        playSoundsThread.join()
        if rpiButtonsLeds: rpiButtonsLeds.cleanup()

    return 0


if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s %(asctime)s %(message)s')

    try:
        from docopt import docopt
    except ImportError:
        sys.exit("the 'docopt' module is needed to execute this program")

    # remove restructured text formatting before input to docopt
    usage = re.sub(r'(?<=\n)\*\*(\w+:)\*\*.*\n', r'\1', __doc__)
    # sys.exit(main(docopt(usage)))
    # Check if the event loop is already running
    try:
        asyncio.get_running_loop()
        # If the loop is already running, just run the main function
        asyncio.ensure_future(main(docopt(usage)))
    except RuntimeError:
        # No loop is running, so we can safely run it
        asyncio.run(main(docopt(usage)))

