import cv2
import os


# cv2.destroyAllWindows()
cap = cv2.VideoCapture(0)
show_flag = False
cnt = 0
duration = 0
while True:
    if cnt > duration:

        f = open("status.txt", "r")
        line = f.readline()
        f.close()
        split = line.split(" ")
        ff = open("status.txt", "w")
        ff.write("0 0 0")
        ff.close()

    ret, frame = cap.read()

    f = open("status.txt", "r")
    line = f.readline()
    f.close()
    status = line.split(" ")[0]
    duration = int(line.split(" ")[1])

    if status == "1":
        cnt += 1
        print(cnt)
        show_flag = True
        cv2.namedWindow("frame", cv2.WND_PROP_FULLSCREEN)
        # cv2.startWindowThread()
        os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "python" to true' ''')
        cv2.setWindowProperty("frame", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.imshow("frame", frame)
    else:
        if show_flag:
            cv2.destroyAllWindows()
            cv2.namedWindow("empty")

            cv2.moveWindow("empty", 6000, 6000)

            cnt = 0
            duration = 0
            show_flag = False

    if cv2.waitKey(1) & 0xff == ord('q'):
        break



