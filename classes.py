# ----------------------------- #
# ---------- CLASSES ---------- #
# ----------------------------- #

from __future__ import division

# libs #
import queue
import math
import heapq
from numpy.random import randint
from numpy.random import exponential
from numpy.random import binomial

# print formatting #
from tabulate import tabulate

# my libs #
from init import Init as init

class Node(object):

	def __init__( self, x, y, nodeId ):
		self.nodeId 	= nodeId
		self.x 			= x
		self.y 			= y
		self.neighbours = []
		self.queue 		= queue.Queue( init.QUEUE_SIZE )
		self.status 	= 'idle'

		# collision handling
		self.occupiedUntil 			= -1
		self.occupiedTransmittingUntil = -1
		self.lastIdleTransmission 	= None

		# distribution inter arrival time
		self.lastPrepareTransmission = 0

		# stats
		self.colliding 				= 0
		self.sendCollision 		= [ 0, 0 ]
		self.receiveCollision = [ 0, 0 ]
		self.sendGeneral 			= [ 0, 0 ]
		self.receiveGeneral  	= [ 0, 0 ]
		self.losses 					= [ 0, 0 ]
		self.load          		= [ 0, 0 ]

	def __str__(self):
		return 	"NODE id:%s occupiedUntil:%s neighbour:%s" % (self.nodeId, self.occupiedUntil, self.stampNeighbours())

	def __addNeighbour( self, neighbour ):
		self.neighbours.append( neighbour )

	def __isNeighbour( self, neighbour ):
		distance = math.hypot(self.x-neighbour.x, self.y-neighbour.y)
		if (distance <= init.BOUNDS):
			return 1
		return 0

	def getId( self ):
		return self.nodeId

	def __isMe( self, nodeId ):
		return self.nodeId == nodeId

	def findNeighbours( self, nodes ):
		for node in nodes:
			if self.__isNeighbour( node ) and not self.__isMe( node.getId() ):
				self.__addNeighbour( node )

	def stampNeighbours( self ):
		str_neighbours = ""
		for n in self.neighbours:
			str_neighbours += str(n.nodeId)+" "
		return str_neighbours

	def updateLoad( self, transmission ):
		self.load[0] += 1
		self.load[1] += transmission.size

	# metodi di transmissione
	def updateLastPrepareTransmission( self, time ):
		self.lastPrepareTransmission = time

	def isIdleAtTime( self, time ):
		return self.occupiedUntil < time

	def canTransmit( self, time ):
		
		if( self.isIdleAtTime( time ) ):
			return 1
		else :
			# allow transmission happening at the same point in time
			# receiving from another node and transmitting at the same time
			t_last = self.lastIdleTransmission
			if( self.getStatus()!="transmitting" and t_last and t_last.startTime == time and not self.__isMe( t_last.nodeId ) ):
				# collision!! I'm receiving and transmitting at the same point in time. Cannot prevent it :(
				return 1
			return 0

	def addToQueue( self, transmission ):
		if( not self.__queueIsFull() ):
			self.queue.put_nowait( transmission )
		else:
			self.losses[0] += 1
			self.losses[1] += transmission.size

	def getFromQueue( self, wakeUp ):
		transmission = self.queue.get_nowait()
		transmission.resetTime( wakeUp.startTime )
		return transmission

	def queueIsEmpty( self ):
		return self.queue.empty()

	def __queueIsFull( self ):
		return self.queue.full()

	# status
	def setStatus( self, status ):
		self.status = status

	def getStatus( self ):
		return self.status

	def removeSendedTransmission(self, t):
		if( init.VERBOSE ):
			print("update send stats of node: ", self.getId(), " removing ", t.size, "bytes")
		self.sendCollision[0] += 1
		self.sendCollision[1] += t.size

	def removeReceivedTransmission( self, t ):
		if( init.VERBOSE ):
			print("update received stats of node: ", self.getId(), " removing ", t.size, "bytes from node ", t.nodeId)
		self.receiveCollision[0] += 1
		self.receiveCollision[1] += t.size

	def isColliding( self ):
		return self.colliding

	def getLastIdleTransmission( self ):
		return self.lastIdleTransmission

	def transmit( self, t ):
		if( not self.isIdleAtTime( t.startTime ) ):
			# collision. Transmitting and receiving at the same time
			self.colliding = 1
		else:
			self.colliding = 0
			self.lastIdleTransmission = t
		self.status = "transmitting"
		self.occupiedTransmittingUntil = t.endTime

		self.sendGeneral[0] += len(self.neighbours)
		self.sendGeneral[1] += t.size * len(self.neighbours)
		self.setOccupiedTime( t.endTime )

	def receive( self, t ):
		self.receiveGeneral[0] += 1
		self.receiveGeneral[1] += t.size

		if(self.status == "idle"):
			self.status = "receiving"

		if( not self.isIdleAtTime( t.startTime ) ):
			self.colliding = 1
		else:
			self.colliding = 0
			self.lastIdleTransmission = t

		self.setOccupiedTime( t.endTime )

	def setOccupiedTime( self, end ):
		if( end > self.occupiedUntil ):
			self.occupiedUntil = end

	def updateStateAtTime( self, time ):
		if( self.isIdleAtTime(time) ):
			self.status = "idle"
			self.colliding = 0
		elif( self.occupiedTransmittingUntil < time ):
			# if not transmitting then i'm busy receiving
			self.status = "receiving"

	# clear
	def clear( self ):
		self.queue = queue.Queue( init.QUEUE_SIZE )
		self.status = 'idle'

		# collision handling
		self.occupiedUntil = -1
		self.lastIdleTransmission = None

		# distribution inter arrival time
		self.lastPrepareTransmission = 0

		# stats
		self.colliding 				= 0
		self.sendCollision 		= [ 0, 0 ]
		self.receiveCollision = [ 0, 0 ]
		self.sendGeneral 			= [ 0, 0 ]
		self.receiveGeneral 	= [ 0, 0 ]
		self.losses 					= [ 0, 0 ]
		self.load          = [ 0, 0 ]

	def as_dict( self ):
		return {
			"nodeId": self.nodeId,
			"x": self.x,
			"y": self.y,
			"occupiedUntil": self.occupiedUntil,
			"isColliding": self.colliding,
			"sendGeneral": self.sendGeneral[1],
			"sendCollision": self.sendCollision[1],
			"queueSize": self.queue.qsize(),
			"neighbours": [node.getId() for node in self.neighbours],
			"status": self.status
		}


