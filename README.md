# Yonsei_deum
use MLX90640 and control microwave oven 


시발 연세대학교 이수홍 교수 == 개멍청한 병신새끼임

전자레인지 가동 알고리즘을 지가 멍청해서 이해를 못해놓고 완성 못한거 처리해버린다. 와.. 시발

이코드 쓰실 분은 이수홍이 장애인새끼라는거 인정한하면 안돌아가게 할거임

12/15등 평가가 말이되냐 시발 

시연회에서 반응 가장좋은 건데 시발 평가 기준이 뭐냐 




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


