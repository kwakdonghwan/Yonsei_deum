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
