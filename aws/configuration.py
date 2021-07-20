import logging


class configuration:
    def __init__(self):
        # logging information
        self.logging_level = logging.INFO

        # manager
        self.alpha = 0.9
        self.mu = self.alpha
        self.wait_for_server = True
        

        # experiment parameters
        self.start_time = 1  # it should always start from greater than 0
        self.end_time = 1800  # 30 mins
        self.epoch_time = 1

        # ===================================================================
        # The corresponding cases in paper:     'vm_cloud_max'  = MAX
        #                                       'serverless'    = Faas
        #                                       'vm_cloud'      = AUTO
        #                                       'hybrid'        = LIBRA
        #                                       'vm_cloud_hide' = SPOCK
        # ===================================================================
        self.policy = 'vm_cloud'    # self.policy = 'vm_cloud_max'#'serverless' #'vm_cloud'#'hybrid' #'vm_cloud_hide'
        

        # load
        # self.total_requests = 10
        # self.load_type = 'poisson'
        self.load_type = 'logs'
        self.log_file_name = 'traces/wits_logs.txt'
        self.LoadFactor=16  # traffic scale, i.e., 234 requests per second / LoadFactor
        
        self.no_vm_update_freq = 300  # period in sec for scaling manager to scale
        self.vm_provison_prop = 0.80  # expected load percentage: 
        self.req_config = {'memory': 512,   
                           'cpu': 2.4}  # logging
        

        # vm cloud
        self.vm_state_epoch = 1
        self.NumOfReqPerVM = 4  # based on off-line profiling: how many requests can be handled within SLA per VM
        self.WaitingTimeForCloudWatch = 0   # 5 data points before alarm triggers.
        self.scaling_policy_type = "simple"   # self.scaling_policy_type = "target" | "simple"
        self.url = "http://testing-711529452.us-east-2.elb.amazonaws.com:8080"  # ALB url
        self.payload = ''
        self.headers = {'Content-Type': 'application/json'}
        self.min_num_instance = 1
        self.max_num_instance = 9
        self.des_num_instance = 3

        # VM_utils
        self.launch_configuration_name = 't3.medium'    # VM image
        self.auto_scaling_group_name = '53_20200519_VM_simple_2_240_-140_-180_req_per_vm_3_to_1_to_9_pos_std_wait_for_server_new_alarm_1_pts_in_1_1_min_pts_scaling_per_300_sec_1800_total'
        self.DefaultCooldown=300
        self.target_group_ARNs=[
                'arn:aws:elasticloadbalancing:us-east-2:123456789012:targetgroup/testing/5e87cffbc05e2dbb',
            ]
        self.VPC_zone_identifier='subnet-0a1f3a70, subnet-8b1b96c7, subnet-12da3579'
        self.service_linked_role_ARN='arn:aws:iam::123456789012:role/aws-service-role/autoscaling.amazonaws.com/AWSServiceRoleForAutoScaling'
        self.UpperAlarmName = '53_testingHigh'
        self.LowerAlarmName = '53_testingLow'
        self.PolicyCooldown=300
        self.TargetTrackingConfiguration={
                    'PredefinedMetricSpecification': {
                        'PredefinedMetricType': 'ALBRequestCountPerTarget',
                        'ResourceLabel': 'app/testing/38dcefbd67e07150/targetgroup/testing/5e87cffbc05e2dbb'
                    },
                    # 'CustomizedMetricSpecification': {
                    #     'MetricName': 'string',
                    #     'Namespace': 'string',
                    #     'Dimensions': [
                    #         {
                    #             'Name': 'string',
                    #             'Value': 'string'
                    #         },
                    #     ],
                    #     'Statistic': 'Average'|'Minimum'|'Maximum'|'SampleCount'|'Sum',
                    #     'Unit': 'string'
                    # },
                    'TargetValue': 240.0,
                    'DisableScaleIn': False
                }
        self.AlarmDimensions=[
                    {
                        'Name': 'TargetGroup',
                        'Value': 'targetgroup/testing/5e87cffbc05e2dbb'
                    },
                    {
                        'Name': 'LoadBalancer',
                        'Value': 'app/testing/38dcefbd67e07150'
                    },
                ]
        self.UpperAlarmThreshold=100.0
        self.LowerAlarmThreshold=60.0

        self.log_file = 'serverless_' + self.policy + '_update_' + str(self.no_vm_update_freq) + '_' + str(
            self.vm_provison_prop) + '.log'

        # req_utils
        self.FunctionName = "ImgLoad1Sec"   # Lambda function name


