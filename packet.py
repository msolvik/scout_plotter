class Packet:
	def __init__(self):
		self.number = -1
		self.battery_voltage = -1
		self.sf = -1
		self.rtc_time = ""
		self.lte_time = -1
		self.ai = -1
		self.local_time = -1
		self.event_source = -1

	def is_packet_complete(self,sfbol):
		if sfbol == True:
			if (self.battery_voltage != -1) and (self.sf != -1) \
			and (self.ai != -1) and (self.event_source != -1) and (self.local_time!=-1) and (self.lte_time != -1):
				return True

			else:
				return False

		else:
			if (self.battery_voltage != -1) and (self.sf == -1) \
			and (self.ai != -1) and (self.event_source != -1) and (self.local_time!=-1) and (self.lte_time != -1):
				return True

			else:
				return False

	def __repr__(self):
		return '({},{},{},{},{},{},{},{})'.format(self.number,self.battery_voltage, self.sf, self.rtc_time, self.lte_time, self.ai, self.local_time, self.event_source)
