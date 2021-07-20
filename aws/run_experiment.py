import logging
import threading
import time

import configuration
from VM_utils import setup_auto_scaling
from traffic_generator import traffic_generator
from manager import manager

import VM_utils

logger = logging.getLogger(__name__)


def setup_logging(config):
    logging.basicConfig(filename=config.log_file, level=config.logging_level,
                        format='%(name)s - %(levelname)s - %(message)s', filemode='w')
    console = logging.StreamHandler()
    formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)


class experiment:
    def __init__(self, config):
        self.config = config
        self.terminateEvent = threading.Event()
        self.wait_event = threading.Event()
        self.manager = manager(self.config)



    def run(self):

        # Setup auto scaling group. Note for LIBRA(hybrid) case, we setup a group that has some fixed number of node and change it later.
        setup_auto_scaling()
        t1 = time.time()
        if config.policy == "vm_cloud" or config.policy == "vm_cloud_max":  # "vm_cloud": named AUTO case in fig 7a; "vm_cloud_max": named MAX case in fig7a
            x = threading.Thread(target=VM_utils.log_target_group,
                                 args=(self.terminateEvent,))
            x.start()
            x = threading.Thread(target=VM_utils.wait_target_group, args=(config.des_num_instance, self.wait_event))
            x.start()
            self.wait_event.wait(600)
            print("target group is ready(max 600s passed)")
        if config.policy == "hybrid":   # "hybrid": LIBRA in fig 7a
            x = threading.Thread(target=VM_utils.log_target_group,
                                 args=(self.terminateEvent,))
            x.start()
        if config.policy == "vm_cloud_hide":    # "vm_cloud_hide": SPOCK in fig 7a

            x = threading.Thread(target=VM_utils.log_target_group,
                                 args=(self.terminateEvent,))
            x.start()
        print(time.time() - t1)

        traffic_load = traffic_generator(self.config)

        # each second/epoch has some load
        for epoch in range(self.config.start_time, self.config.end_time + 1):
            t1 = time.time()
            logger.info("epoch {0}".format(epoch))

            requests = traffic_load.get_requests_at(epoch)

            if len(requests) == 0:
                self.manager.handle_requests(None, epoch)
            else:
                self.manager.handle_requests(requests, epoch)

            # time.sleep(60)  #wait 1 sec for aws to react
            time.sleep(config.epoch_time - (time.time() -t1)%config.epoch_time)

        VM_utils.Spin_VMs(self.config.end_time + 1, 0) # stop VMs
        self.terminateEvent.set() # stop monitoring active VMs
        if config.policy == "vm_cloud_hide":
            self.manager.terminate()



if __name__ == "__main__":
    config = configuration.configuration()
    setup_logging(config)
    expr = experiment(config)
    expr.run()
