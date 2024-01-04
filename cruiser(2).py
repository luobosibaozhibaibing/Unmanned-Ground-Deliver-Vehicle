import cv2
import numpy as np
import predictor_wrapper
import config

import time
import struct
from serial_port import serial_connection

from camera import Camera

from cart import Cart

front_camera = Camera(config.front_cam, [640, 480])
side_camera = Camera(config.side_cam, [640, 480])

serial = serial_connection

cnn_args = {
    "shape": [1, 3, 128, 128],
    "ms": [125.5, 0.00392157]
}

cruise_model = config.cruise["model"]

#确认"DOWN"按键是否按下，程序是否处于等待直行状态
def check_stop():
    if stop_button.clicked():
        return True
    return False


# CNN网络的图片预处理
def process_image(frame, size, ms):
    frame = cv2.resize(frame, (size, size))
    img = frame.astype(np.float32)
    img = img - ms[0]
    img = img * ms[1]
    img = np.expand_dims(img, axis=0)
    return img

# CNN网络预处理
def cnn_preprocess(args, img, buf):
    shape = args["shape"]
    img = process_image(img, shape[2], args["ms"])
    hwc_shape = list(shape)
    hwc_shape[3], hwc_shape[1] = hwc_shape[1], hwc_shape[3]
    data = buf
    img = img.reshape(hwc_shape)
    # print("hwc_shape:{}".format(hwc_shape))
    data[0:, 0:hwc_shape[1], 0:hwc_shape[2], 0:hwc_shape[3]] = img
    data = data.reshape(shape)
    return data

# CNN网络预测
def infer_cnn(predictor, buf, image):
    data = cnn_preprocess(cnn_args, image, buf)
    predictor.set_input(data, 0)
    predictor.run()
    out = predictor.get_output(0)
    return np.array(out)[0][0]

class Driver:

    def __init__(self):
        self.max_speed=25
        self.full_speed = 25
        self.cart = Cart()
        self.cart.velocity=self.full_speed
        self.cruiser = Cruiser()

    def stop(self):
        self.cart.stop()

    def go(self, frame):
        angle = self.cruiser.cruise(frame)
        self.cart.steer(angle)

    def speed(self):
        return self.cart.velocity

    def set_speed(self, speed):
        # self.full_speed=speed
        self.cart.velocity=speed

    def set_Kx(self, Kx):
        self.cart.Kx=Kx

    def get_min_speed(self):
        return self.cart.min_speed

    def change_posture(self, basespeed):
        # basespeed=15
        l_speed = basespeed
        r_speed = basespeed * 0.4
        self.cart.move([l_speed, r_speed, l_speed, r_speed])
        time.sleep(1)
        l_speed = basespeed * 0.4
        r_speed = basespeed
        self.cart.move([l_speed, r_speed, l_speed, r_speed])
        time.sleep(1)
        self.cart.stop()

    def change_posture_cm(self, distance):
        basespeed = 15
        speed_ratio = 0.4
        drivetime = distance * 0.9
        if distance < 2:
            speed_ratio = 0.2
            drivetime = distance * 0.95
        elif distance < 4:
            speed_ratio = 0.15
            drivetime = distance * 0.75
        else:
            speed_ratio = -0.05
            drivetime = distance * 0.5
        l_speed = basespeed
        r_speed = basespeed * speed_ratio
        self.cart.move([l_speed, r_speed, l_speed, r_speed])
        time.sleep(drivetime)
        l_speed = basespeed * speed_ratio
        r_speed = basespeed
        self.cart.move([l_speed, r_speed, l_speed, r_speed])
        time.sleep(drivetime-0.5)
        self.cart.stop()
    def driver_run(self,left,right):
        self.cart.move([left,right,left,right])

# d = Driver();
SLOW_DOWN_RATE = 0.6

class Button:
    def __init__(self, port, buttonstr):
        self.state = False
        self.port = port
        self.buttonstr = buttonstr
        port_str = '{:02x}'.format(port)
        self.cmd_data = bytes.fromhex('77 68 05 00 01 E1 {} 01 0A'.format(port_str))

    def clicked(self):
        serial.write(self.cmd_data)
        response = serial.read()
        buttonclick="no"
        if len(response) == 9 and  response[5]==0xE1 and response[6]==self.port:
            button_byte=response[3:5]+bytes.fromhex('00 00')
            button_value=struct.unpack('<i', struct.pack('4B', *(button_byte)))[0]
            # print("%x"%button_value)
            if button_value>=0x1f1 and button_value<=0x1ff:
                buttonclick="UP"
            elif button_value>=0x330 and button_value<=0x33f:
                buttonclick = "LEFT"
            elif button_value>=0x2ff and button_value<=0x30f:
                buttonclick = "DOWN"
            elif button_value>=0x2a0 and button_value<=0x2af:
                buttonclick = "RIGHT"
            else:
                buttonclick
        return self.buttonstr==buttonclick

class Cruiser:
    def __init__(self):
        hwc_shape = list(cnn_args["shape"])
        hwc_shape[3], hwc_shape[1] = hwc_shape[1], hwc_shape[3]
        self.buf = np.zeros(hwc_shape).astype('float32')
        self.predictor = predictor_wrapper.PaddleLitePredictor()
        self.predictor.load(cruise_model)

    def cruise(self, frame):
        res = infer_cnn(self.predictor,self.buf, frame)
        # print(res)
        return res

if __name__ == "__main__":
     c = Cruiser()
    # b = Button()
     driver = Driver()
     start_button = Button(1, "UP")

     stop_button = Button(1, "DOWN")
     front_camera.start()
     # 基准速度
     driver.set_speed(25)
     # 转弯系数
     driver.cart.Kx = 0.8
     # 延时
     time.sleep(0.5)
     while True:
         if start_button.clicked():
             time.sleep(0.3)
             break
         print("Wait for start!")
     while True:
         front_image = front_camera.read()
         driver.go(front_image)
         if check_stop():
             driver.stop()
             print("End of program!")
             break
    # img_cv = cv2.imread('/home/root/workspace/autocar/src/test/cruise/7.png')
    # data = c.cruise(img_cv)