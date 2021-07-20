import json
import logging
import threading

import time

import requests

import SimpleLB
import configuration
from datetime import datetime
import pytz
import boto3

# from manager import healthy_count

# healthy_count = 0

logger = logging.getLogger(__name__)
logging.getLogger('boto3').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)

# debug
AutoScalingClient = boto3.client('autoscaling')
# AutoScalingGroup = "20200428_fix_num_VM_"

d = {}
# epoch_tz = datetime.utcfromtimestamp(0).astimezone(pytz.utc)
# epoch = datetime.utcfromtimestamp(0)

def unix_time_millis(tt, t):
    return (tt - t).total_seconds() * 1000.0

def setup_logging(config):
    logging.basicConfig(filename=config.log_file+"_VM_instances", level=config.logging_level,
                        format='%(name)s - %(levelname)s - %(message)s', filemode='w')
    console = logging.StreamHandler()
    formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)

def Spin_VMs(epoch, n):

    response = AutoScalingClient.update_auto_scaling_group(
        AutoScalingGroupName=config.auto_scaling_group_name,
        MinSize=n,
        MaxSize=n,
        DesiredCapacity=n
    )
    print("(provisioned): at epoch: {0}, {1}, vms provisioned".format(epoch, n))
    logger.info(
        "!!(provisioned): at epoch: {0}, {1}, vms provisioned".format(epoch, n))



