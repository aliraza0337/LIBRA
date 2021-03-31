import logging 

class configuration:
	def __init__(self):
		# logging information 
		self.logging_level = logging.INFO
		
		# manager EWMA weights.
		self.alpha = 0.2
		self.mu = self.alpha

		# simulation parameter
		self.start_time = 1 # it should always start from greater than 0 
		self.end_time = 45000
		self.factor_to_hours = 60
		
		# traffic 
		self.load_type = 'logs'
		self.log_file_name = './traces/wits_logs.txt'
		
		# if hybrid, make vm_auto_scaling, False.

		self.policy = 'hybrid' 
		self.vm_auto_scaling = False # LIBRA scales based on its on policies.
		self.no_vm_update_freq = 300 # sec
		self.auto_scale_start_point = 1
		self.vm_provison_prop = 0.80
		self.break_even_point = 4

		# request x 
		self.req_duration = 1
		self.req_config = {'memory': 512, 
							  'cpu': 2.4}
		
		# vm cloud 
		self.min_num_instance = 10
		self.max_num_instance = 292 # https://aws.amazon.com/ec2/pricing/on-demand/

		self.vm_instance_name = 'm4.large'
		self.auto_scale_out_thresh = 0.70 #percentage usage of current resources 
		self.auto_scale_in_thresh = 0.30  
		self.auto_scale_group = 10 # how many instance to add
		self.auto_scale_grace_period = 120 # 2 min 
		self.vm_cold_start = 100 # in seconds 

		
		self.log_file = 'serverless_'+self.policy+'_update_'+str(self.no_vm_update_freq)+'_'+str(self.vm_provison_prop)+'_'+str(self.alpha)+'.log'
		

		# lambda execution model 
		self.lambda_t_o = 40.0
		self.lambda_t_c = 2.0
		self.lambda_r = 0.01

		# lambda price for each per second execution for given memory
		self.lambda_prices = {
				 128:2.08000000000000e-06,
				 192:3.13000000000000e-06,
				 256:4.17000000000000e-06,
				 320:5.21000000000000e-06,
				 384:6.25000000000000e-06,
				 448:7.29000000000000e-06,
				 512:8.34000000000000e-06,
				 576:9.38000000000000e-06,
				 640:1.04200000000000e-05,
				 704:1.14600000000000e-05,
				 768:1.25000000000000e-05,
				 832:1.35400000000000e-05,
				 896:1.45900000000000e-05,
				 960:1.56300000000000e-05,
				1024:1.66700000000000e-05,
				1088:1.77100000000000e-05,
				1152:1.87500000000000e-05,
				1216:1.98000000000000e-05,
				1280:2.08400000000000e-05,
				1344:2.18800000000000e-05,
				1408:2.29200000000000e-05,
				1472:2.39600000000000e-05,
				1536:2.50100000000000e-05,
				1600:2.60500000000000e-05,
				1664:2.70900000000000e-05,
				1728:2.81300000000000e-05,
				1792:2.91700000000000e-05,
				1856:3.02100000000000e-05,
				1920:3.12600000000000e-05,
				1984:3.23000000000000e-05,
				2048:3.33400000000000e-05,
				2112:3.43800000000000e-05,
				2176:3.54200000000000e-05,
				2240:3.64700000000000e-05,
				2304:3.75100000000000e-05,
				2368:3.85500000000000e-05,
				2432:3.95900000000000e-05,
				2496:4.06300000000000e-05,
				2560:4.16800000000000e-05,
				2624:4.27200000000000e-05,
				2688:4.37600000000000e-05,
				2752:4.48000000000000e-05,
				2816:4.58400000000000e-05,
				2880:4.68800000000000e-05,
				2944:4.79300000000000e-05,
				3008:4.89700000000000e-05
				}

		self.ec2_prices = {
				  "t2.nano": {
				    "memory": "0.5",
				    "hourly_price": "0.0058"
				  },
				  "t2.micro": {
				    "memory": "1",
				    "hourly_price": "0.0116"
				  },
				  "t2.small": {
				    "memory": "2",
				    "hourly_price": "0.023"
				  },
				  "t2.medium": {
				    "memory": "4",
				    "hourly_price": "0.0464"
				  },
				  "t2.large": {
				    "memory": "8",
				    "hourly_price": "0.0928"
				  },
				  "t2.xlarge": {
				    "memory": "16",
				    "hourly_price": "0.1856"
				  },
				  "t2.2xlarge": {
				    "memory": "32",
				    "hourly_price": "0.3712"
				  },

				  "t3.medium": {
				    "memory": "4",
				    "hourly_price": "0.0416"
				  },

				  "m3.medium": {
				    "memory": "3.75",
				    "hourly_price": "0.067"
				  },
				  "m4.large": {
				    "memory": "8",
				    "hourly_price": "0.1"
				  },
				  "m4.xlarge": {
				    "memory": "16",
				    "hourly_price": "0.2"
				  },
				  "m4.2xlarge": {
				    "memory": "32",
				    "hourly_price": "0.4"
				  },
				  "m4.4xlarge": {
				    "memory": "64",
				    "hourly_price": "0.8"
				  },
				  "m4.10xlarge": {
				    "memory": "160",
				    "hourly_price": "2"
				  },
				  "m4.16xlarge": {
				    "memory": "256",
				    "hourly_price": "3.2"
				  }
				}