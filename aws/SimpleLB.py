import boto3




# client = boto3.client('autoscaling')
# response = client.describe_auto_scaling_groups(
#     AutoScalingGroupNames=[
#         'fixed number of running VMs',
#     ],
# )
#
# print(response['AutoScalingGroups'][0])
import configuration


def getPublicDNSName():
    config = configuration.configuration()
    ec2_client = boto3.client('ec2')
    # instance = ec2.Instance('id')

    # asg_client = boto3.client('autoscaling', aws_access_key_id=acc_key, aws_secret_access_key=sec_key,
    #                           region_name='us-west-2')
    asg_client = boto3.client('autoscaling')

    # asg = "fixed number of running VMs"
    # print
    # asg
    asg_response = asg_client.describe_auto_scaling_groups(AutoScalingGroupNames=[config.auto_scaling_group_name])

    instance_ids = []  # List to hold the instance-ids

    for i in asg_response['AutoScalingGroups']:
        for k in i['Instances']:
            instance_ids.append(k['InstanceId'])

    # print(instance_ids)
    if(instance_ids==[]):
        return []
    ec2_response = ec2_client.describe_instances(
        InstanceIds=instance_ids
    )
    # print
    # instance_ids  # This line will print the instance_ids

    PublicDnsNameList = []  # List to hold the Private IP Address

    # print(ec2_response)

    for instances in ec2_response['Reservations']:
        for ip in instances['Instances']:
            # print(ip)
            PublicDnsNameList.append(ip['PublicDnsName'])

    return PublicDnsNameList
    # print("\n".join(PublicDnsNameList))