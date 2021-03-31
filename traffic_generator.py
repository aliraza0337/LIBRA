import random
from configuration import configuration
import numpy as np
import itertools


class request:
	
	def __init__(self, _id, arrival_time, resources = {}):
		self.id = _id
		self.resources = resources # will be configured by the manager
		self.arrival_time = arrival_time


class traffic_generator:

	def __init__(self, config = None):
		self.new_id = itertools.count().next
		self.requests = {}
		self.start_time = config.start_time
		self.end_time = config.end_time
		self.config = config
		if config.load_type == 'poisson':
			self.poisson_load_generate(config)
		
		if config.load_type == 'logs':
			self.load_logs(config.log_file_name)

	def load_logs(self, filename):
		f = open(filename, 'r')
		lines = f.readlines()
		counter = 0 
		for i in lines:
			counter+=1
			self.requests[counter] = int(i)

	def get_requests_at(self, epoch):
		reqs = []
		for i in range(self.requests[epoch]):
			reqs.append(request(self.new_id(), epoch, resources=self.config.req_config))
		return reqs

	
	def poisson_load_generate(self, config):
		t = config.start_time

		while  t < config.end_time:
			t += random.expovariate(config.total_requests/ (config.end_time -config.start_time))
			if int(t) in self.requests: 
				self.requests[int(t)] +=1
			else:
				self.requests[int(t)] = 1

		# if any time slot doesn't have requests, fill it with 0 request
		for i in range(config.start_time, config.end_time+1):
			if not (i in self.requests):
				self.requests[i] = 0 

