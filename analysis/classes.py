from scipy.stats import binom
from scipy.stats import expon
import matplotlib.pyplot as plt
import matplotlib.markers as mmark
import matplotlib
import numpy as np

# setting network
meanPacketSize = binom.mean(n=7111, p=0.843, loc=0) + 32
convertMegabyte = 0.000001
N = 10
CAPACITY = 1000000
maxLoad = CAPACITY * N

# setting graphs
font = {'size'   : 14}
fontLeg = {'fontsize': 11}

matplotlib.rc('font', **font)
matplotlib.rc('legend', **fontLeg)

class StatsHandler(object):
  def __init__(self, data):
    self.subsets = data
    self.rate = []
    self.load = []
    self.computedLoad = []
    self.offered = []
    self.throughput = []
    self.lost = []
    self.collided = []
    self.throughputNodes = []
    self.nodes_stats = []
    self.perc = []

  def getRate(self):
    return self.rate

  def getLoad(self): 
    return self.load

  def getComputedLoad(self): 
    return self.computedLoad

  def getOffered(self): 
    return self.offered

  def getThroughput(self): 
    return self.throughput

  def getLost(self): 
    return self.lost

  def getCollided(self): 
    return self.collided

  def getThroughputNodes(self): 
    return self.throughputNodes

  def getNodesStats(self): 
    return self.nodes_stats

  def getPers(self):
    return self.perc

  def computeSomeStats(self):
    for subset in self.subsets:
      rate = float(subset[0]["rate"])
      i_load = loadFromRate(rate)
      self.load.append(i_load*convertMegabyte)

      # compute packet lost
      # loosing = splitInt(subset, "loosing")
      # loosing_rate = column(loosing[1], "prob")
      # print(loosing_rate)
      # loss = float(np.sum(loosing_rate))

      states = split(subset, "state")
      transmitting_rate = columnFusion(states[0], "prob", "transmitting")
      colliding_rate = columnFusion(states[1], "prob", "transmitting")
      offered_rate = columnFusion(subset, "prob", "transmitting")

      transmitting = float(np.sum(transmitting_rate))
      colliding = float(np.sum(colliding_rate))
      offered = float(np.sum(offered_rate))

      total = transmitting + colliding
      self.throughput.append(transmitting*CAPACITY*convertMegabyte)
      self.offered.append(offered*CAPACITY*convertMegabyte)
      self.collided.append(colliding*CAPACITY*convertMegabyte)
      #self.lost.append(loss)

  def computeStats(self):
    for i,v in enumerate([0] * N):
      self.nodes_stats.append([])

    for idx, subset in enumerate(self.subsets):

      # load esperimental parameters
      gamma   = float(subset[0]["gamma"])
      simTime = float(subset[0]["simTime"])
      numNodes = int(subset[0]["numNodes"])
      
      repetition = countDistinct(subset, "repetition")

      byteOffered = column(subset, "offered")
      byteSent    = column(subset, "sent")
      byteLoad    = column(subset, "load")
      percSuccess = column(subset, "percSuccess")
      byteLost    = column(subset, "losses")
      
      i_load        = sum(byteLoad)/simTime/repetition*convertMegabyte
      i_throughput  = sum(byteSent)/simTime/repetition*convertMegabyte
      i_offered     = sum(byteOffered)/simTime/repetition*convertMegabyte
      i_lost        = sum(byteLost)/simTime/repetition*convertMegabyte
      i_collided    = i_offered - i_throughput
      i_correctP    = avg(percSuccess)

      i_computedLoad = meanPacketSize / expon.mean(loc=0, scale=gamma) * numNodes * convertMegabyte

      self.rate.append(1/gamma)
      self.load.append(i_load)
      self.computedLoad.append(i_computedLoad)
      self.offered.append(i_offered)
      self.throughput.append(i_throughput)
      self.lost.append(i_lost)
      self.collided.append(i_collided)
      self.perc.append(i_correctP)
      self.throughputNodes.append([sent/simTime for sent in byteSent])

      print(gamma, " - p:", meanPacketSize, " > ", i_load, " = ", i_computedLoad)

      # add offered load statistic for every node to undestand network topology behaviour
      subset_nodes = splitInt(subset, "node")
      for n, sub in enumerate(subset_nodes):
        byteOffered = column(sub, "offered")
        percSuccess = column(sub, "percSuccess")

        n_offered = avg(byteOffered)/simTime*convertMegabyte
        p = avg(percSuccess)
        self.nodes_stats[n].append(n_offered)


