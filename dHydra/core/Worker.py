# -*- coding: utf-8 -*-
"""
Action类
每个Action自带一个Queue
Created on 03/30/2016
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
from datetime import datetime
# from dHydra.core.Globals import *
# from dHydra.core.Functions import *
# from dHydra.app import PRODUCER_NAME, PRODUCER_HASH
# import dHydra.core.ThreadManager as ThreadManager
# import dHydra.core.util as util
from abc import ABCMeta

class Worker(multiprocessing.Process):
	__metaclass__ = ABCMeta
	def __init__(	self
				,	singleton = True	# 单例模式
				,	name = "Default"	# Worker的自定义名字
				,	description = "No Description"	# 备注说明
				,	log_level = "INFO" # "DEBUG","INFO","WARNING"
				,	heart_beat_interval = 3	# 默认3秒心跳
				,	**kwargs
				):
		self.__name__ = name
		self.__singleton__ = singleton
		self.__description__ = description
		self.__heart_beat_interval__ = heart_beat_interval
		self.__threads__ = dict()	# 被监控的线程
		self.redis_key = "dHydra.Worker."+self.__class__.__name__+"."+self.__name__+"."
		"""
		self.__threads__ = {
			"description"	: "该线程功能备注说明",
			"name"			: "该线程的名字",
			"target"		: "该线程的target"
			"restart_mode"	: "重启模式，可以为 manual/auto/remove;manual则代表允许管理员发送命令手工重启线程,auto则一旦线程关闭立即自动开启，remove则代表一旦线程结束就从监控列表移除",
			"restart_func"	: "自动/手动重启时调用的方法",
		}
		"""
		self.logger = self.get_logger( level = log_level )
		if self.check_prerequisites() is True:
			super().__init__()
		else:
			exit(0)

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
		pass


	def monitor_add_thread( self, thread, description = "No Description", restart_mode = "manual", restart_func = self.__auto_restart_thread__ ):
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
			self.redis_conn = redis.Redis()
			self.redis_conn.client_list()
		except redis.ConnectionError:
			self.logger.error("Cannot connect to redis")
			return False
		self.mongo = V("DB").get_mongodb()
		if self.mongo is False:
			self.logger.error("Cannot connect to mongodb")
			return False
		# 如果是单例，检测是否重复开启
		return True

	def __thread_listen_command__(self):
		#
		self.command_listener = self.redis_conn.pubsub()
		channel_name = self.redis_key + "Command"
		self.command_listener.subscribe( [channel_name] )
		while True:
			msg_command = self.command_listener.get_message()
			if msg_command:
				self.__command_handler__(msg_command)
			else:
				time.sleep(0.01)

	def __heart_beat__(self):
		# 心跳线程
		while True:
			# flush status infomation to redis
			status = dict()
			status["heart_beat"] = datetime.now()
			time.sleep(self.__heart_beat_interval__)

	def run(self):
		"""
		初始化Worker
		"""
		# 开启心跳线程，并且加入线程监控
		self.__thread_heart_beat__ = threading.Thread( target = self.__heart_beat__ )
		self.__thread_heart_beat__.setDaemon(True)
		self.monitor_add_thread( thread = self.__thread_heart_beat__, description = "Heart Beat", restart_mode = "auto", restart_func = self.__thread_auto_restart__ )
		self.__thread_heart_beat__.start()

		# 开启监听命令线程
		self.__thread_listen_command__ = threading.Thread( target = self.__listen_command__ )
		self.__thread_listen_command__.setDaemon(True)
		self.monitor_add_thread( thread = self.__thread_listen_command__, description = "Listening Command Channel", restart_mode = "auto", restart_func = self.__thread_auto_restart__ )
		self.__thread_listen_command__.start()

		# 检查初始化设置，按需开启
		#### PUB线程
		self.__thread_pub__ = threading.Thread( target = self.__producer__ )
		self.__thread_pub__.setDaemon(True)
		self.monitor_add_thread( thread = self.__thread_pub__, description = "DATA PUBLISHER", restart_mode = "auto", restart_func = self.__thread_auto_restart__ )
		self.__thread_pub__.start()

		#### LISTENER
		self.__thread_sub__ = threading.Thread( target = self.__consumer__ )
		self.__thread_sub__.setDaemon(True)
		self.__thread_sub__.start()

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


	def subscribe(self, worker_name):
		"""
		订阅Worker
		"""
		# Step 1 : 检查Worker是否存在
		# Step 2 : 检查Worker是否开启

	def msg_listener(self):
		while True:
			msg = self.listener.get_message()
			if msg:
				self.handler(msg)
			else:
				time.sleep(0.001)

	def unsubscribe(self, worker_name):
		"""
		退订Worker
		"""
		pass

	# 需要在子类中重写的数据处理方法
	def handler(self, msg):
		return
