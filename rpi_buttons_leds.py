import RPi.GPIO as GPIO
import time
import asyncio

class RpiButtonsLeds:
    LED_PIN = 18
    BUTTON_PIN = 10
    t0 = -1
    t1 = -1
    buttonPressed = False

      # total = t1-t0

    def __init__(self, debug=False):
      self.buttonCallback = None
      self.setupGPIO()
      # self.setup_buttons()
      self.setup_leds()

    def setButtonCallback(self, callback):
      self.buttonCallback = callback
      
    def setupGPIO(self):
      GPIO.setwarnings(False) # Ignore warning for now
      GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
    
    def setup_buttons(self):
      print('setup buttons')
      
      GPIO.setwarnings(False) # Ignore warning for now
      GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
      GPIO.setup(self.BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) 
    
    def setup_leds(self):
      print('setup leds')
      # Set up the GPIO pin for the LED
      GPIO.setup(self.LED_PIN, GPIO.OUT)
    
    def ledOn(self):
      # Turn on the LED
      GPIO.output(self.LED_PIN, GPIO.HIGH)
      print("LED is ON")
    
    def ledOff(self):
      # Turn off the LED
      GPIO.output(self.LED_PIN, GPIO.LOW)
      print("LED is OFF")
    
    def resetLed(self):
      self.ledOff()
      self.cleanup()
    def cleanup():
      GPIO.cleanup()
    
    async def checkButtons(self):
      try:
        while True:  
          if GPIO.input(self.BUTTON_PIN) == GPIO.HIGH:
            # print("Button was pushed!")
            if self.t0 == -1:
                self.t0 = time.time()
            self.t1 = time.time()
            total = self.t1-self.t0
            if (total > 0.5 and self.buttonPressed is not True):
              print(f"Button was pressed! {total}")
              if self.buttonCallback:
                await self.buttonCallback()
              else:
                print('No button callback')
              self.buttonPressed = True
          elif self.t0 >= 0 and GPIO.input(self.BUTTON_PIN) == GPIO.LOW:
              # t1 = time.time()
              # total = t1-t0
              # if (total > 0.5):
              print(f"Button was released! {total}")
              self.t0 = -1
              self.t1 = -1
              self.buttonPressed = False
          await asyncio.sleep(0.5)
            
      except KeyboardInterrupt:
          print("Exiting...")  # Always print this message
          
      # finally:
      #     self.pi.stop()
      
# print('rpi')
        




