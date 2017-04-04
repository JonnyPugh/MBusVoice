# Use this error for HTTP error responses
class RequestError(Exception):
	def __init__(self, message, code):
		self.code = code
		self.json = {"error":  message}
		super(RequestError, self).__init__(message)
