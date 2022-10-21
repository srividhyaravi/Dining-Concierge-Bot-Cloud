import imp
import math
from unittest import result
from wsgiref import validate
from datetime import datetime, timedelta
import time
import os
import logging
import json
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
SQS_QUEUE = 'https://sqs.us-east-1.amazonaws.com/006253412285/diningbotQueue'

def get_slots(intent_request):
    return intent_request['currentIntent']['slots']
    
def publishToSQS(slots):
    logger.debug("Intent is DiningIntent, entered publishToSQS")
    sqs = boto3.client('sqs')

    try:
        response = sqs.send_message(
            QueueUrl=SQS_QUEUE,
            DelaySeconds=0,
            MessageAttributes={
                'cuisine': {
                    'DataType': 'String',
                    'StringValue': slots['cuisine']
                },
                'location': {
                    'DataType': 'String',
                    'StringValue': slots['location']
                },
                'email': {
                    'DataType': 'String',
                    'StringValue': slots['email']
                },
                'time': {
                    'DataType': 'String',
                    'StringValue': slots['time']
                },
                'date': {
                    'DataType': 'String',
                    'StringValue': slots['date']
                },
                'number': {
                    'DataType': 'Number',
                    'StringValue': slots['number']
                }
            },
            MessageBody=(
                'Details for Dining'
            )
        )
        logger.info(response)
    except ClientError as e:
        logging.error(e)
        return None
    return response    


def buildmsg(msg):
    return {'contentType': 'PlainText', 'content': msg}

def dispatchelicitSlot(event, slotToElicit, message):
    logger.info(f"Entered Invalid Slot value for {slotToElicit}")
    return {
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': event['currentIntent']['name'],
            'slots': event['currentIntent']['slots'],
            'slotToElicit': slotToElicit,
            'message': message
        }
    }

def handleDiningSuggestionsIntent(event):
    logger.info("handing DiningIntent")

    slots = event['currentIntent']['slots']

    logger.debug(slots)

    # first validate all parameters

    if not slots['location']:
        return dispatchelicitSlot(event, 'location', buildmsg("Awesome! I can help you with that. Where would you like to eat?"))

    if slots['location'].lower() not in ['manhattan', 'newyork', 'ny', 'nyc', 'brooklyn', 'bronx', 'queens', 'staten island']:
        return dispatchelicitSlot(event, 'location', buildmsg("Unfortunately we could not find anything there. Could you please enter a different location?"))

    if not slots['cuisine']:
        return dispatchelicitSlot(event, 'cuisine', buildmsg("That works! What cuisine would you like to eat?"))

    if slots['cuisine'].lower() not in ['italian', 'chinese', 'mexican', 'greek', 'french', 'korean', 'jewish', 'japanese', 'malaysian','mediterranean', 'persian']:
        return dispatchelicitSlot(event, 'cuisine', buildmsg("Hmmm.. Unfortunately, we couldn't find any results for that cuisine. Could you please enter a different cuisine?"))

    if not slots['number']:
        return dispatchelicitSlot(event, 'number', buildmsg("Good choice! Could you please tell me how many people will be dining?"))

    if int(slots['number']) < 0:
        return dispatchelicitSlot(event, 'number', buildmsg("Oi. Please enter positive numbers only!"))

    if int(slots['number']) > 100:
        return dispatchelicitSlot(event, 'number', buildmsg("Wow, you sure have a lot of friends. Unfortunately the maximum capacity is 100. Could you please enter a number less than 100?"))

    if not slots['date']:
        return dispatchelicitSlot(event, 'date', buildmsg("Nice! Could you please enter the dining date?"))

    if slots['date']:
        logger.debug("entered date validation")
        current_time = datetime.now()
        entered = datetime.strptime(
            slots['date']+" "+datetime.now().strftime("%H:%M:%S"), '%Y-%m-%d %H:%M:%S') + timedelta(seconds=5)
        logger.debug(f"Entered Date: {entered}")
        logger.debug(f"Entered Date: {current_time}")
        if(entered < current_time):
            return dispatchelicitSlot(event, 'date', buildmsg("Oi. We can't make a reservation in the past, man. Could you please enter a valid date?"))

    if not slots['time']:
        return dispatchelicitSlot(event, 'time', buildmsg("That sounds good. Could you please enter the dining time?"))

    if slots['time']:
        logger.debug("entered time validation")
        entered = datetime.strptime(
            slots['date']+" "+slots['time'], '%Y-%m-%d %H:%M')
        logger.debug("Entered Time: {entered}")
        if(datetime.now() > entered):
            return dispatchelicitSlot(event, 'date', buildmsg("Oi. We can't make a reservation in the past, man. Could you please enter a valid time?"))

    if not slots['email']:
        return dispatchelicitSlot(event, 'email', buildmsg("Perfect! I need one last piece of information. Could you please enter your email address?"))
        
    if slots['email']:
        email_address = slots['email']
        if slots['email'].split("@")[1] not in ["gmail.com", "nyu.edu", "outlook.com", "hotmail.com", "yahoo.com"]:
            return dispatchelicitSlot(event, 'email', buildmsg("Hmmm.. looks like the email address provided is invalid. Could you please enter a valid email address?"))

    result = publishToSQS(slots)
    print(result)

    response = {
        "dialogAction":
        {
            "fulfillmentState": "Fulfilled" if result else "Failed",
            "type": "Close",  # Informs Amazon Lex not to expect a response from the user
            "message": {
                    "contentType": "PlainText",  # "PlainText or SSML or CustomPayload"
                    "content": 'Alright, we are all set. I have collected a set of exciting options for you. I will send detailed information regarding my picks to the email address provided by you: {}'.format(email_address) if result else "Try Again"
            }
        }
    }
    logger.info(response)
    return response


def handleGreetingIntent(event):
    logger.info("handing Greeting Intent")
    response = {
        "dialogAction":
            {
                "type": "ElicitIntent",  # Informs Amazon Lex not to expect a response from the user
                "message":
                {
                    "contentType": "PlainText",  # "PlainText or SSML or CustomPayload"
                    "content": "Hello! How can I help?",
                }
            }
    }
    logger.info(response)
    return response
    

def handleThankingIntent(event):
    logger.info("handing Greeting Intent")
    response = {
        "dialogAction":
            {
                "fulfillmentState": "Fulfilled",  # or Failed
                "type": "Close",  # Informs Amazon Lex not to expect a response from the user
                "message":
                {
                    "contentType": "PlainText",  # "PlainText or SSML or CustomPayload"
                    "content": "You're most welcome! Have a nice day!",
                }
            }
    }
    logger.info(response)
    return response


def lambda_handler(event, context):
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    
    if event['currentIntent']['name'] == "DiningIntent":
        return handleDiningSuggestionsIntent(event)
    if event['currentIntent']['name'] == "GreetingIntent":
        return handleGreetingIntent(event)
    if event['currentIntent']['name'] == "Thanking":
        return handleThankingIntent(event)

