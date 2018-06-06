import csv
import classes as dh
from classes import StatsHandler

try:
  with open('stats_nodes.csv', "r") as f:
    reader = csv.DictReader( f )
    subsets = dh.split(reader, "gamma")
except:
  print('oops! no ./stats_node.csv file found! Exit')
  exit()

sim = StatsHandler(subsets)
sim.computeStats()

#plotLine(rate, load, "rate", "avg offered load")
#plotMultiple(load, nodes_stats, "avg load", "avg offered throughput")
#plotThroughput(load, throughput)

dh.plotLine(sim.getRate(), sim.getComputedLoad(), "rate", "total load (MB/s)")
#plotSpecial(sim.getComputedLoad(), sim.getThroughputNodes())
dh.plotMultiple(sim.getComputedLoad(), sim.getNodesStats(), "total load (MB/s)", "offered throughput (MB/s)")
dh.plotLine(sim.getComputedLoad(), sim.getOffered(), "total load (MB/s)", "total offered throughput (MB/s)")
dh.plotLine(sim.getComputedLoad(), sim.getThroughput(), "total load (MB/s)", "total actual throughput (MB/s)")
dh.plotThreeLine(sim.getComputedLoad(),
  [a/b if b else 0 for a,b in zip(sim.getOffered(), sim.getComputedLoad())],
  [a/b if b else 0 for a,b in zip(sim.getLost(), sim.getComputedLoad())],
  [a/b if b else 0 for a,b in zip(sim.getThroughput(), sim.getComputedLoad())], "total load (MB/s)", "rate %")

try:
  with open('./model/data/output.csv', "r") as f:
    reader = csv.DictReader( f )
    subsets = dh.split(reader, "rate")
except:
  print('oops! no ./model/data/output.csv file found')
  plt.show()
  exit()

loads = []
m_throughput = []
m_colliding = []

model = StatsHandler(subsets)
model.computeSomeStats()

dh.plotCompare(model.getLoad(), model.getThroughput(), sim.getComputedLoad(), sim.getThroughput(), "total load (MB/s)", "total actual throughput (MB/s)")
dh.plotCompare(model.getLoad(), [a/b if b else 0 for a,b in zip(model.getCollided(), model.getOffered())],
               sim.getComputedLoad(), [a/b if b else 0 for a,b in zip(sim.getCollided(), sim.getOffered())], "total load (MB/s)", "collision rate %")
#plotCompare(loads, m_colliding, sim.getComputedLoad(), [x/y for x,y in zip(sim.getCollided(), sim.getComputedLoad())])
#dh.plotCompare(model.getLoad(), model.getLost(),
#  sim.getComputedLoad(), [a/b if b else 0 for a,b in zip(sim.getLost(), sim.getComputedLoad())], "", "")

dh.plotCompare(model.getLoad(), [a/b if b else 0 for a,b in zip(model.getThroughput(), model.getLoad())],
  sim.getComputedLoad(), [a/b if b else 0 for a,b in zip(sim.getThroughput(), sim.getComputedLoad())], "", "")


dh.show()
