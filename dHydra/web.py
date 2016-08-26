# -*- coding: utf-8 -*-
"""
# Created on
# @author:
# @contact:
"""
import tornado.ioloop
import tornado.web
import os
from dHydra.console import *

# 首页根目录
class IndexHandler(tornado.web.RequestHandler):
	def prepare(self):
		"""
		单入口做URI路由转发，交给对应Handler处理
		"""
		request = self.request
		application = self.application
		# kwargs = self.kwargs
		uri = self.request.uri
		print("This is IndexHandler")

	def get(self, *args ):
		self.render( "index.html" )
		print(args)

	def get_template_path(self):
		"""
		重写get_template_path
		"""
		return os.path.split(os.path.realpath(__file__))[0] + "/templates"

class WorkerHandler(tornado.web.RequestHandler):
	def get(self, worker_name, method_name):
		if method_name == "":
			method_name = "index"
		print("Worker Name: {}, method_name: {}".format(worker_name, method_name))
		self.render(method_name+".html")
		# self.render("index.html")

	def prepare(self):
		print("This is WorkerHandler")

	def get_template_path(self):
		"""
		重写get_template_path
		"""
		if self.path_args[1] == "":
			self.path_args[1] = "index"
		if os.path.exists( os.getcwd()+"/Worker/" + self.path_args[0] + "/templates/"+self.path_args[1]+".html" ):
			return os.getcwd()+"/Worker/" + self.path_args[0] + "/templates"
		else:
			return os.path.split(os.path.realpath(__file__))[0] + "/Worker/"+self.path_args[0]+"/templates"

class ApiHandler(tornado.web.RequestHandler):
	def get(self, class_name, method):
		controller = {"class_name": class_name, "method": method}
		self.write(controller)

def make_app():
	"""
	/<addon_type>/<addon_name>/<addon_controller>/<method>
	------
		e.g.:
		"/action/print_sina_l2/main_controller/index"
	"""
	return tornado.web.Application([
		# (r"/favicon.ico", tornado.web.StaticFileHandler, { "path": os.getcwd() + "/static/" } ),
		(r"/static/js/(.*)", tornado.web.StaticFileHandler,  { "path": os.getcwd() + "/static/js/" } ),
		(r"/static/css/(.*)", tornado.web.StaticFileHandler,  { "path": os.getcwd() + "/static/css/" } ),
		(r"/", IndexHandler),
		(r"/api/Worker/(.*)/(.*)/", ApiHandler),	# ClassName, MethodName
		(r"/Worker/(.*)/(.*)", WorkerHandler)
    ])

if __name__ == "__main__":
	app = make_app()
	app.listen(5000)
	tornado.ioloop.IOLoop.current().start()
