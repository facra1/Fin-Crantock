# Program: SUMOPaint
# Goal: Permits the user to connect to the Monash simulation and subsequently locate and track a bicycle using cars as antennas
# Original Author: Wynita Griggs
# Tested and works with SUMO 1.2.0.
#
# Additional Developements made by Fin Crantock (26904594)

import os, sys
import traci
import multiprocessing
from multiprocessing import Process, Value
import socket
import time

#Added modules
from multiprocessing import Process, Manager
import thread
import threading
import subprocess
import random
import numpy
from xlwt import Workbook, easyxf

stopThread = False
AppConnected = 0   #Ensures the app only recieves the last detected position from after connection


# server program:  creates the server, handles incoming calls and subsequent user requests
def server(data, bikePosition):


	# size of buffer and backlog
	buffer = 2048 # value should be a relatively small power of 2, e.g. 4096
	backlog = 1 # tells the operating system to keep a backlog of 1 connection; this means that you can have at most 1 client waiting while the server is handling the current client; the operating system will typically allow a maximum of 5 waiting connections; to cope with this, busy servers need to generate a new thread to handle each incoming connection so that it can quickly serve the queue of waiting clients

	# create a socket
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # AF_INET = IPv4 socket family; SOCK_STREAM = TCP socket type

	# bind the socket to an address and port
	host = '127.0.0.1' # localhost
	port = 8080 # reserve a port for the service (i.e. a large number less than 2^16); the call will fail if some other application is already using this port number on the same machine
	server_socket.bind((host, port)) # binds the socket to the hostname and port number

	# listen for incoming connections
	server_socket.listen(backlog)


	while True: # infinite loop 1
		client_socket, address = server_socket.accept() # passively accept TCP client connections; the call returns a pair of arguments: client is a new Socket object used to communicate with the client and address is the address of the client
	
		# record client connection time (as seen from the server)
		start_time = time.strftime('%d %b %Y at %H:%M:%S')
		init_time = str(start_time) # convert connection time to a string
		print( 'Made a connection with', address, 'on', init_time + '.')
		
        
		while True: # infinite loop 2
			incoming = client_socket.recv(buffer) # receive client data into buffer

			if (incoming == 'quit'):
				data.value = 0.7
                
				#t1 = threading.Thread(target = SendLocation, args = (client_socket,bikePosition))				
				stopThread = True
				time.sleep(1)
				t1.join()

				print( 'Client is bored of painting cars.  Ending session with client.')
				client_socket.send('Quit message received.  Goodbye.')
				client_socket.close() # close the connection with the client
				t1.close()
				
				break # breaks out of infinite loop 2
                
			if (incoming == 'position'):
				data.value = 0.8

				t1 = threading.Thread(target = SendLocation, args = (client_socket,bikePosition))
				t1.start()

			print( 'Client wants to paint the car:', incoming)


def SendLocation(client_socket,bikePosition):
	
	while True:
		global stopThread    
		if stopThread == False:
			# Send Position Data
			# //////////////////////////////////////////
			client_socket.send(str(bikePosition) + '\n') # send the data to the client
			# //////////////////////////////////////////
			time.sleep(0.5)
			#print("Location Sent")
		else:
			time.sleep(1)
			break

   
