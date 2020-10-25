# Program: Localising Missing Entities using Parked Vehicles: City of Melbourne Scenario
# Goal: Use feedback control to regulate the number and distribution of Switched On participating parked vehicles.
# Programmer: Wynita Griggs
# Date: 20 July, 2020
# Tested and works with SUMO 1.2.0.

# Constants and variables:
# i) The maximum speed of the Bicycle = 1.39 m/s (i.e., the maxSpeed default).
# ii) Total no. of parking spaces = approximately 24,000 (i.e., 24,067).
# iii) The RFID sampling rate (i.e. the frequency at which each car's RFID is sampling) = Always On
# iv) The radius of the RFID field around each car = 6m.
# v) The probability of a parking space being occupied by a vehicle capable of participating in the service = 0.5.
# vi) The probability of a participating vehicle being Switched On at the commencement of the simulation = 0.3.
# vii) The target number of Switched On vehicles.

# Colour convention:
# orange = Bicycle
# yellow = default empty parking space colour
# red circle = geometric centre of a parking space
# purple = indicates a parking space occupied by a vehicle that is capable of, but not currently, participating in the service (i.e. Switched Off)
# blue = indicates a parking space occupied by a vehicle that is capable of, and currently, participating in the service (i.e. Switched On)
# green = indicates that the Switched On vehicle has successfully located the Bicycle
# red = indicates that the Switched On vehicle failed to locate the Bicycle, even though the Bicycle was in range

import os, sys
import traci
import random
import numpy as np
from xlwt import Workbook, easyxf

# probability curves
def probabilityFunctionFew(s):
	probability = min + max/(1+np.exp(-steepnessFew*(s-midpointFew))) # https://en.wikipedia.org/wiki/Logistic_function
	return probability
	
def probabilityFunctionMedium(s):
	probability = min + max/(1+np.exp(-steepnessMedium*(s-midpointMedium))) # https://en.wikipedia.org/wiki/Logistic_function
	return probability
	
def probabilityFunctionMany(s):
	probability = min + max/(1+np.exp(-steepnessMany*(s-midpointMany))) # https://en.wikipedia.org/wiki/Logistic_function
	return probability

# polygon centroid formulae; see https://en.wikipedia.org/wiki/Centroid
def centroid(polyID):
	shape = traci.polygon.getShape(polyID) # in x and y coordinates (as opposed to latitude and longitude)
	
	# compute the polygon's signed area
	area = 0
	for i in range(len(shape)):
		x_i = shape[i][0]
		y_i = shape[i][1]
		if i+1 > range(len(shape))[-1]:
			x_iplus1 = shape[0][0]
		else:
			x_iplus1 = shape[i+1][0]
		if i+1 > range(len(shape))[-1]:
			y_iplus1 = shape[0][1]
		else:
			y_iplus1 = shape[i+1][1]
		area += (x_i * y_iplus1 - x_iplus1 * y_i) / 2
	
	# compute the x coordinate of the polygon's geometric centre
	c_x = 0
	for i in range(len(shape)):
		x_i = shape[i][0]
		y_i = shape[i][1]
		if i+1 > range(len(shape))[-1]:
			x_iplus1 = shape[0][0]
		else:
			x_iplus1 = shape[i+1][0]
		if i+1 > range(len(shape))[-1]:
			y_iplus1 = shape[0][1]
		else:
			y_iplus1 = shape[i+1][1]
		c_x += (x_i + x_iplus1) * (x_i * y_iplus1 - x_iplus1 * y_i) / (6 * area)
	
	# compute the y coordinate of the polygon's geometric centre
	c_y = 0
	for i in range(len(shape)):
		x_i = shape[i][0]
		y_i = shape[i][1]
		if i+1 > range(len(shape))[-1]:
			x_iplus1 = shape[0][0]
		else:
			x_iplus1 = shape[i+1][0]
		if i+1 > range(len(shape))[-1]:
			y_iplus1 = shape[0][1]
		else:
			y_iplus1 = shape[i+1][1]
		c_y += (y_i + y_iplus1) * (x_i * y_iplus1 - x_iplus1 * y_i) / (6 * area)
	
	polygonCentroid = (c_x, c_y)
	return polygonCentroid
	
