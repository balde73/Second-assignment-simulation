prepare:
	sudo apt-get install python3
	sudo apt-get install python3-pip

install:
	pip3 install -r requirements.txt

start:
	python3 main.py

start-default:
	python3 main.py

start-beautiful:
	python3 main_web.py

start-analysis:
	python3 analysis

start-and-plot:
	python3 code.py

.PHONY : all
