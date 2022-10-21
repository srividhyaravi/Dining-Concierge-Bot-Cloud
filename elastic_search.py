import json
import boto3
import requests
from requests_aws4auth import AWS4Auth
from boto3.dynamodb.conditions import Key
# from botocore.vendored import requests

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('yelp-restaurants-2')
fn = getattr(requests, 'post')


def send(url, body=None):
    fn(url, data=body,
       headers={"Content-Type": "application/json"})

def putRequests():
    resp = table.scan()
    i = 1
    url = 'https://search-restaurants-xjclhbfl7u32lyn2l6xs4qjt6a.us-east-1.es.amazonaws.com/restaurants/restaurant'
    headers = {"Content-Type": "application/json"}
    while True:
        #print(len(resp['Items']))
        for item in resp['Items']:
            #print(item)
            body = {"Business_ID": item['Business_ID'], "Cuisine": item['Cuisine']}
            r = requests.post(url,auth=("roshnisen", "#Cloudtest123"), data=json.dumps(body).encode("utf-8"), headers=headers)
            print(r.content.decode('utf-8'))
            i += 1
            #break;
        if 'LastEvaluatedKey' in resp:
            resp = table.scan(
                ExclusiveStartKey=resp['LastEvaluatedKey']
            )
            #break;
        else:
            break;
        print(i)

putRequests()