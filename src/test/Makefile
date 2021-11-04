all: test_jenkins

test_jenkins:
	pytest --junitxml=${WORKSPACE}/offline/test/test-results.xml -v -s ${WORKSPACE}/offline/test

test:
	pytest -v -s .

coverage:
	coverage run --source . $$(which pytest) ~/code/s1/offline/test
	coverage report -m
	coverage html
	@echo for report : open htmlcov/index.html

mutate:
	mutmut run --paths-to-mutate . || true

clean-test:
	rm -f .coverage
	rm -rf htmlcov
	rm -rf .pytest_cache
