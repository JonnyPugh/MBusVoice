from config import bitly_token
from requests import get
from boto3 import resource
from botocore.exceptions import ClientError

# Indicate that there was an error trying to modify the database
# Use a user level error message and an HTTP error code
class DatabaseError(Exception):
	def __init__(self, message, code):
		self.code = code
		self.json = {"error":  message}
		super(DatabaseError, self).__init__(message)

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

		# Cast min_time and all stop ids in nicknames to 
		# ints since they are returned as decimals
		self.__min_time = int(item.get("min_time", 0))
		self.__nicknames = item.get("nicknames", {})
		for nickname in self.__nicknames:
			for i in xrange(len(self.__nicknames[nickname])):
				self.__nicknames[nickname][i] = int(self.__nicknames[nickname][i])

	# Write the preferences of the user to the 
	# database if they were modified
	def __del__(self):
		if self.__write:
			item = {
				"ID": self.__ID, 
				"nicknames": self.__nicknames, 
				"order": self.__order, 
				"min_time":self.__min_time,
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
	# setter for min_time
	@property
	def home(self):
		return self.__home
	@property
	def destination(self):
		return self.__destination
	@property
	def nicknames(self):
		return self.__nicknames
	@property
	def order(self):
		return self.__order
	@property
	def min_time(self):
		return self.__min_time
	@min_time.setter
	def min_time(self, min_time):
		if not isinstance(min_time, (int, long)) or min_time < 0 or min_time > 30:
			raise _InvalidTime
		self.__min_time = min_time
		self.__write = True
	@property
	def url(self):
		return self.__url

	# Swap the current destination group with the specified group
	# Raise an exception if the specified group does not exist or
	# if the specified group is the home or destination group
	def swap_destination(self, nickname):
		self.__verify_nickname(nickname)
		if nickname in [self.__home, self.__destination]:
			raise _InvalidSwap
		index = 0
		while self.__order[index] != nickname:
			index += 1
		if self.__destination:	
			self.__order[index] = self.__destination
		self.__destination = nickname
		self.__write = True

	# Give the specified nickname the specified stops
	# This is used for both creating new groups and modifying existing groups
	# If the nickname is for the home, the home flag should be True
	# If the nickname is for the destination, the home flag should be False
	# Otherwise, the home flag should be None
	# Setting the home flag is only necessary when initially creating a
	# home or destination group but it will not be a problem if it is set
	# when the home or destination group already exists
	def put_nickname(self, nickname, stops, home=None):
		if home:
			self.__home = nickname
		elif home == False:
			self.__destination = nickname
		elif nickname not in self.__nicknames:
			self.__order.append(nickname)
		self.__nicknames[nickname] = stops
		self.__write = True

	# Change the specified nickname to the new specified nickname
	# Raise an exception if the current nickname doesn't exist or if
	# the new nickname already exists
	def change_nickname(self, current_nickname, new_nickname):
		self.__verify_nickname(current_nickname)
		if new_nickname in self.__nicknames:
			raise _DuplicateNickname(new_nickname)
		if current_nickname == self.__home:
			self.__home = new_nickname
		elif current_nickname == self.__destination:
			self.__destination = new_nickname
		else:
			self.__order[self.__order.index(current_nickname)] = new_nickname
		self.__nicknames[new_nickname] = self.__nicknames[current_nickname]
		del self.__nicknames[current_nickname]
		self.__write = True
		
	# Delete the specified nickname
	# Raise an exception if the nickname does not exist
	def delete_nickname(self, nickname):
		self.__verify_nickname(nickname)
		if nickname == self.__home:
			self.__home = None
		elif nickname == self.__destination:
			self.__destination = None
		else:
			self.__order.remove(nickname)
		del self.__nicknames[nickname]
		self.__write = True

	# Verify that the specified nickname is valid
	# Raise an exception if the nickname does not exist
	def __verify_nickname(self, nickname):
		if nickname not in self.__nicknames:
			raise _InvalidNickname(nickname)

# Internal Exception types used by Records
# Only DatabaseErrors should be used outside this file
class _NoUser(DatabaseError):
	def __init__(self):
		super(_NoUser, self).__init__("The user does not exist in the database", 401)

class _DynamoError(DatabaseError):
	def __init__(self):
		super(_DynamoError, self).__init__("There was a problem communicating with the database", 502)

class _InvalidInput(DatabaseError):
	def __init__(self, message):
		super(_InvalidInput, self).__init__(message, 400)

class _InvalidNickname(_InvalidInput):
	def __init__(self, nickname):
		super(_InvalidNickname, self).__init__("The nickname '" + nickname + "' does not exist")

class _InvalidSwap(_InvalidInput):
	def __init__(self):
		super(_InvalidSwap, self).__init__("Home and destination groups cannot swap with the destination group")

class _InvalidTime(_InvalidInput):
	def __init__(self):
		super(_InvalidTime, self).__init__("The time must be an integer between 0 and 30")

class _DuplicateNickname(_InvalidInput):
	def __init__(self, nickname):
		super(_DuplicateNickname, self).__init__("The nickname '" + nickname + "' already exists")
