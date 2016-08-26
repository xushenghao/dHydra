# -*- coding: utf-8 -*-
import redis
conn = redis.Redis( host = "127.0.0.1" )

def get_workers_from_redis():
    keys = conn.keys("dHydra.Worker.*.*.Info")

def get_workers_from_folder():
    
