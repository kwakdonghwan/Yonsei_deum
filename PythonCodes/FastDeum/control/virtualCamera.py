import cv2
import os

from status_io import *

# cv2.destroyAllWindows()
cap = cv2.VideoCapture(0)
show_flag = False
cnt = 0
duration = 0


while True:
    if cnt > duration:
        write_status(0, 0, 0, 0)


    ret, frame = cap.read()

    status = read_status()
    duration = status["duration"]

    if status["on"] == 1:
        cnt += 1
        print(cnt)
        show_flag = True
        # os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "python" to true' ''')
        cv2.namedWindow("frame", cv2.WND_PROP_FULLSCREEN)
        # cv2.startWindowThread()
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



