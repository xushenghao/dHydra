# -*- coding: utf-8 -*-
import redis
import copy
from dHydra.core.Functions import *

conn = redis.Redis( host = "127.0.0.1" )

def get_workers_from_redis( arguments = None ):
    keys = conn.keys("dHydra.Worker.*.*.Info")
    for i in range(0, len(keys)):
        keys[i] = keys[i].decode("utf-8")
    result = {
        "error_code" : 0,
        "error_msg" : "",
        "res"       : keys,
    }
    return result

def get_alive_workers( arguments = None ):
    alive_workers = dict()
    keys = get_workers_from_redis()["res"]
    for item in keys:
        x = item.split(".")
        worker_name = x[2].encode("utf-8")
        nickname = x[3].encode("utf-8")
        info = conn.hgetall( item )
        if info[b"status"] == b"started":
            alive_workers[nickname] = copy.deepcopy(info)
    result = {
        "error_code" : 0,
        "error_msg" : "",
        "res"       : alive_workers,
    }
    print(result)
    return result


def workers( arguments = None ):
    result = {
        "error_code" : 0,
        "error_msg" : "",
        "res"       : get_workers(),
    }
    return result
