from __future__ import print_function # Python 2/3 compatibility
import boto3
import json

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

table = dynamodb.Table('UserFavorites')

response = table.put_item(
   Item={
        'AlexaID': 'amzn1.ask.account.AGU7XV2XHFF2AZGA4SG4FAWDBQWK7JOTSW5GP3SCUCXDAIOZHUALSGKVSEZMGP4KULYBXRR3S4FEYEUP4NVXI73YGJGAIIXPE6IBSLUCNPRKECOKQ773ZI2WFVZLY5AMB6257MIQTMPNJIBJGFWSU34YUCJVD7ZHGWOVLBQ2AJ44WPU4ILGGL4DPSB6IMZHWOYZ65FH36WAJBBA',
        'origins': {},
        'destinations': {},
        'default_destination':-1
    }
)
