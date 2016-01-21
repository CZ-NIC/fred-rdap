APP = rdap

.PHONY: default isort check-isort

default:
	echo "No default action, specify the target"

isort:
	isort --recursive ${APP}

check-isort:
	isort --recursive --check-only --diff ${APP}
