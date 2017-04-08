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

	# Define getters for all user preferences and a
	# setter for time
	@property
	def home(self):
		return self.__home
	@property
	def destination(self):
		return self.__destination
	@property
	def groups(self):
		return self.__groups
	@property
	def order(self):
		return self.__order
	@property
	def time(self):
		return self.__time
	@time.setter
	def time(self, time):
		if time < 0 or time > 30:
			raise _InvalidTime
		self.__time = time
		self.__write = True
	@property
	def url(self):
		return self.__url

	# Give the specified group the specified stops
	# This is used for both creating new groups and modifying existing groups
	# If the nickname is for the home, the home flag should be True
	# If the nickname is for the destination, the home flag should be False
	# Otherwise, the home flag should be None
	# Raise an exception if the nickname or any stop IDs are invalid
	def put_group(self, nickname, stops, home=None):
		if not nickname.replace(" ", "").isalnum():
			raise _InvalidNickname
		bus_info = BusInfo()
		for stop_id in stops:
			if stop_id not in bus_info.stops:
				raise _InvalidStop(stop_id)
		if home:
			self.__home = nickname
		elif home == False:
			self.__destination = nickname
		elif nickname not in self.__groups:
			self.__order.append(nickname)
		self.__groups[nickname] = stops
		self.__write = True
		
	# Delete the specified group
	# Raise an exception if the nickname does not exist
	def delete_group(self, nickname):
		if nickname not in self.__groups:
			raise _NicknameDoesNotExist(nickname)
		if nickname == self.__home:
			self.__home = None
		elif nickname == self.__destination:
			self.__destination = None
		else:
			self.__order.remove(nickname)
		del self.__groups[nickname]
		self.__write = True		

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
