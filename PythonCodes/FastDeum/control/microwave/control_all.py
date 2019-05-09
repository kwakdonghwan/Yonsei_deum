

import RPi.GPIO as GPIO

import time #sleep함수를쓰기위해

magnetron_pin = 18
fan_pin = 23
max_power = 10
control_time = 10  # 10 -> 한 루프가 1/10초 100 -> 1/100
GPIO.setmode(GPIO.BCM)

GPIO.setup(magnetron_pin, GPIO.OUT)
GPIO.setup(fan_pin, GPIO.OUT)
GPIO.output(magnetron_pin, True)
GPIO.output(fan_pin, True)
print("setup")
time.sleep(2)


t = int(input("enter time (s): "))
power = int(input("enter power(1-{}): ".format(max_power)))

GPIO.output(fan_pin, False)
start_time = time.time()
while True:
    current_time = time.time()
    if(current_time - start_time > t):
        GPIO.output(magnetron_pin, True)
        GPIO.output(fan_pin, True)
        break



    GPIO.output(magnetron_pin, False)
    time.sleep(power/(max_power*control_time))
    GPIO.output(magnetron_pin, True)
    time.sleep((max_power-power)/(max_power*control_time))


GPIO.output(magnetron_pin, True)
GPIO.output(fan_pin, True)
GPIO.cleanup()
print("cleanup")
time.sleep(2)

