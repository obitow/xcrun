#!/usr/bin/env python

from __future__ import print_function
import sys

import runtime
import listall
import simctl

class MultipleMatchesException(Exception):
	"""Raised when we have multiple matches, but only expect a single one."""
	pass

class DeviceState(object):
	shutdown = 0
	# TODO

class Device(object):
	"""Represents a device for the iOS simulator."""

	@staticmethod
	def create_from_xcrun_info(info):
		runtime_map = info["devices"]
		all_devices = {}
		for runtime_key in runtime_map.keys():
			runtime_devices_info = runtime_map[runtime_key]
			devices = []
			for device_info in runtime_devices_info:
				devices.append(Device(device_info, runtime_key))
			all_devices[runtime_key] = devices
		return all_devices

	def __init__(self, device_info, runtime_key):
		"""Construct a Device object from xcrun output and a runtime key.
		
		device_info: The dictionary representing the xcrun output for a device.
		runtime_key: A unique key representing the runtime that the device uses.
		"""

		self.raw_info = device_info
		self.state = device_info["state"]
		self.availability = device_info["availability"]
		self.name = device_info["name"]
		self.udid = device_info["udid"]
		self.runtime_key = runtime_key
		self.runtime = None

	def runtime(self):
		if self.runtime == None:
			self.runtime = runtime.Runtime.create_from_key(runtime_key)
		return self.runtime

	def get_app_container(self, app_identifier, container=None):
		return simctl.get_app_container(self, app_identifier, container)

	def openurl(self, url):
		simctl.openurl(self, url)
	
	def logverbose(self, enable):
		simctl.logverbose(self, enable)
	
	def icloud_sync(self):
		simctl.icloud_sync(self)
	
	def getenv(self, variable_name):
		return simctl.getenv(self, variable_name)

	def addmedia(self, paths):
		return simctl.addmedia(self, paths)

	def __str__(self):
		"""Return the string representation of the object."""
		return self.name + ": " + self.udid

	def __repr__(self):
		"""Return the raw representation of the object."""
		return str([str(self.raw_info), self.runtime.__repr__()])


def from_name(name, runtime=None):
	# Get all devices
	all_devices = listall.devices()

	# Now only get the ones matching the name (keep track of the runtime_id in case there are multiple)
	matching_name_devices = []

	for runtime_name in all_devices.keys():
		runtime_devices = all_devices[runtime_name]
		for device in runtime_devices:
			if device.name == name:
				matching_name_devices.append((device, runtime_name))
	
	# If there were none, then we have none to return
	if len(matching_name_devices) == 0:
		return None

	# If there was 1, then we return it
	if len(matching_name_devices) == 1:
		return matching_name_devices[0][0]
	
	# If we have more than one, we need a run time in order to differentate between them
	if runtime == None:
		raise MultipleMatchesException("Multiple device matches, but no runtime supplied")

	# Get devices where the runtime name matches
	matching_devices = [device for device in matching_name_devices if device[1] == runtime.name]

	if len(matching_devices) == 0:
		return None

	# We should only have one
	if len(matching_devices) > 1:
		raise MultipleMatchesException("Multiple device matches even with runtime supplied")
	
	return matching_devices[0][0]
