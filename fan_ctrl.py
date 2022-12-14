#!/usr/bin/python
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import time
import sys
import os

# Configuration
if 'FAN_PIN' in os.environ:
    FAN_PIN = int(os.environ['FAN_PIN']) # BCM pin used to drive transistor's base
else:
    print("FAN_PIN required as FAN_PIN env value.")
    sys.exit(1)

WAIT_TIME = 1  # [s] Time to wait between each refresh
if 'WAIT_TIME' in os.environ:
    WAIT_TIME = int(os.environ['WAIT_TIME'])
    
FAN_MIN = 10  # [%] Fan minimum speed.
if 'FAN_MIN' in os.environ:
    FAN_MIN = int(os.environ['FAN_MIN'])

PWM_FREQ = 25000  # [Hz] Change this value if fan has strange behavior
if 'PWM_FREQ' in os.environ:
    PWM_FREQ = int(os.environ['PWM_FREQ'])

# Configurable temperature and fan speed steps
tempSteps = [50, 70]  # [°C]
speedSteps = [0, 100]  # [%]

# Fan speed will change only of the difference of temperature is higher than hysteresis
hyst = 4

# Setup GPIO pin
GPIO.setmode(GPIO.BCM)
GPIO.setup(FAN_PIN, GPIO.OUT, initial=GPIO.LOW)
fan = GPIO.PWM(FAN_PIN, PWM_FREQ)
fan.start(0)

i = 0
cpuTemp = 0
fanSpeed = 0
cpuTempOld = 0
fanSpeedOld = 0

# We must set a speed value for each temperature step
if len(speedSteps) != len(tempSteps):
    print("Numbers of temp steps and speed steps are different")
    exit(0)

try:
    while 1:
        # Read CPU temperature
        cpuTempFile = open("/sys/class/thermal/thermal_zone0/temp", "r")
        cpuTemp = float(cpuTempFile.read()) / 1000
        cpuTempFile.close()

        # Calculate desired fan speed
        if abs(cpuTemp - cpuTempOld) > hyst:
            # Below first value, fan will run at min speed.
            if cpuTemp < tempSteps[0]:
                fanSpeed = speedSteps[0]
            # Above last value, fan will run at max speed
            elif cpuTemp >= tempSteps[len(tempSteps) - 1]:
                fanSpeed = speedSteps[len(tempSteps) - 1]
            # If temperature is between 2 steps, fan speed is calculated by linear interpolation
            else:
                for i in range(0, len(tempSteps) - 1):
                    if (cpuTemp >= tempSteps[i]) and (cpuTemp < tempSteps[i + 1]):
                        fanSpeed = round((speedSteps[i + 1] - speedSteps[i])
                                         / (tempSteps[i + 1] - tempSteps[i])
                                         * (cpuTemp - tempSteps[i])
                                         + speedSteps[i], 1)

            if fanSpeed != fanSpeedOld:
                if (fanSpeed != fanSpeedOld
                        and (fanSpeed >= FAN_MIN or fanSpeed == 0)):
                    fan.ChangeDutyCycle(fanSpeed)                    
                    fanSpeedOld = fanSpeed
                    print("Setting fan speed to %f" % fanSpeed)
            cpuTempOld = cpuTemp

        # Wait until next refresh
        time.sleep(WAIT_TIME)


# If a keyboard interrupt occurs (ctrl + c), the GPIO is set to 0 and the program exits.
except KeyboardInterrupt:
    print("Fan ctrl interrupted by keyboard")
    GPIO.cleanup()
    sys.exit()
