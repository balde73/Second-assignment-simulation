from classes import NodeController
from classes import TransmissionController
from classes import StatsController
from classes import Simulator
from classes import Transmission
import sys
from init import Init as init
from font import colors

from flask import render_template, jsonify
from flask import Flask
import webbrowser

syms = ['\\', '|', '/', '-']
bs = '\b'
fileName = 'stats'

number = 0

init.config()
#statsCtrl = StatsController( fileName )

nodeCtrl = NodeController()
nodeCtrl.createNodes()
nodeCtrl.findAllNeighbours()

print("> Inizio simulazione")

gamma = 0.005

transmissionCtrl = TransmissionController( gamma )
simulation = Simulator( nodeCtrl, transmissionCtrl, gamma )
simulation.initialize()

webbrowser.open('http://127.0.0.1:5000/', new=0)

app = Flask('testapp')

@app.route('/')
def hello():
  return render_template('index.html', data = number)

@app.route('/_init', methods= ['GET'])
def init():
  transmissions = transmissionCtrl.getDictTransmission()
  nodes = nodeCtrl.getDictNodes()
  return jsonify(nodeCtrl = transmissions, nodes = nodes)

@app.route('/_stuff', methods= ['GET'])
def stuff():
  elem = ''
  if(not simulation.finish()):
    elem = simulation.step()
    nodes = nodeCtrl.getDictNodes()
    transmissions = transmissionCtrl.getDictTransmission()
    print(elem)
    return jsonify(data = elem[0], t = elem[1].as_dict(), nodeCtrl = transmissions, nodes = nodes)
  print("finish")
  return jsonify(data = {}, t = {}, nodeCtrl = {}, nodes = {})


@app.route('/_reset', methods= ['GET'])
def reset():
  transmissionCtrl = TransmissionController( gamma )
  simulation = simulationLine( nodeCtrl, transmissionCtrl )
  simulation.initialize()

if __name__ == "__main__":
  app.run(debug=True)
