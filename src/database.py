from boto3 import resource

class DatabaseFailure(Exception):
	def __init__(self, function):
		super(Exception, self).__init__("Database Failure in function " + function)

# Records are used to cache user preferences from the database and
# write back those preferences if they are modified
class Record(object):
	# Table used by all Records
	__table = resource("dynamodb", region_name="us-east-1").Table("UserPreferences")

	# Put an empty record for the spcified user in the database
	@staticmethod
	def create(ID):
		try:
			Record.__table.put_item(Item={"ID": ID})
		except:
			raise DatabaseFailure("create")

	# Get the preferences of the specified user from the database
	def __init__(self, ID):
		try:
			# Cache the user's preferences
			self.__write = False
			item = Record.__table.get_item(Key={"ID": ID})["Item"]
			self.__ID = ID
			self.__home = item.get("home")
			self.__destination = item.get("destination")
			self.__order = item.get("order", [])

			# Cast min_time and all stop ids in nicknames to 
			# ints since they are returned as decimals
			self.__min_time = int(item.get("min_time", 0))
			self.__nicknames = item.get("nicknames", {})
			for nickname in self.__nicknames:
				for i in xrange(len(self.__nicknames[nickname])):
					self.__nicknames[nickname][i] = int(self.__nicknames[nickname][i])
		except Exception as e:
			raise DatabaseFailure("__init__")

	# Write the preferences of the user to the 
	# database if they were modified
	def __del__(self):
		if self.__write:
			try:
				item = {
					"ID": self.__ID, 
					"nicknames": self.__nicknames, 
					"order": self.__order, 
					"min_time":self.__min_time
				}
				if self.__home:
					item["home"] = self.__home
				if self.__destination:
					item["destination"] = self.__destination
				Record.__table.put_item(Item=item)
			except:
				raise DatabaseFailure("__del__")

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
		if min_time < 0 or min_time > 30:
			raise DatabaseFailure("set_time")
		self.__min_time = min_time
		self.__write = True

	# Swap the current destination group with the specified group
	# Raise an exception if the specified group does not exist
	def swap_destination(self, nickname):
		index = 0
		while self.__order[index] != nickname:
			index += 1
			if index == len(self.__order):
				raise DatabaseFailure("swap_destination")
		if self.__destination:	
			self.__order[index] = self.__destination
		self.__destination = nickname
		self.__write = True

	# Give the specified nickname the specified stops
	# This is used for both creating new groups and modifying 
	# existing groups
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
	# Raise an exception if the old nickname doesn't exist or if
	# the new nickname already exists
	def change_nickname(self, old_nickname, new_nickname):
		if old_nickname not in self.__nicknames or new_nickname in self.__nicknames:
			raise DatabaseFailure("change_nickname")
		if old_nickname == self.__home:
			self.__home = new_nickname
		elif old_nickname == self.__destination:
			self.__destination = new_nickname
		else:
			self.__order[self.__order.index(old_nickname)] = new_nickname
		self.__nicknames[new_nickname] = self.__nicknames[old_nickname]
		del self.__nicknames[old_nickname]
		self.__write = True
		
	# Delete the specified nickname
	# Raise an exception if the nickname does not exist
	def delete_nickname(self, nickname):
		if nickname not in self.__nicknames:
			raise DatabaseFailure("delete_nickname")
		if nickname == self.__home:
			self.__home = None
		elif nickname == self.__destination:
			self.__destination = None
		else:
			self.__order.remove(nickname)
		del self.__nicknames[nickname]
		self.__write = True
