import asyncio
import os
import signal
import subprocess
import threading
import random
import time

# The os.setsid() is passed in the argument preexec_fn so
# it's run after the fork() and before  exec() to run the shell.

pro = None
proRain = None
proAmbient = None
runningsounds = False
includeSilenceStart = False

# Define the directory path
dir_path = os.path.dirname(os.path.realpath(__file__))
soundpath = dir_path + '/sounds/'
print(f'soundpath {soundpath}')
# Dictionary of sounds
sounds = {str(index): file.replace("'", "\\'").replace(" ", "\\ ") for index, file in enumerate(os.listdir(soundpath)) if file.endswith('.mp3')}
# print(f'sounds {sounds}')
# Remove 'silence.mp3' from the sounds dictionary if it exists
sounds = {key: value for key, value in sounds.items() if value != 'silence.mp3'}

def play_random_sound(app='afplay'):
  key = random.choice(list(sounds.keys()))
  asyncio.run(playsoundfromkey(key, app=app))

async def play_random_sounds(number_of_sounds=3, sleep_time=3, app='afplay', finishedCallback=None):
  played_keys = set()
  for _ in range(number_of_sounds):
    available_keys = list(set(sounds.keys()) - played_keys)
    if not available_keys:
      break
    key = random.choice(available_keys)
    played_keys.add(key)
    await playsoundfromkey(key, app=app)
    time.sleep(sleep_time)
  if finishedCallback:
    finishedCallback()


def playbackgroundsound(key, app='afplay', vol=50):
    global pro, proRain, proAmbient
    appcommands = [app]
    if app == 'afplay':
        appWithVol = f'{app} -v 1'
        appcommands.append('-v')
        appcommands.append('1')
    else:
        appWithVol = f'{app} -g {vol}'
        if key == 'bg1' or key == 'bg2':
            appWithVol = f'{appWithVol} -l 0'
        appcommands.append('-g')
        appcommands.append(f'{vol}')
    if proAmbient is not None:
        killbackgroundsound(process=proAmbient)
    if pro is not None:
        killbackgroundsound(process=pro)
    if proRain is not None and key == '4':
        timer = threading.Timer(4, killRain)  # 2 seconds delay
        timer.start()
    if proRain is not None and key == '5':
        print('kill rain')
        killRain()
    # Build the command
    command = f'{appWithVol} {soundpath}{sounds[key]}'
    appcommands.append(f'{soundpath}{sounds[key]}')
    # command = f'{app} {soundpath}{sounds[key]}'
    # Create an asynchronous subprocess
    # process = asyncio.create_subprocess_shell(command)
    print(f'appcommands {appcommands}')
    if key == 'bg1' or key == 'bg2':
        proAmbient = subprocess.Popen(command, stdout=subprocess.PIPE, 
                       shell=True, preexec_fn=os.setsid)
    if key == '2':
        proRain = subprocess.Popen(command, stdout=subprocess.PIPE, 
                       shell=True, preexec_fn=os.setsid)
    else:
        pro = subprocess.Popen(command, stdout=subprocess.PIPE, 
                           shell=True, preexec_fn=os.setsid) 

def killRain():
    killbackgroundsound(process=proRain)
def killbackgroundsound(process):
    try:
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
    except ProcessLookupError:
        print("Process has already terminated.")
def killall():
    if proAmbient is not None:
        killbackgroundsound(process=proAmbient)
    if pro is not None:
        killbackgroundsound(process=pro)
    if proRain is not None:
        print('kill rain')
        killRain()
    
# Asynchronous function to play sound
async def playsoundfromkey(key, app='afplay'):
    global includeSilenceStart
    if proRain is not None and key == '5':
      print('kill rain')
      killbackgroundsound(process=proRain)
    # Build the command
    if includeSilenceStart:
      command = f'{app} {soundpath}silence.mp3 {soundpath}{sounds[key]}'
    else:
      command = f'{app} {soundpath}{sounds[key]}'
    print(f'command {command}')
    # Create an asynchronous subprocess
    process = await asyncio.create_subprocess_shell(command)
    
    await asyncio.sleep(0.1)
    # Wait for the process to finish
    await process.wait()


# Test function to play multiple sounds asynchronously
async def test(app='afplay'):
    # Run all play sound tasks concurrently
    await asyncio.gather(
        playsoundfromkey('0', app=app),
        playsoundfromkey('1', app=app),
        playsoundfromkey('2', app=app),
        playsoundfromkey('3', app=app),
        playsoundfromkey('4', app=app),
    )

def connectToSpeaker(speakerid):
    print(f'Connecting to speaker {speakerid}')
    if speakerid != 'none':
        print(f'Connecting to speaker {speakerid}')
        os.system(f'bluetoothctl connect {speakerid}')
# # Run the test function
# if __name__ == "__main__":
#     asyncio.run(test())
