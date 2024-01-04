#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import os
import datetime
import time
import cv2
import config
import numpy as np
from widgets import Button
from camera import Camera
from driver import Driver, SLOW_DOWN_RATE
from cruiser import Cruiser
import argparse
import threading

from detectors import SignDetector,TaskDetector


# 测试图片存放位置和测试输出结果位置
cruiser_images_dir = "test/cruise"
cruiser_result_dir = "test/cruise_res"
task_images_dir = "test/task"
task_result_dir = "test/task_res"
sign_images_dir = "test/sign"
sign_result_dir = "test/sign_res"
front_image_dir = "test/front"
front_result_dir = "test/front_res"

image_extensions = [".png",".jpg",".jpeg"]

# front_camera = Camera(config.front_cam, [640, 480])
# side_camera = Camera(config.side_cam, [640, 480])
driver = Driver()
cruiser = Cruiser()
sd = SignDetector()
# 程序开启运行开关
start_button = Button(1, "UP")
# 程序关闭开关
stop_button = Button(1, "DOWN")


def draw_cruise_result(frame, res):
    color = (0, 244, 10)
    thickness = 2

    font = cv2.FONT_HERSHEY_SIMPLEX
    org = 450, 50

    fontScale = 1
    txt = "{:.4f}".format(round(res, 5))
    frame = cv2.putText(frame, txt, org, font,
                       fontScale, color, thickness, cv2.LINE_AA)
    print("angle=",txt)
    return frame


#######################################################################
def draw_res(frame, results):
    res = list(frame.shape)
    print(results)
    for item in results:
        print(item)
        print(type(item))
        left = item.relative_box[0] * res[1]
        top = item.relative_box[1] * res[0]
        right = item.relative_box[2] * res[1]
        bottom = item.relative_box[3] * res[0]
        start_point = (int(left), int(top))
        end_point = (int(right), int(bottom))
        color = (0, 244, 10)
        thickness = 2
        frame = cv2.rectangle(frame, start_point, end_point, color, thickness)
        font = cv2.FONT_HERSHEY_SIMPLEX
        org = start_point[0], start_point[1] - 10
        fontScale = 1
        frame = cv2.putText(frame, item.name, org, font,
                           fontScale, color, thickness, cv2.LINE_AA)
        return frame


#######################################################################
# front_camera.start()
# side_camera.start()
# 基准速度
driver.set_speed(20)
# 转弯系数
driver.cart.Kx = 0.9
# 延时
time.sleep(0.5)


#######################################################################
def test_camera():
    # 选择摄像头
    # side_video = cv2.VideoCapture(config.side_cam)
    # front_video = cv2.VideoCapture(config.front_cam)

    front_video = Camera(config.front_cam, [640, 480]).stream
    side_video = Camera(config.side_cam, [320, 240]).stream

    width = (int(side_video.get(cv2.CAP_PROP_FRAME_WIDTH)))
    height = (int(side_video.get(cv2.CAP_PROP_FRAME_HEIGHT)))

    while side_video.isOpened():
        ret_side, frame_side = side_video.read()
        ret_front, frame_front = front_video.read()

        angle = driver.go(frame_front)
        text = str(angle)[:9]
        cv2.putText(frame_front, text, (20, 50), cv2.FONT_HERSHEY_COMPLEX, 1.0,
                    (10, 20, 20), 2)

        # 前向，用于输入到预训练好的分类器
        frame_front = cv2.resize(frame_front, (int(width), int(height)), interpolation=cv2.INTER_CUBIC)
        # 侧向
        frame_side = cv2.resize(frame_side, (int(width), int(height)), interpolation=cv2.INTER_CUBIC)

        '''
            分别放入对应的分类器
        '''
        # 前向分类器输入, frame_front
        # frame = draw_cruise_result(frame_front, angle)
        signs, index = sd.detect(frame_front)
        draw_res(frame_front, signs)
        # 侧向分类器输入, frame_side

        # 结果处理

        frame_up = np.hstack((frame_front, frame_side))
        cv2.imshow('frame', frame_up)

        # cv2.imshow('front_frame', frame_front)

        key = cv2.waitKey(10)
        if int(key) == 113:
            break
        if check_stop():
            driver.stop()
            print("End of program!")
            break

    side_video.release()
    front_video.release()


#######################################################################

# 确认"DOWN"按键是否按下，程序是否处于等待直行状态
def check_stop():
    if stop_button.clicked():
        return True
    return False


def front_cam_thread_func():
    front_camera = Camera(config.front_cam, [640, 480])
    while True:
        front_image = front_camera.read()

        if cv2.waitKey(200) == ord('q'):
            break
        angle = driver.go(front_image)

        text = str(angle)[:9]
        cv2.putText(front_image, text, (20, 50), cv2.FONT_HERSHEY_COMPLEX, 1.0,
                    (10, 20, 20), 2)
        cv2.imshow('front_camera', front_image)

        if check_stop():
            driver.stop()
            print("End of program!")
            break
        (front_camera.grabbed, front_camera.frame) = front_camera.stream.read()
    # driver.stop()
    front_camera.stop()
    pass


def side_cam_thread_func():
    while True:
        side_image = side_camera.read()
        if cv2.waitKey(200) == ord('q'):
            break
        cv2.imshow('side_camera', side_image)
        if check_stop():
            print("End of program!")
            break
        (side_camera.grabbed, side_camera.frame) = side_camera.stream.read()
    # driver.stop()
    side_camera.stop()
    # pass


if __name__ == '__main__':
    # 将注释取消则关闭开机自启动
    # while not start_button.clicked():
    #     pass
    print('start!')
    parser = argparse.ArgumentParser(description='arg parser.')
    parser.add_argument('-s', '--switch', default='1')

    args = parser.parse_args()
    if args.switch == '1':
        front_cam_thr = threading.Thread(target=front_cam_thread_func)
        front_cam_thr.start()
    elif args.switch == '2':
        test_cam_thr = threading.Thread(target=test_camera)
        test_cam_thr.start()

    # side_cam_thr = threading.Thread(target=side_cam_thread_func)
    # side_cam_thr.start()
    # os.system('killall -9 python3')
    # side_camera.stop()
