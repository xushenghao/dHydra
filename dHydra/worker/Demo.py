# -*- coding: utf-8 -*-
from dHydra.core.Worker import Worker
import time


class Demo(Worker):
    def __init__(self):
        super().__init__(

        )
        self.__listener__.subscribe( [ "dHydra.Worker.Demo.Default.Pub" ] )

    def __producer__(self):
        i = 0
        while True:
            self.publish( i )
            i += 1
            time.sleep(1)
