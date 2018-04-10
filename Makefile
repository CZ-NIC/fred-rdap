APP = rdap

.PHONY: default test isort

default: test

test:
	tox

isort:
	isort --recursive ${APP}
