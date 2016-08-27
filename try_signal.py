# coding: utf-8
from dHydra.console import *
import time

demo = get_worker_class("Demo")
demo.start()
print(demo.pid)
demo.join()
print(demo.pid)
while True:
    time.sleep(10)