# add a simulated Bicycle to the scenario
def addBicycle(simCounter,simBikeCounter):
	# print 'Inserting a simulated Bicycle.'
   
	traci.vehicle.add('sim{}simBicycle{}'.format(simCounter,simBikeCounter),'bikeRoute{}'.format(simCounter), depart=0, typeID='Bicycle') # should be followed by appending Stages or the vehicle will immediately vanish on departure
																															# DEPART_NOW = -3
        #'Route{}'.format(simCounter),
                                                                                                                            
def createRoutes(simCounter,simBikeCounter,bicycleAllowedLanes):

	number_of_routes = 100
	number_of_edges = 100

	f = open('bikeRoutes.rou.xml', "w")
	f.write("")
	f.close()

	for route in range(number_of_routes): # Creates 100 different bike routes and puts them in a file

		availableLanes = []
		bikeRoute = []
		bikeRouteLanes = []

		while len(availableLanes) <= 0:
			startLaneIndex = random.randint(0,len(bicycleAllowedLanes)-1) # obtain a random starting lane for the bike
			startLane = bicycleAllowedLanes[startLaneIndex]
			startEdge = traci.lane.getEdgeID(startLane)

			availableLanes = traci.lane.getLinks(startLane)

		bikeRoute.append(startEdge)
		bikeRouteLanes.append(startLane)

		for edge in range(number_of_edges): # Creates bike route with 100 edges

			availableLanes = traci.lane.getLinks(bikeRouteLanes[edge])
			nextAvailableLanes = []
			#print(availableLanes)

			# filter for only bicycle allowed edges
			for i in range(len(bicycleAllowedLanes)):
				for j in range(len(availableLanes)):
					if availableLanes[j][0] == bicycleAllowedLanes[i]:
						nextAvailableLanes.append(availableLanes[j][0])
			#print(nextAvailableLanes)

			if len(nextAvailableLanes) > 0: 
        
				nextLaneIndex = random.randint(0,len(nextAvailableLanes)-1) # obtain a random next lane for the bike
				nextLane = nextAvailableLanes[nextLaneIndex]

				#print(nextLane)
				nextEdge = traci.lane.getEdgeID(nextLane)

				bikeRoute.append(nextEdge)
				bikeRouteLanes.append(nextLane)
                    
			else:
				#bikeRoute.append('-' + bikeRoute[x-1])  # if no available lanes, allows bike to double back
				break	
            

		#FinalisedRoute = str(bikeRoute[1:]).strip('[]') # Make route a readable string for the rou.xml file
		#FinalisedRoute.replace(',','')
		#FinalisedRoute.replace('\'','')
		FinalisedRoute = convert_list_to_string(bikeRoute)
    
		#print(FinalisedRoute)
    
		f = open('bikeRoutes.rou.xml', "a+")
		f.write("\n\t<route id=\"bikeRoute{}\" edges=\"{}\" />".format(route+1,FinalisedRoute))
		f.close()
    
	print('RouteSuccessful')

def convert_list_to_string(org_list, seperator=' '):
#""" Convert list to string, by joining all item in list with given separator. Returns the concatenated string """
	return seperator.join(org_list)

    