class NodeController(object):
	def __init__( self ):
		self.points = init.DEBUG_POINTS if init.DEBUG else init.POINTS
		self.nodes 	= []

	def __str__(self):
		header = ['Id', 'state', 'sendCol', 'recCol', 'sendGen', 'recGen', 'losses']
		infos = []
		for node in self.nodes :
			sendReal = node.sendGeneral[1] - node.sendCollision[1]
			info = [ node.nodeId, node.status, node.sendCollision, node.receiveCollision, node.sendGeneral, node.receiveGeneral, node.losses ]
			infos.append( info )

		if( init.VERBOSE ):
			print(tabulate( infos, headers=header, tablefmt='orgtbl' ))
		return "-----------"

	def createNodes( self ):
		for nodeId, point in enumerate(self.points):
			node = Node( point[0], point[1], nodeId )
			self.nodes.append( node )

	def findAllNeighbours( self ):
		for node in self.nodes:
			node.findNeighbours( self.nodes )

		if( init.VERBOSE ):
			for node in self.nodes:
				print( node )
				node.stampNeighbours( )

	def getNodes( self ):
		return self.nodes

	def getNode( self, nodeId ):
		return self.nodes[nodeId]

	def getDictNodes( self ):
		return [node.as_dict() for node in self.nodes]

	def clear( self ):
		for node in self.nodes:
			node.clear()


