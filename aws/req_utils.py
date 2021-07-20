import logging

import json
import ast

import requests
import time
import threading

import boto3

import SimpleLB
import configuration

from botocore.config import Config


logger = logging.getLogger(__name__)
logging.getLogger('boto3').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)
logging.getLogger('urllib3').setLevel(logging.CRITICAL)

# debug
# AutoScalingClient = boto3.client('autoscaling')

LambdaClient = boto3.client('lambda',config=Config(read_timeout=120, retries={'max_attempts': 0}))
# AutoScalingClient = boto3.client('autoscaling')


def setup_logging(config):
    logging.basicConfig(filename=config.log_file+"_request", level=config.logging_level,
                        format='%(name)s - %(levelname)s - %(message)s', filemode='w')
    console = logging.StreamHandler()
    formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)

# using AWS ELB
def request_VM_AWS_LB(url, payload, headers, i, epoch):
    # retry = 0
    start   = time.time()
    try:
        res     = requests.post(url, data=payload, headers=headers)
    except:
        res= None
    end   = time.time()

    # print(res)
    if res is None:
        print("(VM): requestID(epoch, starttime, localID): " + str(epoch) + ", " + str(i))
        logger.info("!!(VM): requestID(epoch, starttime, localID): " + str(epoch) + ", " + str(i))
    elif res.status_code == 200:
        # t = res.text
        # t.replace("'", "")
        # # print(t)
        response_dict = json.loads(res.text)
        # print(response_dict["predicttime"])

        print("(VM): requestID(epoch, starttime, localID), ExecutionTime, TurnAroundTime, StatusCode, UploadTime, DownloadTime, instance_id: "+str(epoch)+", "+str(start)+", "+str(i)+", "+ str(response_dict["predicttime"]) + ", " + str(end - start) +", "+str(res.status_code)+", "+str(response_dict["receivedTime"]-start)+", "+str(end-response_dict["sentTime"]))
        logger.info("!!(VM): requestID(epoch, starttime, localID), ExecutionTime, TurnAroundTime, StatusCode, UploadTime, DownloadTime, instance_id: " +str(epoch)+", "+str(start)+", "+str(i)+", "+ str(response_dict["predicttime"]) + ", " + str(end - start) + ", "+str(res.status_code)+", "+str(response_dict["receivedTime"]-start)+", "+str(end-response_dict["sentTime"]))
    else:
        print("(VM): requestID(epoch, starttime, localID), statusCode: " + str(epoch) + ", " + str(
            i) + ", " + str(res.status_code))
        logger.info("!!(VM): requestID(epoch, starttime, localID), statusCode: " + str(epoch) + ", " + str(
            i) + ", " + str(res.status_code))


# using simple LB
def request_VM_simple_LB(target, payload, headers, i, epoch):
    url = "http://"+target+":80/cgi-bin/echo.py"
    start   = time.time()

    try:
        res = requests.post(url, data=payload, headers=headers)
    except:
        res = None
    end   = time.time()
    if res is None:
        print("(VM): requestID(epoch, starttime, localID): " + str(epoch) + ", " + str(i))
        logger.info("!!(VM): requestID(epoch, starttime, localID): " + str(epoch) + ", " + str(i))
    elif res.status_code == 200:
        # t = res.text
        # t.replace("'", "")
        # # print(t)
        response_dict = json.loads(res.text)
        # print(response_dict["predicttime"])
        print("(VM): requestID(epoch, starttime, localID), predicttime, TurnAroundTime, statusCode, UploadTime, DownloadTime, instance_id: "+str(epoch)+", "+str(start)+", "+str(i)+", "+ str(response_dict["predicttime"]) + ", " + str(end - start) +", "+str(res.status_code)+", "+str(response_dict["receivedTime"]-start)+", "+str(end-response_dict["sentTime"]))
        logger.info("!!(VM): requestID(epoch, starttime, localID), predicttime, TurnAroundTime, statusCode, UploadTime, DownloadTime, instance_id: " +str(epoch)+", "+str(start)+", "+str(i)+", "+ str(response_dict["predicttime"]) + ", " + str(end - start) + ", "+str(res.status_code)+", "+str(response_dict["receivedTime"]-start)+", "+str(end-response_dict["sentTime"]))
    else:
        print("(VM): requestID(epoch, starttime, localID), statusCode: " + str(epoch) + ", " + str(
            i) + ", " + str(res.status_code))
        logger.info("!!(VM): requestID(epoch, starttime, localID), statusCode: " + str(epoch) + ", " + str(
            i) + ", " + str(res.status_code))