def setup_auto_scaling():
    client = boto3.client('autoscaling')

    if(config.policy=="vm_cloud_hide" or config.policy=="vm_cloud" or config.policy=="hybrid" or config.policy=="vm_cloud_max"):

        response = client.create_auto_scaling_group(
            AutoScalingGroupName=config.auto_scaling_group_name,
            LaunchConfigurationName=config.launch_configuration_name,
            # LaunchTemplate={
            #     'LaunchTemplateId': 'string',
            #     'LaunchTemplateName': 'string',
            #     'Version': 'string'
            # },
            # MixedInstancesPolicy={
            #     'LaunchTemplate': {
            #         'LaunchTemplateSpecification': {
            #             'LaunchTemplateId': 'string',
            #             'LaunchTemplateName': 'string',
            #             'Version': 'string'
            #         },
            #         'Overrides': [
            #             {
            #                 'InstanceType': 'string',
            #                 'WeightedCapacity': 'string'
            #             },
            #         ]
            #     },
            #     'InstancesDistribution': {
            #         'OnDemandAllocationStrategy': 'string',
            #         'OnDemandBaseCapacity': 123,
            #         'OnDemandPercentageAboveBaseCapacity': 123,
            #         'SpotAllocationStrategy': 'string',
            #         'SpotInstancePools': 123,
            #         'SpotMaxPrice': 'string'
            #     }
            # },
            # InstanceId='string',
            MinSize=config.min_num_instance,
            MaxSize=config.max_num_instance,
            DesiredCapacity=config.des_num_instance,
            DefaultCooldown=config.DefaultCooldown,
            # AvailabilityZones=[
            #     'string',
            # ],
            # LoadBalancerNames=[
            #     'string',
            # ],
            TargetGroupARNs=config.target_group_ARNs,
            HealthCheckType='EC2',
            HealthCheckGracePeriod=123,
            # PlacementGroup='string',
            VPCZoneIdentifier=config.VPC_zone_identifier,
            # TerminationPolicies=[
            #     'string',
            # ],
            # NewInstancesProtectedFromScaleIn=True|False,
            # LifecycleHookSpecificationList=[
            #     {
            #         'LifecycleHookName': 'string',
            #         'LifecycleTransition': 'string',
            #         'NotificationMetadata': 'string',
            #         'HeartbeatTimeout': 123,
            #         'DefaultResult': 'string',
            #         'NotificationTargetARN': 'string',
            #         'RoleARN': 'string'
            #     },
            # ],
            # Tags=[
            #     {
            #         'ResourceId': 'string',
            #         'ResourceType': 'string',
            #         'Key': 'string',
            #         'Value': 'string',
            #         'PropagateAtLaunch': True|False
            #     },
            # ],
            ServiceLinkedRoleARN=config.service_linked_role_ARN
            # MaxInstanceLifetime=123
        )

    if (config.policy == "vm_cloud" or config.policy == "vm_cloud_hide"):
        if (config.scaling_policy_type=="target"):
            response = client.put_scaling_policy(
                AutoScalingGroupName=config.auto_scaling_group_name,
                PolicyName='TargetScaling',
                PolicyType='TargetTrackingScaling',
                # AdjustmentType='string',
                # MinAdjustmentStep=123,
                # MinAdjustmentMagnitude=123,
                # ScalingAdjustment=123,
                Cooldown=config.PolicyCooldown,
                # MetricAggregationType='string',
                # StepAdjustments=[
                #     {
                #         'MetricIntervalLowerBound': 123.0,
                #         'MetricIntervalUpperBound': 123.0,
                #         'ScalingAdjustment': 123
                #     },
                # ],
                EstimatedInstanceWarmup=10,
                TargetTrackingConfiguration=config.TargetTrackingConfiguration,
                Enabled=True
            )
        if (config.scaling_policy_type=="simple"):
            response1 = client.put_scaling_policy(
                AutoScalingGroupName=config.auto_scaling_group_name,
                PolicyName='SimpleScalingOut', #'StepScalingOut',
                PolicyType='SimpleScaling', # 'StepScaling',
                AdjustmentType='ChangeInCapacity',
                # MinAdjustmentStep=1,
                # MinAdjustmentMagnitude=2,
                ScalingAdjustment=2,
                Cooldown=300,
                # MetricAggregationType='string',
                # StepAdjustments=[
                #     {
                #         'MetricIntervalLowerBound': 0.0,
                #         # 'MetricIntervalUpperBound': 10.0,
                #         'ScalingAdjustment': 2
                #     },
                # ],
                # EstimatedInstanceWarmup=300,
                Enabled=True
            )
            response2 = client.put_scaling_policy(
                AutoScalingGroupName=config.auto_scaling_group_name,
                PolicyName='SimpleScalingIn', #'StepScalingIn',
                PolicyType='SimpleScaling', # 'StepScaling',
                AdjustmentType='ChangeInCapacity',
                # MinAdjustmentStep=1,
                # MinAdjustmentMagnitude=2,
                ScalingAdjustment=-2,
                Cooldown=300,
                # MetricAggregationType='string',
                # StepAdjustments=[
                #     {
                #         # 'MetricIntervalLowerBound': -10,
                #         'MetricIntervalUpperBound': 0,
                #         'ScalingAdjustment': -2
                #     },
                # ],
                # EstimatedInstanceWarmup=300,
                Enabled=True
            )
            client = boto3.client('cloudwatch')
            response3 = client.put_metric_alarm(
                AlarmName=config.UpperAlarmName,
                # AlarmDescription='string',
                # ActionsEnabled=True | False,
                # OKActions=[
                #     response1["PolicyARN"],
                # ],
                AlarmActions=[
                    response1["PolicyARN"],
                ],
                # InsufficientDataActions=[
                #     'string',
                # ],
                MetricName='RequestCountPerTarget',
                Namespace='AWS/ApplicationELB',
                Statistic='Sum',
                # ExtendedStatistic='string',
                Dimensions=config.AlarmDimensions,
                Period=60,
                #Unit='Seconds',
                EvaluationPeriods=1,
                DatapointsToAlarm=1,
                Threshold=config.UpperAlarmThreshold,
                ComparisonOperator='GreaterThanThreshold',
                TreatMissingData='notBreaching',
                # EvaluateLowSampleCountPercentile='ignore'
                # Metrics=[
                #     {
                #         'Id': 'string',
                #         'MetricStat': {
                #             'Metric': {
                #                 'Namespace': 'string',
                #                 'MetricName': 'string',
                #                 'Dimensions': [
                #                     {
                #                         'Name': 'string',
                #                         'Value': 'string'
                #                     },
                #                 ]
                #             },
                #             'Period': 123,
                #             'Stat': 'string',
                #             'Unit': 'Seconds' | 'Microseconds' | 'Milliseconds' | 'Bytes' | 'Kilobytes' | 'Megabytes' | 'Gigabytes' | 'Terabytes' | 'Bits' | 'Kilobits' | 'Megabits' | 'Gigabits' | 'Terabits' | 'Percent' | 'Count' | 'Bytes/Second' | 'Kilobytes/Second' | 'Megabytes/Second' | 'Gigabytes/Second' | 'Terabytes/Second' | 'Bits/Second' | 'Kilobits/Second' | 'Megabits/Second' | 'Gigabits/Second' | 'Terabits/Second' | 'Count/Second' | 'None'
                #         },
                #         'Expression': 'string',
                #         'Label': 'string',
                #         'ReturnData': True | False,
                #         'Period': 123
                #     },
                # ],
                # Tags=[
                #     {
                #         'Key': 'string',
                #         'Value': 'string'
                #     },
                # ],
                # ThresholdMetricId='string'
            )
            response4 = client.put_metric_alarm(
                AlarmName=config.LowerAlarmName,
                # AlarmDescription='string',
                # ActionsEnabled=True | False,
                # OKActions=[
                #     response1["PolicyARN"],
                # ],
                AlarmActions=[
                    response2["PolicyARN"],
                ],
                # InsufficientDataActions=[
                #     'string',
                # ],
                MetricName='RequestCountPerTarget',
                Namespace='AWS/ApplicationELB',
                Statistic='Sum',
                # ExtendedStatistic='string',
                Dimensions=config.AlarmDimensions,
                Period=60,
                # Unit='Seconds',
                EvaluationPeriods=1,
                DatapointsToAlarm=1,
                Threshold=config.LowerAlarmThreshold,
                ComparisonOperator='LessThanThreshold',
                TreatMissingData='notBreaching',
                # EvaluateLowSampleCountPercentile='ignore'
                # Metrics=[
                #     {
                #         'Id': 'string',
                #         'MetricStat': {
                #             'Metric': {
                #                 'Namespace': 'string',
                #                 'MetricName': 'string',
                #                 'Dimensions': [
                #                     {
                #                         'Name': 'string',
                #                         'Value': 'string'
                #                     },
                #                 ]
                #             },
                #             'Period': 123,
                #             'Stat': 'string',
                #             'Unit': 'Seconds' | 'Microseconds' | 'Milliseconds' | 'Bytes' | 'Kilobytes' | 'Megabytes' | 'Gigabytes' | 'Terabytes' | 'Bits' | 'Kilobits' | 'Megabits' | 'Gigabits' | 'Terabits' | 'Percent' | 'Count' | 'Bytes/Second' | 'Kilobytes/Second' | 'Megabytes/Second' | 'Gigabytes/Second' | 'Terabytes/Second' | 'Bits/Second' | 'Kilobits/Second' | 'Megabits/Second' | 'Gigabits/Second' | 'Terabits/Second' | 'Count/Second' | 'None'
                #         },
                #         'Expression': 'string',
                #         'Label': 'string',
                #         'ReturnData': True | False,
                #         'Period': 123
                #     },
                # ],
                # Tags=[
                #     {
                #         'Key': 'string',
                #         'Value': 'string'
                #     },
                # ],
                # ThresholdMetricId='string'
            )


