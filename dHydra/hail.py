import click
from dHydra.console import *
import dHydra.web
import threading

@click.command()
@click.argument('what', nargs = -1)
def hail(what = None):
    try:
        if what[0] != "dHydra":
            print("Hail What??")
            exit(0)
        else:
            print("Welcome to dHydra!")
            # open a thread for the Worker of Monitor
            monitor = get_worker_class("Monitor")
            thread_monitor = threading.Thread(target = thread_start_worker ,args=(monitor,) )
            thread_monitor.setDaemon(True)

            # open a thread for webserver
            thread_tornado = threading.Thread(target = dHydra.web.start_server)
            # web = dHydra.web.start_server()
            thread_monitor.start()
            print("Monitor has started")
            thread_tornado.start()
            thread_monitor.join()
            thread_tornado.join()
    except Exception as e:
        print("Hail What?")
        print(e)

@click.command()
@click.argument('worker_name', nargs = 1)
@click.argument('nickname', nargs = -1)
def start(worker_name = None, nickname = None):
    # if worker_name is not None:
    #     # get the Worker instance
    #     t = threading.Thread(target = thread_start_worker, args = (worker) )
    #     t.setDaemon(True)
    #     t.start()
    pass
