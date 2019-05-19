def read_status():

    f = open("status.txt", "r")
    line = f.readline()
    f.close()
    mode = int(line.split(" ")[0])
    on = int(line.split(" ")[1])
    duration = int(line.split(" ")[2])
    power = int(line.split(" ")[3])

    return {"mode": mode, "on": on, "duration": duration, "power": power}


def write_status(mode, on, duration, power):
    f = open("status.txt", "w")
    f.write("{} {} {} {}".format(mode, on, duration, power))
    f.close()
