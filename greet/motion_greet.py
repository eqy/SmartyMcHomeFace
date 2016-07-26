import time
import subprocess
from gpiozero import MotionSensor
import random

phrases = [ 'clips/lionel_hello.wav',
            'clips/seinfeld.wav',
            'clips/howdoing.mp3',
            'here come dat boy; oh shet waddup', 
            'do you want to buy some illegal meemes']

SATURATION_TIME = 30
TIMEOUT = 30

def main():
    pir = MotionSensor(16)
    last_time = 0
    index = 0
    while True:
        time.sleep(0.05)
        if pir.motion_detected:
            print("Motion Detected")
            cur_time = time.mktime(time.gmtime())
            if cur_time - last_time > SATURATION_TIME:
                if 'clips' in phrases[index]:
                    subprocess.call(['omxplayer', phrases[index]])
                else: 
                    subprocess.call(['./speech.sh', phrases[index], '0'])
                     
                last_time = cur_time
                if (index >= len(phrases) - 1):
                    index = 0
                    random.shuffle(phrases)
                else:
                    index += 1
                
        else:
            print("No Motion")

if __name__ == '__main__':
    main()
