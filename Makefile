APP = rdap

.PHONY: default isort check-isort check-flake8

default:
	echo "No default action, specify the target"

isort:
	isort --recursive ${APP}

check-isort:
	isort --recursive --check-only --diff ${APP}

check-flake8:
	flake8 --config=.flake8 --format=pylint --show-source ${APP}
