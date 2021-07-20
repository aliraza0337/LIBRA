from __future__ import division
# from simulator import *

import logging
import math
import threading

import VM_utils
import req_utils
import time
import boto3
logger = logging.getLogger(__name__)

healthy_count: int = 0


class manager:
	def __init__(self, config):
		self.cloudwatch_client = boto3.client('cloudwatch')
		# self.VM_Monitor
		self.config = config
		# self.vm_cloud = vm_cloud(config)
		# self.ser_cloud = serverless_cloud(config)
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
		self.Autoscaling_Client = boto3.client('autoscaling')
		self.wait_event = threading.Event()
		if self.config.policy == 'vm_cloud_hide':
			self.targetgroup_change_event = threading.Event()
			self.terminateEvent = threading.Event()
			# self.targetgroup_change_event.set()
			x = threading.Thread(target=self.trace_target_group,
								 args=(self.targetgroup_change_event, self.config, self.terminateEvent))
			x.start()
		
	def terminate(self):
		self.terminateEvent.set()
		
	def handle_requests(self, requests, epoch):
		# send in a given epoch for all cases: the worst case is 'vm_cloud': we don't want to overwhelm the system too fast.
		if requests is not None:
			print("number of requests: "+str(len(requests)))
			if self.config.policy == 'vm_cloud_hide':

				if not self.targetgroup_change_event.is_set():
					# print("!!(alarm): status: is not set")
					# logger.info("!!(alarm): status: is not set")
					req_utils.VM_Send_Request(len(requests), epoch)
				else:
					# print("!!(alarm): status: is set")
					# logger.info("!!(alarm): status: is set")
					print("healthy_count: " + str(healthy_count))
					req_utils.VM_Send_Request(min(math.floor(int(self.config.NumOfReqPerVM*healthy_count)), len(requests)), epoch)
					req_utils.SER_Send_Request(max(len(requests) - math.floor(int(self.config.NumOfReqPerVM*healthy_count)), 0), epoch)

			# both serverless and EC2, but scaling on our own.
			elif self.config.policy == 'hybrid':

				total_requests = len(requests)
				# logger.info("manager received |requests,epoch|{0},{1}".format(total_requests, epoch))

				if self.mean is None and self.std is None:
					self.mean = total_requests
					self.std = 0
				else:
					self.std = (self.mu)*self.std + (1-self.mu)*(abs(self.mean-total_requests))
					self.mean = (1-self.alpha)*total_requests + self.alpha*self.mean


				# from 1 to end_time, each send some requests. Will provision at no_vm_update_freq.
				if epoch == 1 or (epoch % self.config.no_vm_update_freq) == 0:
					self.vm_share = int(abs(self.mean+self.std))  # number of requests for VM 	# mean + 1 * standard deviation, from fig 6a.
					self.vms = self.calculate_vms(self.vm_share)  # expectation utilization for this epoch
					VM_utils.Spin_VMs(epoch, self.vms)

					# print("mean, share, vms", self.mean, self.vm_share, self.vms)
					# print("at epoch: {0}, {1} vms provisioned".format(epoch, self.vms))
					# logger.info(
					# 	"at epoch: {0}, {1} vms provisioned".format(epoch, self.vms))

					if self.vms > self.prev_n_vms:
						x = threading.Thread(target=VM_utils.wait_target_group,
											 args=(self.vms, self.wait_event))
						x.start()

					else:
						self.prev_n_vms = self.vms
						self.provision_for = int(self.vm_share*self.config.vm_provison_prop)	# Only send 'vm_provison_prop' persentage of 'vm_share' to VM: leave some resource idle to handle dynamics in real world infrastructure.

				if self.wait_event.is_set(): # keep using the previous provision number.
					self.prev_n_vms = self.vms
					self.provision_for = int(self.vm_share*self.config.vm_provison_prop)
					print("self.provision_for: "+str(self.provision_for) + "self.vm_share: "+ str(self.vm_share) + "self.config.vm_provison_prop: " + str(self.config.vm_provison_prop))
					self.wait_event.clear()


				req_utils.VM_Send_Request(min(self.provision_for, len(requests)), epoch) # we only need total number, the ALB can distribute jobs evenly.
				req_utils.SER_Send_Request(max(len(requests) - self.provision_for, 0), epoch)
			#
			elif self.config.policy == 'serverless':
				req_utils.SER_Send_Request(len(requests), epoch)
				# res = self.ser_cloud.handle_requests(requests, epoch)

			# AWS EC2 with auto scaling
			elif self.config.policy == 'vm_cloud' or self.config.policy == 'vm_cloud_max': # again we don't have a queue here!!!!!!: just need to lower the amount of request sent and set time interval to be the autoscaling setup time.
				# print("number of requests: "+str(len(requests)))
				req_utils.VM_Send_Request(len(requests), epoch)



		else: # previously handling queue; now each thread would retry on its own.
			print("manager completing simulation |epoch|{0}".format(epoch))
			# logger.info("manager completing simulation |epoch|{0}".format(epoch))
			# res = self.vm_cloud.handle_requests(requests, epoch)


	def calculate_vms(self, mean):
		return int(math.ceil((mean / self.config.NumOfReqPerVM))) # according to SLA



	def configure_resources(self):
		pass

	def trace_target_group(self, terminateEvent, config,  targetgroup_change_event):
		global healthy_count
		elbList = boto3.client('elbv2')
		# total_count_prev = 0
		t1 = time.time()
		while True:
			print("tracking period: "+ str(time.time()-t1))
			t1 = time.time()

			# label_1 = False

			# shortest first
			# check target group
			count_d = {"initial": 0, "healthy": 0, "unhealthy": 0, "unused": 0, "draining": 0, "unavailable": 0}
			total_count = 0
			for d in elbList.describe_target_health(
					TargetGroupArn=elbList.describe_target_groups()['TargetGroups'][0]['TargetGroupArn'])[
				'TargetHealthDescriptions']:
				total_count = total_count + 1
				count_d[d['TargetHealth']['State']] = count_d[d['TargetHealth']['State']] + 1
			print("!!(target): timestamp, initial, healthy, unhealthy, unused, draining, unavailable, total: " + str(
				time.time()) + ", " + str(count_d["initial"]) + ", " + str(count_d["healthy"]) + ", " + str(
				count_d["unhealthy"]) + ", " + str(count_d["unused"]) + ", " + str(count_d["draining"]) + ", " + str(
				count_d["unavailable"]) + ", " + str(total_count))
			# print("total_count_prev " + str(total_count_prev))
			if total_count == 0 or total_count == count_d["draining"]:  # going to/currently have 0 instance: init or done or during experiment
				self.targetgroup_change_event.set()
				print("was set, 1")
				logger.info("!!(alarm): status, reason: is set, 1")
				if count_d["initial"] == 0 and count_d["draining"] == 0:  # align healthy count
					healthy_count = 0

				time.sleep(self.config.vm_state_epoch - (time.time() - t1) % self.config.vm_state_epoch)
				if self.terminateEvent.is_set():
					break

				continue

			# elif total_count_prev != total_count:  # some change happened
			elif count_d["initial"] != 0 or count_d["draining"] != 0:  # some change happened
				self.targetgroup_change_event.set()
				print("was set, 2")
				logger.info("!!(alarm): status, reason: is set, 2")
				time.sleep(self.config.vm_state_epoch - (time.time() - t1) % self.config.vm_state_epoch)
				if self.terminateEvent.is_set():
					break
				continue

			# else:
			# 	healthy_count = count_d["healthy"]

			# check alarm
			response1 = self.cloudwatch_client.describe_alarms(
				AlarmNames=[
					self.config.UpperAlarmName,
				],
				AlarmTypes=[
					'MetricAlarm',
				],
			)
			response2 = self.cloudwatch_client.describe_alarms(
				AlarmNames=[
					self.config.LowerAlarmName,
				],
				AlarmTypes=[
					'MetricAlarm',
				],
			)
			if response1["MetricAlarms"][0]['StateValue'] == "ALARM" or response2["MetricAlarms"][0]['StateValue'] == "ALARM":
				self.targetgroup_change_event.set()
				print("was set, 3")
				logger.info("!!(alarm): status, reason: is set, 3")
			# elif label_1: # new instances are up and no alarm is on
			else:
				self.targetgroup_change_event.clear()
				# total_count_prev = total_count
				print("was clear, 2")
				logger.info("!!(alarm): status, reason: is cleared, 2")
				# total_count_prev = total_count
				# healthy_count = total_count
				healthy_count = count_d["healthy"]

			time.sleep(self.config.vm_state_epoch - (time.time() - t1) % self.config.vm_state_epoch)
			if self.terminateEvent.is_set():
				break