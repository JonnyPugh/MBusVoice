from boto3 import resource

table = resource("dynamodb", region_name="us-east-1").create_table(
    TableName="UserPreferences",
    KeySchema=[
        {
            'AttributeName': "ID",
            'KeyType': 'HASH'  #Partition key
        }
    ],
    AttributeDefinitions=[
        {
            "AttributeName": "ID",
            "AttributeType": "S"
        }
    ],
    ProvisionedThroughput={
        "ReadCapacityUnits": 10,
        "WriteCapacityUnits": 10
    }
)
print("Table status:", table.table_status)