# send request
def VM_Send_Request(n, epoch):
     print("requests served by vm_cloud at epoch ,{0}: {1}, at time {2}".format(epoch, n, time.time()))
     logger.info(
         "requests served by vm_cloud at epoch ,{0}: {1}, at time {2}".format(epoch, n, time.time()))
     for i in range(1, n+1):
         # from time import sleep
         # time.sleep(0.2)
         threading.Thread(target=request_VM_AWS_LB, args=(config.url, config.payload, config.headers, i, epoch)).start()

# using simple Round Robin LB
#def VM_Send_Request(n, epoch):
#    PublicDnsNameList = SimpleLB.getPublicDNSName()
#    if(PublicDnsNameList==[]):
#        return
#    print(PublicDnsNameList)
#    print(len(PublicDnsNameList))
#    print("requests served by vm_cloud at epoch ,{0}: {1}, at time {2}".format(epoch, n, time.time()))
#    logger.info(
#        "requests served by vm_cloud at epoch ,{0}: {1}, at time {2}".format(epoch, n, time.time()))
#    for i in range(0, n):
#        # from time import sleep
#        # time.sleep(0.2)
#        threading.Thread(target=request_VM_simple_LB, args=(PublicDnsNameList[i%len(PublicDnsNameList)], payload, headers, i, epoch)).start()


#target = "ec2-18-220-158-178.us-east-2.compute.amazonaws.com"

# using one VM
#def VM_Send_Request(n, epoch):
#    for i in range(0, n):
#        # from time import sleep
#        # time.sleep(0.2)
#        threading.Thread(target=request_VM, args=(target, payload, headers, i, epoch)).start()




s = {
  "key1": "value1",
  "key2": "value2",
  "key3": "value3"
}

def request_serverless(LambdaClient, i, epoch):
    start   = time.time()
    try:
        response = LambdaClient.invoke(
            # ClientContext='MyApp',
            FunctionName=config.FunctionName,
            # InvocationType='Event',
            LogType='Tail',
            Payload=json.dumps(s),
            # Qualifier='1',
        )
    except:
        response = None
    end   = time.time()

    if response is None:
        print("(Serverless): requestID(epoch, starttime, localID): " + str(epoch) + ", " + str(start) + ", " + str(i))
        logger.info(
            "!!(Serverless): requestID(epoch, starttime, localID): " + str(epoch) + ", " + str(start) + ", " + str(i))
    else:
        response_dict = json.loads((response["Payload"].read()).decode('utf-8'))

        print("(Serverless): requestID(epoch, starttime, localID), predicttime, TurnAroundTime, statusCode: "+str(epoch)+", "+str(start)+", "+str(i)+", "+ str(response_dict["predicttime"]) + ", " + str(end - start) +", "+str(response["ResponseMetadata"]["HTTPStatusCode"]))
        logger.info("!!(Serverless): requestID(epoch, starttime, localID), predicttime, TurnAroundTime, statusCode: " + str(epoch) + ", "+str(start)+", "+str(i) + ", " + str(response_dict["predicttime"]) + ", " + str(end - start) + ", " + str(response["ResponseMetadata"]["HTTPStatusCode"]))

def SER_Send_Request(n, epoch):
    print("!!!!!")
    if n < 0:
        return
    # logger.info(
    #     "requests served by Serverless at epoch: {0}, {1}".format(epoch, n))
    # LambdaClient = boto3.client('lambda')
    for i in range(1, n+1):
        threading.Thread(target=request_serverless, args=(LambdaClient, i, epoch)).start()


config = configuration.configuration()
setup_logging(config)



if __name__ == "__main__":
    config = configuration.configuration()
    setup_logging(config)
    # VM_Send_Request(3, 1)
    epoch_time = 1
    while True:
        t1 = time.time()
        VM_Send_Request(1, 1)
        time.sleep(epoch_time - (time.time() - t1) % epoch_time)

    # SER_Send_Request(1, 1)
    # Spin_VMs(1)