# main program
if __name__ == '__main__':

	global lon, lat
	polyVehicles = [] # Create list for number of antennas in the simulation

	# constants
	endSim = 1800000 # the simulation will be permitted to run for a total of endSim milliseconds; 1800000 milliseconds = 30 minutes
	timeout = 1 # a floating point number specified in seconds

	# initialisations
	step = 0 # time step
	d = Value('d', 0.0) # 'd' is a string containing a type code as used by the array module (where 'd' is a floating point number implemented in double in C) and 0.0 is an initial value for 'd'
	
	print
	print( '===========================')
	print( 'Beginning the main program.')
	print( '===========================')
	print	
	print( "Connecting to SUMO via TraCI.")
	print
	
	# import TraCI (to use the library, the <SUMO_HOME>/tools directory must be on the python load path)
	if 'SUMO_HOME' in os.environ:
		tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
		sys.path.append(tools)
	else:	
		sys.exit("Please declare environment variable 'SUMO_HOME'.")
		
	# compose the command line to start SUMO-GUI
	sumoBinary = "/Program Files (x86)/Eclipse/Sumo/bin/sumo-gui"
	sumoCmd = [sumoBinary, "-S", "-c", "SUMOPaint.sumo.cfg"]
	
	# start the simulation and connect to it with the python script
	traci.start(sumoCmd)
	
	x,y = traci.vehicle.getPosition("Thief") # Get position of bike thief
	lon, lat = traci.simulation.convertGeo(x,y) # Convert bike location to geo coordinates

	#print('Longitude: {} \nLatitude: {}' .format(lon, lat))
    
	manager = Manager() # create a running manager server in a separate process
	bikePosition = manager.list() # create a shared list instance on the manager server
	bikePosition.append(lon) # add an element to the list    
	bikePosition.append(lat)
	lon = 0
	lat = 0
    
	thread = Process(target=server, args=(d,bikePosition)) # represents a task (i.e. the server program) running in a subprocess
	print( "Launching the server.")
	thread.start()
	print( "The server has been launched.")
	

	while step < endSim:
		#thread.join(timeout) # implicitly controls the speed of the simulation; blocks the main program either until the server program terminates (if no timeout is defined) or until the timeout occurs	

		x,y = traci.vehicle.getPosition("Thief") # Get position of bike thief
		#lon, lat = traci.simulation.convertGeo(x,y) # Convert bike location to geo coordinates

		bikePosition[0] = lon # add an element to the list    
		bikePosition[1] = lat # add an element to the list    
		thread.join(timeout) # implicitly controls the speed of the simulation; blocks the main program either until the server program terminates (if no timeout is defined) or until the timeout occurs	


		#print('Longitude: {} \nLatitude: {}' .format(lon, lat))

		print( 'Time step [s]: {}'.format(step/1000))
		print( 'Current value of d: {}'.format(d.value))
		#print( 'Thief Location: {} {}'.format(x,y)) # Location of Bike Thief
		
  
		if (d.value == 0.8):                
			#print('Transmitting Position')    
			AppConnected = 1            
        
        
		# go to the next time step
		step += 1000 # in milliseconds
		traci.simulationStep()
        
        #////////////////////////////////////////////////////
        
        # get a list of all cars parking spaces
		n = 10 # radius to neighbours [m]
		Vehicles = traci.vehicle.getIDList() # a list of all vehicles currently in the scenario, except the bike
		VehiclesPositions = []               # a list of all vehicle Positions currently in the scenario, except the bike
		CarList = [] # list of vehicles without the bike thief
        
        # Determine if bike is within range of a cars antenna
		for i in range(len(Vehicles)):
			if Vehicles[i] != 'Thief':
				CarList.append(Vehicles[i])
				VehiclesPositions.append(traci.vehicle.getPosition(Vehicles[i]))

		for i in range(len(CarList)):
			if ((VehiclesPositions[i][0]-x)**2 + (VehiclesPositions[i][1]-y)**2 <= n**2): # i.e. if the position of a jth vehicle is on or inside a circle around the ith vehicle...
				vlon, vlat = traci.simulation.convertGeo(VehiclesPositions[i][0],VehiclesPositions[i][1])
				print('Bicycle is detected by: {}' .format(CarList[i]))
				print('At Longitude: {} \nAnd Latitude: {}' .format(vlon, vlat))
                
				if (AppConnected == 1):
					lon, lat = traci.simulation.convertGeo(VehiclesPositions[i][0],VehiclesPositions[i][1])
	
        ''' # Creates Points of interest on every vehicle except the Bike
        # get a list of all polygon parking spaces
		Vehicles = traci.vehicle.getIDList() # a list of all vehicles currently in the scenario
		CarList = [] # list of vehicles without the bike thief
        
        # Create mutable list of antenna vehicles
		for i in range(len(Vehicles)):
			if Vehicles[i] != 'Thief':
				CarList.append(Vehicles[i])	
    
       		# determine which polygon parking spaces are occupied by vehicles capable of participating in the service
		poiCounter = 1 # for visualising the geometric centres
		for i in range(len(CarList)):

			#c = random.uniform(0,1) # flip a weighted coin; returns a random floating point number r such that 0 <= r < 1
			#if c < p: # i.e. if the polygon parking space is occupied by a vehicle capable of participating...
			if len(polyVehicles) < len(CarList):
				geometricCentre = traci.vehicle.getPosition(CarList[i]) # obtain the position of the vehicles;
				traci.poi.add('poi{}'.format(poiCounter), geometricCentre[0], geometricCentre[1], (255,0,0,255), poiType='', layer=1000, imgFile='', width=1, height=1, angle=0) # for visualising the geometric centres
				polyVehicles.append(poiCounter) # for visualising the geometric centres)
			else:
				geometricCentre = traci.vehicle.getPosition(CarList[i]) # obtain the position of the vehicles;
				traci.poi.setPosition('poi{}'.format(poiCounter), geometricCentre[0], geometricCentre[1]) # for visualising the geometric centres

			poiCounter += 1 # for visualising the geometric centres
			#traci.poi.setColor(Vehicles[i],(118,32,176,255)) # purple, i.e. Switched Off
		'''
        
    
	print( "Shutting the server down.")
	thread.terminate()	
	print( "Closing the main program. Goodbye.")
	traci.close() # close the connection to SUMO