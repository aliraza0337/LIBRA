from __future__ import division
import logging 
import math
from vm_cloud import vm_cloud 
from serverless_cloud import serverless_cloud
from random import gauss

logger = logging.getLogger(__name__)

class manager:
	def __init__(self, config):
		self.config = config
		self.vm_cloud = vm_cloud(config)
		self.ser_cloud = serverless_cloud(config)
		self.alpha = self.config.alpha 
		self.mu = self.config.mu 	
		self.mean = None 
		self.std = None 
		self.vms = 0 
		self.prev_n_vms = 0 
		self.provision_for = 0
		self.vm_share = 0 
		self.vm_share_provisioned = 0
		self.wait_for_cold_start = False
		self.cold_start_counter = 0 
		self.next_update_epoch = -1
	def handle_requests(self, requests, epoch):

		if requests is not None:
			if self.config.policy == 'hybrid':

				total_requests = len(requests)
				logger.info("manager received |requests,epoch|{0},{1}".format(total_requests, epoch))
				
				if self.mean is None and self.std is None:
					self.mean = total_requests
					self.std = 0 
				else:
					self.std = (1-self.mu)*self.std + self.mu*(abs(self.mean-total_requests))
					self.mean = (1-self.alpha)*self.mean + self.alpha*total_requests 
				
				if epoch ==  self.config.auto_scale_start_point or epoch == self.next_update_epoch:
					logger.info("manager making scaling decion at epoch = {0}".format(epoch))
					self.next_update_epoch = epoch+self.config.no_vm_update_freq
					self.vm_share = int(abs(self.mean+1*self.std)) 
					self.vms = self.calculate_vms(self.vm_share)
					self.vm_cloud.provision_vms(self.vms, epoch)
					if self.vms > self.prev_n_vms:
						self.wait_for_cold_start = True 
					else:
						self.prev_n_vms = self.vms 
						self.provision_for = int(self.vm_share*self.config.vm_provison_prop)
						logger.info("manager provision_for {0}".format(self.provision_for))
				
				if self.wait_for_cold_start:
					if self.cold_start_counter == self.config.vm_cold_start:
						self.prev_n_vms = self.vms 
						self.provision_for = int(self.vm_share*self.config.vm_provison_prop)
						logger.info("manager provision_for {0}".format(self.provision_for))
						self.wait_for_cold_start = False
						self.cold_start_counter = 0 
					else:	
						self.cold_start_counter +=1
				
				res = self.vm_cloud.handle_requests(requests[:self.provision_for], epoch)
				res = self.ser_cloud.handle_requests(requests[self.provision_for:], epoch)
				
			elif self.config.policy == 'serverless':
				res = self.ser_cloud.handle_requests(requests, epoch)
			
			elif self.config.policy == 'vm_cloud' or self.config.policy == 'vm_cloud_max':
				cold_s, req_count = self.vm_cloud.get_active_vms(epoch)
				res = self.vm_cloud.handle_requests(requests, epoch)

		else: 
			logger.info("manager completing simulation |epoch|{0}".format(epoch))	
			res = self.vm_cloud.handle_requests(requests, epoch)
		return res
	
	def calculate_vms(self, mean):
		instance_memory = float(self.config.ec2_prices[self.config.vm_instance_name]['memory'])
		max_instance_handle = int(instance_memory/(self.config.req_config['memory']/1024)*(1/self.config.req_duration))
		return int(math.ceil((mean/max_instance_handle)))

	def finish_sim(self, epoch):
		if not (self.config.policy == 'serverless'):
			self.vm_cloud.calculate_cost(epoch)


	def configure_resources(self):
		pass