from __future__ import print_function
import boto3
import json
from flask_ask import session
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

table = dynamodb.Table('UserFavorites')

try:
    response = table.get_item(
        Key={
            'AlexaID': 'amzn1.ask.account.AGU7XV2XHFF2AZGA4SG4FAWDBQWK7JOTSW5GP3SCUCXDAIOZHUALSGKVSEZMGP4KULYBXRR3S4FEYEUP4NVXI73YGJGAIIXPE6IBSLUCNPRKECOKQ773ZI2WFVZLY5AMB6257MIQTMPNJIBJGFWSU34YUCJVD7ZHGWOVLBQ2AJ44WPU4ILGGL4DPSB6IMZHWOYZ65FH36WAJBBA'
            }
    )
except ClientError as e:
    print(e.response['Error']['Message'])
else:
    item = response['Item']
    print("GetItem succeeded:")
    print (item)