def log_target_group(terminateEvent):
    elbList = boto3.client('elbv2')
    while True:
        t1 = time.time()
        count_d = { "initial":0, "healthy": 0, "unhealthy" : 0, "unused" : 0, "draining" : 0, "unavailable" : 0}
        total_count = 0
        for d in elbList.describe_target_health(TargetGroupArn=elbList.describe_target_groups()['TargetGroups'][0]['TargetGroupArn'])['TargetHealthDescriptions']:
            total_count = total_count + 1
            count_d[d['TargetHealth']['State']] = count_d[d['TargetHealth']['State']]+1
        # print("!!(target): timestamp, initial, healthy, unhealthy, unused, draining, unavailable, total: " + str(time.time()) + ", " + str(count_d["initial"]) + ", " + str(count_d["healthy"]) + ", " + str(count_d["unhealthy"]) + ", " + str(count_d["unused"]) + ", " + str(count_d["draining"]) + ", " + str(count_d["unavailable"]) + ", " + str(total_count))
        logger.info("!!(target): timestamp, initial, healthy, unhealthy, unused, draining, unavailable, total: " + str(time.time()) + ", " + str(count_d["initial"]) + ", " + str(count_d["healthy"]) + ", " + str(count_d["unhealthy"]) + ", " + str(count_d["unused"]) + ", " + str(count_d["draining"]) + ", " + str(count_d["unavailable"]) + ", " + str(total_count))
        print(time.time() - t1)
        time.sleep(config.vm_state_epoch - (time.time() - t1) % config.vm_state_epoch)
        if terminateEvent.is_set():
            break

