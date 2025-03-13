class demandResponse():
	def __init__(self):
		self.name = name
		self.modes = ['DR','TOU']
		self.mode = self.modes[0]
		self.eventWindow = {'start':0,'duration':4} # start time and duraction in hours
		self.promise = 0 #kW
		self.baseline = 0
		self.performance = 0
		self.reliability = 0
		self.predictability = 0
		self.isEvent = False # flag to indiciate if event is going on
		self.isEventUpcoming = False
		self.timeToEvent = 0 # countdown hours until event
		self.shiftable = False #indicates if the load is appropriate for shifting

	#reports the power at each point in the system
	def getStatus(self):
		pass

	# connect load to battery
	def replace(self)
		pass

	# turn off all outputs
	def curtail(self)
		pass

	# turn off all outputs and schedule grid-to-load at later point
	def autoShift(self)
		if self.shiftable:
			pass

	#detects consumption and alerts user to shift
	def manualShift(self)
		pass

	#charge battery from the grid
	def gridCharge()
		# dont charge during an event
		if not self.isEvent:
			pass

	#set an amount of power to flex eveningly for the duration of the event
	def flexPower(self, watts, duration):
		pass

	#set an amount of energy to flex during the event
	def flexEnergy(self, wattHours, duration)
		pass


	def getWeather(self)
		pass

	# checks for upcoming DR event
	def checkAlert(self)
		pass