# -*- coding: utf-8 -*-
from dHydra.core.Worker import Worker
import time


class Demo(Worker):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__listener__.subscribe( [ self.redis_key + "Pub" ] )

    def __producer__(self):
        i = 0
        while True:
            self.publish( i )
            i += 1
            time.sleep(1)
