from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from nhl_schedule_translate import app

HTTP_SERVER = HTTPServer(WSGIContainer(app))
HTTP_SERVER.listen(8080)
IOLoop.instance().start()