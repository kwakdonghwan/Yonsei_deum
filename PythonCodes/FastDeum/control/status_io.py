def read_status():

    #f = open("/Users/changmin/CLionProjects/Yonsei_deum/PythonCodes/FastDeum/control/status.txt", "r")  ## 절대경로로 바꾸기
    f = open("/home/pi/Yonsei_deum/PythonCodes/FastDeum/control/status.txt", "r")  ## 절대경로로 바꾸기

    line = f.readline()
    f.close()
    mode = int(line.split(" ")[0])
    on = int(line.split(" ")[1])
    duration = int(line.split(" ")[2])
    power = int(line.split(" ")[3])
    device = int(line.split(" ")[4])

    return {"mode": mode, "on": on, "duration": duration, "power": power, "device": device}


def write_status(mode, on, duration, power, device):
    #f = open("/Users/changmin/CLionProjects/Yonsei_deum/PythonCodes/FastDeum/control/status.txt", "w")
    f = open("/home/pi/Yonsei_deum/PythonCodes/FastDeum/control/status.txt", "w")
    f.write("{} {} {} {} {}".format(mode, on, duration, power, device))
    f.close()
