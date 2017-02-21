from __future__ import print_function # Python 2/3 compatibility
import boto3
import json
from configDB import *

dynamodb = boto3.resource('dynamodb', region_name=dbConfig['region_name'])

table = dynamodb.Table(dbConfig['table'])

response = table.put_item(
   Item={
        'AlexaID': 'amzn1.ask.account.AGU7XV2XHFF2AZGA4SG4FAWDBQWK7JOTSW5GP3SCUCXDAIOZHUALSGKVSEZMGP4KULYBXRR3S4FEYEUP4NVXI73YGJGAIIXPE6IBSLUCNPRKECOKQ773ZI2WFVZLY5AMB6257MIQTMPNJIBJGFWSU34YUCJVD7ZHGWOVLBQ2AJ44WPU4ILGGL4DPSB6IMZHWOYZ65FH36WAJBBA',
        'origins': {
            'pierpont': 101 
        },
        'destinations': {
            'dog': 44
        },
        'primary':44
    }
)