class Transmission(object):
	def __init__( self, node, gamma, lastPrepareTransmission ):
		self.size = self.__calculateSize()
		self.duration = self.__getDuration()
		self.startTime = lastPrepareTransmission + self.__getStart( gamma )
		self.endTime = self.startTime + self.duration
		self.node = node
		self.nodeId = node.nodeId
		self.type = "standard"

	def __str__(self):
		return 	"<TRANSMISSION node:%s start:%s end:%s d:%s>" % (self.nodeId, self.startTime, self.endTime, self.size)

	def __calculateSize( self ):
		size = binomial(init.N, init.P) + init.MIN_SIZE
		return size if size <= init.MAX_SIZE else init.MAX_SIZE

	def __getDuration( self ):
		return self.size / init.SPEED

	def __getStart( self, gamma ):
		return exponential( gamma )

	def resetTime( self, time ):
		self.startTime = time
		self.endTime = self.startTime + self.duration

	def __lt__(self, other):
		return self.startTime < other.startTime

	def as_dict(self):
		return {
			"size": self.size,
			"duration": self.duration,
			"startTime": self.startTime,
			"endTime": self.endTime,
			"nodeId": self.nodeId,
			"type": self.type
		}

class FakeTransmission( Transmission ):
	def __init__( self, node, startTime ):
		self.size = 1
		self.duration = 1
		self.startTime = startTime + self.getRandomDelay()
		self.endTime = self.startTime + 0.01
		self.node = node
		self.nodeId = node.nodeId
		self.type = "wakeUp"

	def __lt__(self, other):
		return self.startTime < other.startTime

	def __str__(self):
		return 	"<WAKEUP_EVENT node:%s start:%s>" % (self.nodeId, self.startTime)

	def getRandomDelay(self):
		#i = randint(10000) / 1000000
		#i += 0.001
		#return i

		# not random for our implementation!
		return 0.00000000001

	def as_dict(self):
		return {
			"size": self.size,
			"duration": self.duration,
			"startTime": self.startTime,
			"endTime": self.endTime,
			"nodeId": self.nodeId,
			"type": self.type
		}

class DebugTransmission( Transmission ):

	def __init__( self, node ):
		conta = init.DEBUG_COUNT[node.nodeId]
		if conta < len(init.DEBUG_TRANSMISSION[node.nodeId]):
			data = init.DEBUG_TRANSMISSION[node.nodeId][conta]

			self.size = data[1]
			self.duration = self.__getDuration()
			self.startTime = data[0]
			self.endTime = self.startTime + self.duration
			self.node = node
			self.nodeId = node.nodeId
			self.type = "debug"

			# update debug counter
			init.DEBUG_COUNT[node.nodeId] += 1
		else:
			# out of MAX_TIME: will be ignored
			self.startTime = init.MAX_TIME + 10
			self.endTime = init.MAX_TIME + 100

	def __str__(self):
		return 	"<TRANSMISSION node:%s start:%s end:%s size:%s>" % (self.nodeId, self.startTime, self.endTime, self.size)

	def __getDuration( self ):
		return self.size / init.SPEED

	def resetTime( self, time ):
		self.startTime = time
		self.endTime = self.startTime + self.duration

	def as_dict(self):
		return {
			"size": self.size,
			"duration": self.duration,
			"startTime": self.startTime,
			"endTime": self.endTime,
			"nodeId": self.nodeId,
			"type": self.type
		}

class TransmissionController(object):
	def __init__( self, gamma ):
		self.gamma = gamma
		self.transmissionList = []
		return

	def prepareTransmission( self, node ):
		if( not init.DEBUG ):
			t = Transmission( node, self.gamma, node.lastPrepareTransmission )
		else:
			t = DebugTransmission( node )

		if(t.endTime < init.max_time(self.gamma)):
			node.updateLoad( t )
			node.updateLastPrepareTransmission( t.startTime )

			# la aggiungo alla coda
			self.addTransmission( t )

	def prepareWakeUp( self, node ):
		if( init.VERBOSE ):
			print("node to wakeup: %s" % node)
		t = FakeTransmission( node, node.occupiedUntil )
		
		# la aggiungo alla coda
		self.addTransmission( t )

	def getAllTransmission( self ):
		return self.transmissionList

	def addTransmission( self, transmission ):
		heapq.heappush( self.transmissionList, ( transmission.startTime, transmission ) )

	def popTransmission( self ):
		obj = heapq.heappop( self.transmissionList )
		return obj[1]

	def isEmpty( self ):
		return self.transmissionList == []

	def getDictTransmission( self ):
		return [task[1].as_dict() for task in self.transmissionList]


