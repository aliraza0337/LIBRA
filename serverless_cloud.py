from __future__ import division
from collections import Counter
import math 
import logging
logger = logging.getLogger(__name__)

class serverless_cloud:
	
	def __init__(self, config=None):
		self.name = "--"
		self.config = config 
		self.handling_requests = Counter()

	def handle_requests(self, request, epoch):
		logger.info("requests served by ser_cloud at epoch: {0}, {1}".format(epoch, len(request)))
		total_req = len(request)
		if total_req > 0:
			c, r = self.exec_model(request[0])
			logger.info('requests served by serverless at |requests,time,duration,cost|{0},{1},{2},{3}'.format(total_req,
																							        epoch, 
																							        r,
																							        c*total_req))
		return 0

	def exec_model(self, request):
		m = request.resources['memory']
		#t = self.config.lambda_t_c + self.config.lambda_t_o * (1 - self.config.lambda_r) ** (m - 128) # returns runtime in secs		
		t = self.config.req_duration
		c = 0.0000002+(m/1024.0)*t*0.00001667
		return c, t