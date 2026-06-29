.PHONY: test package

test:
	PYTHONPATH=addon python3 -m unittest discover -s tests
	python3 -m compileall addon tests

package:
	python3 scripts/package_addon.py
