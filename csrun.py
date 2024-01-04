#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import datetime
import time
import config
from widgets import Button
from camera import Camera
from driver import Driver, SLOW_DOWN_RATE
from cruiser import Cruiser
from run import check_stop
from  config import front_cam
from camera import Camera
front_camera = Camera(config.front_cam, [640, 480])
driver = Driver()
cruiser = Cruiser()
start_button = Button(1, "UP")
stop_button = Button(1, "DOWN")
if __name__=='__main__':
    front_camera.start()
    #基准速度
    driver.set_speed(25)
    #转弯系数
    driver.cart.Kx=0.9

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
    front_camera.stop()
while True:
    front_image = front_camera.read()
    driver.go(front_image)
    if check_stop():
        print("End of program!")
        break
front_camera.stop()

