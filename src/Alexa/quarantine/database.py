import boto3
import json
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

#add more custom exceptions
#figure out why raising this exception doesn't work for the check in webapp/main.py
class DatabaseFailure(Exception):
    def __init__(self, message):
        super(DatabaseFailure, self).__init__("Database Failure in function " + message)

class Database(object):

	def __init__(self):
		self.__table = boto3.resource('dynamodb', region_name='us-east-1').Table('UserFavorites')

	def get_item(self, alexaID):
		try:
		    response = self.__table.get_item(Key={ 'AlexaID': str(alexaID)})
		except:
		    raise DatabaseFailure("get_item")
		    return None
		else:
		    item = response['Item']
		    self.__castDecimalToInt(item)
		    return item

	def __castDecimalToInt(self, item):
		for key in item:
			if key == 'default_destination':
				item[key] = int(item[key])
			if key == 'destinations' or key == 'origins':
				for stop_alias in item[key]:
					item[key][stop_alias] = int(item[key][stop_alias])

	#for updating one field of an item
	#field must be 'origins', 'destinations', or 'default_destination'
	#item must be the entire new JSON object for origins/destinations, or a new stopID for default_destination 
	def update_item_field(self, alexaID, field, item):
		try:
			response = self.__table.update_item(
			    Key={
			        'AlexaID': str(alexaID)
			    },
			    UpdateExpression="set " + str(field) + " = :r",
			    ExpressionAttributeValues={
			        ':r': item
			    }
			)
		except:
			raise DatabaseFailure("update_item_field")

	#origins, destinations must be JSON onject, and default_destination should be a number	    
	def put_item(self, alexaID, origins, destinations, default):
		try:
			response = self.__table.put_item(
			   Item={
			        'AlexaID': str(alexaID),
			        'origins': origins,
			        'destinations': destinations,
			        'default_destination': default
			    }
			)
		except:
			raise DatabaseFailure("put_item")

	#if we only want to delete one part, for now we will have to delete the whole item and recreate it
	def delete_item(self, alexaID):
		try:
		    response = self.__table.delete_item(
		        Key={
		            'AlexaID': str(alexaID)
		        }
		    )
		except:
			raise DatabaseFailure("delete_item")