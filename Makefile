.PHONY: test

test:
	PYTHONPATH=addon python3 -m unittest discover -s tests
	python3 -m compileall addon tests
