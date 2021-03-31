import logging 
import sys
import configuration
from traffic_generator import traffic_generator
from manager import manager
from random import seed
import sys
logger = logging.getLogger(__name__)

def setup_logging(config):
	logging.basicConfig(filename=config.log_file, level=config.logging_level, format= '%(name)s - %(levelname)s - %(message)s', mode='w')
	console = logging.StreamHandler()
	formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
	console.setFormatter(formatter)


class simulator:
	def __init__(self, config):
		self.config = config
		self.manager = manager(self.config)

	def run(self):

		traffic_load = traffic_generator(self.config)

		for epoch in range(self.config.start_time, self.config.end_time+1):
			#print epoch
			logger.info("epoch {0}".format(epoch))
			
			requests = traffic_load.get_requests_at(epoch)

			if len(requests) == 0:
				res = self.manager.handle_requests([], epoch)
			else:
				res = self.manager.handle_requests(requests, epoch)	

		epoch +=1
		while self.manager.handle_requests(None, epoch) > 0: 
			epoch +=1  #take care of the queued requests.

		self.manager.finish_sim(epoch) # calculate cost for the vms active


if __name__=="__main__":
	config = configuration.configuration()
	setup_logging(config)
	sim = simulator(config)
	sim.run()





