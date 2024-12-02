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

rpiButtonsLeds = None
runningsounds = False

def on_event(ws, e):
    global runningsounds
    global rpiButtonsLeds
    s = "[%s][%s]" % (e.Timestamp.strftime("%Y-%m-%d %H:%M:%S"), e.MAC)
    if e.Type == 'state':
        s += "StateEvent: sensor_type=%s, state=%s, battery=%d, signal=%d" % e.Data
        print(f'e.Data {e.Data}')
        if e.Data[0] == 'motion' and e.Data[1] == 'active':
            if not runningsounds:
                print(f'Active')
                logging.debug("Active")
                runningsounds = True
                if rpiButtonsLeds: rpiButtonsLeds.ledOff()
                asyncio.run(Sound.play_random_sounds(3, 3, 'mpg321'))
                if rpiButtonsLeds: rpiButtonsLeds.ledOn()
                runningsounds = False
                # Sound.play_random_sound('mpg321')
    else:
        s += "RawEvent: type=%s, data=%r" % (e.Type, e.Data)
    print(s)


def main(args):
    if args['--debug']:
        loglevel = logging.DEBUG - (1 if args['--verbose'] else 0)
        logging.getLogger("wyzesense").setLevel(loglevel)
        logging.getLogger().setLevel(loglevel)

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
                pass
        else:
            while HandleCmd():
                pass
    finally:
        ws.Stop()

    return 0


if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s %(asctime)s %(message)s')

    try:
        from docopt import docopt
    except ImportError:
        sys.exit("the 'docopt' module is needed to execute this program")

    # remove restructured text formatting before input to docopt
    usage = re.sub(r'(?<=\n)\*\*(\w+:)\*\*.*\n', r'\1', __doc__)
    sys.exit(main(docopt(usage)))
