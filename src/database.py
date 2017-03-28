from boto3 import resource
from hashlib import md5

#add more custom exceptions
#figure out why raising this exception doesn't work for the check in webapp/main.py
class DatabaseFailure(Exception):
	def __init__(self, function):
		super(Exception, self).__init__("Database Failure in function " + function)

class Database(object):
	def __init__(self):
		self.__table = resource("dynamodb", region_name="us-east-1").Table("UserPreferences")

	def __get_hash(self, alexaID):
		return md5(str(alexaID)).hexdigest()

	def get_item(self, alexaID):
		try:
			item = self.__table.get_item(Key={"ID": self.__get_hash(alexaID)})["Item"]

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
							item[key][stop_alias][i] = int(item[key][stop_alias][i])
			return item
		except:
			raise DatabaseFailure("get_item")

	#for updating one value of a key
	#key must be 'order', 'home', 'destination', 'nickanmes', or 'min_time'
	#value must be a list for order, strings for home/destination, a dictionary for nicknames, or an int for min_time 
	def update_item_field(self, alexaID, key, value):
		try:
			self.__table.update_item(Key={"ID": self.__get_hash(alexaID)},
				UpdateExpression="set " + str(key) + " = :r",
				ExpressionAttributeValues={":r": value}
			)
		except:
			raise DatabaseFailure("update_item_field")

	#order must be a list, home/destination must be strings, nicknames must be a dictionary, and min_time must be a number		
	def put_item(self, alexaID, order, home, destination, nicknames, min_time):
		try:
			self.__table.put_item(
				Item={"ID": self.__get_hash(alexaID),
					"order": order,
					"home": home,
					"destination": destination,
					"nicknames": nicknames,
					"min_time": min_time
				}
			)
		except:
			raise DatabaseFailure("put_item")

	#if we only want to delete one part, for now we will have to delete the whole item and recreate it
	def delete_item(self, alexaID):
		try:
			self.__table.delete_item(Key={"ID": self.__get_hash(alexaID)})
		except:
			raise DatabaseFailure("delete_item")
