import RPi.GPIO as GPIO
import time #sleep함수를쓰기위해




class auto_contoroler:
    def __init__(self):

        self.run_TYPE = 0

        #will check the type of run
        self.TYPE_A = 1
        self.TYPE_B = 2
        self.TYPE_C = 3

        self.temperature_max = 0
        self.temperature_average = 0
        self.temperature_min = 0

#####################################################################raspberry_pi
        self.magnetron_pin = 18
        self.fan_pin = 23
        self.max_power = 10
        self.control_time = 20  # 10 -> 한 루프가 1/10초 100 -> 1/100
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.magnetron_pin, GPIO.OUT)
        GPIO.setup(self.fan_pin, GPIO.OUT)
        GPIO.output(self.magnetron_pin, True)
        GPIO.output(self.fan_pin, True)
##################################################################################
        self.refference_time = 10   ## this is roop for magnetron_control


        # t = int(input("enter time (s): "))
        # power = int(input("enter power(1-{}): ".format(max_power)))

        self.start_time = time.time()  ##will not need
        self.duration = 0
        self.power = 0
        self.stop_flag = False

    def reset_origin(self):

        GPIO.output(self.magnetron_pin, True)
        GPIO.output(self.fan_pin, True)
        self.start_time = time.time()
        self.duration = 0
        self.power = 0
        self.stop_flag = False

    def run_only_fan(self):

        try:
            GPIO.output(self.fan_pin, False)
            GPIO.output(self.magnetron_pin, True)
            return True
        except:
            return False
    def run_only_magnetron(self):

        try:
            GPIO.output(self.fan_pin, True)
            GPIO.output(self.magnetron_pin, False)
            return True
        except:
            return False
    def run_all(self):
        try:
            GPIO.output(self.fan_pin, False)
            GPIO.output(self.magnetron_pin, False)
            return True
        except:
            return False
    def run_turn_off(self):
        try:
            GPIO.output(self.fan_pin, True)
            GPIO.output(self.magnetron_pin, True)
            return True
        except:
            return False

    def get_temperature_data_form_TD(self,max,averagem,min):
        self.temperature_max = max
        self.temperature_average = averagem
        self.temperature_min = min


    def type_checker(self,seven_sec_rise):
        if seven_sec_rise > 10 :
            self.run_TYPE = self.TYPE_A
        elif seven_sec_rise > 5 :
            self.run_TYPE = self.TYPE_B
        elif seven_sec_rise > 1 :
            self.run_TYPE = self.TYPE_C


    def reset_param(self, power, duration):
        self.start_time = time.time()
        self.duration = duration
        self.power = power
        self.stop_flag = False
        GPIO.output(self.magnetron_pin, True)
        GPIO.output(self.fan_pin, True)
        print("target duration:", duration)

    def run(self,start_time2):


        if self.stop_flag:
            return True

        current_time = time.time()
        operation_time = current_time - start_time2
        operation_time2 = int(operation_time)
        operation_range = operation_time2 % self.refference_time
        if operation_range < self.power * self.refference_time / 10:
            GPIO.output(self.fan_pin, False)
            GPIO.output(self.magnetron_pin, False)
        else:
            GPIO.output(self.fan_pin, False)
            GPIO.output(self.magnetron_pin, True)

        if(operation_time > self.duration):
            GPIO.output(self.magnetron_pin, True)
            GPIO.output(self.fan_pin, True)
            self.stop_flag = True
            print("micro_wave_is_duen")

        return False

    def autorun(self):



        if self.run_TYPE == self.TYPE_A:
            print("TYPE_A")

        elif self.run_TYPE == self.TYPE_B:
            print("TYPE_B")

        elif self.run_TYPE == self.TYPE_C:
            print("TYPE_C")

        elif self.run_TYPE == 0:
            print("NO_TYPE")

    def TYPE_A_contorol(self):  #####need to make more

        TYPE_A_refference_1 = 400

        if self.temperature_max > TYPE_A_refference_1:
            self.run_only_fan()
        else
            self.run_all()
