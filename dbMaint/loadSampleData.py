from __future__ import print_function # Python 2/3 compatibility
import boto3
import json

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

table = dynamodb.Table('UserFavorites')

response = table.put_item(
   Item={
        'AlexaID': '1',
        'favorites': {
            'StartStops': 'pierpont', 
            'EndStops': 'rackham'
        }
    }
)

response = table.put_item(
   Item={
        'AlexaID': '2',
        'favorites': {
            'StartStops': 'cc little', 
            'EndStops': 'pierpont'
        }
    }
)

response = table.put_item(
   Item={
        'AlexaID': '3',
        'favorites': {
            'StartStops': 'baits 2', 
            'EndStops': 'pierpont'
        }
    }
)