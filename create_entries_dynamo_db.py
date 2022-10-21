from collections import defaultdict
import requests
import time
from datetime import datetime
from decimal import *
import simplejson as json
import json
import boto3
from requests_aws4auth import AWS4Auth
from elasticsearch import Elasticsearch, RequestsHttpConnection

def check_empty(input):
	if len(str(input)) == 0:
		return 'N/A'
	else:
		return input

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('yelp-restaurants-2')

session = boto3.session.Session()
credentials = session.get_credentials()

region = 'us-east-1'

awsauth = AWS4Auth(credentials.access_key,
                credentials.secret_key,
                session.region_name, 'es',
                session_token=credentials.token,
				region_name='us-east-1')

#define api key, define the endpoint, and define the header
API_KEY = '2oR7y3LFa9DZss9TCbgZifszuukhMW_P6Q-QzXGJCei53MF0tmp15TgThbweKZyOZxCHaOOHedd2vo0Qb_IoSnaBvRd9m06wEWAdES6M9AzjXg3XsuTh-gQH-PdNY3Yx' 
ENDPOINT = 'https://api.yelp.com/v3/businesses/search'
ENDPOINT_ID = 'https://api.yelp.com/v3/businesses/' # + {id}
HEADERS = {'Authorization': 'bearer %s' % API_KEY}

#define parameters
PARAMETERS = {'term': 'food', 
			  'limit': 50,
			  'radius': 15000,
			  'offset': 200,
			  'location': 'Manhattan'}

cuisines = ['italian', 'chinese', 'mexican', 'greek', 'french', 'korean', 'jewish', 'japanese', 'malaysian','mediterranean', 'persian']

manhattan_nbhds = 	['Lower East Side, Manhattan',
					'Upper East Side, Manhattan',
					'Upper West Side, Manhattan',
					'Washington Heights, Manhattan',
					'Central Harlem, Manhattan',
					'Chelsea, Manhattan',
					'Manhattan',
					'East Harlem, Manhattan',
					'Gramercy Park, Manhattan',
					'Greenwich, Manhattan',
					'Lower Manhattan, Manhattan',
					'Bay Ridge, Brooklyn',
					'Williamsburg, Brooklyn',
					'Sunset Park, Brooklyn',
					'Dyker Heights, Brooklyn',
					'Midwood, Brooklyn',
					'Flatbush, Brooklyn',
					'Bushwick, Brooklyn',
					'Martin Luther King Rd, Brooklyn',
					'Dumbo, Brooklyn',
					'Downtown Brooklyn',
					'Greenpoint, Brooklyn',
					'Park Slope, Brooklyn',
					'Bedford Park, Bronx',
					'Belmont, Bronx',
					'Fordham, Bronx',
					'Highbridge, Bronx',
					'Hunts Point, Bronx',
					'Jerome Park, Bronx',
					'Kingsbridge, Bronx',
					'Mott Haven, Bronx',
					'Parkchester, Bronx',
					'Riverdale, Bronx',
					'Woodlawn, Bronx',
					'Astoria, Queens',
					'Jackson Heights, Queens',
					'Long Island City, Queens',
					'Sunnyside, Queens',
					'Woodside, Queens',
					'Bayside, Queens',
					'Corona, Queens',
					'Flushing, Queens',
					'Glen Oaks, Queens',
					'Jamaica, Queens']

start = time.time()
for nbhd in manhattan_nbhds:
    PARAMETERS['location'] = nbhd
    for cuisine in cuisines:
        PARAMETERS['term'] = cuisine
        response = requests.get(url = ENDPOINT, params =  PARAMETERS, headers=HEADERS)
        business_data = response.json()['businesses']
        for business in business_data:
            now = datetime.now()
            restauraunt_data = {}
            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
            table.put_item(
			Item = {
				'Business_ID':check_empty(business['id']),
				'insertedAtTimestamp': check_empty(dt_string),
				'Name':  check_empty(business['name']),
				'Cuisine': check_empty(cuisine),
				'Rating': check_empty(Decimal(business['rating'])),
				'Number of Reviews' : check_empty(Decimal(business['review_count'])),
				'Address': check_empty(business['location']['address1']),
				'Zip Code': check_empty(business['location']['zip_code']),
				'Latitude': check_empty(str(business['coordinates']['latitude'])),
				'Longitude': check_empty(str(business['coordinates']['longitude'])),
				'Open': 'N/A'
			}
			)            
    print('Fin ',nbhd, time.time()- start)
