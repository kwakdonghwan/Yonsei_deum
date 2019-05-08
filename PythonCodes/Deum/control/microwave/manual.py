import RPi.GPIO as GPIO
import time #sleep함수를쓰기위해


class ManualController:
    def __init__(self):

        self.magnetron_pin = 18
        self.fan_pin = 23
        self.max_power = 10
        self.control_time = 10  # 10 -> 한 루프가 1/10초 100 -> 1/100
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.magnetron_pin, GPIO.OUT)
        GPIO.setup(self.fan_pin, GPIO.OUT)
        GPIO.output(self.magnetron_pin, True)
        GPIO.output(self.fan_pin, True)


        # t = int(input("enter time (s): "))
        # power = int(input("enter power(1-{}): ".format(max_power)))

        self.start_time = time.time()
        self.duration = 0
        self.power = 0
        self.stop_flag = False

    def reset_param(self, power, duration):
        self.start_time = time.time()
        self.duration = duration
        self.power = power
        self.stop_flag = False
        GPIO.output(self.magnetron_pin, True)
        GPIO.output(self.fan_pin, True)
        print("target duration:", duration)

    def run(self):

        if self.stop_flag:
            return

        GPIO.output(self.fan_pin, False)
        GPIO.output(self.magnetron_pin, False)
        time.sleep(self.power/(self.max_power*self.control_time))
        GPIO.output(self.magnetron_pin, True)
        time.sleep((self.max_power-self.power)/(self.max_power*self.control_time))
        GPIO.output(self.magnetron_pin, False)

        current_time = time.time()
        if(current_time - self.start_time > self.duration):
            GPIO.output(self.magnetron_pin, True)
            GPIO.output(self.fan_pin, True)
            self.stop_flag = True
