from classes import NodeController
import matplotlib.pyplot as plt

def plotNodeAndEdges(node):
  plt.figure(1, figsize = (6,6))
  axes = plt.gca()
  axes.set_xlim([0,1])
  axes.set_ylim([0,1])
  for neighbour in node.neighbours:
    if neighbour.getId() > node.getId():
      x = (node.x, neighbour.x)
      y = (node.y, neighbour.y) 
      plt.plot(x, y, color='gray')
  plt.plot(node.x, node.y, 'o', color='black')
  space_x = 0.01 if (node.x < 0.5) else -0.02
  plt.text(node.x + space_x, node.y + 0.02 , node.getId(), fontsize=12)

nodeCtrl = NodeController()
nodeCtrl.createNodes()
nodeCtrl.findAllNeighbours()

nodes = nodeCtrl.getNodes()
for node in nodes:
  plotNodeAndEdges(node)

plt.show()