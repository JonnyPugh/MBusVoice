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
