# -*- coding: utf-8 -*-
"""
Worker抽象类
@author: Wen Gu
@contact: emptyset110@gmail.com
"""
import multiprocessing
import threading
import time
import logging
import redis
import pymongo
import json
import copy
from dHydra.console import *
from datetime import datetime
from abc import ABCMeta
import signal
import sys
import os

class Worker(multiprocessing.Process):
	__metaclass__ = ABCMeta
	def __init__(	self
				,	singleton = True	# 单例模式
				,	nickname = None	# Worker的自定义名字
				,	description = "No Description"	# 备注说明
				,	log_level = "INFO" # "DEBUG","INFO","WARNING"
				,	heart_beat_interval = 3	# 默认3秒心跳
				,	**kwargs
				):
		if nickname is None:
			self.__nickname__ = self.__class__.__name__ + "Default"
		else:
			self.__nickname__ = nickname
		self.nickname = self.__nickname__
		self.name = self.__nickname__
		self.__singleton__ = singleton
		self.__description__ = description
		self.__heart_beat_interval__ = heart_beat_interval
		self.__threads__ = dict()		# 被监控的线程
		self.__data_feeder__ = set()	# 本Worker订阅的内容
		self.__follower__ = set()		# Follower
		self.__error_msg__ = None		#
		self.__stop_info__ = None		#
		self.__stop_time__ = None		#
		self.__status__ = "init"		# "init", "error_exit", "suspended", "user_stopped", "normal"
		self.redis_key = "dHydra.Worker."+self.__class__.__name__+"."+self.__nickname__+"."
		self.channel_pub = self.redis_key + "Pub"
		"""
		self.__threads__ = {
		"nickname": {
			"description"	: "该线程功能备注说明",
			"name"			: "该线程的名字",
			"target"		: "该线程的target"
			"restart_mode"	: "重启模式，可以为 manual/auto/remove;manual则代表允许管理员发送命令手工重启线程,auto则一旦线程关闭立即自动开启，remove则代表一旦线程结束就从监控列表移除",
			"restart_func"	: "自动/手动重启时调用的方法",
		},
		}
		"""
		self.logger = self.get_logger( level = log_level )
		if self.check_prerequisites() is True:
			super().__init__()
			self.daemon = True
		else:
			sys.exit(0)
		self.shutdown_signals = [
			signal.SIGQUIT,  # quit 信号
			signal.SIGINT,  # 键盘信号
			signal.SIGHUP,  # nohup 命令
			signal.SIGTERM,  # kill 命令
		]

		for s in self.shutdown_signals:
			# 捕获退出信号后的要调用的,唯一的 shutdown 接口
			signal.signal(s, self.__on_termination__)

	def __auto_restart_thread__( self ):
		# Worker内置的默认自动重启线程方法
		pass

	def __command_handler__(self, msg_command):
		# cli is a dict with the following structure:
		"""
		msg_command = {
			"type"	:		"sys/customized",
			"operation"	:	"operation_name",
			"kwargs"	:	"suppose that the operation is a function, we need to pass some arguments",
			"token"		:	"the token is used to verify the authentication of the operation"
		}
		"""
		print(msg_command)
		msg_command = json.loads( msg_command.decode("utf-8").replace("\'","\"") )
		if msg_command["type"] == "sys":
			str_kwargs = ""
			for k in msg_command["kwargs"].keys():
				str_kwargs += (k + "=" + "\'"+msg_command["kwargs"][k] + "\'" + "," )
			eval( "self."+msg_command["operation_name"]+"("+ str_kwargs +")" )


	def monitor_add_thread( self, thread, description = "No Description", restart_mode = "manual", restart_func = None ):
		# 将该线程加入管理员监控范围
		pass

	def monitor_remove_thread(self, thread):
		# 取消管理员对线程thread的监控
		pass

	def check_prerequisites(self):
		"""
		检查是否满足开启进程的条件
		"""
		# 检测redis, mongodb连接
		try:
			self.__redis__ = redis.Redis(host = '127.0.0.1', port = 6379)
			self.__redis__.client_list()
			self.__listener__ = self.__redis__.pubsub()
			self.__listener__.subscribe(["dHydra"])
		except redis.ConnectionError:
			self.logger.error("Cannot connect to redis")
			return False
		self.mongo = V("DB").get_mongodb()
		if self.mongo is False:
			self.logger.error("Cannot connect to mongodb")
			return False
		# 如果是单例，检测是否重复开启
		return True

	def __listen_command__(self):
		#
		self.command_listener = self.__redis__.pubsub()
		channel_name = self.redis_key + "Command"
		self.command_listener.subscribe( [channel_name] )
		while True:
			msg_command = self.command_listener.get_message()
			if msg_command:
				if msg_command["type"] == "message":
					self.__command_handler__(msg_command["data"])
			else:
				time.sleep(0.01)

	def __heart_beat__(self):
		# flush status infomation to redis
		status = dict()
		status["heart_beat"] = datetime.now()
		status["nickname"] = self.__nickname__
		status["error_msg"] = self.__error_msg__
		status["stop_info"] = self.__stop_info__
		status["stop_time"] = self.__stop_time__
		status["status"] = self.__status__
		status["threads"] = copy.deepcopy( self.__threads__ )
		status["data_feeder"] = self.__data_feeder__
		status["pid"] = self.pid
		status["follower"] = self.__follower__
		self.__redis__.hmset( self.redis_key + "Info", status )

	def __producer__(self):
		pass

	def __consumer__(self):
		while True:
			data = self.__listener__.get_message()
			if data is not None:
				self.__data_handler__( data )
			else:
				time.sleep(0.001)

	def __before_termination__(self, sig):
		pass

	def __on_termination__(self, sig, frame):
		self.__before_termination__(sig)
		self.__status__ = "terminated"
		self.__heart_beat__()		# The last heart_beat, sad...
		sys.exit(0)

	def publish(self, data):
		# publish data to redis
		try:
			self.__redis__.publish( self.channel_pub , data )
		except Exception as e:
			self.logger.warning(e)

	def run(self):
		"""
		初始化Worker
		"""
		self.__status__ = "started"

		# 开启监听命令线程
		self.__thread_listen_command__ = threading.Thread( target = self.__listen_command__ )
		self.__thread_listen_command__.setDaemon(True)
		self.monitor_add_thread( thread = self.__thread_listen_command__, description = "Listening Command Channel", restart_mode = "auto", restart_func = self.__auto_restart_thread__ )
		self.__thread_listen_command__.start()

		# 检查初始化设置，按需开启
		#### PUB线程
		self.__thread_pub__ = threading.Thread( target = self.__producer__ )
		self.__thread_pub__.setDaemon(True)
		self.monitor_add_thread( thread = self.__thread_pub__, description = "DATA PUBLISHER", restart_mode = "auto", restart_func = self.__auto_restart_thread__ )
		self.__thread_pub__.start()

		#### LISTENER
		self.__thread_sub__ = threading.Thread( target = self.__consumer__ )
		self.__thread_sub__.setDaemon(True)
		self.monitor_add_thread( thread = self.__thread_sub__, description = "DATA CONSUMER", restart_mode = "auto", restart_func = self.__auto_restart_thread__ )
		self.__thread_sub__.start()

		while True:
			# heart beat
			self.__heart_beat__()
			time.sleep(self.__heart_beat_interval__)

	def get_logger(self, level):
		logger = logging.getLogger(self.__class__.__name__)
		if level is "DEBUG":
			logger.setLevel(10)
		elif level is "INFO":
			logger.setLevel(20)
		elif level is "WARNING":
			logger.setLevel(30)
		elif level is "ERROR":
			logger.setLevel(40)
		elif level is "CRITICAL":
			logger.setLevel(50)
		else:
			logger.setLevel(20)
		return logger

	def subscribe(self, worker_class_name = None, nickname = None ):
		"""
		订阅Worker
		"""
		# Step 1 : 检查Worker是否存在
		# if nickname is None:
			# find the worker_name
		# Step 2 : 检查Worker是否开启

	def unsubscribe(self, worker_name):
		"""
		退订Worker
		"""
		pass

	# 需要在子类中重写的数据处理方法
	def __data_handler__(self, msg):
		pass
