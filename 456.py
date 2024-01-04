import time

import cv2
import config
from camera import Camera
import os

# cam = 0
# camera = cv2.VideoCapture(cam)
camera = Camera(config.front_cam, [640, 480])
# camera = Camera(config.side_cam, [640, 480])

print(camera)

while True:
    camera.start()
    front_image = camera.read()
    cv2.imshow('winname', front_image)

    if cv2.waitKey(200) == ord('q'):
        break
    # cv2.destroyAllWindows()

# camera.stream.release()
cv2.destroyAllWindows()
os.system('killall -9 python3')
