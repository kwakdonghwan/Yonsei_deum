import RPi.GPIO as GPIO
import time


class TemperatureController:
    def __init__(self, limit_temp):
        self.stop = False
        self.magnetron_pin = 18
        self.fan_pin = 23
        self.max_power = 10
        self.control_time = 10  # 10 -> 한 루프가 1/10초 100 -> 1/100
        self.limit_temp = limit_temp
        self.on_flag = 0

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.magnetron_pin, GPIO.OUT)
        GPIO.setup(self.fan_pin, GPIO.OUT)
        GPIO.output(self.magnetron_pin, True)
        GPIO.output(self.fan_pin, True)
        #print("setup")
        time.sleep(1)

        self.start_time = time.time()


    def run(self, current_max):
        if self.stop:
            return
        if self.on_flag >= 3:
            power = True
            if self.on_flag >= 5:
                self.on_flag = 0
        else:
            power = False

        self.on_flag += 1
        GPIO.output(self.magnetron_pin, power)
        GPIO.output(self.fan_pin, False)
        # GPIO.output(self.magnetron_pin, False)
        # GPIO.output(self.fan_pin, False)
        #print("running microwave!")
        self.check_temp(current_max)

    def on(self):
        self.stop = False
        self.on_flag = 0

    def check_temp(self, current_max):
        if current_max > self.limit_temp:
            print("!!!!!!!micro wave off!!!!!")
            GPIO.output(self.magnetron_pin, True)
            GPIO.output(self.fan_pin, True)
            self.stop = True
