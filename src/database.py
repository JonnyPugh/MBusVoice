from config import bitly_token
from bus_info import BusInfo
from request_error import RequestError
from requests import get
from boto3 import resource
from botocore.exceptions import ClientError

# Records are used to cache user preferences from the database and
# write back those preferences if they are modified
class Record(object):
	# Table used by all Records
	__table = resource("dynamodb", region_name="us-east-1").Table("UserPreferences")

	# Put an empty record for the specified user in the database
	@staticmethod
	def create(ID):
		try:
			r = get("https://api-ssl.bitly.com/v3/shorten", 
				params={
					"access_token": bitly_token, 
					"longUrl": "https://y7r89izao4.execute-api.us-east-1.amazonaws.com/web?ID="+ID
				}
			)
			r.raise_for_status()
			Record.__table.put_item(Item={"ID": ID, "url": r.json()["data"]["url"]})
		except ClientError:
			raise _DynamoError

	# Get the preferences of the specified user from the database
	def __init__(self, ID):
		self.__write = False
		try:
			# Get the user's preferences
			item = Record.__table.get_item(Key={"ID": ID})["Item"]
		except KeyError:
			raise _NoUser
		except ClientError as e:
			raise _DynamoError

		# Cache the user's preferences
		self.__ID = ID
		self.__home = item.get("home")
		self.__destination = item.get("destination")
		self.__order = item.get("order", [])
		self.__url = item["url"]

		# Cast time and all stop ids in groups to 
		# ints since they are returned as decimals
		self.__time = int(item.get("time", 0))
		self.__groups = item.get("groups", {})
		for nickname in self.__groups:
			for i in xrange(len(self.__groups[nickname])):
				self.__groups[nickname][i] = int(self.__groups[nickname][i])

	# Write the preferences of the user to the 
	# database if they were modified
	def __del__(self):
		if self.__write:
			item = {
				"ID": self.__ID, 
				"groups": self.__groups, 
				"order": self.__order, 
				"time":self.__time,
				"url": self.__url
			}
			if self.__home:
				item["home"] = self.__home
			if self.__destination:
				item["destination"] = self.__destination
			try:
				Record.__table.put_item(Item=item)
			except ClientError:
				raise _DynamoError

	# Define getters and setters for all user preferences
	@property
	def time(self):
		return self.__time
	@time.setter
	def time(self, time):
		if time < 0 or time > 30:
			self.__write = False
			raise _InvalidTime
		self.__time = time
		self.__write = True

	@property
	def home(self):
		return self.__home
	@home.setter
	def home(self, home):
		if home != None and home not in self.__groups:
			self.__write = False
			raise _NicknameDoesNotExist(home)
		self.__home = home
		self.__write = True

	@property
	def destination(self):
		return self.__destination
	@destination.setter
	def destination(self, destination):
		if destination != None and destination not in self.__groups:
			self.__write = False
			raise _NicknameDoesNotExist(destination)
		self.__destination = destination
		self.__write = True

	@property
	def groups(self):
		return self.__groups
	@groups.setter
	def groups(self, groups):
		for nickname in groups:
			if not nickname.replace(" ", "").isalnum():
				self.__write = False
				raise _InvalidNickname
			bus_info = BusInfo()
			for stop_id in groups[nickname]:
				if stop_id not in bus_info.stops:
					self.__write = False
					raise _InvalidStop(stop_id)
		self.__groups = groups
		self.__write = True

	@property
	def order(self):
		return self.__order
	@order.setter
	def order(self, order):
		for nickname in order:
			if nickname not in self.__groups:
				self.__write = False
				raise _InvalidNickname(nickname)
			if nickname in [self.__home, self.__destination]:
				self.write = False
				raise _InvalidOrder
		self.__order = order
		self.__write = True

	@property
	def url(self):
		return self.__url

# Internal Exception types used by Records
class _NoUser(RequestError):
	def __init__(self):
		super(_NoUser, self).__init__("The user does not exist in the database", 401)

class _DynamoError(RequestError):
	def __init__(self):
		super(_DynamoError, self).__init__("There was a problem communicating with the database", 502)

class _InvalidInput(RequestError):
	def __init__(self, message):
		super(_InvalidInput, self).__init__(message, 400)

class _InvalidTime(_InvalidInput):
	def __init__(self):
		super(_InvalidTime, self).__init__("The time must be between 0 and 30")

class _InvalidNickname(_InvalidInput):
	def __init__(self):
		super(_InvalidNickname, self).__init__("Nicknames must only contain alphanumeric characters and spaces")

class _InvalidStop(_InvalidInput):
	def __init__(self, stop_id):
		super(_InvalidStop, self).__init__("The stop ID '" + str(stop_id) + "' is invalid")

class _NicknameDoesNotExist(_InvalidInput):
	def __init__(self, nickname):
		super(_NicknameDoesNotExist, self).__init__("The nickname '" + nickname + "' does not exist")

class _InvalidOrder(_InvalidInput):
	def __init__(self):
		super(_InvalidOrder, self).__init__("The order must not contain the home or destination")
