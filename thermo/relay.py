import time
import gpiozero

fan = gpiozero.DigitalOutputDevice(5, active_high=False)
heat = gpiozero.DigitalOutputDevice(6, active_high=False)

