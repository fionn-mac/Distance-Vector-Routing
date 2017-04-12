from __future__ import print_function
from sys import argv
import csv
import threading
import time
import socket
import datetime
import json

class nodeThread(threading.Thread):
	def __init__(self, threadID, table, neigh):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.table = table
		self.neigh = neigh
		self.result = 0
		self.port = 65505
		self.close = True

	def updateRow(self, newRow, verNum):
		if self.table[newRow[0]-1][1] > self.table[int(verNum)-1][1] + newRow[1]:
			self.table[newRow[0]-1][1] = self.table[int(verNum)-1][1] + newRow[1]
			self.table[newRow[0]-1][2] = verNum
	
	def end(self):
		self.close = False
		
		UDPSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		UDPSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		host = ''
		address = (host, self.port + self.threadID)
		UDPSocket.sendto("End", address)
		UDPSocket.close()

	def printTable(self):
		f.write(str(nVertices-1) + " ")
		for i in xrange(nVertices):
			if i != self.threadID-1:
				f.write(str(i+1) + " " + str(self.table[i][1]) + " ")

		f.write("\n")
		return

	def run(self):
		while(self.close):
			host = ''
			UDPSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			UDPSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			UDPSocket.bind((host, self.port + self.threadID))
			bufferSize = 1024
			recvNode , address = UDPSocket.recvfrom(bufferSize)
			
			if recvNode == "End":
				return
			
			for k in xrange(nVertices):
				message , address = UDPSocket.recvfrom(bufferSize)
				self.updateRow(json.loads(message), int(recvNode))

	def send(self):
		UDPSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		UDPSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		host = ''

		for i in xrange(1, 6):
			address = (host, self.port + i)
			if i in self.neigh:
				UDPSocket.sendto(str(self.threadID), address)
				time.sleep(0.00001)
				for k in xrange(nVertices):
					UDPSocket.sendto(json.dumps(self.table[k]), address)
					time.sleep(0.00001)

		UDPSocket.close()

inp = []
with open(argv[1], 'r') as file:
	read = csv.reader(file, delimiter = ' ')
	for row in read:
		text = row
		inp.append(text)

nVertices = int(inp[0][0])

routingInfo = []
neighbours = [[] for i in xrange(nVertices)]

for i in xrange(nVertices):
	vertexInfo = []
	for j in xrange(nVertices):
		if i == j:
			vertexInfo.append([j+1, 0, j+1])
		else:
			vertexInfo.append([j+1, 10000000, j+1])
	routingInfo.append(vertexInfo)

for i in xrange(nVertices):
	nEdges = int(inp[i+1][0])
	for j in xrange(nEdges):
		routingInfo[i][int(inp[i+1][2*j+1])-1][0] = int(inp[i+1][2*j+1])
		routingInfo[i][int(inp[i+1][2*j+1])-1][1] = int(inp[i+1][2*j+2])
		neighbours[int(inp[i+1][2*j+1])-1].append(i+1)

threadNum = [0 for i in xrange(nVertices)]

for i in xrange(nVertices):
	threadNum[i] = nodeThread(i+1, routingInfo[i], neighbours[i])
	threadNum[i].start()

for i in xrange(nVertices-1):
	for j in xrange(nVertices):
		threadNum[j].send()

f = open("out", 'wb')
f.write(str(nVertices) + "\n")
for i in xrange(nVertices):
	threadNum[i].printTable()
f.close()

for i in xrange(nVertices):
	threadNum[i].end()
	threadNum[i].join()
