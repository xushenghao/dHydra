from dHydra.core.Worker import Worker
from dHydra.console import *

class Monitor(Worker):
    def __init__(self):
        super().__init__()

    def start_worker(self, worker_name, nickname):
        worker = get_worker_class(worker_name)
        thread_start_worker(worker, nickname)