class Simulator(object):
	def __init__( self, nodeCtrl, transmissionCtrl, gamma ):
		self.nodeCtrl = nodeCtrl
		self.transmissionCtrl = transmissionCtrl
		self.timer = 0
		self.gamma = gamma

	def initialize( self ):
		for node in self.nodeCtrl.nodes:
			self.transmissionCtrl.prepareTransmission( node )

	def updateNodesStatus(self, time):
		for node in self.nodeCtrl.nodes:
			node.updateStateAtTime( time )

	def step( self ):

		status = ''

		t = self.transmissionCtrl.popTransmission()
		node = t.node
		connectionType = t.type

		self.updateNodesStatus(t.startTime)

		if( node.canTransmit( t.startTime ) ):
			status = "transmitting"

			if( connectionType == "wakeUp" ):
				# override with transmission in the queue
				status = "wakeup - "+status
				t = node.getFromQueue( t )

			if( not node.isIdleAtTime(t.startTime) ):
				# transmitting while receiving
				if( not node.isColliding() ):
					# invalidate previous transmission
					tLast = node.getLastIdleTransmission()
					tLast.node.removeSendedTransmission( tLast )
					node.removeReceivedTransmission( tLast )
			node.transmit( t )

			if( connectionType == "wakeUp" and not node.queueIsEmpty() ):
					self.transmissionCtrl.prepareWakeUp( node )

			neighbours = node.neighbours
			for neighbour in neighbours:
				if( not neighbour.isIdleAtTime( t.startTime ) ):
					node.removeSendedTransmission( t )
					neighbour.removeReceivedTransmission( t )
					if( not neighbour.isColliding() and neighbour.getStatus()=="receiving"):
						tLast = neighbour.getLastIdleTransmission()
						tLast.node.removeSendedTransmission( tLast )
						neighbour.removeReceivedTransmission( tLast )
				neighbour.receive(t)
		else:
			status = "cannot transmit: delay"
			if( node.queueIsEmpty() or (connectionType == "wakeUp" and not node.queueIsEmpty()) ):
				# add a fake transmission to retry later
				self.transmissionCtrl.prepareWakeUp( node )

			if( connectionType != "wakeUp" ): # if not already in the queue
				node.addToQueue( t )

		if( init.VERBOSE ):
			print(status)
			print(t)
			print( self.nodeCtrl )

		# add next transmission for node: <node> if it was not a wakeup event
		if( connectionType != "wakeUp" ):
			self.transmissionCtrl.prepareTransmission( node )

		return (status, t)

	def finish( self ):
		# check if simulation is finished
		if(self.transmissionCtrl.isEmpty()):
			return 1
		t = self.transmissionCtrl.transmissionList[0][1]
		# if next transmission is out of MAX_TIME then stop simulation
		return t.endTime > init.max_time(self.gamma)

class StatsController(object):

	def __init__( self, file ):
		# open file to save statistics
		self.fileNode = open( file+"_nodes.csv", "w" )

		# headers
		self.fileNode.write( 'gamma,repetition,node,simTime,numNodes,offered,sent,load,losses,percSuccess\n' )

	def process( self, nodeCtrl, gamma, repetition ):
		statsNode = []
		for node in nodeCtrl.nodes:

			perc = node.sendGeneral[1] - node.sendCollision[1]
			if( perc > 0 ):
				perc = perc / node.sendGeneral[1]
			else:
				perc = 0

			sendReal = node.sendGeneral[1] / len(node.neighbours)
			sendCorrect = sendReal * perc
			time = init.max_time(gamma)

			statsNode = [
				gamma,
				repetition,
				node.nodeId,
				time,
				len(init.POINTS),
				sendReal,
				sendCorrect,
				node.load[1],
				node.losses[1],
				perc
			]

			self.fileNode.write( ",".join(str(x) for x in statsNode) )
			self.fileNode.write( '\n' )

	def close( self ):
		self.fileNode.close()
