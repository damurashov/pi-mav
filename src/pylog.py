
class Level:

	ERROR = 1
	WARNING = 2
	DEBUG = 3

class Log:

	@staticmethod
	def output(level, context, *args, **kwargs):
		pass

	@staticmethod
	def debug(context: list, *args, **kwargs):
		Log.output(Level.DEBUG, context, *args, **kwargs)

	@staticmethod
	def error(context: list, *args, **kwargs):
		Log.output(Level.ERROR, context, *args, **kwargs)