def split(data, index):
  subsets = []
  value = "*_"
  num = -1
  for row in data:
    if(value!=row[index]):
      value = row[index]
      num = num + 1
      subsets.append([])
    subsets[num].append(row);
  return subsets

def splitInt(data, index):
  subsets = []
  cMax = -1
  for row in data:
    num = int(row[index])
    if(num > cMax):
      cMax = num
      subsets.append([])
    subsets[num].append(row);
  return subsets

def columnFusion(data, index, multiplier):
  d = column(data, index)
  m = column(data, multiplier)
  return [a*b for a,b in zip(d,m)]

def column(data, index):
  columnValues = []
  for row in data:
    columnValues.append(float(row[index]))
  return columnValues

def countDistinct(data, index):
  columnValues = []
  oldValue = ""
  count = 0
  for row in data:
    value = float(row[index])
    if(value != oldValue):
      count = count+1
      oldValue = value
  return int(count)

def avg(data):
  return sum(data) / float(len(data))

def sumAvg(data):
  subdata = splitInt(data, "repetition")
  return sum(data)/float(len(subdata))

def plotMultiple(x, data_y, xLabel, yLabel):
  plt.figure()
  label = []
  markers = ["s", "|", "|", "*", "^", "o", "|", "x", "^", "|"]
  ls = ["--", "-", ":", ":", "--", "-", "--", "-", ":", "-"]
  sizes = [5, 7, 7, 7, 7, 5, 7, 7, 7, 7]
  plots = []
  for i,y in enumerate(data_y):
    label.append("node"+str(i))
    j = i%len(markers)
    p = plt.plot(x, y, marker=markers[j], markersize=sizes[j], ls=ls[j], label="node"+str(i))
    plots.append(p)
  plt.xlabel(xLabel)
  plt.ylabel(yLabel)

  plt.legend(loc='best')

def plotCompare(x1, y1, x2, y2, xLabel, yLabel):
  plt.figure()
  plt.plot(x1, y1, marker="o", markersize=5, ls="-", label="model")
  plt.plot(x2, y2, marker="s", markersize=5, ls=":", label="simulation")
  plt.xlabel(xLabel)
  plt.ylabel(yLabel)

  plt.legend(loc='best')

def plotLine(x, y, xLabel, yLabel):
  plt.figure()
  plt.plot(x, y, marker='o', markersize=5)
  plt.xlabel(xLabel)
  plt.ylabel(yLabel)

def plotThreeLine(x, y1, y2, y3, xLabel, yLabel):
  plt.figure()
  
  plt.plot([0, max(x)], [50, 50], color="gray", lw=.5)
  p1 = plt.plot(x, [x*100 for x in y1], marker='o', markersize=5, ls='-', color="orange", label="sended")
  p2 = plt.plot(x, [x*100 for x in y2], marker='o', markersize=5, ls='--', color="red", label="lost")
  p3 = plt.plot(x, [x*100 for x in y3], marker='x', markersize=5, ls=':', color="green", label="correctly sended")

  plt.xlabel(xLabel)
  plt.ylabel(yLabel)

  plt.legend(loc='best')

def plotSpecial(x_values, y_values):
  fig, ax = plt.subplots()
  # i=0
  # for y in y_values:
  #   median = min(y)
  #   plt.plot(x_values[i], median, 'o')
  #   i=i+1

  #plt.boxplot(y_values, positions=x_values)
  x = [round(x/1000000,1) for x in x_values]
  ax.boxplot(y_values, positions=x)

  x_labels = []
  last_x = 0
  for x_i in x:
    if(x_i > (last_x + 5) or x_i < (last_x - 5)):
      x_labels.append(x_i)
      last_x = x_i
    else:
      x_labels.append("")


  ax.set_xticklabels(x_labels)

def plotThroughput(load, throughput):
  x = load
  y = [y/x*100 for x,y in zip(load, throughput) ]
  plotLine(x, y, 'load', '% throughput')

def loadFromRate(rate):
  arrival_time = 1/rate
  return 6026 / arrival_time * 10

def show():
  return plt.show()
