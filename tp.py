import threading
import cv2
import numpy as np
import datetime
import time
from widgets import Button


def tp(x):
    # 摄像头编号
    cam = x
    # cam=1
    # 程序开启运行开关
    start_button = Button(1, "UP")
    # 程序关闭开关
    stop_button = Button(1, "DOWN")
    camera = cv2.VideoCapture(cam)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    btn = 0
    if __name__ == "__main__":
        if cam == 1:
            result_dir = "./side_image"
        # cam=1
        else:
            result_dir = "./front_image"

        print("Start!")
        print('''Press the "Down button" to take photos!''')
        while True:
            if start_button.clicked():
                print("btn", btn)
                path = "{}/{}.png".format(result_dir, btn);
                btn += 1
                time.sleep(0.2)
                return_value, image = camera.read()
                name = "{}.png".format(btn)
                cv2.imwrite(path, image)
            if stop_button.clicked():
                break
    return
a = threading.Thread(target=tp(1))
a.setName('1')
a.start()
tp(0)
tp(1)

# def tp1():
#     cam = 1
#
#     start_button = Button(1, "UP")
#
#     stop_button = Button(1, "DOWN")
#     camera = cv2.VideoCapture(cam)
#     camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
#     camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
#     btn = 0
#     if __name__ == "__main__":
#         if cam == 1:
#             result_dir = "./front_image"
#         # cam=1
#         else:
#             result_dir = "./side_image"
#
#         print("Start!")
#         print('''Press the "Down button" to take photos!''')
#         while True:
#             if stop_button.clicked():
#                 print("btn", btn)
#                 path = "{}/{}.png".format(result_dir, btn);
#                 btn += 1
#                 time.sleep(0.2)
#                 return_value, image = camera.read()
#                 name = "{}.png".format(btn)
#                 cv2.imwrite(path, image)
#
#     return
# b = threading.Thread(target=tp1)
# b.setName('2')
# b.start()

