

import RPi.GPIO as GPIO

import time #sleep함수를쓰기위해


class TemperatureController:
    def __init__(self, limit_temp):
        self.stop = False
        self.magnetron_pin = 18
        self.fan_pin = 23
        self.max_power = 10
        self.control_time = 10  # 10 -> 한 루프가 1/10초 100 -> 1/100
        self.limit_temp = limit_temp

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.magnetron_pin, GPIO.OUT)
        GPIO.setup(self.fan_pin, GPIO.OUT)
        GPIO.output(self.magnetron_pin, True)
        GPIO.output(self.fan_pin, True)
        print("setup")
        time.sleep(1)

        self.start_time = time.time()


    def run(self, current_max):
        if self.stop:
            return
        self.check_temp(current_max)
        current_time = time.time()
        if(current_time - self.start_time > t):
            self.stop = True
            GPIO.output(self.magnetron_pin, True)
            GPIO.output(self.fan_pin, True)
            print("!!!!!!!micro wave off!!!!!")
            # GPIO.cleanup()
            # print("cleanup")

        GPIO.output(self.magnetron_pin, False)
        print("running microwave!")

    def on(self):
        self.stop = False

    def check_temp(self, current_max):
        if current_max > self.limit_temp:
            self.stop = True



