'''
/*
 * Copyright 2010-2016 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License").
 * You may not use this file except in compliance with the License.
 * A copy of the License is located at
 *
 *  http://aws.amazon.com/apache2.0
 *
 * or in the "license" file accompanying this file. This file is distributed
 * on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
 * express or implied. See the License for the specific language governing
 * permissions and limitations under the License.
 */
 '''

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import sys
import logging
import time
import argparse
import json
import boto3
import uuid
import os
import threading




# Custom MQTT message callback
def ping_callback(client, userdata, message):

	logger.debug("Received a new message: ")
	logger.debug(message.payload)
	logger.debug("Hellloooo")


def download_dir(client, resource, dist, local, bucket):
    paginator = client.get_paginator('list_objects')
    for result in paginator.paginate(Bucket=bucket, Delimiter='/', Prefix=dist):
        if result.get('CommonPrefixes') is not None:
            for subdir in result.get('CommonPrefixes'):
                download_dir(client, resource, subdir.get('Prefix'), local, bucket)
        if result.get('Contents') is not None:
            for file in result.get('Contents'):
                if not os.path.exists(os.path.dirname(local + os.sep + file.get('Key'))):
                     os.makedirs(os.path.dirname(local + os.sep + file.get('Key')))
                resource.meta.client.download_file(bucket, file.get('Key'), local + os.sep + file.get('Key'))
                print(file.get('Key')," downloaded")


# Custom MQTT message callback
def download_callback(client, userdata, message):

	logger.debug("Received a new message: for download %s ",message.payload)
	
	msg = json.loads(message.payload.decode())

	logger.debug("Token %s ", json.dumps(msg['params']['token']))

	s3_bucket = msg['params']['token']['bucket']
	space_id = msg['params']['token']['key']
	try:
		session = boto3.session.Session(aws_access_key_id=msg['params']['token']['accessKey'], aws_secret_access_key=msg['params']['token']['secretKey'], aws_session_token=msg['params']['token']['sessionToken'], region_name=msg['params']['token']['region'])
		s3_client = session.client('s3')
		s3_resource = session.resource('s3')

		download_dir(s3_client, s3_resource, space_id,output_directory,s3_bucket)

	except Exception as e:
		logger.error( str(e))
	print("Files downloaded to ", output_directory)
	terminate_agent17()

def terminate_agent17():
	global terminate_flag
	logger.debug("Shutting down agent17 after downloading the files.")
	terminate_flag = True


# Configure logging

logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.ERROR)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)


# Read in command-line parameters
parser = argparse.ArgumentParser()

parser.add_argument("-c", "--config", action="store", required=True, dest="config", help="Device Config file")
parser.add_argument("-p", "--prefix", action="store", required=True, dest="prefix", help="S3 Prefix/Key for download")
parser.add_argument("-o", "--output", action="store", required=True, dest="output_directory", help="Output directory for downloading files from healthcloud")

args,unknown = parser.parse_known_args()


config_file = args.config

output_directory = args.output_directory

prefix = args.prefix

global terminate_flag

terminate_flag = False

device_config = {}

with open(config_file, 'r') as f:
	device_config = json.load(f)

logger.debug("device config is %s ", json.dumps(device_config))

host = device_config['endpoint']
rootCAPath = device_config['rootCertificate']
certificatePath = device_config['deviceCertificate']
privateKeyPath = device_config['devicePrivateKey']
device_id = device_config['id']
thing_name =  device_config['thingName']
metadata = device_config['metadata']




# Init AWSIoTMQTTClient
myAWSIoTMQTTClient = None

myAWSIoTMQTTClient = AWSIoTMQTTClient(device_id)
myAWSIoTMQTTClient.configureEndpoint(host, 8883)
myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

# Connect and subscribe to AWS IoT
myAWSIoTMQTTClient.connect()


request_topic = 'gehc/request/'

request_body = {}

request_id = str(uuid.uuid4())

request_body['requestId'] = request_id
request_body['action'] = 'DOWNLOAD_TOKEN_REQUEST_V2'
request_body['params'] = {'prefix':prefix}

logger.debug("download request is %s ",request_body)

response_topic = 'gehc/response/' + device_id + '/' + request_id + '/'

logger.debug("response topic is %s", response_topic)

ping_request_topic = 'gehc/ping/'
ping_response_topic = 'gehc/pong/' + device_id + '/'


myAWSIoTMQTTClient.subscribe(str(ping_response_topic), 1, ping_callback)

myAWSIoTMQTTClient.subscribe(str(response_topic), 0, download_callback)

time.sleep(2)

myAWSIoTMQTTClient.publish(ping_request_topic, json.dumps({"message":"hello"}), 1)

elapsed_time = 0
myAWSIoTMQTTClient.publish(request_topic, json.dumps(request_body), 1)
while not terminate_flag:
	time.sleep(5)
	elapsed_time += 5
	logger.debug( "elapsed %s secs", elapsed_time )
	#break
sys.exit(0)
