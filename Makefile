
init:
	sudo pip install -r requirements.txt

test:
	nosetests

run:
	sudo python2 loserver/app.py

clean:
	find . -name "*.pyc" -exec rm -rf {} \;


.PHONY: init test clean
