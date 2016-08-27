# -*- coding: utf-8 -*-
import redis
from dHydra.core.Functions import *

conn = redis.Redis( host = "127.0.0.1" )

def get_workers_from_redis( arguments = None ):
    keys = conn.keys("dHydra.Worker.*.*.Info")
    return keys

def workers( arguments = None ):
    result = {
        "error_code" : 0,
        "error_msg" : "",
        "res"       : get_workers(),
    }
    return result
