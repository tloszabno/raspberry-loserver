
init:
	sudo pip install -r requirements.txt

init2:
	sudo pip2.7 install -r requirements.txt


test:
	nosetests

test2:
	nosetests-2.7


run:
	sudo python2 loserver/app.py


run-mocked:
	sudo python2 loserver/app.py --mocked


clean:
	find . -name "*.pyc" -exec rm -rf {} \;


.PHONY: init test clean
