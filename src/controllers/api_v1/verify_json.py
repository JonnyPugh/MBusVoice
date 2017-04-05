from request_error import RequestError

# Verify that the key is in the JSON, its value is of type t,
# and optionally that its value is one of the specified values
def verify(json, key, t, values=None):
	if key not in json:
		raise _JSONKeyError(key)
	if not isinstance(json[key], t):
		raise _JSONTypeError(t.__name__)
	if values and json[key] not in values:
		raise _JSONValueError(values)

# Internal errors used by the verification functions
class _JSONError(RequestError):
	def __init__(self, expected, value):
		super(_JSONError, self).__init__("Expected a " + expected + " of '" + value + "'", 400)

class _JSONKeyError(_JSONError):
	def __init__(self, key):
		super(_JSONKeyError, self).__init__("key", key)

class _JSONTypeError(_JSONError):
	def __init__(self, t):
		super(_JSONTypeError, self).__init__("type", t)

class _JSONValueError(_JSONError):
	def __init__(self, values):
		super(_JSONValueError, self).__init__("value", "/".join(values))
