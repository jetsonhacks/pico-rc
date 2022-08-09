# Simple 2 Channel R/C Receiver for Raspberry Pi Pico
# Uses Pin 20 (GP15) for the steering
# Uses Pin 17 (GP13) for the throttle

from machine import Pin
import time
from PWMCounter import PWMCounter
import _thread
import gamepad

# For R/C servos, pulse width time in µS 
min_cycle = 1000
mid_cycle = 1500
max_cycle = 2000

# These are the global variables to keep track of the pulse width 
throttle_pulse = 1500
steering_pulse = 1500

# Is the global program running
running = True

def core1_function():
    global throttle_pulse
    global steering_pulse
    global running
   
    # We'll use counter pin for triggering, so set it up.
    steering_pin = Pin(15, Pin.IN) # GP15, Pin 20 - Channel 1 on Traxxas Receiver
    throttle_pin = Pin(13, Pin.IN) # GP13, Pin 17 - Channel 3 on Traxxas Receiver

    # Configure counter to count rising edges on GP15
    steering_counter = PWMCounter(15, PWMCounter.LEVEL_HIGH)
    # Set divisor to 16 (helps avoid counter overflow)
    steering_counter.set_div(16)
    # Start counter
    steering_counter.start()

    # Configure counter to count rising edges on GP15
    throttle_counter = PWMCounter(13, PWMCounter.LEVEL_HIGH)
    # Set divisor to 16 (helps avoid counter overflow)
    throttle_counter.set_div(16)
    # Start counter
    throttle_counter.start()

    last_state_steering = 0
    last_state_throttle = 0
    
    while running:
        steering_value = steering_pin.value()
        throttle_value = throttle_pin.value()
        
        if ~(x := steering_value) & last_state_steering:
            # Print pulse width in µS
            steering_pulse = (steering_counter.read_and_reset() * 16) / 125
            # print("S: ", steering_pulse)
        last_state_steering = x

        
        if ~(x := throttle_value) & last_state_throttle:
            # Print pulse width in µS 
            # print("T: ", (throttle_counter.read_and_reset() * 16) / 125)
            throttle_pulse = (throttle_counter.read_and_reset() * 16) / 125
            # print("T: ",throttle_pulse)
        last_state_throttle = x
    
def range_map(x, in_min, in_max, out_min, out_max):
    return int((x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min)

'''
bound_and_range
Bound the value to a R/C signal (1000 - 2000) pulsewidth
and convert to -127 to 127 for gamepad
'''
def bound_and_range(x):
   return range_map(max(min(x,max_cycle),min_cycle), 1000, 2000, -127, 127)

def core0_function():

    global throttle_pulse
    global steering_pulse
    
    try:
        game_pad = gamepad.GamePad()
        while True:
            throttle_ranged = bound_and_range(throttle_pulse)
            steering_ranged = bound_and_range(steering_pulse)
            game_pad.set_linear(0,throttle_ranged,0)
            game_pad.set_rotation(steering_ranged,0,0)
            game_pad.send()
            # print(int(throttle_pulse),int(steering_pulse))
            time.sleep(0.05)
    except (SystemExit, KeyboardInterrupt):
        # This may not work, but we can say we tried
        running = False        
    
# start new thread (on the second core) 
_thread.start_new_thread(core1_function, ())
   
if __name__ == "__main__":
    
    core0_function()
    