def wait_target_group(des_num_instance, waitEvent):
    elbList = boto3.client('elbv2')
    while True:
        t1 = time.time()
        count_d = { "initial":0, "healthy": 0, "unhealthy" : 0, "unused" : 0, "draining" : 0, "unavailable" : 0}
        total_count = 0
        for d in elbList.describe_target_health(TargetGroupArn=elbList.describe_target_groups()['TargetGroups'][0]['TargetGroupArn'])['TargetHealthDescriptions']:
            total_count = total_count + 1
            count_d[d['TargetHealth']['State']] = count_d[d['TargetHealth']['State']]+1
        if not waitEvent.is_set() and count_d['healthy'] == des_num_instance:
            waitEvent.set()
            print("leave wait")
            break
        # print(time.time() - t1)
        time.sleep(config.vm_state_epoch - (time.time() - t1) % config.vm_state_epoch)


# def VM_Send_Request():
#    PublicDnsNameList = SimpleLB.getPublicDNSName()
#    if len(PublicDnsNameList) != config.des_num_instance:
#        return False
#    print(PublicDnsNameList)
#    count = 0
#    for i in range(0, len(PublicDnsNameList)):
#        url = "http://" + PublicDnsNameList[i] + ":8080"
#        try:
#            res = requests.get(url, data=config.payload, headers=config.headers)
#            print(res.status_code)
#            if res.status_code == 200:
#                print(PublicDnsNameList[i])
#                count = count + 1
#        except:
#            return False
#    if count == len(PublicDnsNameList) and len(PublicDnsNameList) != 0:
#        return True
#    return False

# def ALB_Send_Request():
#     for i in range(0):
#         # from time import sleep
#         # time.sleep(0.2)
#         threading.Thread(target=Send_Request, args=(i,)).start()

# def Send_Request(i):
#     start =  time.time()
#     res = requests.post(config.url, data=config.payload, headers=config.headers)
#     end = time.time()
#     if res.status_code == 200:
#         print(res.text)
#         response_dict = json.loads(res.text)
#         print(
#             "(VM): requestID(epoch, starttime, localID), predicttime, TurnAroundTime, statusCode, UploadTime, DownloadTime, instance_id: " + str(
#                 0) + ", " + str(start) + ", " + str(i) + ", " + str(response_dict["predicttime"]) + ", " + str(
#                 end - start) + ", " + str(res.status_code) + ", " + str(response_dict["receivedTime"] - start) + ", " + str(
#                 end - response_dict["sentTime"]))
#     else:
#         print("(VM): requestID(epoch, starttime, localID), statusCode: " + str(0) + ", " + str(
#             i) + ", " + str(res.status_code))

# def wait_for_server():
#     while True:
#         if VM_Send_Request():
#             break
#         print("waiting for server(s)")
#         time.sleep(0.01)
#     count = 0
#     t1 = time.time()
#     while time.time()-t1 < config.WaitingTimeForCloudWatch:
#         t2 = time.time()
#         ALB_Send_Request()
#         count = count + config.des_num_instance*config.NumOfReqPerVM
#         time.sleep(config.epoch_time - (time.time() -t2)%config.epoch_time)
#     print("extra waiting: " + str(time.time()-t1))
#     print("sent "+ str(count)+" req's")

config = configuration.configuration()
# setup_logging(config)

# debug
if __name__ == "__main__":
    setup_auto_scaling()    
    # wait_for_server()