# main program
if __name__ == '__main__':

	# constants and parameters
	endSim = 1800000 # the simulation will be permitted to run for a total of endSim milliseconds; for example, 1800000 milliseconds = 30 minutes
	simsRequired = 100 # total number of simulations to perform
	n = 20 # radius to neighbours [m]
	r = 10 # rfid range [m]
	prob = 1 # sampling rate is Always On
	upperlimitFew = 0 # upper limit of FEW neighbours category; an integer >= 0
	upperlimitMedium = 5 # upper limit of MEDIUM neighbours category; an integer >= 0
	update = 20000 # time interval regarding when a new control signal is sent; in milliseconds
	p = 0.5 # probability of a parking space being occupied by a vehicle capable of participating in the service; between 0 and 1, inclusive
	proportionInitiallySwitchedOn = 0.3 # probability of a participating vehicle being Switched On at the commencement of the simulation; between 0 and 1, inclusive
	targetNumberVehicles = 7200 # target number of Switched On vehicles; for convenience, written as a % of total parking spaces, which are provided below
								# 10% = 2400; 20% = 4800; 30% = 7200; 40% = 9600; 50% = 12,000; 60% = 14,400; 70% = 16,800; 80% = 19,200; 90% = 21,600; 100% = 24,000
	
	# constants for the probability curves
	min = 0.05 # curve's minimum value
	max = 0.90 # curve's maximum value
	steepnessFew = 0.0005 # curve's steepness
	midpointFew = -12000.0 # 'x'-axis value of the sigmoid's midpoint
	steepnessMedium = 0.0005 # curve's steepness
	midpointMedium = 0.0 # 'x'-axis value of the sigmoid's midpoint
	steepnessMany = 0.0005 # curve's steepness
	midpointMany = 12000.0 # 'x'-axis value of the sigmoid's midpoint
	
	# constants and initialisations for the controller; note: pi(k) - beta*pi(k-1) = kappa*(e(k) - alpha*e(k-1)) rewritten is like (1-alpha*z^{-1})/(1-beta*z^{-1}), so set beta < 1 else the controller will be unstable
	alpha = -4.01 # default value: -4.01
	beta = 0.99 # default value: 0.99
	kappa = 0.1 # default value: 0.1
	signalHistory = 0.0
	inputHistory = 0.0
	
	# global initialisations
	simCounter = 1 # simulation counter
	
	# per simulation initialisations
	step = 0 # time step
	simBikeCounter = 0 # simulated Bicycle counter
	flag = 0
	timeSnapshot = -1
	
	# statistics initialisations
	statisticOneData = 0
	statisticTwoData = 0
	statisticThreeDataA = 0
	statisticThreeDataB = 0
	statisticFourDataA = 0
	statisticFourDataB = 0
	statisticFiveData = 0
	statisticSixData = 0
	statisticSevenData = 0    
	
	# set up an Excel Workbook
	rowCounter = 1
	book = Workbook()
	sheet1 = book.add_sheet('Detection Times')
	style1 = easyxf('alignment: horizontal centre')
	style2 = easyxf('font: bold true;' 'alignment: horizontal centre')
	
	print
	print '==========================='
	print 'Beginning the main program.'
	print '==========================='
	print	
	print "Connecting to SUMO via TraCI."
	print
	
	# import TraCI (to use the library, the <SUMO_HOME>/tools directory must be on the python load path)
	if 'SUMO_HOME' in os.environ:
		tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
		sys.path.append(tools)
	else:	
		sys.exit("Please declare environment variable 'SUMO_HOME'.")
		
	# compose the command line to start SUMO-GUI
	sumoBinary = "C:/Program Files (x86)/Eclipse/Sumo/bin/sumo-gui"
	sumoCmd = [sumoBinary, "-S", "-c", "locatingentities.sumo.cfg"]
	
	# start the simulation and connect to it with the python script
	traci.start(sumoCmd)
	
	# get a list of all polygon parking spaces
	polys = traci.polygon.getIDList() # a list of all polygons currently in the scenario
	
	# determine which polygon parking spaces are occupied by vehicles capable of participating in the service
	poiCounter = 1 # for visualising the geometric centres
	polyVehicles = []
	polyVehiclesPositions = [] # paired with polyVehicles
	for i in range(len(polys)):
		c = random.uniform(0,1) # flip a weighted coin; returns a random floating point number r such that 0 <= r < 1
		if c < p: # i.e. if the polygon parking space is occupied by a vehicle capable of participating...
			polyVehicles.append(polys[i])
			geometricCentre = centroid(polys[i]) # obtain the geometric centre of the parking space; in x and y coordinates (as opposed to latitude and longitude)
			traci.poi.add('poi{}'.format(poiCounter), geometricCentre[0], geometricCentre[1], (255,0,0,255), poiType='', layer=1000, imgFile='', width=1, height=1, angle=0) # for visualising the geometric centres
			poiCounter += 1 # for visualising the geometric centres
			polyVehiclesPositions.append(geometricCentre)
			traci.polygon.setColor(polys[i],(118,32,176,255)) # purple, i.e. Switched Off
	print 'Total no. of vehicles capable of participating: {}'.format(len(polyVehicles))
	# print 'List of vehicles capable of participating: {}'.format(polyVehicles)
	
	# calculate number of neighbours
	'''
	polyVehiclesProbabilityCurves = [] # paired with polyVehicles
	for i in range(len(polyVehicles)):
		numberNeighbours = 0 # initialise number of neighbours
		for j in range(len(polyVehicles)):
			if i != j:
				if ((polyVehiclesPositions[j][0]-polyVehiclesPositions[i][0])**2 + (polyVehiclesPositions[j][1]-polyVehiclesPositions[i][1])**2 <= n**2): # i.e. if the position of a jth vehicle is on or inside a circle around the ith vehicle...
					numberNeighbours += 1
		if numberNeighbours <= upperlimitFew:
			polyVehiclesProbabilityCurves.append('few')
			print '{} has FEW neighbours capable of participating.'.format(polyVehicles[i])
		elif (numberNeighbours > upperlimitFew) & (numberNeighbours <= upperlimitMedium):
			polyVehiclesProbabilityCurves.append('medium')
			print '{} has MEDIUM neighbours capable of participating.'.format(polyVehicles[i])
		else:
			polyVehiclesProbabilityCurves.append('many')
			print '{} has MANY neighbours capable of participating.'.format(polyVehicles[i])
	# print 'No. of neighbours capable of participating, of each vehicle capable of participating: {}'.format(polyVehiclesProbabilityCurves)
	'''
    
	# determine which vehicles capable of participating in the service are Switched On at the beginning of the simulation
	polyVehiclesSwitchedOn = []
	polyVehiclesSwitchedOnPositions = [] # paired with polyVehiclesSwitchedOn
	for i in range(len(polyVehicles)):
		c = random.uniform(0,1) # flip a weighted coin; returns a random floating point number r such that 0 <= r < 1
		if c < proportionInitiallySwitchedOn: # i.e. if the vehicle is Switched On...
			polyVehiclesSwitchedOn.append(polyVehicles[i])
			polyVehiclesSwitchedOnPositions.append(centroid(polyVehicles[i])) # obtain the x and y position of the Switched On Vehicle
			traci.polygon.setColor(polyVehicles[i],(0,102,204,255)) # blue, i.e. Switched On
	print 'No. of Switched On vehicles at simulation commencement: {}'.format(len(polyVehiclesSwitchedOn))
	print
	
	# get a subset list of lanes, from all lanes in the network, on which Bicycles are allowed
	lanes = traci.lane.getIDList() # a list of all lanes in the network
	# bufferTemp = 0 # unbuffered; see https://docs.python.org/2/library/functions.html#open
	# file = open("cityofmelbournelistofalllanes.txt", "w", bufferTemp)
	# file.write(str(lanes))
	# file.close()
	bicycleAllowedLanes = [] # a subset list of lanes, from all lanes in the network, on which Bicycles are allowed
	for i in range(len(lanes)):
		if ('bicycle' in traci.lane.getAllowed(lanes[i])) or (len(traci.lane.getAllowed(lanes[i])) == 0): # traci.lane.getAllowed(laneID) returns a list of allowed vehicle classes; an empty list means all vehicles
																											 # are allowed
			bicycleAllowedLanes.append(lanes[i])
	# print 'No. of lanes in network on which Bicycle is allowed: {}'.format(len(bicycleAllowedLanes))
	# file = open("cityofmelbournelistofBicycleallowedlanes.txt", "w", bufferTemp)
	# file.write(str(bicycleAllowedLanes))
	# file.close()
	
	#print(bicycleAllowedLanes[0:100])
    
	# add a simulated Bicycle
	simBikeCounter += 1
    
    # add a route for the simulated Bicycle
	#createRoutes(simCounter,simBikeCounter,bicycleAllowedLanes)
    
	addBicycle(simCounter,simBikeCounter)
	
	# begin the simulation
	traci.simulationStep()
	
	while simCounter <= simsRequired:
	
		powerPerSim = 0  # Calculation for power sunsumed by RFID's per simulation
		powerTillDet = 0  # Calculation for power sunsumed by RFID's per simulation

		dBm = 30  # Antenna power consumption in dBm (-3 cable compensation)
		wattPerSec = 10**((dBm-30)/10)   # Watts per second consumed while RFID is activated
                                        # calculated from Alien Antenna Data sheet (30dBm => 1 Watt)
                                        # P(W) = 10^(dBm-30/10)
		totalTime = 0 # records the total amount of time the bike is detected in the sim
    
		while step < endSim: # End simulation if time runs out
		
			print '==========================='
			print '------ SIMULATION {} ------'.format(simCounter)
			print '==========================='			
			print
			print 'Time step [s]: {}'.format(step/1000)
			# print 'Current simulation time [ms]: {}'.format(traci.simulation.getCurrentTime())
			print 'Current no. of Switched On vehicles: {}'.format(len(polyVehiclesSwitchedOn))
			print
			
			vehicles = traci.vehicle.getIDList() # a list of vehicles currently in the scenario
			if len(vehicles) != 0:
				#if len(vehicles) > 1:
					#raw_input('More than one simulated Bicycle currently in the scenario.  Enter an acknowledgement message to continue.')

				for j in range(len(vehicles)):
					# print 'vehicle currently in the scenario: {}'.format(vehicles[j])
					# print 'Current edge: {}'.format(traci.vehicle.getRoadID(vehicles[j])) # returns the id of the edge that the vehicle was at within the last time step
					# print 'Position along lane [m]: {}'.format(traci.vehicle.getLanePosition(vehicles[j])) # position of the vehicle along the lane measured in m
																										 # note: when building the route, this position value does not seem to stall or
																										 # decrease, meaning that the vehicle continues on from where they are currently
																										 # when appending a new walking stage
					
					# obtain the position of the simulated Bicycle
					(x, y) = traci.vehicle.getPosition(vehicles[j])
					# print 'Position of simulated Bicycle: {}'.format((x, y))
					# traci.gui.setOffset('View #0', x, y) # this is buggy
					
					for i in range(len(polyVehiclesSwitchedOn)):
						if ((x-polyVehiclesSwitchedOnPositions[i][0])**2 +(y-polyVehiclesSwitchedOnPositions[i][1])**2 <= r**2): # i.e. if the position of the simulated Bicycle is on or inside a circle around a Switched On vehicle...
							print 'Bicycle in range of: {}'.format(polyVehiclesSwitchedOn[i])
							coin = random.uniform(0,1) # flip a weighted coin; returns a random floating point number r such that 0 <= r < 1
							if coin < prob: # i.e. if the simulated Bicycle is detected...
								traci.polygon.setColor(polyVehiclesSwitchedOn[i],(0,204,0,255)) # green
								print 'Successful detection.'
								print 'Time taken to detection [s]: {}'.format(step/1000)
								print 'Time taken to detection [min]: {}'.format(step/60000.00)
								print
                                
								if (timeSnapshot == -1):
									timeSnapshot = step
                                
								totalTime += 1 # records the total amount of time the bike is detected in the sim
								#flag = 1 # flag to end the simulation
								#step = 1799000
								break
							else:
								traci.polygon.setColor(polyVehiclesSwitchedOn[i],(255,0,0,255)) # red
								print 'Failed to detect.'
								print

					#if flag == 0:
						# determine if the simulated Bicycle is on the last edge of their route
						#route = traci.vehicle.getEdges(vehicles[j], nextStageIndex=0) # returns a list of all edges in the nth next stage; for walking stages this is the complete route;
																					# nextStageIndex 0 retrieves value for the current stage; nextStageIndex must be lower then value of
																					# getRemainingStages(vehicleID)
						#print 'Route: {}'.format(route)						
						#if len(route) > 1: # a fix/check in case the route consists of only one edge
						#	if traci.vehicle.getNextEdge(vehicles[j]) == route[-1]:
						#		endLaneIndex = random.randint(0,len(bicycleAllowedLanes)-1) # obtain a new random ending lane for the Bicycle
						#		endLane = bicycleAllowedLanes[endLaneIndex]
						#		endEdge = traci.lane.getEdgeID(endLane)
						#		bicycleRoute = traci.simulation.findIntermodalRoute(traci.vehicle.getRoadID(vehicles[j]), endEdge, modes='', depart=-1.0, routingMode=0, speed=-1.0, walkFactor=-1.0, departPos=0.0, arrivalPos=-1073741824.0, departPosLat=0.0, pType='', vType='Bicycle', destStop='')
						#		(stageTypeRoute, vTypeRoute, lineRoute, destStopRoute, edgesRoute, travelTimeRoute, costRoute, lengthRoute, intendedRoute, departRoute, departPosRoute, arrivalPosRoute, descriptionRoute) = bicycleRoute[0]
						#		traci.vehicle.removeStages(vehicles[j]) # removes all stages of the vehicle; if no new phases are appended, the vehicle will be removed from the simulation in the next simulationStep()
						#		traci.vehicle.appendBikeStage('sim{}simBicycle{}'.format(simCounter,simBikeCounter), edgesRoute, arrivalPos=-0.001, duration=-1, speed=-1, stopID='') # default arrivalPos = -1

			else:
				print 'No vehicles currently in the scenario.'
				print
				
				# add a simulated Bicycle
				#simBikeCounter += 1
				addBicycle(simCounter,simBikeCounter)
			
			#####################################################################
			# determine which vehicles will be Switched On for the next time step
			#####################################################################
			if flag == 0:
				if (step+1000) % update == 0: # evaluates true if and only if 'step+1000' is an exact multiple of 'update'
					input = targetNumberVehicles - len(polyVehiclesSwitchedOn) # ASSUMPTION: m = 0 for the filter
					signal = beta*signalHistory + kappa*(input - alpha*inputHistory) # implement the controller, return the signal 'pi'
					inputHistory = input # store the input data for future use
					signalHistory = signal # store the signal data for future use
                    
					for i in range(len(polyVehiclesSwitchedOn)): # next, reset all vehicles to Switched Off
						traci.polygon.setColor(polyVehiclesSwitchedOn[i],(118,32,176,255)) # purple, i.e. Switched Off
					polyVehiclesSwitchedOn = []
					polyVehiclesSwitchedOnPositions = [] # paired with polyVehiclesSwitchedOn
					
					for i in range(len(polyVehicles)):
						#if polyVehiclesProbabilityCurves[i] == 'few':
						#	probabilitySwitchOn = probabilityFunctionFew(signal)				
						#elif polyVehiclesProbabilityCurves[i] == 'medium':
						#	probabilitySwitchOn = probabilityFunctionMedium(signal)
						#else:
						#	probabilitySwitchOn = probabilityFunctionMany(signal)
						c = random.uniform(0,1) # flip a weighted coin; returns a random floating point number r such that 0 <= r < 1
						if c < proportionInitiallySwitchedOn: # i.e. if the vehicle is to Switch On...
							polyVehiclesSwitchedOn.append(polyVehicles[i])
							polyVehiclesSwitchedOnPositions.append(centroid(polyVehicles[i])) # obtain the x and y position of the Switched On Vehicle
							traci.polygon.setColor(polyVehicles[i],(0,102,204,255)) # blue, i.e. Switched On
                                                
			#####################################################################		
			
			# goto the next time step
			step += 1000 # in milliseconds
            
			powerPerSim += len(polyVehiclesSwitchedOn)*wattPerSec  # Calcualtion for power consumed every update period
            
			firstDetect = timeSnapshot
            
			if (timeSnapshot == -1):
				powerTillDet += len(polyVehiclesSwitchedOn)*wattPerSec
			elif (timeSnapshot == 0):
				powerTillDet += len(polyVehiclesSwitchedOn)*wattPerSec
				firstDetect = 0
				timeSnapshot += 1
            
			if flag == 0:
				traci.simulationStep()

		# write to Excel Workbook
		sheet1.write(rowCounter,0,simCounter,style1)
		sheet1.write(rowCounter,1,len(polyVehicles),style1) # no. of vehicles capable of participating in the service
        
		sheet1.write(rowCounter,4,powerTillDet,style1) 
		sheet1.write(rowCounter,5,powerPerSim,style1) # Total power consumed by RFIDs per simulation [W]
		sheet1.write(rowCounter,6,totalTime,style1) 
        
		statisticFiveData = statisticFiveData + powerPerSim
		statisticSixData = statisticSixData + totalTime
		statisticSevenData = statisticSevenData + powerTillDet        
       
		statisticOneData = statisticOneData + len(polyVehicles)
		if timeSnapshot != -1:
			sheet1.write(rowCounter,2,firstDetect/1000,style1) # time taken to detection [s]
			sheet1.write(rowCounter,3,firstDetect/60000.0,style1) # time taken to detection [min]            
			statisticThreeDataA = statisticThreeDataA + (firstDetect/1000)
			statisticThreeDataB += 1
			statisticFourDataA = statisticFourDataA + (firstDetect/60000.0)
			statisticFourDataB += 1
		else:
			sheet1.write(rowCounter,2,'FAIL',style1)
			sheet1.write(rowCounter,3,'FAIL',style1)
			statisticTwoData += 1
		timeSnapshot = -1
		rowCounter += 1
		
		# prepare for the next simulation
		simCounter += 1
		if simCounter <= simsRequired: # i.e. if there are more simulations to do...
		
			traci.simulationStep()
		
			# remove any vehicles from the prior simulation that are still currently in the scenario
			if len(traci.vehicle.getIDList()) != 0: # don't use the above "vehicles" list, as simulated Bicycles may have been added to or removed from the scenario since the last time that the
												   # list was compiled and named
				for j in range(len(vehicles)):
					traci.vehicle.remove(vehicles[j]) # removes all stages of the vehicle; if no new phases are appended, the vehicle will be removed from the simulation in the next simulationStep()
			
			# remove prior geometric centre visualisations
			pois = traci.poi.getIDList() # a list of all pois currently in the scenario
			numberOfPois = len(pois)
			for i in range(numberOfPois):
				traci.poi.remove(pois[i])
			
			# reinitialise
			step = 0 # time step
			simBikeCounter = 0 # simulated Bicycle counter
			flag = 0
			signalHistory = 0.0
			inputHistory = 0.0
			for i in range(len(polys)):
				traci.polygon.setColor(polys[i],(255,255,0,255)) # yellow
			
			# determine which polygon parking spaces are occupied by vehicles capable of participating in the service
			poiCounter = 1 # for visualising the geometric centres
			polyVehicles = []
			polyVehiclesPositions = [] # paired with polyVehicles
			for i in range(len(polys)):
				c = random.uniform(0,1) # flip a weighted coin; returns a random floating point number r such that 0 <= r < 1
				if c < p: # i.e. if the polygon parking space is occupied by a vehicle capable of participating...
					polyVehicles.append(polys[i])
					geometricCentre = centroid(polys[i]) # obtain the geometric centre of the parking space; in x and y coordinates (as opposed to latitude and longitude)
					traci.poi.add('poi{}'.format(poiCounter), geometricCentre[0], geometricCentre[1], (255,0,0,255), poiType='', layer=1000, imgFile='', width=1, height=1, angle=0) # for visualising the geometric centres
					poiCounter += 1 # for visualising the geometric centres
					polyVehiclesPositions.append(geometricCentre)
					traci.polygon.setColor(polys[i],(118,32,176,255)) # purple, i.e. Switched Off
			print 'Total no. of vehicles capable of participating: {}'.format(len(polyVehicles))
			# print 'List of vehicles capable of participating: {}'.format(polyVehicles)
			'''
			# calculate number of neighbours
			polyVehiclesProbabilityCurves = [] # paired with polyVehicles
			for i in range(len(polyVehicles)):
				numberNeighbours = 0 # initialise number of neighbours
				for j in range(len(polyVehicles)):
					if i != j:
						if ((polyVehiclesPositions[j][0]-polyVehiclesPositions[i][0])**2 + (polyVehiclesPositions[j][1]-polyVehiclesPositions[i][1])**2 <= n**2): # i.e. if the position of a jth vehicle is on or inside a circle around the ith vehicle...
							numberNeighbours += 1
				if numberNeighbours <= upperlimitFew:
					polyVehiclesProbabilityCurves.append('few')
					print '{} has FEW neighbours capable of participating.'.format(polyVehicles[i])
				elif (numberNeighbours > upperlimitFew) & (numberNeighbours <= upperlimitMedium):
					polyVehiclesProbabilityCurves.append('medium')
					print '{} has MEDIUM neighbours capable of participating.'.format(polyVehicles[i])
				else:
					polyVehiclesProbabilityCurves.append('many')
					print '{} has MANY neighbours capable of participating.'.format(polyVehicles[i])
			# print 'No. of neighbours capable of participating, of each vehicle capable of participating: {}'.format(polyVehiclesProbabilityCurves)
			'''         
			# determine which vehicles capable of participating in the service are Switched On at the beginning of the simulation
			polyVehiclesSwitchedOn = []
			polyVehiclesSwitchedOnPositions = [] # paired with polyVehiclesSwitchedOn
			for i in range(len(polyVehicles)):
				c = random.uniform(0,1) # flip a weighted coin; returns a random floating point number r such that 0 <= r < 1
				if c < proportionInitiallySwitchedOn: # i.e. if the vehicle is Switched On...
					polyVehiclesSwitchedOn.append(polyVehicles[i])
					polyVehiclesSwitchedOnPositions.append(centroid(polyVehicles[i])) # obtain the x and y position of the Switched On Vehicle
					traci.polygon.setColor(polyVehicles[i],(0,102,204,255)) # blue, i.e. Switched On
			print 'No. of Switched On vehicles at simulation commencement: {}'.format(len(polyVehiclesSwitchedOn))
			print
			
			# add a simulated Bicycle
			simBikeCounter += 1
			addBicycle(simCounter,simBikeCounter)
			
			# begin the simulation
			traci.simulationStep()
		
	print "Writing to the Excel Workbook."
	sheet1.write(0,0,'Simulation No.',style2)
	sheet1.col(0).width = 4000
	sheet1.write(0,1,'No. Capable Vehicles',style2)
	sheet1.col(1).width = 6000
	sheet1.write(0,2,'Detection Time [s]',style2)
	sheet1.col(2).width = 5000
	sheet1.write(0,3,'Detection Time [min]',style2)
	sheet1.col(3).width = 5500
    
	sheet1.write(0,4,'Power Consumed Till Detection [W]',style2) # simulation Power excel output
	sheet1.col(4).width = 5500
	sheet1.write(0,5,'Power Consumed [W]',style2) # simulation Power excel output
	sheet1.col(5).width = 5500
	sheet1.write(0,6,'Total Time Detected [s]',style2) # simulation Power excel output
	sheet1.col(6).width = 5500
	
	# statistics
	statisticOne = statisticOneData/float(simsRequired)
	statisticTwo = statisticTwoData
	statisticThree = statisticThreeDataA/float(statisticThreeDataB)
	statisticFour = statisticFourDataA/statisticFourDataB # recall that statisticFourDataA is already a float

	statisticFive = statisticFiveData/float(simsRequired) # Average Power Calculation
	statisticSix = statisticSixData/float(simsRequired) # Average Time Detected Calculation
	statisticSeven = statisticSevenData/float(simsRequired) # Average Power Calculation
    
	sheet1.write(0,8,'Average No. Participating Polys',style2)
	sheet1.col(8).width = 8000
	sheet1.write(1,8,statisticOne,style1)
	sheet1.write(3,8,'Total No. FAIL to Detects',style2)
	sheet1.write(4,8,statisticTwo,style1)
	sheet1.write(6,8,'Average Detection Time [s]',style2)
	sheet1.write(7,8,statisticThree,style1)
	sheet1.write(9,8,'Average Detection Time [min]',style2)
	sheet1.write(10,8,statisticFour,style1)
	sheet1.write(12,8,'Average Power Consumed Till Detection [W]',style2) # Average Power excel output
	sheet1.write(13,8,statisticSeven,style1)
	sheet1.write(15,8,'Average Power Consumed [W]',style2) # Average Power excel output
	sheet1.write(16,8,statisticFive,style1)
	sheet1.write(18,8,'Average Time Detected [s]',style2) # Average Time Detected output
	sheet1.write(19,8,statisticSix,style1)

	print "Saving the Excel Workbook."
	book.save('locatingentities_feedbackcontrol_IoTpaper_Demo_Delete.xls')
	print "Closing the main program. Goodbye."
	traci.close() # close the connection to SUMO