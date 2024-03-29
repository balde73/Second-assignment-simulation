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
sim.compute_stats()

dh.plot_line(sim.get_rate(), sim.get_computed_load(), "rate", "total load (MB/s)")
dh.plot_multiple(sim.get_computed_load(), sim.get_nodes_stats(), "total load (MB/s)", "offered throughput (MB/s)")
dh.plot_line(sim.get_computed_load(), sim.get_offered(), "total load (MB/s)", "total offered throughput (MB/s)")
dh.plot_line(sim.get_computed_load(), sim.get_throughput(), "total load (MB/s)", "total actual throughput (MB/s)")
dh.plot_four_line(sim.get_computed_load(),
  [a/b if b else 0 for a,b in zip(sim.get_offered(), sim.get_computed_load())],
  [a/b if b else 0 for a,b in zip(sim.get_lost(), sim.get_computed_load())],
  [a/b if b else 0 for a,b in zip(sim.get_throughput(), sim.get_offered())],
  [a/b if b else 0 for a,b in zip(sim.get_collided(), sim.get_offered())], "total load (MB/s)", "rate %")

try:
  with open('model.csv', "r") as f:
    reader = csv.DictReader( f )
    subsets = dh.split(reader, "rate")
except:
  print('oops! no model.csv file found')
  plt.show()
  exit()

loads = []
m_throughput = []
m_colliding = []

model = StatsHandler(subsets)
model.compute_some_stats()

dh.plot_compare(model.get_load(), model.get_throughput(), sim.get_computed_load(), sim.get_throughput(), "total load (MB/s)", "total actual throughput (MB/s)")
dh.plot_compare(model.get_load(), [a/b*100 if b else 0 for a,b in zip(model.get_collided(), model.get_offered())],
               sim.get_computed_load(), [a/b*100 if b else 0 for a,b in zip(sim.get_collided(), sim.get_offered())], "total load (MB/s)", "collision rate %")

dh.plot_compare(model.get_load(), [a/b*100 if b else 0 for a,b in zip(model.get_throughput(), model.get_load())],
  sim.get_computed_load(), [a/b*100 if b else 0 for a,b in zip(sim.get_throughput(), sim.get_computed_load())], "total load (MB/s)", "success rate %")


dh.show()
