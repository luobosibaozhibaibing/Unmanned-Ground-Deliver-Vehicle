#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import threading
from time import sleep
from queue import Queue
import cv2
import numpy as np
from functools import reduce

print(sys.version)

q = Queue()

def run(n):
    thread = threading.current_thread()
    thread.setName('thread-fuck')
    print('tid is: {0}'.format(thread.ident))
    print('thread name is: {0}'.format(thread.getName()))

    for i in range(100):
        img = np.random.randint(0,255,(200,300)).astype(np.uint8)
        q.put(img)
        sleep(0.1)

    q.put(0)


if __name__ == '__main__':
    thread = threading.Thread(target=run, args=(6,))
    thread.start()

    while True:
        try:
            item = q.get(block=False)
        except Exception as e:
            keycode = cv2.waitKey(20)
            if keycode & 0xFF == ord('q'):
                break
            continue

        if type(item) == int:
            break

        if type(item) == type(0):
            break
        cv2.imshow('fuck', item)

    thread.join()

    cv2.waitKey(0)
    cv2.destroyAllWindows()
    print('done!')