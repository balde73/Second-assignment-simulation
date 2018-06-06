from classes import NodeController
from classes import TransmissionController
from classes import StatsController
from classes import Simulator
import sys
from init import Init as init
from font import colors

syms = ['\\', '|', '/', '-']
bs = '\b'
fileName = 'stats'

def main():

	init.config()
	statsCtrl = StatsController( fileName )

	nodeCtrl = NodeController()
	nodeCtrl.createNodes()
	nodeCtrl.findAllNeighbours()

	print("> Inizio simulazione ")

	for gamma in init.GAMMA:
		print("\b> "+str(gamma)+" ")
		for a in range(0, init.SIMULATION_REPETITION):

			transmissionCtrl = TransmissionController( gamma )

			simulation = Simulator( nodeCtrl, transmissionCtrl, gamma )
			simulation.initialize()

			while( not simulation.finish() ):
				simulation.step()

			statsCtrl.process( nodeCtrl, gamma, a )
			nodeCtrl.clear();

			sys.stdout.write("\b%s" % syms[ a % len(syms) ])
			sys.stdout.flush()

	print("\b" + colors.OKGREEN + "Simulazione conclusa" + colors.ENDC)
	print("Ho creato il file: " + colors.OKGREEN + fileName + ".svg" + colors.ENDC)
	print("Ho creato il file: " + colors.OKGREEN + fileName + "-nodes.svg" + colors.ENDC)

if __name__ == "__main__":
	main()
