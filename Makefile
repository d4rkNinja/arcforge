.PHONY: test doctor package

test:
	python -m unittest discover -s tests -p 'test_*.py' -v

doctor:
	python scripts/doctor.py

package:
	python scripts/build_package.py
