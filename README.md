# Yonsei_deum
use MLX90640 and control microwave oven 





# Curcuit
raspberrypi GPIO18 -> arduino in 8 -> out 13  -> magnetron

raspberrypi GPIO23 -> arduino in 9 -> out 11  -> plate, fan, led



# Camera


refference : https://github.com/abood91/RPiMLX90640 

before use it 

to build

cmake .   

make

to use

sudo ./MLX90640 10 8800

(sudo ./MLX90640 sleepsec portnumber)


#How to run 

1. turn on camera. 

>> sudo ./MLX90640 0.0625 8888

2. turn on main.py 

>> python3 main.py  (it is on Pythoncode/FestDeum/control/)

3. turn on server

>> python3 manage.py runserver (it is in Pythonconde/FestDeum/)


4. turn on webpage

>> web browser. and access it 


