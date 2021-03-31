from __future__ import division
import logging
from collections import Counter
import math 

logger = logging.getLogger(__name__)


class vm_instance:
	
	def __init__(self, start_time, config = None):
		self.config = config
		self.instance_memory = float(self.config.ec2_prices[self.config.vm_instance_name]['memory'])
		self.instance_hourly_price = float(self.config.ec2_prices[self.config.vm_instance_name]['hourly_price'])
		self.start_time = start_time
		self.last_used = start_time
		self.max_instance_handle = int(self.instance_memory/(self.config.req_config['memory']/1024))
		self.handling_requests = Counter()
	

	def can_handle_request(self, epoch):
		if self.start_time <= epoch:
			return max(0, self.max_instance_handle - self.handling_requests[epoch])
		return -1

	def place_requests(self, requests, epoch):

			for req in requests:
				req_start_time = epoch
				req_end_time = epoch + self.config.req_duration
				req_queued_delay = epoch - req.arrival_time
				logger.info('request served at |id,time,duration,queue_delay|{0},{1},{2},{3}'.format(req.id,
																							     epoch, 
																							     self.config.req_duration,
																							     req_queued_delay))
			for i in range(req_start_time, req_end_time):
				self.handling_requests[i] += len(requests)
			self.last_used = req_end_time
	
	def calculate_cost(self, epoch):
		while self.handling_requests[epoch] > 0:
			epoch+=1
		uptime_sec = max(0, epoch - self.start_time)+self.config.vm_cold_start
		logger.info('vm cost |duration(s), cost|{0}, {1}'.format(uptime_sec, uptime_sec*(self.instance_hourly_price/3600)))
		


class vm_cloud:
	
	def __init__(self, config=None):
		
		self.config = config

		self.active_vms = []
		self.vms_to_kill = []
		
		
		self.min_num_instance = self.config.min_num_instance
		self.max_num_instance = self.config.max_num_instance
		self.scale_in_counter = 0 
		self.scale_out_counter = 0 
		self.utilization_hist = []

		if self.config.policy == 'vm_cloud_max':
			self.init_vms(1, self.max_num_instance)
		else:	
			self.init_vms(1, self.min_num_instance)

		self.queue = []
		self.cost = 0

	def init_vms(self, start_time, count):
		for i in range(count):
			self.active_vms.append(vm_instance(start_time+self.config.vm_cold_start, self.config))
			#self.active_vms.append(vm_instance(start_time, self.config))

	def provision_vms(self, count, epoch):
		curr_active_vms = len(self.active_vms)
		if count  < curr_active_vms:
			self.vms_to_kill = self.active_vms[count:]
			self.active_vms = self.active_vms[:count]
		else:
			more_vms = count - curr_active_vms
			self.init_vms(epoch, more_vms)
	
	def kill_vms(self, epoch):
		can_not_kill = []
		for vm in self.vms_to_kill:
			if epoch > vm.last_used:
				vm.calculate_cost(epoch)
			else:
				can_not_kill.append(vm)
		self.vms_to_kill = can_not_kill

	def calculate_cost(self, epoch):
		for vm in self.active_vms:
			vm.calculate_cost(epoch)

	def queue_requests(self, request):
		self.queue.extend(request)

	def dequeue_request(self, num):
		reqs = self.queue[:num]
		del self.queue[:num]
		return reqs

	def get_queue_len(self):
		return len(self.queue)

	def calculate_utilization(self, epoch):
		total_load = 0 
		total_capacity = 0 
		for vm in self.active_vms:
			total_load += vm.handling_requests[epoch]
			total_capacity += vm.max_instance_handle
		return total_load / total_capacity

	def get_active_vms(self, epoch):
		count = 0
		cold_start = False 
		for v in self.active_vms:
			if v.start_time < epoch:
				count += v.can_handle_request(epoch)
			else:
				cold_start = True 
		return cold_start, count


	def auto_scale(self, epoch):
		u = self.calculate_utilization(epoch)
		logger.info("current utilization at epoch: {0}, {1}".format(epoch, u))
		
		self.utilization_hist.append(u)
		
		if len(self.utilization_hist) > self.config.auto_scale_grace_period:
			ave_util = sum(self.utilization_hist[-300:])/self.config.auto_scale_grace_period 
			logger.info("ave utilization at epoch: {0}, {1}".format(epoch, ave_util))

			if ave_util > self.config.auto_scale_out_thresh:
				print epoch, 'scalling out', ave_util
				if len(self.active_vms) < self.config.max_num_instance:
					self.init_vms(epoch, self.config.auto_scale_group)
				self.utilization_hist = []

			if ave_util < self.config.auto_scale_in_thresh:
				print epoch, 'scalling in', ave_util
				if len(self.active_vms) > self.config.auto_scale_group:
					self.vms_to_kill = self.active_vms[-self.config.auto_scale_group:]
					self.active_vms = self.active_vms[:-self.config.auto_scale_group]
				self.utilization_hist = []

	def handle_requests(self, request, epoch):
		
		self.kill_vms(epoch)
		
		logger.info("active vms in vm_cloud at epoch, # of vms: {0}, {1}".format(epoch, len(self.active_vms)))
		# put requests in the queue and later just take care of the queue

		if request is not None:
			logger.info("requests served by vm_cloud at epoch: {0}, {1}".format(epoch, len(request)))
			self.queue_requests(request)

		for vm in self.active_vms:
			if self.get_queue_len() > 0:
				vm_capacity = vm.can_handle_request(epoch)
				if vm_capacity > 0:
					request_to_handle = self.dequeue_request(vm_capacity)
					vm.place_requests(request_to_handle, epoch)
		
		if self.config.vm_auto_scaling:
			self.auto_scale(epoch)

		return self.get_queue_len()


	

	

	



