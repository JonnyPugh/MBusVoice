from boto3 import resource

class DatabaseFailure(Exception):
	def __init__(self, function):
		super(Exception, self).__init__("Database Failure in function " + function)

class Database(object):
	def __init__(self):
		self.__table = resource("dynamodb", region_name="us-east-1").Table("UserPreferences")

	def get_item(self, ID):
		try:
			item = self.__table.get_item(Key={"ID": ID})["Item"]

			# Don't return the ID since it has to be used to get the item
			del item["ID"]

			# Cast all numbers in min_time and nicknames from the database to ints since 
			# they are returned as decimals
			for key in item:
				if key == "min_time":
					item[key] = int(item[key])
				elif key == "nicknames":
					for aliases in item[key]:
						for i in range(len(item[key][aliases])):
							item[key][aliases][i] = int(item[key][aliases][i])
			return item
		except:
			raise DatabaseFailure("get_item")

	# Update a value in the specified item
	def update_item_field(self, ID, key, value):
		try:
			self.__table.update_item(Key={"ID": ID},
				UpdateExpression="set " + str(key) + " = :r",
				ExpressionAttributeValues={":r": value}
			)
		except:
			raise DatabaseFailure("update_item_field")

	# Put an empty item into the database		
	def put_item(self, ID):
		try:
			self.__table.put_item(
				Item={"ID": ID,
					"order": [],
					"nicknames": {},
					"min_time": 0
				}
			)
		except:
			raise DatabaseFailure("put_item")

	# Delete an item from the database
	def delete_item(self, ID):
		try:
			self.__table.delete_item(Key={"ID": ID})
		except:
			raise DatabaseFailure("delete_item")

# Interface:
# Edit home (check that it isn't a duplicate of another nickname) - set_home
# Edit destination (check that it isn't a duplicate of another nickname) - set_destination
# Swap destination with existing nickname - swap_destination(nickname)
# Change nicknames
#	Put a nickname (check that nickname isn't duplicate of another one)
#	Change a nickname (check that the new nickname isn't in the nicknames and original exists)
#	Delete entire nickname - delete_nickname(nickname)
# Change min_time (check that 0 <= value <= 30) - set_time(time)
class Item(object):
	# Table used by all Item objects
	__table = resource("dynamodb", region_name="us-east-1").Table("UserPreferences")

	def __init__(self, ID, write=True):
		try:
			# Cast min_time and all numbers in nicknames to 
			# ints since they are returned as decimals
			item = Item.__table.get_item(Key={"ID": ID})["Item"]
			for key in item:
				if key == "min_time":
					item[key] = int(item[key])
				elif key == "nicknames":
					for nickname in item[key]:
						for i in xrange(len(item[key][nickname])):
							item[key][nickname][i] = int(item[key][nickname][i])

			self.ID = ID
			self.home = item.get("home")
			self.destination = item.get("destination")
			self.nicknames = item.get("nicknames", {})
			self.order = item.get("order", [])
			self.min_time = item.get("min_time", 0)
			self.__write = write
		except Exception as e:
			raise DatabaseFailure("__init__")

	def __del__(self):
		if self.__write:
			try:
				item = {
					"ID": self.ID, 
					"nicknames": self.nicknames, 
					"order": self.order, 
					"min_time":self.min_time
				}
				if self.home:
					item["home"] = self.home
				if self.destination:
					item["destination"] = self.destination
				Item.__table.put_item(Item=item)
			except Exception as e:
				raise DatabaseFailure("__del__")
