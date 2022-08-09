# pico-rc
Interface a Raspberry Pi Pico with a R/C radio receiver

Here we read PWM signals from a R/C receiver, and then convert them use them to emulate a gamepad which is transmitted via USB to a host computer. In this case, we are using a Traxxas 6528 two channel transmitter paired with a Traxxas 6533B receiver. The code will read only 2 channels (throttle and steering) concurrently in this initial iteration. This is exploratory code.

There are several different ways to read PWM signals on the Raspberry Pi Pico. First, there's the usual suspect, signalling pins to trigger an interrupt on the signal edge and measuring the time interval. Second, the Pico has a PWM slice for dealing specifically with PWM signals (input and output). Third, there are programmable state machines (PIO) which can provide a solution. Last there is polling pins in a tight loop and doing a little book keeping to measure the corresponding pulse width.

For this exploration project, the first implementation is in Micropython. The initial implementation used the interrupt path, but exhibited timing issues. In Micropython an interrupt on the Pico takes ~50 uS to process (versus ~3 uS for a C implementation). A R/C signal produces a pulse width of between 1000 to 2000 uS (1-2 milliseconds). It is possible to have multiple interrupts at the same time, so it was not unusual to see the values of a pulse width be off by 100 uS or more when implemented on one CPU core of the Pico. 

The PWM slice for the Pico provides an different solution. A PWM counter starts when it sees a high signal on the pin. In a loop, we check to see when the pin goes low, grab the counter value and reset the pin to get ready for the next pulse. This loop is on the second CPU core of the Pico. In this implementation, there are two channels (pins) that we monitor. The Pico allows 16 PWM channels, 8 of which may be specified as input. Note that this also specifies which physical pins can be used, see the Raspberry Pi Pico manual for more details (https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf).

In this implementation, the PWM slice is accessed via registers. The PWMCounter code is from the @phoreglad pico-MP-modules repository (https://github.com/phoreglad/pico-MP-modules/) 

Running on CPU core 0 is a polling which which gathers up the pulsewidths, converts them to gamepad format, and then transmits them over USB emulating a gamepad. A modified version of Micropython is used which emulates a USB-HID format, including a simple gamepad module. The modified Micropython is available in the JetsonHacks Github repository in the usb-hid branch (https://github.com/jetsonhacks/micropython). The usb-hid branch is built on v1.19.1 of Micropython. 

In order to run code in this repository, you will need to build the above Micropython from source and load the resulting .uf2 file on to the Pico. Then load the PWMCounter.py and pulse_width_measurement.py files on to the Pico. After testing, you can change the name of of the pulse_width_measurement.py to main.py to have the Pico boot and start the code.

This is simply software sketches and subject to change.


#Release Notes

##August, 2022
* Initial Release
* PWMCounter.py by @phoreglad 

  


