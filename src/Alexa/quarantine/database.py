import boto3
import json
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

class DatabaseFailure(Exception):
    def __init__(self):
        super(DatabaseFailure, self).__init__("Database Failure")

class Database(object):

	def __init__(self):
		self.__table = boto3.resource('dynamodb', region_name='us-east-1').Table('UserFavorites')

	def get_item(self, alexaID):
		try:
		    response = self.__table.get_item(Key={ 'AlexaID': str(alexaID)})
		except:
		    raise DatabaseFailure()
		    return None
		else:
		    item = response['Item']
		    return item

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
			raise DatabaseFailure()

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
			raise DatabaseFailure()

	#if we only want to delete one part, for now we will have to delete the whole item and recreate it
	def delete_item(self, alexaID):
		try:
		    response = self.__table.delete_item(
		        Key={
		            'AlexaID': str(alexaID)
		        }
		    )
		except:
			raise DatabaseFailure()